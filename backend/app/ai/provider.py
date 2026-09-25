import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import httpx
from app.config.settings import settings

logger = logging.getLogger(__name__)

class AIProvider(ABC):
    @abstractmethod
    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: Dict[str, Any],
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        context_data: Optional[Dict[str, Any]] = None
    ) -> str:
        pass

class GeminiProvider(AIProvider):
    """Google Gemini AI Provider with generous free tier access."""
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL or "gemini-3.5-flash-lite"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def _call_gemini(self, payload: Dict[str, Any], model_override: Optional[str] = None) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured")

        models_to_try = [
            model_override or self.model,
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-3.5-flash",
            "gemini-3.6-flash",
            "gemini-flash-lite-latest",
            "gemini-flash-latest",
            "gemma-4-26b-a4b-it"
        ]
        # Remove duplicates while preserving order
        seen = set()
        models = [m for m in models_to_try if not (m in seen or seen.add(m))]

        last_err = None
        async with httpx.AsyncClient(timeout=20.0) as client:
            for m in models:
                url = f"{self.base_url}/models/{m}:generateContent?key={self.api_key}"
                try:
                    resp = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
                    if resp.status_code == 200:
                        return resp.json()
                    elif resp.status_code in [404, 400, 429, 503]:
                        last_err = f"Model {m} returned {resp.status_code}: {resp.text[:150]}"
                        continue
                    else:
                        resp.raise_for_status()
                except Exception as e:
                    last_err = e
                    continue
            raise RuntimeError(f"Gemini API request failed across models {models}: {last_err}")

    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        context_data: Optional[Dict[str, Any]] = None
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

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048
            }
        }
        if system_instruction:
            payload["system_instruction"] = system_instruction

        res = await self._call_gemini(payload)
        try:
            candidates = res.get("candidates", [])
            if not candidates:
                raise ValueError("No candidates returned from Gemini")
            parts = candidates[0].get("content", {}).get("parts", [])
            return parts[0].get("text", "") if parts else ""
        except (KeyError, IndexError) as e:
            raise ValueError(f"Unexpected Gemini response structure: {res}") from e

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: Dict[str, Any],
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        prompt_with_schema = (
            f"{user_prompt}\n\n"
            f"You MUST return strictly valid JSON matching this schema:\n"
            f"{json.dumps(json_schema, indent=2)}"
        )
        payload = {
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
            raise ValueError(f"Failed to parse Gemini structured JSON output: {res}") from e

class OpenAIProvider(AIProvider):
    def __init__(self):
        import httpx
        self.client = httpx.AsyncClient(timeout=60.0)
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.base_url = settings.OPENAI_API_BASE or "https://api.openai.com/v1"

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: Dict[str, Any],
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt_with_schema = f"{user_prompt}\n\nYou MUST return valid JSON conforming to this schema:\n{json.dumps(json_schema)}"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_with_schema}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }
        
        resp = await self.client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return json.loads(content)

    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        context_data: Optional[Dict[str, Any]] = None
    ) -> str:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7
        }
        resp = await self.client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

class AzureOpenAIProvider(AIProvider):
    def __init__(self):
        import httpx
        self.client = httpx.AsyncClient(timeout=60.0)
        self.endpoint = settings.AZURE_OPENAI_ENDPOINT
        self.api_key = settings.AZURE_OPENAI_API_KEY
        self.deployment = settings.AZURE_OPENAI_DEPLOYMENT
        self.api_version = settings.AZURE_OPENAI_API_VERSION

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: Dict[str, Any],
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if not self.api_key or not self.endpoint:
            raise ValueError("Azure OpenAI credentials not configured")

        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
        prompt_with_schema = f"{user_prompt}\n\nYou MUST return valid JSON conforming to this schema:\n{json.dumps(json_schema)}"
        
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_with_schema}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }
        resp = await self.client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return json.loads(content)

    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        context_data: Optional[Dict[str, Any]] = None
    ) -> str:
        if not self.api_key or not self.endpoint:
            raise ValueError("Azure OpenAI credentials not configured")

        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
        payload = {
            "messages": messages,
            "temperature": 0.7
        }
        resp = await self.client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
