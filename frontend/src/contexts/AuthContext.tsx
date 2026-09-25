import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import { User } from '../types';
import {
  hasPermission as checkHasPermission,
  hasAnyPermission as checkHasAnyPermission,
  hasAllPermissions as checkHasAllPermissions,
  canView as checkCanView,
  canEdit as checkCanEdit,
  canCreate as checkCanCreate,
  canDelete as checkCanDelete,
  canApprove as checkCanApprove,
  isReadOnlyRole,
  VALID_ROLES
} from '../utils/permissions';

export interface AuthContextType {
  user: User | null;
  token: string | null;
  role: string; // Effective UI role (evaluationRole if in evaluation mode)
  actualRole: string; // Real immutable database role
  evaluationRole: string; // Current evaluation preview role
  isEvaluationMode: boolean; // True only when real ADMIN is previewing a non-admin role
  isRealAdmin: boolean; // True only if actual database role is ADMIN
  isAuthenticated: boolean;
  isLoading: boolean;
  isReadOnly: boolean;
  hasPermission: (permissionKey: string) => boolean;
  hasAnyPermission: (permissionKeys: string[]) => boolean;
  hasAllPermissions: (permissionKeys: string[]) => boolean;
  canView: (moduleName: string) => boolean;
  canEdit: (moduleName: string) => boolean;
  canCreate: (moduleName: string) => boolean;
  canDelete: (moduleName: string) => boolean;
  canApprove: (moduleName: string) => boolean;
  login: (email: string, password: string) => Promise<User | undefined>;
  setEvaluationRole: (targetRole: string) => Promise<void>;
  switchRole: (targetRole: string) => Promise<void>; // Alias for setEvaluationRole
  exitEvaluationMode: () => Promise<void>;
  register: (email: string, password: string, full_name: string, org_name?: string, industry?: string) => Promise<User | undefined>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  role: 'VIEWER',
  actualRole: 'VIEWER',
  evaluationRole: 'VIEWER',
  isEvaluationMode: false,
  isRealAdmin: false,
  isAuthenticated: false,
  isLoading: true,
  isReadOnly: true,
  hasPermission: () => false,
  hasAnyPermission: () => false,
  hasAllPermissions: () => false,
  canView: () => false,
  canEdit: () => false,
  canCreate: () => false,
  canDelete: () => false,
  canApprove: () => false,
  login: async () => undefined,
  setEvaluationRole: async () => {},
  switchRole: async () => {},
  exitEvaluationMode: async () => {},
  register: async () => undefined,
  logout: () => {},
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('transformiq_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [evalRole, setEvalRole] = useState<string>(() => sessionStorage.getItem('transformiq_eval_role') || 'ADMIN');

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('transformiq_token');
      if (storedToken) {
        try {
          const res: any = await api.get('/auth/me');
          if (res.success && res.data) {
            setUser(res.data);
            setToken(storedToken);
            
            // Only preserve evaluation role if user is an ADMIN in database
            const realRole = (res.data.role || 'VIEWER').toUpperCase();
            if (realRole === 'ADMIN') {
              const savedEval = sessionStorage.getItem('transformiq_eval_role');
              if (savedEval && VALID_ROLES.includes(savedEval as any)) {
                setEvalRole(savedEval);
              } else {
                setEvalRole('ADMIN');
              }
            } else {
              // Non-admin accounts must NEVER have an evaluation role
              sessionStorage.removeItem('transformiq_eval_role');
              setEvalRole(realRole);
            }
          } else {
            throw new Error('Invalid auth token payload');
          }
        } catch (e) {
          console.warn('Session expired or invalid token:', e);
          localStorage.removeItem('transformiq_token');
          sessionStorage.removeItem('transformiq_eval_role');
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);

  // Real immutable database role
  const actualRole = (user?.role || 'VIEWER').toUpperCase();
  const isRealAdmin = actualRole === 'ADMIN';

  // Evaluation role is ONLY allowed for real ADMIN accounts.
  // For non-admin users, evaluationRole is ALWAYS equal to their actualRole.
  const evaluationRole = isRealAdmin ? (evalRole || 'ADMIN') : actualRole;
  const isEvaluationMode = isRealAdmin && evaluationRole !== 'ADMIN';

  // Effective UI role used across navigation, sidebars, and permission checks
  const effectiveRole = isEvaluationMode ? evaluationRole : actualRole;
  const isReadOnly = isReadOnlyRole(effectiveRole);

  // Permission utilities bound to effectiveRole
  const hasPermission = useCallback((perm: string) => checkHasPermission(effectiveRole, perm), [effectiveRole]);
  const hasAnyPermission = useCallback((perms: string[]) => checkHasAnyPermission(effectiveRole, perms), [effectiveRole]);
  const hasAllPermissions = useCallback((perms: string[]) => checkHasAllPermissions(effectiveRole, perms), [effectiveRole]);
  const canView = useCallback((mod: string) => checkCanView(effectiveRole, mod), [effectiveRole]);
  const canEdit = useCallback((mod: string) => checkCanEdit(effectiveRole, mod), [effectiveRole]);
  const canCreate = useCallback((mod: string) => checkCanCreate(effectiveRole, mod), [effectiveRole]);
  const canDelete = useCallback((mod: string) => checkCanDelete(effectiveRole, mod), [effectiveRole]);
  const canApprove = useCallback((mod: string) => checkCanApprove(effectiveRole, mod), [effectiveRole]);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const res: any = await api.post('/auth/login', { email, password });
      if (res.success && res.data) {
        const authToken = res.data.token.access_token;
        localStorage.setItem('transformiq_token', authToken);
        sessionStorage.removeItem('transformiq_eval_role');
        setToken(authToken);
        setUser(res.data.user);
        const roleUpper = res.data.user.role.toUpperCase();
        setEvalRole(roleUpper);
        return res.data.user;
      }
      throw new Error(res?.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Set Evaluation Role (strictly ADMIN only)
   * Does NOT modify database `users.role` - updates temporary UI evaluation context.
   */
  const setEvaluationRole = async (targetRole: string) => {
    if (!isRealAdmin) {
      console.error('SECURITY WARNING: Privilege escalation attempt blocked. Evaluation mode is restricted to ADMIN.');
      return;
    }

    const cleanTarget = targetRole.toUpperCase();
    if (!VALID_ROLES.includes(cleanTarget as any)) {
      console.warn(`Unknown evaluation role requested: ${targetRole}`);
      return;
    }

    const prevRole = evaluationRole;
    setEvalRole(cleanTarget);

    if (cleanTarget === 'ADMIN') {
      sessionStorage.removeItem('transformiq_eval_role');
    } else {
      sessionStorage.setItem('transformiq_eval_role', cleanTarget);
    }

    // Send server-side audit event
    try {
      await api.post('/admin/evaluation-role', {
        evaluation_role: cleanTarget,
        previous_evaluation_role: prevRole,
        action: cleanTarget === 'ADMIN'
          ? 'ROLE_EVALUATION_EXITED'
          : (prevRole === 'ADMIN' ? 'ROLE_EVALUATION_STARTED' : 'ROLE_EVALUATION_SWITCHED')
      });
    } catch (err) {
      console.warn('Evaluation audit logging error (non-fatal):', err);
    }
  };

  /**
   * Exit Evaluation Mode (Restore Admin Context)
   */
  const exitEvaluationMode = async () => {
    if (!isRealAdmin) return;
    const prevRole = evaluationRole;
    setEvalRole('ADMIN');
    sessionStorage.removeItem('transformiq_eval_role');

    try {
      await api.post('/admin/evaluation-role', {
        evaluation_role: 'ADMIN',
        previous_evaluation_role: prevRole,
        action: 'ROLE_EVALUATION_EXITED'
      });
    } catch (err) {
      console.warn('Exit evaluation audit error:', err);
    }
  };

  const register = async (email: string, password: string, full_name: string, org_name?: string, industry?: string) => {
    setIsLoading(true);
    try {
      const res: any = await api.post('/auth/register', {
        email,
        password,
        full_name,
        organization_name: org_name,
        industry
      });
      if (res.success && res.data) {
        const authToken = res.data.token.access_token;
        localStorage.setItem('transformiq_token', authToken);
        sessionStorage.removeItem('transformiq_eval_role');
        setToken(authToken);
        setUser(res.data.user);
        const roleUpper = res.data.user.role.toUpperCase();
        setEvalRole(roleUpper);
        return res.data.user;
      }
      throw new Error(res?.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('transformiq_token');
    sessionStorage.removeItem('transformiq_eval_role');
    sessionStorage.clear();
    setToken(null);
    setUser(null);
    setEvalRole('ADMIN');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        role: effectiveRole,
        actualRole,
        evaluationRole,
        isEvaluationMode,
        isRealAdmin,
        isAuthenticated: !!user,
        isLoading,
        isReadOnly,
        hasPermission,
        hasAnyPermission,
        hasAllPermissions,
        canView,
        canEdit,
        canCreate,
        canDelete,
        canApprove,
        login,
        setEvaluationRole,
        switchRole: setEvaluationRole,
        exitEvaluationMode,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
