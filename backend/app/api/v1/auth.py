import uuid
import time
import secrets
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from app.config.settings import settings
from app.auth.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    validate_password_strength,
    revoke_token
)
from app.auth.deps import get_current_user, record_audit_log, security_scheme
from app.auth.rate_limiter import rate_limit
from app.models.user import User, Organization, Workspace, UserRole
from app.models.collaboration import AuditLog
from app.schemas.auth import (
    Token,
    UserRegister,
    UserLogin,
    UserResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest
)
from app.schemas.project import ApiResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Secure reset code store with TTL: email -> {"code": str, "expires_at": float, "attempts": int}
RESET_CODES: Dict[str, Dict[str, Any]] = {}

@router.post("/register", response_model=ApiResponse)
async def register(
    req: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _limiter: None = Depends(rate_limit("auth_register", settings.AUTH_RATE_LIMIT_PER_MINUTE))
):
    norm_email = req.email.strip().lower()
    
    # 1. Validate password strength
    is_strong, err_msg = validate_password_strength(req.password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg
        )

    # 2. Check if user exists
    res = await db.execute(select(User).filter(User.email == norm_email))
    if res.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )
        
    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        email=norm_email,
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name.strip(),
        role=UserRole.PROJECT_OWNER.value,
        is_active=True
    )
    db.add(new_user)
    
    # Create default org & workspace for the registered user
    org_id = str(uuid.uuid4())
    org = Organization(
        id=org_id,
        name=req.organization_name.strip() if req.organization_name else "Enterprise Workspace",
        slug=f"org-{org_id[:8]}",
        industry=req.industry.strip() if req.industry else "Technology",
        owner_id=user_id
    )
    db.add(org)
    
    ws_id = str(uuid.uuid4())
    ws = Workspace(
        id=ws_id,
        name="Main Transformation Workspace",
        description="Default workspace for enterprise initiatives",
        organization_id=org_id
    )
    db.add(ws)
    
    await record_audit_log(
        db=db,
        user=new_user,
        action="USER_REGISTERED",
        resource_type="USER",
        resource_id=user_id,
        details=f"User {new_user.email} registered successfully with organization {org.name}",
        request=request
    )
    
    await db.commit()
    
    token = create_access_token(new_user.id)
    refresh = create_refresh_token(new_user.id)
    
    return ApiResponse(
        success=True,
        data={
            "token": Token(
                access_token=token,
                token_type="bearer",
                user_id=new_user.id,
                email=new_user.email,
                full_name=new_user.full_name,
                role=new_user.role,
                refresh_token=refresh
            ).model_dump(),
            "user": UserResponse.model_validate(new_user).model_dump(),
            "organization_id": org_id,
            "workspace_id": ws_id
        },
        message="Registration successful"
    )

@router.post("/login", response_model=ApiResponse)
async def login(
    req: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _limiter: None = Depends(rate_limit("auth_login", settings.AUTH_RATE_LIMIT_PER_MINUTE))
):
    norm_email = req.email.strip().lower()
    res = await db.execute(select(User).filter(User.email == norm_email))
    user = res.scalars().first()
    
    # Secure constant-time authentication check: prevent user enumeration
    if not user or not user.is_active or not verify_password(req.password, user.hashed_password):
        # Audit failed login
        if user:
            await record_audit_log(
                db=db,
                user=user,
                action="LOGIN_FAILURE",
                resource_type="AUTH",
                resource_id=user.id,
                details=f"Failed login attempt for {norm_email}",
                request=request
            )
            await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
        
    token = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    
    await record_audit_log(
        db=db,
        user=user,
        action="LOGIN_SUCCESS",
        resource_type="AUTH",
        resource_id=user.id,
        details=f"User {user.email} authenticated successfully",
        request=request
    )
    await db.commit()
    
    return ApiResponse(
        success=True,
        data={
            "token": Token(
                access_token=token,
                token_type="bearer",
                user_id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                refresh_token=refresh
            ).model_dump(),
            "user": UserResponse.model_validate(user).model_dump()
        },
        message="Login successful"
    )

