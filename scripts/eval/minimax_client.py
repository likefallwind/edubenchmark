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
import threading
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


_USAGE_FIELDS = ("prompt_tokens", "completion_tokens", "total_tokens")


def _empty_window() -> dict[str, int]:
    # ``reasoning_tokens`` is the chain-of-thought billed by reasoning models,
    # summed from ``usage.completion_tokens_details.reasoning_tokens`` when
    # present. It is the only reasoning trace that survives on the non-streamed
    # path (gpt-5.5 via LIGHTER omits the reasoning text there); on the streaming
    # path the text itself is also captured (see ``_delta_reasoning``).
    return {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "reasoning_tokens": 0,
        "calls": 0,
    }


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
        extra_params: dict[str, Any] | None = None,
    ) -> None:
        self.model = model
        self.base_url = (base_url or os.environ.get("MINIMAX_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.api_key = api_key or os.environ.get("MINIMAX_API_KEY")
        self.timeout = timeout
        path = chat_path or os.environ.get("MINIMAX_CHAT_PATH") or DEFAULT_CHAT_PATH
        self.chat_path = "/" + path.lstrip("/")
        # Extra request-body fields merged into every chat() payload, e.g. a
        # reasoning model's default ``{"reasoning_effort": "medium"}``. Per-call
        # ``max_tokens`` / ``stream`` still take precedence over anything here.
        self.extra_params = dict(extra_params or {})
        # Per-thread token-usage accumulator. A caller brackets one logical unit
        # of work (e.g. predicting / extracting one item, including retries) with
        # reset_usage_window() ... read_usage_window(); every chat() call in
        # between adds its API-reported usage. Thread-local so concurrent items
        # sharing one client never cross-count.
        self._usage_tls = threading.local()
        # Per-thread store of the most recent chat()'s reasoning text (the visible
        # chain-of-thought some models return in ``reasoning_content``). It mirrors
        # the kept ``response``: each chat() overwrites it, so reading it right
        # after a chat() (or after the retry loop) gives the reasoning that
        # accompanies the returned answer. Empty string when the provider doesn't
        # send reasoning text (non-reasoning models, or the non-streamed path for
        # providers that only return it while streaming).
        self._reasoning_tls = threading.local()

    def reset_usage_window(self) -> None:
        """Zero this thread's usage window before measuring a unit of work."""
        self._usage_tls.window = _empty_window()

    def read_last_reasoning(self) -> str:
        """Return the reasoning text captured by this thread's most recent chat()."""
        return getattr(self._reasoning_tls, "text", "") or ""

    def read_usage_window(self) -> dict[str, int]:
        """Return a copy of this thread's accumulated usage since the last reset."""
        return dict(getattr(self._usage_tls, "window", None) or _empty_window())

    def _record_usage(self, usage: dict[str, Any] | None) -> None:
        """Add one API response's usage to this thread's window (calls += 1).

        ``usage`` is None / empty when the provider omits it (some gateways or
        self-hosted endpoints): we still bump ``calls`` so a window with calls>0
        but zero tokens is distinguishable from "no call happened".
        """
        window = getattr(self._usage_tls, "window", None)
        if window is None:
            window = _empty_window()
            self._usage_tls.window = window
        window["calls"] += 1
        if not isinstance(usage, dict):
            return
        for field in _USAGE_FIELDS:
            value = usage.get(field)
            if isinstance(value, (int, float)):
                window[field] += int(value)
        # Hidden reasoning tokens live under completion_tokens_details for
        # OpenAI-style reasoning models (gpt-5.5, o-series, DeepSeek-R1, ...).
        details = usage.get("completion_tokens_details")
        if isinstance(details, dict):
            rtok = details.get("reasoning_tokens")
            if isinstance(rtok, (int, float)):
                window["reasoning_tokens"] += int(rtok)

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
        # Client-level defaults (e.g. reasoning_effort); explicit per-call args
        # below override any colliding key.
        if self.extra_params:
            payload.update(self.extra_params)
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if stream:
            payload["stream"] = True
            # Ask OpenAI-compatible endpoints to emit a final usage chunk. Servers
            # that don't support it ignore the unknown field; usage is then simply
            # absent and _record_usage(None) just counts the call.
            payload["stream_options"] = {"include_usage": True}
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
                    text, reasoning, usage = read_sse_stream(response)
                    self._record_usage(usage)
                    self._reasoning_tls.text = reasoning
                    return text
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"MiniMax HTTP {exc.code}: {body[:500]}") from exc
        self._record_usage(data.get("usage"))
        self._reasoning_tls.text = extract_reasoning(data)
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


def _delta_reasoning(choice: dict[str, Any]) -> str:
    """Pull incremental reasoning text from one streaming ``choices[]`` entry.

    Reasoning models (MiniMax-M3, DeepSeek-R1, GLM, ...) stream their visible
    chain-of-thought under ``delta.reasoning_content`` (a few use ``reasoning``).
    Captured separately from the answer so the kept ``content`` stays clean while
    the thinking is still preserved for the run record.
    """
    delta = (choice or {}).get("delta") or {}
    value = delta.get("reasoning_content")
    if value is None:
        value = delta.get("reasoning")
    return value if isinstance(value, str) else ""


def read_sse_stream(response: Any) -> tuple[str, str, dict[str, Any] | None]:
    """Accumulate assistant text + token usage from an OpenAI SSE token stream.

    Each event is a ``data: {json}`` line; the stream ends at ``data: [DONE]``.
    Only ``choices[].delta.content`` is concatenated (see ``_delta_text``); the
    final usage/finish chunk carries no delta and is skipped for text, so
    MiniMax's habit of repeating the full message in the last chunk does not
    double-count. Any chunk's top-level ``usage`` object (emitted by endpoints
    that honor ``stream_options.include_usage``) is captured, last non-empty one
    winning; it is None when the provider doesn't send one. Reading line by line
    lets the per-read socket timeout act as a stall detector.

    ``delta.reasoning_content`` is accumulated separately (see ``_delta_reasoning``)
    so a reasoning model's chain-of-thought is preserved without polluting the
    answer text.

    Returns ``(text, reasoning, usage)``.
    """
    parts: list[str] = []
    reasoning_parts: list[str] = []
    usage: dict[str, Any] | None = None
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
        chunk_usage = obj.get("usage")
        if isinstance(chunk_usage, dict) and chunk_usage:
            usage = chunk_usage
        for choice in obj.get("choices") or []:
            parts.append(_delta_text(choice))
            reasoning_parts.append(_delta_reasoning(choice))
    return "".join(parts).strip(), "".join(reasoning_parts).strip(), usage


def extract_reasoning(data: dict[str, Any]) -> str:
    """Pull reasoning text from a non-streamed OpenAI-style chat completion.

    Mirrors ``_delta_reasoning`` for the blob response: reads
    ``choices[].message.reasoning_content`` (or ``reasoning``). Empty when the
    provider hides reasoning (e.g. gpt-5.5 via LIGHTER returns only the count).
    """
    parts: list[str] = []
    for choice in data.get("choices") or []:
        message = (choice or {}).get("message") or {}
        value = message.get("reasoning_content")
        if value is None:
            value = message.get("reasoning")
        if isinstance(value, str) and value:
            parts.append(value)
    return "\n".join(parts).strip()


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
