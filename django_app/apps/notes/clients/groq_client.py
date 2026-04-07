from pathlib import Path

import httpx
from django.conf import settings

from apps.common.exceptions import ExternalServiceError


class GroqClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model_name: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model_name = model_name or settings.GROQ_MODEL
        self.timeout = timeout

    def generate_note(self, *, transcript_text: str, note_type: str, prompt_name: str) -> dict:
        if not self.api_key:
            raise ExternalServiceError("GROQ_API_KEY is missing.")

        prompt_body = self._load_prompt(prompt_name=prompt_name)
        response = self._post_chat_completion(prompt_body=prompt_body, transcript_text=transcript_text)

        return {
            "content": response["choices"][0]["message"]["content"],
            "model_name": response.get("model", self.model_name),
            "note_type": note_type,
            "prompt_version": prompt_name.replace(".txt", ""),
            "raw_payload": response,
        }

    def _load_prompt(self, *, prompt_name: str) -> str:
        prompt_path = Path(__file__).resolve().parent.parent / "prompts" / prompt_name
        return prompt_path.read_text(encoding="utf-8")

    def _post_chat_completion(self, *, prompt_body: str, transcript_text: str) -> dict:
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": prompt_body},
                {"role": "user", "content": transcript_text},
            ],
            "temperature": 0.2,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = httpx.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalServiceError("Groq API call failed.") from exc

        return response.json()
