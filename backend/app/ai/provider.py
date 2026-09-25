import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
import httpx
from app.config.settings import settings

logger = logging.getLogger(__name__)

class AIProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        pass

    @abstractmethod
    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        context_data: Optional[Dict[str, Any]] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> str:
        pass

    @abstractmethod
    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: Dict[str, Any],
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        pass

# -------------------------------------------------------------------------
# 1. Google Gemini Provider
# -------------------------------------------------------------------------
class GeminiProvider(AIProvider):
    @property
    def name(self) -> str:
        return "gemini"

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL or "gemini-2.5-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    async def _call_gemini(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_configured():
            raise ValueError("GEMINI_API_KEY is not configured.")

        # If test error simulation is enabled for gemini
        if settings.AI_TEST_FORCE_PROVIDER_ERROR == "429":
            raise RuntimeError("Simulated 429 Rate Limit on Gemini")
        elif settings.AI_TEST_FORCE_PROVIDER_ERROR in ["500", "503", "timeout"]:
            raise RuntimeError(f"Simulated {settings.AI_TEST_FORCE_PROVIDER_ERROR} on Gemini")

        models_to_try = [
            self.model,
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro"
        ]
        seen = set()
        models = [m for m in models_to_try if not (m in seen or seen.add(m))]

        last_err = None
        timeout = httpx.Timeout(settings.AI_REQUEST_TIMEOUT, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            for m in models:
                url = f"{self.base_url}/models/{m}:generateContent?key={self.api_key}"
                try:
                    resp = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
                    if resp.status_code == 200:
                        return resp.json()
                    elif resp.status_code in [404, 400, 429, 503]:
                        last_err = f"Model {m} status {resp.status_code}: {resp.text[:120]}"
                        continue
                    else:
                        resp.raise_for_status()
                except Exception as e:
                    last_err = e
                    continue
            raise RuntimeError(f"Gemini API call failed across models: {last_err}")

    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        context_data: Optional[Dict[str, Any]] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> str:
        contents = []
        system_instruction = None

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                system_instruction = {"parts": [{"text": content}]}
            elif role in ["user", "human"]:
                contents.append({"role": "user", "parts": [{"text": content}]})
            elif role in ["assistant", "model"]:
                contents.append({"role": "model", "parts": [{"text": content}]})

        if not contents:
            contents.append({"role": "user", "parts": [{"text": "Hello"}]})

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        if system_instruction:
            payload["system_instruction"] = system_instruction

        res = await self._call_gemini(payload)
        try:
            candidates = res.get("candidates", [])
            if not candidates:
                raise ValueError("No candidates returned by Gemini")
            parts = candidates[0].get("content", {}).get("parts", [])
            return parts[0].get("text", "").strip() if parts else ""
        except (KeyError, IndexError) as e:
            raise ValueError(f"Unexpected Gemini response format: {res}") from e

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: Dict[str, Any],
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        prompt_with_schema = (
            f"{user_prompt}\n\n"
            f"You MUST return valid JSON matching this schema:\n"
            f"{json.dumps(json_schema, indent=2)}"
        )
        payload: Dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt_with_schema}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        }
        if system_prompt:
            payload["system_instruction"] = {"parts": [{"text": system_prompt}]}

        res = await self._call_gemini(payload)
        try:
            text = res["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
        except Exception as e:
            raise ValueError(f"Failed to parse structured JSON from Gemini: {res}") from e

# -------------------------------------------------------------------------
# 2. Groq Provider (Ultra-Fast Free/Low-Cost LLM)
# -------------------------------------------------------------------------
class GroqProvider(AIProvider):
    @property
    def name(self) -> str:
        return "groq"

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL or "llama-3.3-70b-versatile"
        self.base_url = settings.GROQ_API_BASE or "https://api.groq.com/openai/v1"

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        context_data: Optional[Dict[str, Any]] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> str:
        if not self.is_configured():
            raise ValueError("GROQ_API_KEY is not configured.")

        timeout = httpx.Timeout(settings.AI_REQUEST_TIMEOUT, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: Dict[str, Any],
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if not self.is_configured():
            raise ValueError("GROQ_API_KEY is not configured.")

        prompt_with_schema = f"{user_prompt}\n\nYou MUST return valid JSON adhering to:\n{json.dumps(json_schema)}"
        messages = [
            {"role": "system", "content": system_prompt + "\nOutput strictly valid JSON."},
            {"role": "user", "content": prompt_with_schema}
        ]
        
        timeout = httpx.Timeout(settings.AI_REQUEST_TIMEOUT, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": messages,
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)

# -------------------------------------------------------------------------
# 3. OpenRouter Provider (Free-tier openrouter/free & fallback)
# -------------------------------------------------------------------------
class OpenRouterProvider(AIProvider):
    @property
    def name(self) -> str:
        return "openrouter"

    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL or "openrouter/free"
        self.base_url = settings.OPENROUTER_API_BASE or "https://openrouter.ai/api/v1"

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        context_data: Optional[Dict[str, Any]] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> str:
        if not self.is_configured():
            raise ValueError("OPENROUTER_API_KEY is not configured.")

        timeout = httpx.Timeout(settings.AI_REQUEST_TIMEOUT, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://transformiq.ai",
                "X-Title": "TransformIQ Platform",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: Dict[str, Any],
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if not self.is_configured():
            raise ValueError("OPENROUTER_API_KEY is not configured.")

        prompt_with_schema = f"{user_prompt}\n\nYou MUST return valid JSON adhering to:\n{json.dumps(json_schema)}"
        messages = [
            {"role": "system", "content": system_prompt + "\nOutput strictly valid JSON."},
            {"role": "user", "content": prompt_with_schema}
        ]
        
        timeout = httpx.Timeout(settings.AI_REQUEST_TIMEOUT, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://transformiq.ai",
                "X-Title": "TransformIQ Platform",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": messages,
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)

# -------------------------------------------------------------------------
# 4. OpenAI Provider
# -------------------------------------------------------------------------
class OpenAIProvider(AIProvider):
    @property
    def name(self) -> str:
        return "openai"

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL or "gpt-4o-mini"
        self.base_url = settings.OPENAI_API_BASE or "https://api.openai.com/v1"

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        context_data: Optional[Dict[str, Any]] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> str:
        if not self.is_configured():
            raise ValueError("OPENAI_API_KEY is not configured.")

        timeout = httpx.Timeout(settings.AI_REQUEST_TIMEOUT, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: Dict[str, Any],
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if not self.is_configured():
            raise ValueError("OPENAI_API_KEY is not configured.")

        prompt_with_schema = f"{user_prompt}\n\nYou MUST return valid JSON conforming to this schema:\n{json.dumps(json_schema)}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_with_schema}
        ]
        
        timeout = httpx.Timeout(settings.AI_REQUEST_TIMEOUT, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": messages,
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            return json.loads(content)

# -------------------------------------------------------------------------
# 5. Azure OpenAI Provider
# -------------------------------------------------------------------------
class AzureOpenAIProvider(AIProvider):
    @property
    def name(self) -> str:
        return "azure"

    def __init__(self):
        self.endpoint = settings.AZURE_OPENAI_ENDPOINT
        self.api_key = settings.AZURE_OPENAI_API_KEY
        self.deployment = settings.AZURE_OPENAI_DEPLOYMENT or "gpt-4o"
        self.api_version = settings.AZURE_OPENAI_API_VERSION or "2024-02-15-preview"

    def is_configured(self) -> bool:
        return bool(self.endpoint and self.api_key and self.endpoint.strip() and self.api_key.strip())

    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        context_data: Optional[Dict[str, Any]] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> str:
        if not self.is_configured():
            raise ValueError("Azure OpenAI endpoint/API key not configured.")

        url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
        timeout = httpx.Timeout(settings.AI_REQUEST_TIMEOUT, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: Dict[str, Any],
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if not self.is_configured():
            raise ValueError("Azure OpenAI endpoint/API key not configured.")

        url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
        prompt_with_schema = f"{user_prompt}\n\nYou MUST return valid JSON conforming to this schema:\n{json.dumps(json_schema)}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_with_schema}
        ]
        
        timeout = httpx.Timeout(settings.AI_REQUEST_TIMEOUT, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "messages": messages,
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            return json.loads(content)

# -------------------------------------------------------------------------
# 6. Provider Health & Multi-Provider Resilient Router Manager
# -------------------------------------------------------------------------
class ProviderHealth:
    def __init__(self):
        self.failures: int = 0
        self.cooldown_until: float = 0.0
        self.last_error: Optional[str] = None
        self.total_success: int = 0

    def is_available(self) -> bool:
        return time.time() >= self.cooldown_until

    def record_success(self):
        self.failures = 0
        self.cooldown_until = 0.0
        self.total_success += 1
        self.last_error = None

    def record_failure(self, error_str: str, cooldown_seconds: int = 60):
        self.failures += 1
        self.cooldown_until = time.time() + cooldown_seconds
        self.last_error = error_str
        logger.warning(f"[AI Router] Provider failure ({self.failures} consecutive). Cooling down for {cooldown_seconds}s. Reason: {error_str}")

class AIProviderRouter:
    """
    Intelligent multi-provider AI manager supporting:
    - Health-aware round-robin / Priority fallback
    - Free-first priority (Gemini -> Groq -> OpenRouter -> OpenAI -> Azure)
    - Automatic failover & retry
    - Circuit breaker cooldowns
    """
    def __init__(self):
        self.providers: Dict[str, AIProvider] = {
            "gemini": GeminiProvider(),
            "groq": GroqProvider(),
            "openrouter": OpenRouterProvider(),
            "openai": OpenAIProvider(),
            "azure": AzureOpenAIProvider(),
        }
        self.health: Dict[str, ProviderHealth] = {
            p_name: ProviderHealth() for p_name in self.providers
        }
        self._round_robin_idx = 0

    def get_provider_order(self) -> List[str]:
        raw_order = settings.AI_PROVIDER_ORDER.split(",")
        cleaned = [p.strip().lower() for p in raw_order if p.strip().lower() in self.providers]
        # Include any remaining providers
        for p in self.providers:
            if p not in cleaned:
                cleaned.append(p)
        return cleaned

    def get_candidate_providers(self) -> List[Tuple[str, AIProvider]]:
        order = self.get_provider_order()
        candidates = []
        for name in order:
            provider = self.providers[name]
            if provider.is_configured():
                health = self.health[name]
                if health.is_available():
                    candidates.append((name, provider))
                else:
                    logger.info(f"[AI Router] Provider '{name}' in cooldown until {int(health.cooldown_until - time.time())}s remaining.")
        return candidates

    async def execute_chat(
        self,
        messages: List[Dict[str, str]],
        context_data: Optional[Dict[str, Any]] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> Tuple[str, str]:
        candidates = self.get_candidate_providers()
        
        # If specific provider requested
        if settings.AI_PROVIDER != "auto" and settings.AI_PROVIDER in self.providers:
            req_name = settings.AI_PROVIDER
            req_p = self.providers[req_name]
            if req_p.is_configured():
                candidates = [(req_name, req_p)] + [c for c in candidates if c[0] != req_name]

        if not candidates:
            # Check if any configured provider is in cooldown, try the one with lowest cooldown
            configured = [(n, self.providers[n]) for n in self.get_provider_order() if self.providers[n].is_configured()]
            if configured:
                candidates = configured
            else:
                raise RuntimeError("No AI providers are configured with API keys. Please configure GEMINI_API_KEY, GROQ_API_KEY, or OPENROUTER_API_KEY.")

        last_error = None
        for name, provider in candidates:
            for retry in range(settings.AI_MAX_RETRIES):
                try:
                    logger.info(f"[AI Router] Dispatching chat request to '{name}' (attempt {retry + 1})...")
                    reply = await provider.generate_chat(
                        messages=messages,
                        context_data=context_data,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    if reply and reply.strip():
                        self.health[name].record_success()
                        return reply.strip(), name
                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"[AI Router] Provider '{name}' failed on attempt {retry + 1}: {e}")
                    self.health[name].record_failure(str(e), settings.AI_COOLDOWN_SECONDS)
                    break  # Failover to next provider in order

        raise RuntimeError(f"All available AI providers failed. Last error: {last_error}")

    async def execute_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: Dict[str, Any],
        context_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], str]:
        candidates = self.get_candidate_providers()
        
        if settings.AI_PROVIDER != "auto" and settings.AI_PROVIDER in self.providers:
            req_name = settings.AI_PROVIDER
            req_p = self.providers[req_name]
            if req_p.is_configured():
                candidates = [(req_name, req_p)] + [c for c in candidates if c[0] != req_name]

        if not candidates:
            configured = [(n, self.providers[n]) for n in self.get_provider_order() if self.providers[n].is_configured()]
            if configured:
                candidates = configured
            else:
                raise RuntimeError("No AI providers configured for structured generation.")

        last_error = None
        for name, provider in candidates:
            for retry in range(settings.AI_MAX_RETRIES):
                try:
                    logger.info(f"[AI Router] Dispatching structured JSON request to '{name}' (attempt {retry + 1})...")
                    result = await provider.generate_structured(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        json_schema=json_schema,
                        context_data=context_data
                    )
                    if isinstance(result, dict):
                        self.health[name].record_success()
                        return result, name
                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"[AI Router] Structured generation on '{name}' failed (attempt {retry + 1}): {e}")
                    self.health[name].record_failure(str(e), settings.AI_COOLDOWN_SECONDS)
                    break

        raise RuntimeError(f"All available AI providers failed structured generation. Last error: {last_error}")

ai_router = AIProviderRouter()
