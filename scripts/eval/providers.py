"""Model -> provider resolution and client factory.

The eval harness talks to several OpenAI-compatible backends through one client
class (``MiniMaxClient``). A *provider* bundles the three things that differ
between backends — base URL, the env var holding the API key, and the chat path
— so a caller only has to name a model (``--model doubao-seed-2.0-pro``) and the
right endpoint is selected automatically.

Seven providers ship today:

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
* ``silicon`` — SiliconFlow (``https://api.siliconflow.cn/v1``, key env
  ``SILICON_API``) at ``/chat/completions``; default route for the ``Qwen/``
  prefix. Registered for ``Qwen/Qwen3-8B`` only — ``Qwen/Qwen3.5-4B`` moved to
  the self-hosted ``vllm`` provider (see below).
* ``vllm``    — a self-hosted vLLM OpenAI-compatible server, **no auth**. Serves
  ``Qwen/Qwen3.5-4B`` and is that model's route (a longer prefix than
  ``qwen/``, so it beats silicon).

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
    # False for backends that accept unauthenticated requests (a self-hosted
    # vLLM started without ``--api-key``). ``build_client`` then tolerates an
    # unset key env instead of raising, and sends a placeholder bearer token —
    # such servers ignore the header entirely. Setting the env var still works
    # and takes precedence, so turning auth on later needs no code change.
    api_key_required: bool = True

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

# SiliconFlow (``https://api.siliconflow.cn/v1``, key ``SILICON_API``). A Chinese
# model-hosting platform serving ~91 open-weight models under vendor-prefixed ids
# (``Qwen/...``, ``deepseek-ai/...``, ``zai-org/...``). OpenAI-compatible chat
# completions, so the same MiniMaxClient drives it; the base URL already carries
# ``/v1``, so the chat path is ``/chat/completions``.
#
# Registered for ``Qwen/Qwen3-8B`` (verified present in ``/v1/models`` and
# answered a smoke-test call on 2026-07-28). It runs with thinking enabled by
# default and returns the chain of thought in ``reasoning_content`` with only the
# answer in ``content`` — it spent 7,300 of 7,309 completion tokens on reasoning
# for "8347*2916", so it is in ``_REASONING_MODEL_PREFIXES`` and must never be
# capped. Expect minutes of wall clock even on trivial prompts; keep concurrency
# modest and rely on the client's streaming stall timeout rather than raising the
# total budget.
#
# ``Qwen/Qwen3.5-4B`` used to be registered here too. It was moved to the
# self-hosted ``VLLM`` provider on 2026-08-10 by decision — that model is served
# only from our own deployment from now on. The two backends are **not**
# interchangeable for that model (different CoT surface, different context
# window); see the VLLM comment.
#
# To evaluate another model here (e.g. ``Qwen/Qwen3.5-27B``), add it to ``models``
# below, and add its lowercase id to ``_REASONING_MODEL_PREFIXES`` if it thinks.
SILICON = Provider(
    name="silicon",
    base_url="https://api.siliconflow.cn/v1",
    base_url_env="SILICON_BASE_URL",
    api_key_env="SILICON_API",
    chat_path="/chat/completions",
    models=frozenset({"Qwen/Qwen3-8B"}),
)

# Self-hosted vLLM OpenAI-compatible server (probed 2026-08-10), the sole route
# for ``Qwen/Qwen3.5-4B``. Started by ``start_vllm_server.sh`` on the GPU box as
# ``vllm serve <local snapshot> --host 0.0.0.0 --port 8000 --served-model-name
# Qwen/Qwen3.5-4B --max-model-len 4096``.
#
# **Reaching it.** The public endpoint below works directly — no tunnel needed.
# It did not at first: vLLM was started on container port 8000 while the platform
# (a k8s pod; the public IP is NAT in front of it) maps public 63550 to container
# port **3631**, so the public port answered with a RST. Proven by parking a
# throwaway ``http.server`` on 3631 and watching ``:63550`` serve its file, then
# fixed by pointing ``--port`` at 3631 in ``start_vllm_server.sh``. The mapping
# lives outside the container and cannot be changed from inside, so **the server
# must listen on 3631** — starting it anywhere else silently loses public access.
# Do not be misled by the host's public 8000: that is a *different* container
# running an sglang video model.
#
# ``scripts/vllm_tunnel.sh`` (SSH local forward to the container) remains as a
# fallback for when the public route is down; point ``VLLM_BASE_URL`` at it.
#
# **Concurrency: use ``--concurrency 64``** (decided 2026-08-10 from the sweep in
# ``scripts/bench_vllm_concurrency.py``; A100-80GB, ``--max-num-seqs 128``). Output
# throughput scales 959 -> 1796 -> 3025 -> 4618 -> 5512 -> 5587 tok/s at 8 / 16 /
# 32 / 64 / 96 / 128 concurrent, i.e. marginal gain falls to 1.17x for 48->64,
# 1.19x for 64->96 and **1.01x for 96->128**. The plateau is GPU compute
# saturation, not the ``max-num-seqs`` ceiling: per-stream speed falls 120 -> 57
# tok/s exactly mirroring it, ``Waiting`` stayed 0 throughout, and TTFT rose
# smoothly (0.16 -> 1.23s p95) instead of stepping the way queueing would. 64 is
# the knee; above 96 is waste. Drop to 32 if anyone is using the service
# interactively at the same time — per-stream speed there is still ~80% of solo.
#
# **No auth**: the server is started without ``--api-key``, so ``api_key_required``
# is False and a placeholder bearer token is sent. Set ``VLLM_API_KEY`` if auth is
# ever turned on.
#
# **Server-side history.** The first deployment ran with ``--max-model-len 4096``
# and no ``--reasoning-parser``, which made 27% of a 30-item mmlu_pro sample
# truncate mid-think (every one of them stopped at exactly 4,096 total tokens) and
# put the raw ``<think>...</think>`` block in ``content``. Both were fixed
# server-side on 2026-08-10: the window is now **65536** and ``--reasoning-parser
# qwen3`` splits the trace out. Re-verified after the fix — 0 truncations, no
# ``<think>`` in ``content``, completion length now reaching 5,453 tokens where the
# old ceiling clipped it at 3,963. Runs made before that fix are not usable.
#
# Thinking is on by default and needs no request param. The trace arrives in the
# bare ``reasoning`` field rather than ``reasoning_content``; ``minimax_client``
# reads both, so nothing to do.
#
# A third defect, ``<|im_end|>`` leaking into ``content`` (every reply ended
# ``...The answer is (H)<|im_end|>``), was fixed the same day. The model snapshot
# had been downloaded incompletely — **``tokenizer_config.json``,
# ``chat_template.jinja``, ``vocab.json`` and ``merges.txt`` were all absent**, so
# vLLM had no ``eos_token`` declaration and fell back to ``config.json``'s
# ``eos_token_id: 248044`` (``<|endoftext|>``) while the token that actually ends a
# chat turn is ``<|im_end|>``. The missing chat template is also why one had to be
# hand-written. Note Qwen3.5-4B genuinely ships **no** ``generation_config.json``
# upstream, and its odd ``model.safetensors-0000N-of-00002`` filenames are upstream
# too — neither is a symptom. Fixed by fetching the four files at the pinned
# revision and dropping ``--chat-template`` from the start script so the official
# template loads (it defaults thinking on and, unlike the hand-written one, keeps
# reasoning history across turns).
# **Second model on this box: ``Qwen/Qwen3.8-27B``** (added 2026-08-17; ModelScope
# ``Qwen/Qwen3.8-27B`` at ``/vepfs-mlp2/mlp-public/100143/models/Qwen3.8-27B``,
# started by ``start_vllm_qwen38_27b.sh`` — same mandatory container port 3631,
# ``--max-model-len 32768``, ``--reasoning-parser qwen3``). Only one model is
# served at a time; check ``/v1/models`` before assuming which is loaded. It is a
# reasoning model (trace in the bare ``reasoning`` field) and multimodal.
#
# **Concurrency: use ``--concurrency 32``** (decided 2026-08-17). Unlike the 4B,
# the binding constraint here is the **KV pool, not compute and not
# ``--max-num-seqs 128``** (which is unreachable). Weights take 51.7 GiB, leaving a
# 16.39 GiB / 249,036-slot KV pool, and one sequence costs **2,250 slots fixed +
# 1 per token** — the fixed part is the per-sequence state of the 48 linear-
# attention layers (only 16 of 64 layers are full attention, 64 KiB/token), which
# does not shrink with length. So the seat count is a function of request length:
#
#     seats = 249,036 / (2250 + prompt+output tokens)
#     1k -> 76,  2k -> 59,  4k -> 40,  8k -> 24,  16k -> 14,  32k -> 7
#
# Measured output throughput on ~780-token requests: 54.7 / 111.1 / 211.1 / 390.0
# / 656.4 / 841.4 / 1019.9 tok/s at 2 / 4 / 8 / 16 / 32 / 48 / 64 concurrent, then
# **96 and 128 are identical** (1083 tok/s, 181.4 vs 181.5 s wall) because both get
# clamped to ~85 running sequences and the surplus just queues — TTFT p95 blows up
# from 4 s to 38-42 s while throughput does not move. **Over-subscription does not
# error, it queues**, so size the concurrency against the expected request length.
# 32 is the chosen default: 64% of peak throughput, TTFT p95 2.1 s, ``Waiting``
# zero throughout, and enough headroom for requests up to ~5.5k tokens. Tasks with
# longer requests should be run at a lower concurrency, per the table above.
VLLM = Provider(
    name="vllm",
    base_url="http://115.190.90.101:63550/v1",
    base_url_env="VLLM_BASE_URL",
    api_key_env="VLLM_API_KEY",
    chat_path="/chat/completions",
    models=frozenset({"Qwen/Qwen3.5-4B", "Qwen/Qwen3.8-27B"}),
    api_key_required=False,
)

PROVIDERS: dict[str, Provider] = {
    p.name: p for p in (MINIMAX, GATEWAY, DEEPSEEK, LIGHTER, ZGC, SILICON, VLLM)
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
    # SiliconFlow ids are vendor-prefixed (``Qwen/Qwen3-8B``). The trailing slash
    # keeps this from swallowing a bare ``qwen-...`` name should another relay ever
    # serve one; the gateway lists no qwen model today (checked 2026-07-28).
    ("qwen/", "silicon"),
    # Longer than ``qwen/``, so longest-match sends these two models to our own
    # vLLM box while every other ``Qwen/*`` id still goes to SiliconFlow.
    ("qwen/qwen3.5-4b", "vllm"),
    ("qwen/qwen3.8-27b", "vllm"),
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
# The Qwen models are the third case. ``Qwen/Qwen3-8B`` on SiliconFlow has
# ``enable_thinking`` on by default and puts its chain of thought in
# ``reasoning_content``, returning only the answer in ``content`` (verified
# 2026-07-28 — 7,300 of 7,309 completion tokens billed as reasoning on
# "8347*2916"). ``Qwen/Qwen3.5-4B`` on our own vLLM box thinks just as hard but
# emits the trace **inline in ``content``** as ``<think>...</think>``, because that
# server runs without ``--reasoning-parser`` (verified 2026-08-10: 3,806 completion
# tokens on the same prompt, answer only after ``</think>``). Either way the
# visible answer arrives last, so capping would truncate it exactly as it does
# MiniMax-M3 — and on the 4B the 4,096-token window is already the binding limit.
_REASONING_MODEL_PREFIXES: tuple[str, ...] = (
    "minimax-m3",
    "deepseek-v3.2-think",
    "qwen/qwen3.5-4b",
    "qwen/qwen3.8-27b",
    "qwen/qwen3-8b",
)


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
        # Providers that declare ``api_key_required=False`` (self-hosted vLLM
        # started without ``--api-key``) accept anything in the Authorization
        # header, so a missing env var is not an error there.
        if prov.api_key_required:
            raise RuntimeError(
                f"environment variable {key_env} is not set "
                f"(needed for model {model!r} via provider {prov.name!r})"
            )
        api_key = "EMPTY"
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
