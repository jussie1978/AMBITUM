"""Local llama.cpp VLM transcription for one governed in-memory image."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from io import BytesIO

import httpx
from PIL import Image

from app.config import settings


ENGINE_NAME = "qwen3-vl"
TRANSCRIPTION_PROMPT = """Objetivo: extração fiel de texto visível.

Regras:
- transcrever somente o que estiver visível;
- não resumir;
- não interpretar;
- não corrigir conteúdo;
- não completar palavras ilegíveis;
- preservar números, nomes, pontuação e quebras relevantes;
- quando algo estiver ilegível, marcar de forma neutra, sem inventar;
- responder somente com a transcrição."""


class VLMExecutionError(Exception):
    """A technical failure from the configured local VLM endpoint."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


@dataclass(frozen=True)
class VLMTextResult:
    raw_text: str
    text_obtained: bool
    engine: str
    engine_version: str


def _http_client() -> httpx.Client:
    return httpx.Client(timeout=settings.vlm_timeout_seconds, trust_env=False)


def _image_data_url(image: Image.Image) -> str:
    buffer = BytesIO()
    image.convert("RGB").save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _response_text(payload: object) -> str:
    if not isinstance(payload, dict):
        raise VLMExecutionError("vlm_invalid_response", "VLM response is not an object.")
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise VLMExecutionError("vlm_invalid_response", "VLM response has no choice.")
    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise VLMExecutionError("vlm_invalid_response", "VLM response has no message.")
    content = message.get("content")
    if content is None:
        return ""
    if not isinstance(content, str):
        raise VLMExecutionError("vlm_invalid_response", "VLM message content is not text.")
    return content.strip()


def extract_vlm_image(image: Image.Image) -> VLMTextResult:
    """Transcribe one in-memory image through the configured local server."""
    if not isinstance(image, Image.Image):
        raise TypeError("image must be a PIL.Image.Image")

    endpoint = f"{settings.vlm_base_url.rstrip('/')}/chat/completions"
    request_payload = {
        "model": settings.vlm_model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": TRANSCRIPTION_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": _image_data_url(image)},
                    },
                ],
            }
        ],
        "temperature": 0,
    }
    try:
        with _http_client() as client:
            response = client.post(endpoint, json=request_payload)
            response.raise_for_status()
            payload = response.json()
    except httpx.TimeoutException as exc:
        raise VLMExecutionError("vlm_timeout", "Local VLM request timed out.") from exc
    except httpx.HTTPStatusError as exc:
        raise VLMExecutionError(
            "vlm_http_error",
            f"Local VLM returned HTTP {exc.response.status_code}.",
        ) from exc
    except (httpx.HTTPError, ValueError) as exc:
        raise VLMExecutionError("vlm_transport_error", "Local VLM request failed.") from exc

    raw_text = _response_text(payload)
    return VLMTextResult(
        raw_text=raw_text,
        text_obtained=bool(raw_text),
        engine=ENGINE_NAME,
        engine_version=settings.vlm_model,
    )