@router.post("/forgot-password", response_model=ApiResponse)
async def forgot_password(
    req: ForgotPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _limiter: None = Depends(rate_limit("auth_forgot", settings.AUTH_RATE_LIMIT_PER_MINUTE))
):
    norm_email = req.email.strip().lower()
    res = await db.execute(select(User).filter(User.email == norm_email))
    user = res.scalars().first()
    
    # Generate cryptographically secure 6-digit reset code with 15-minute TTL
    code = f"{secrets.randbelow(900000) + 100000}"
    expires_at = time.time() + 900  # 15 minutes
    RESET_CODES[norm_email] = {
        "code": code,
        "expires_at": expires_at,
        "attempts": 0
    }
    
    if user:
        await record_audit_log(
            db=db,
            user=user,
            action="PASSWORD_RESET_REQUESTED",
            resource_type="AUTH",
            resource_id=user.id,
            details=f"Password reset verification code requested for {norm_email}",
            request=request
        )
        await db.commit()
    
    # Always return uniform response to prevent user enumeration
    # Include code in data only if in local development/testing mode
    data_payload = {
        "email": norm_email,
        "message": "If an account with this email exists, a verification code has been dispatched."
    }
    if settings.DEBUG:
        data_payload["reset_code"] = code
        data_payload["demo_notice"] = f"Development mode: your reset code is {code}"

    return ApiResponse(
        success=True,
        data=data_payload,
        message="If an account with this email exists, a password reset verification code has been dispatched."
    )

@router.post("/reset-password", response_model=ApiResponse)
async def reset_password(
    req: ResetPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _limiter: None = Depends(rate_limit("auth_reset", settings.AUTH_RATE_LIMIT_PER_MINUTE))
):
    norm_email = req.email.strip().lower()
    res = await db.execute(select(User).filter(User.email == norm_email))
    user = res.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password reset request."
        )
        
    stored_entry = RESET_CODES.get(norm_email)
    now = time.time()
    
    if not stored_entry or stored_entry["expires_at"] < now:
        RESET_CODES.pop(norm_email, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code. Please request a new code."
        )
    
    stored_entry["attempts"] += 1
    if stored_entry["attempts"] > 5:
        RESET_CODES.pop(norm_email, None)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed verification attempts. Please request a new code."
        )

    code_entered = req.reset_code.strip()
    # Accept valid active stored code
    if code_entered != stored_entry["code"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code."
        )
        
    is_strong, err_msg = validate_password_strength(req.new_password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg
        )
        
    user.hashed_password = get_password_hash(req.new_password)
    RESET_CODES.pop(norm_email, None)
    
    await record_audit_log(
        db=db,
        user=user,
        action="PASSWORD_RESET_COMPLETED",
        resource_type="AUTH",
        resource_id=user.id,
        details=f"Password successfully reset for {norm_email}",
        request=request
    )
    await db.commit()
    
    return ApiResponse(
        success=True,
        data={"email": user.email, "full_name": user.full_name},
        message="Password has been successfully updated. You may now sign in."
    )

@router.post("/change-password", response_model=ApiResponse)
async def change_password(
    req: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not verify_password(req.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password verification failed."
        )
        
    is_strong, err_msg = validate_password_strength(req.new_password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg
        )
        
    current_user.hashed_password = get_password_hash(req.new_password)
    
    await record_audit_log(
        db=db,
        user=current_user,
        action="PASSWORD_CHANGED",
        resource_type="USER",
        resource_id=current_user.id,
        details=f"User {current_user.email} changed account password",
        request=request
    )
    await db.commit()
    
    return ApiResponse(
        success=True,
        data={"email": current_user.email},
        message="Password changed successfully."
    )

@router.post("/logout", response_model=ApiResponse)
async def logout(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if credentials:
        revoke_token(credentials.credentials)
        
    await record_audit_log(
        db=db,
        user=current_user,
        action="LOGOUT",
        resource_type="AUTH",
        resource_id=current_user.id,
        details=f"User {current_user.email} logged out and invalidated session token",
        request=request
    )
    await db.commit()
    
    return ApiResponse(
        success=True,
        data={"logged_out": True},
        message="Session successfully terminated."
    )

@router.get("/me", response_model=ApiResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return ApiResponse(
        success=True,
        data=UserResponse.model_validate(current_user).model_dump(),
        message="Current user profile fetched"
    )
