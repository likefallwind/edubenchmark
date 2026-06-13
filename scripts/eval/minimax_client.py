"""MiniMax chat client (OpenAI-compatible endpoint) with vision support.

Reads ``MINIMAX_API_KEY`` from the environment. The base URL can be overridden
with ``MINIMAX_BASE_URL`` (default ``https://api.minimaxi.com/v1``); requests go
to ``<base><chat_path>`` where ``chat_path`` defaults to
``/text/chatcompletion_v2`` (MiniMax) and can be overridden with
``MINIMAX_CHAT_PATH`` — set it to ``/chat/completions`` to point at any other
OpenAI-compatible provider (OpenAI, DeepSeek, vLLM, Together, ...). The request
shape, vision ``image_url`` parts, and the streaming SSE wire format are all the
OpenAI standard, so switching models is a config change, not a code change.

Unlike the anthropic-endpoint helper in ``run_re_benchmark_v1.py`` (model
``MiniMax-M2.7``, text-only), this client sends OpenAI-style ``content`` parts so
a vision model such as ``MiniMax-M3`` can receive base64 ``image_url`` blocks.

A ``message`` for this client is ``{"role": ..., "content": <str | list[part]>}``
where each part is ``{"type": "text", "text": ...}`` or
``{"type": "image_url", "image_url": {"url": "data:image/...;base64,..."}}``.

Requests **stream by default** (``stream=True``): the server emits tokens as it
generates them, so the socket ``timeout`` becomes a *stall* timeout (max gap
between chunks) rather than a budget on total generation time. A reasoning model
that thinks for many minutes keeps the connection fed and never trips it; only a
genuinely hung connection does. Pass ``stream=False`` for the legacy
single-blob response.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://api.minimaxi.com/v1"
DEFAULT_CHAT_PATH = "/text/chatcompletion_v2"
DEFAULT_MODEL = "MiniMax-M3"


def encode_image_data_uri(path: Path) -> str:
    """Read a local image and return a ``data:<mime>;base64,<...>`` URI."""
    mime = mimetypes.guess_type(str(path))[0] or "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def text_part(text: str) -> dict[str, Any]:
    return {"type": "text", "text": text}


def image_part(path: Path) -> dict[str, Any]:
    return {"type": "image_url", "image_url": {"url": encode_image_data_uri(path)}}


class MiniMaxClient:
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: int = 300,
        chat_path: str | None = None,
    ) -> None:
        self.model = model
        self.base_url = (base_url or os.environ.get("MINIMAX_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.api_key = api_key or os.environ.get("MINIMAX_API_KEY")
        self.timeout = timeout
        path = chat_path or os.environ.get("MINIMAX_CHAT_PATH") or DEFAULT_CHAT_PATH
        self.chat_path = "/" + path.lstrip("/")

    def _require_key(self) -> str:
        if not self.api_key:
            raise RuntimeError("MINIMAX_API_KEY is not set")
        return self.api_key

    def chat(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        max_tokens: int | None = None,
        timeout: int | None = None,
        stream: bool = True,
    ) -> str:
        """Send a chat request and return the concatenated text reply.

        When ``stream`` is True (default) the response is read as an SSE token
        stream; the ``timeout`` then bounds the gap between chunks, not the total
        generation time, so long reasoning generations no longer time out.
        """
        api_key = self._require_key()
        payload: dict[str, Any] = {
            "model": model or self.model,
            "messages": messages,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if stream:
            payload["stream"] = True
        request = urllib.request.Request(
            f"{self.base_url}{self.chat_path}",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout or self.timeout) as response:
                if stream:
                    return read_sse_stream(response)
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"MiniMax HTTP {exc.code}: {body[:500]}") from exc
        return extract_text(data)


def _delta_text(choice: dict[str, Any]) -> str:
    """Pull incremental answer text from one streaming ``choices[]`` entry.

    Reads ``delta.content`` only (the visible answer); ``delta.reasoning_content``
    — emitted by reasoning models like MiniMax-M3 / DeepSeek-R1 — is intentionally
    ignored so the returned text is the answer, not the chain of thought. The
    reasoning chunks still count as wire activity, which is what keeps the stall
    timeout from firing during a long think.
    """
    delta = (choice or {}).get("delta") or {}
    content = delta.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            str(b.get("text", ""))
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        ]
        return "".join(parts)
    return ""


def read_sse_stream(response: Any) -> str:
    """Accumulate assistant text from an OpenAI-compatible SSE token stream.

    Each event is a ``data: {json}`` line; the stream ends at ``data: [DONE]``.
    Only ``choices[].delta.content`` is concatenated (see ``_delta_text``); the
    final usage/finish chunk carries no delta and is skipped, so MiniMax's habit
    of repeating the full message in the last chunk does not double-count. Reading
    line by line lets the per-read socket timeout act as a stall detector.
    """
    parts: list[str] = []
    for raw in response:
        line = raw.decode("utf-8", errors="replace").strip() if isinstance(raw, (bytes, bytearray)) else str(raw).strip()
        if not line or not line.startswith("data:"):
            continue
        data = line[len("data:"):].strip()
        if data == "[DONE]":
            break
        try:
            obj = json.loads(data)
        except json.JSONDecodeError:
            continue
        base_resp = obj.get("base_resp") or {}
        status_code = base_resp.get("status_code")
        if status_code not in (None, 0):
            raise RuntimeError(f"MiniMax base_resp {status_code}: {base_resp.get('status_msg')}")
        for choice in obj.get("choices") or []:
            parts.append(_delta_text(choice))
    return "".join(parts).strip()


def extract_text(data: dict[str, Any]) -> str:
    """Pull assistant text out of an OpenAI-style chat completion response."""
    choices = data.get("choices") or []
    parts: list[str] = []
    for choice in choices:
        message = (choice or {}).get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(str(block.get("text", "")))
                elif isinstance(block, str):
                    parts.append(block)
    text = "\n".join(p for p in parts if p).strip()
    if text:
        return text
    # Surface API-level errors (e.g. base_resp status) instead of silent empties.
    base_resp = data.get("base_resp") or {}
    status_code = base_resp.get("status_code")
    if status_code not in (None, 0):
        raise RuntimeError(f"MiniMax base_resp {status_code}: {base_resp.get('status_msg')}")
    return ""
