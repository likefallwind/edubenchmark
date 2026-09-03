"""Best-of-N majority voting for LLM-as-judge adapters.

Several benchmarks judge a response by asking a fixed judge model the same
question ``n`` times and taking the majority answer (EduGuard-Bench P2 ports
this from the official ``run_p2_experiment.py``; Safe-Child-LLM uses it for the
paper's two labels).  The logic is independent of any benchmark, so it lives
here rather than being copied per adapter.

Scoring behaviour is deliberately identical to the original
``EduGuardAdversarialAdapter`` implementation it was lifted from: three attempts
per vote with a linear backoff, replies lowercased and stripped of wrapping
punctuation before counting, and the most-voted token winning with ties broken
by first appearance (verified identical to the original ``Counter.most_common``
call across every ballot combination on the un-normalized path).

The one deliberate departure is that the ``bon`` votes are cast **sequentially**
rather than concurrently. They are independent samples of the same prompt, so
serializing them changes no ballot, no tie-break (order is preserved either way)
and no score -- only wall-clock. What it fixes is the caller's concurrency knob:
``--extract-concurrency N`` runs N items at once, and with concurrent voting each
of those items held ``bon`` judge calls open, so the real in-flight count was
``3N`` while the knob said ``N``. That hidden 3x is what walked a nominally modest
setting into ``base_resp 2062`` (MiniMax Token Plan rate limit). Now the knob
means what it says; to raise judge throughput, raise the caller's concurrency.
"""

from __future__ import annotations

import time
from collections import Counter
from collections.abc import Callable

from .minimax_client import MiniMaxClient
from .providers import extraction_max_tokens


# Votes per question; majority wins. Matches the official EduGuardBench code
# default (--bon 3).
DEFAULT_BON = 3


def cast_vote(client: MiniMaxClient, model: str, prompt: str) -> str:
    """Ask the judge once, retrying transient failures and empty replies.

    Returns the reply lowercased and stripped. Raises the last transport error
    (or ``RuntimeError`` for a persistently empty reply) after three attempts.
    """
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            reply = client.chat(
                [{"role": "user", "content": prompt}],
                model=model,
                # Never cap the judge: a ceiling starves reasoning models, whose
                # budget goes to hidden reasoning_content, and surfaces as bogus
                # "empty reply" failures. extraction_max_tokens always returns None.
                max_tokens=extraction_max_tokens(model, 1024),
            )
            if reply.strip():
                return reply.strip().lower()
        except Exception as exc:  # noqa: BLE001 - retry transient judge failures (e.g. rate limits)
            last_error = exc
        time.sleep(2.0 * (attempt + 1))
    if last_error:
        raise last_error
    raise RuntimeError("judge returned empty response")


def majority_vote(
    client: MiniMaxClient,
    model: str,
    prompt: str,
    bon: int = DEFAULT_BON,
    normalize: Callable[[str], str] | None = None,
) -> tuple[str, list[str]]:
    """Cast ``bon`` votes in sequence; return (majority decision, cleaned votes).

    ``normalize`` maps a raw reply to the token actually voted on, for judges
    whose verdict is a value the reply may wrap in prose (e.g. one digit of a
    0-5 scale). It must map unparseable replies to ``""`` so a failed parse
    cannot win by accident when the real answers disagree. Omit it to vote on
    the cleaned reply text itself, which is what a single-word judge returns.
    """
    votes = [cast_vote(client, model, prompt) for _ in range(bon)]
    # official normalization: lowercase + strip quotes/periods/commas
    cleaned = [v.strip().strip("'\".,") for v in votes]
    ballots = [normalize(v) for v in cleaned] if normalize else cleaned
    # Rank an unparseable ballot last so two disagreeing real answers still beat
    # a single "" (Counter.most_common breaks ties by insertion order alone).
    decision = max(
        Counter(ballots).items(), key=lambda kv: (kv[1], kv[0] != "")
    )[0]
    return decision, cleaned
