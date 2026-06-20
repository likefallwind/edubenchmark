"""Model -> provider resolution and client factory.

The eval harness talks to several OpenAI-compatible backends through one client
class (``MiniMaxClient``). A *provider* bundles the three things that differ
between backends — base URL, the env var holding the API key, and the chat path
— so a caller only has to name a model (``--model doubao-seed-2.0-pro``) and the
right endpoint is selected automatically.

Three providers ship today:

* ``minimax``  — the original MiniMax endpoint (``MINIMAX_API_KEY``); also the
  home of the default extractor model ``MiniMax-M2.7``.
* ``gateway``  — a local OpenAI-compatible relay (``API_GATEWAY``) that fronts
  doubao / glm / deepseek and friends at ``/chat/completions``.
* ``deepseek`` — DeepSeek's official OpenAI-compatible API
  (``https://api.deepseek.com``, key env ``DEEPSEEK_API``) at
  ``/chat/completions``; serves ``deepseek-v4-pro`` and ``deepseek-v4-flash``.
  **Not used by default** — ``deepseek-*`` models route through the gateway (it
  also exposes those models). Reach the official API only when explicitly asked,
  via ``--provider deepseek``.

Model names are matched by prefix (``resolve_provider``); unknown models fall
back to the gateway, and every field can be overridden explicitly by the caller
(``build_client(..., provider=, base_url=, api_key_env=, chat_path=)``).
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

from .minimax_client import (
    DEFAULT_BASE_URL,
    DEFAULT_CHAT_PATH,
    MiniMaxClient,
)


@dataclass(frozen=True)
class Provider:
    name: str
    base_url: str
    api_key_env: str
    chat_path: str
    # Optional env var that, when set, overrides ``base_url``.
    base_url_env: str | None = None

    def resolved_base_url(self) -> str:
        if self.base_url_env:
            return os.environ.get(self.base_url_env) or self.base_url
        return self.base_url


MINIMAX = Provider(
    name="minimax",
    base_url=DEFAULT_BASE_URL,
    base_url_env="MINIMAX_BASE_URL",
    api_key_env="MINIMAX_API_KEY",
    chat_path=DEFAULT_CHAT_PATH,
)

GATEWAY = Provider(
    name="gateway",
    base_url="http://127.0.0.1:8111/v1",
    base_url_env="API_GATEWAY_BASE_URL",
    api_key_env="API_GATEWAY",
    chat_path="/chat/completions",
)

# DeepSeek's official API. OpenAI-compatible, so the same MiniMaxClient drives it
# with only base URL / key env / chat path swapped. Current models:
# ``deepseek-v4-pro`` and ``deepseek-v4-flash`` (the lighter tier; there is no
# ``deepseek-v4-lite``). ``deepseek-v4-pro`` returns a separate reasoning chain.
# Registered but NOT the default route for ``deepseek-*`` models — those go to
# the gateway (see ``_PREFIX_PROVIDER``). Select this explicitly with
# ``--provider deepseek`` when the official endpoint is specifically wanted.
DEEPSEEK = Provider(
    name="deepseek",
    base_url="https://api.deepseek.com",
    base_url_env="DEEPSEEK_BASE_URL",
    api_key_env="DEEPSEEK_API",
    chat_path="/chat/completions",
)

PROVIDERS: dict[str, Provider] = {p.name: p for p in (MINIMAX, GATEWAY, DEEPSEEK)}

# Model-name prefixes -> provider name. Longest match wins.
# ``deepseek-*`` defaults to the gateway (it serves deepseek-v4-pro/-flash too);
# use ``--provider deepseek`` to reach the official API when specifically needed.
_PREFIX_PROVIDER: list[tuple[str, str]] = [
    ("minimax", "minimax"),
    ("doubao", "gateway"),
    ("glm", "gateway"),
    ("deepseek", "gateway"),
]

# Provider used when no prefix matches a given model name.
_DEFAULT_PROVIDER = "gateway"


def resolve_provider(model: str) -> Provider:
    """Pick the provider for ``model`` by case-insensitive prefix match."""
    low = (model or "").lower()
    for prefix, provider in _PREFIX_PROVIDER:
        if low.startswith(prefix):
            return PROVIDERS[provider]
    return PROVIDERS[_DEFAULT_PROVIDER]


def build_client(
    model: str,
    timeout: int = 300,
    *,
    provider: str | None = None,
    base_url: str | None = None,
    api_key_env: str | None = None,
    chat_path: str | None = None,
) -> MiniMaxClient:
    """Construct a client for ``model`` against its resolved provider.

    Explicit ``provider`` / ``base_url`` / ``api_key_env`` / ``chat_path`` args
    override the auto-resolved provider (escape hatch for models not in the
    prefix table). Raises a clear error if the key env var is unset.
    """
    prov = PROVIDERS[provider] if provider else resolve_provider(model)
    url = base_url or prov.resolved_base_url()
    path = chat_path or prov.chat_path
    key_env = api_key_env or prov.api_key_env
    api_key = os.environ.get(key_env)
    if not api_key:
        raise RuntimeError(
            f"environment variable {key_env} is not set "
            f"(needed for model {model!r} via provider {prov.name!r})"
        )
    return MiniMaxClient(
        model=model,
        base_url=url,
        api_key=api_key,
        timeout=timeout,
        chat_path=path,
    )


# Directory-name aliases: keep a model's artifacts in a historical/preferred dir
# regardless of how its raw name would slugify. ``MiniMax-M3`` predates the slug
# convention and its baseline lives under ``minimax3/``.
_SLUG_ALIASES = {"MiniMax-M3": "minimax3"}


def model_slug(model: str) -> str:
    """Filesystem-safe directory name for a model.

    Honors ``_SLUG_ALIASES`` first; otherwise keeps letters, digits, dot, dash,
    underscore and collapses everything else to a single dash. ``doubao-seed-2.0-pro``
    and ``glm-5.1`` pass through unchanged.
    """
    if model in _SLUG_ALIASES:
        return _SLUG_ALIASES[model]
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", (model or "").strip())
    return slug.strip("-") or "model"
