"""Model -> provider resolution and client factory.

The eval harness talks to several OpenAI-compatible backends through one client
class (``MiniMaxClient``). A *provider* bundles the three things that differ
between backends — base URL, the env var holding the API key, and the chat path
— so a caller only has to name a model (``--model doubao-seed-2.0-pro``) and the
right endpoint is selected automatically.

Five providers ship today:

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
* ``lighter``  — the LIGHTER API aggregator (``https://lightingtheword.com/v1``,
  key env ``LIGHTER_API``) at ``/chat/completions``; one key fronts GPT / Claude
  / Gemini / DeepSeek / Qwen / GLM via the OpenAI Chat Completions format. Home
  of the ``gpt-*`` models; ``gpt-5.5`` is a reasoning model defaulting to
  ``reasoning_effort: medium`` (see ``_MODEL_PARAMS`` / ``resolve_model_params``).
* ``zgc``     — the ZGC relay (``https://zgc.apihy.com/v1``, key env ``ZGC_API``)
  at ``/chat/completions``. Registered for exactly one model, ``deepseek-v3.2``,
  and it is that model's **default** route: the official API has retired V3.2 and
  the gateway 404s it. Other ``deepseek-*`` models still go to the gateway.

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
    # Optional allowlist of model names this provider is known to serve. ``None``
    # means "unrestricted" (the default) — the provider is a broad aggregator or
    # its catalogue is not pinned down. When set, ``build_client`` rejects other
    # models up front instead of letting a typo become a 404 mid-run.
    models: frozenset[str] | None = None

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

# The LIGHTER API aggregator, keyed by ``LIGHTER_API``. OpenAI-compatible, so the
# same MiniMaxClient drives it; one key fronts many vendors' models. Base URL
# already includes ``/v1``, so the chat path is ``/chat/completions``. Home of the
# ``gpt-*`` models (e.g. ``gpt-5.5``, which defaults to ``reasoning_effort:
# medium`` — see ``_MODEL_PARAMS``).
LIGHTER = Provider(
    name="lighter",
    base_url="https://lightingtheword.com/v1",
    base_url_env="LIGHTER_BASE_URL",
    api_key_env="LIGHTER_API",
    chat_path="/chat/completions",
)

# The ZGC relay (``https://zgc.apihy.com/v1``, key ``ZGC_API``). It fronts ~109
# models, but only ``deepseek-v3.2`` is registered here: it is the one route the
# local gateway cannot supply an equivalent for, since DeepSeek's official API has
# retired the V3.2 generation (it now lists only ``deepseek-v4-flash`` /
# ``deepseek-v4-pro``).
#
# Identity checked 2026-07-18 against the official API and against this relay's own
# ``deepseek-v4-flash`` route. ``zgc/deepseek-v3.2`` is **not** a rebadged V4: it
# disagrees with both V4 routes on arithmetic and character-counting at
# temperature 0, its ``prompt_tokens`` sit a constant +6 above theirs (same
# DeepSeek tokenizer, plus a ~6-token server-side wrapper), and it answers from a
# different serving stack (``as-*`` request ids, no ``system_fingerprint``, versus
# the relay's own vLLM-backed ``chatcmpl-*`` V4 route). What could not be
# confirmed is the converse — that it is specifically V3.2 — because no official
# V3.2 reference is reachable any more. Treat the label as unverified upstream.
#
# ``deepseek-v3.2-think`` is the reasoning variant of the same model and is served
# here too; it routes to this provider by the same prefix entry.
#
# This is the **default route for ``deepseek-v3.2*``** (``_PREFIX_PROVIDER``): the
# local gateway still lists the model but 404s ``UnsupportedModel`` on every call
# (verified 2026-07-18), so ZGC is the only live route. Other ``deepseek-*`` models
# are unaffected and still resolve to the gateway.
#
# Results written before this switch came from the gateway route and share the same
# ``reports/eval/<benchmark>/deepseek-v3.2/`` directory. They are not directly
# comparable to ZGC-served runs — different backend, different serving stack — so
# re-run rather than append if a directory predates 2026-07-18.
ZGC = Provider(
    name="zgc",
    base_url="https://zgc.apihy.com/v1",
    base_url_env="ZGC_BASE_URL",
    api_key_env="ZGC_API",
    chat_path="/chat/completions",
    models=frozenset({"deepseek-v3.2", "deepseek-v3.2-think"}),
)

PROVIDERS: dict[str, Provider] = {
    p.name: p for p in (MINIMAX, GATEWAY, DEEPSEEK, LIGHTER, ZGC)
}

# Model-name prefixes -> provider name. Longest match wins, so the specific
# ``deepseek-v3.2`` entry overrides the general ``deepseek`` one.
#
# ``deepseek-*`` defaults to the gateway (it serves deepseek-v4-pro/-flash);
# use ``--provider deepseek`` to reach the official API when specifically needed.
# ``deepseek-v3.2`` is the exception: the gateway still advertises it in
# ``/models`` but every call 404s with ``UnsupportedModel`` (verified 2026-07-18),
# and DeepSeek's official API has retired the V3.2 generation entirely — so the
# ZGC relay is the only live route and is now the default for that model.
_PREFIX_PROVIDER: list[tuple[str, str]] = [
    ("minimax", "minimax"),
    ("doubao", "gateway"),
    ("glm", "gateway"),
    ("deepseek", "gateway"),
    ("deepseek-v3.2", "zgc"),
    ("gpt", "lighter"),
]

# Provider used when no prefix matches a given model name.
_DEFAULT_PROVIDER = "gateway"

# Default request-body params merged into every call for a model, matched by
# case-insensitive prefix (longest match wins). ``gpt-5.5`` is a reasoning model
# whose thinking level defaults to ``medium``; override per call by passing a
# different ``reasoning_effort`` (callers that build their own payload win).
#
# The third field scopes an entry to one provider; ``None`` applies it everywhere.
# Scoping exists because these are usually workarounds for a particular relay's
# request handling rather than properties of the model itself, and leaking such a
# cap to another provider would violate the project's no-``max_tokens`` policy.
#
# Historical note: ``deepseek-v3.2`` used to carry ``{"max_tokens": 32768}`` scoped
# to ``gateway`` — omitting it made that gateway inject an illegal 65536 and 400
# every request. The entry is gone because the gateway no longer serves the model
# at all (it 404s ``UnsupportedModel``), and the ZGC relay that replaced it needs
# no cap. Restore it if the gateway route ever comes back.
_MODEL_PARAMS: list[tuple[str, dict, str | None]] = [
    ("gpt-5.5", {"reasoning_effort": "medium"}, None),
]


def resolve_model_params(model: str, provider: str | None = None) -> dict:
    """Return the default extra request params for ``model`` (longest prefix).

    ``provider`` restricts the match to entries that are unscoped or scoped to
    that provider. Passing ``None`` means "no provider context" and considers
    every entry, which keeps callers that only know a model name (e.g.
    ``is_reasoning_model``) working as before.
    """
    low = (model or "").lower()
    best: dict = {}
    best_len = -1
    for prefix, params, scope in _MODEL_PARAMS:
        if scope is not None and provider is not None and scope != provider:
            continue
        if low.startswith(prefix) and len(prefix) > best_len:
            best, best_len = params, len(prefix)
    return dict(best)


# Reasoning models that emit hidden chain-of-thought in ``reasoning_content``
# before the visible answer in ``content``, but do NOT take a ``reasoning_effort``
# request param (so they are invisible to ``_MODEL_PARAMS``). ``MiniMax-M3`` is
# one: capping its extraction/judge calls at a small ``max_tokens`` starves the
# answer (the budget is spent on reasoning) and returns empty ``content`` — which
# surfaced as bogus "empty reply" / "unparsed" judge failures. Matched by
# case-insensitive prefix.
# ``deepseek-v3.2-think`` is the other one: verified 2026-07-18 against the ZGC
# relay, a "what is 8347*2916" call spent 977 of its 982 completion tokens on
# ``reasoning_content`` and put only the bare answer in ``content``. Capping it
# would starve the answer exactly the way it starves MiniMax-M3. The plain
# ``deepseek-v3.2`` is *not* listed: it reasons inline in ``content`` instead.
_REASONING_MODEL_PREFIXES: tuple[str, ...] = ("minimax-m3", "deepseek-v3.2-think")


def is_reasoning_model(model: str) -> bool:
    """True if ``model`` reasons before answering.

    Covers models that ship a default ``reasoning_effort`` (e.g. ``gpt-5.5``) and
    models that emit ``reasoning_content`` without such a param (``MiniMax-M3``).
    """
    if "reasoning_effort" in resolve_model_params(model):
        return True
    low = (model or "").lower()
    return any(low.startswith(p) for p in _REASONING_MODEL_PREFIXES)


def extraction_max_tokens(model: str, default: int | None) -> int | None:
    """Token cap for an extraction / judge call — always ``None`` (uncapped).

    Project policy (see CLAUDE.md / AGENTS.md): **do not cap ``max_tokens`` for
    any model unless explicitly required.** A small cap starves reasoning models
    (the budget is spent on hidden ``reasoning_content`` before the visible
    answer, leaving ``content`` empty), which historically surfaced as bogus
    "empty reply" / "unparsed" judge failures. Non-reasoning models are left
    uncapped too, for consistency; their natural stop handles termination.

    ``default`` is retained in the signature so call sites document their intended
    ceiling, but it is intentionally ignored. The only model that still carries a
    ``max_tokens`` is ``deepseek-v3.2`` (via ``_MODEL_PARAMS``), a hard gateway
    requirement — not a starvation cap. To reinstate a cap, do it explicitly and
    deliberately at the call site.
    """
    return None


def resolve_provider(model: str) -> Provider:
    """Pick the provider for ``model`` by case-insensitive prefix match.

    The **longest** matching prefix wins, so a specific route
    (``deepseek-v3.2`` -> zgc) overrides a family route (``deepseek`` -> gateway)
    regardless of the order entries appear in ``_PREFIX_PROVIDER``.
    """
    low = (model or "").lower()
    best: str | None = None
    best_len = -1
    for prefix, provider in _PREFIX_PROVIDER:
        if low.startswith(prefix) and len(prefix) > best_len:
            best, best_len = provider, len(prefix)
    return PROVIDERS[best or _DEFAULT_PROVIDER]


def build_client(
    model: str,
    timeout: int = 300,
    *,
    provider: str | None = None,
    base_url: str | None = None,
    api_key_env: str | None = None,
    chat_path: str | None = None,
    extra_params: dict | None = None,
    temperature: float | None = None,
) -> MiniMaxClient:
    """Construct a client for ``model`` against its resolved provider.

    Explicit ``provider`` / ``base_url`` / ``api_key_env`` / ``chat_path`` args
    override the auto-resolved provider (escape hatch for models not in the
    prefix table). Default per-model request params (``resolve_model_params``,
    e.g. ``gpt-5.5``'s ``reasoning_effort: medium``) are applied unless
    ``extra_params`` is given explicitly. Raises a clear error if the key env var
    is unset.

    ``temperature`` is merged on top of the resolved params rather than replacing
    them, so pinning a sampling temperature never drops a per-model workaround
    (e.g. ``deepseek-v3.2``'s mandatory ``max_tokens``). Leave it ``None`` to omit
    the field entirely and inherit whatever the backend defaults to — that is the
    historical behaviour of every run in this repo.
    """
    prov = PROVIDERS[provider] if provider else resolve_provider(model)
    if prov.models is not None and model not in prov.models and base_url is None:
        raise RuntimeError(
            f"provider {prov.name!r} is not registered for model {model!r} "
            f"(registered: {', '.join(sorted(prov.models))}). "
            f"The relay may well serve it — add it to the provider's `models` set "
            f"if you want it evaluated, or override with --base-url."
        )
    url = base_url or prov.resolved_base_url()
    path = chat_path or prov.chat_path
    key_env = api_key_env or prov.api_key_env
    api_key = os.environ.get(key_env)
    if not api_key:
        raise RuntimeError(
            f"environment variable {key_env} is not set "
            f"(needed for model {model!r} via provider {prov.name!r})"
        )
    params = (
        resolve_model_params(model, prov.name) if extra_params is None else extra_params
    )
    if temperature is not None:
        params = {**params, "temperature": temperature}
    return MiniMaxClient(
        model=model,
        base_url=url,
        api_key=api_key,
        timeout=timeout,
        chat_path=path,
        extra_params=params,
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
