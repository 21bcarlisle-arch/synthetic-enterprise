"""Where secret env files actually live -- Option 2 floor (2026-07-11,
director in-console authorization, absorbing docs/design/
HARNESS_BEST_PRACTICE_ASSESSMENT.md's own recommendation rather than
re-deriving it): "move background/.env.ntfy and any other secret file out
of the repo working tree into a path never read by tool calls that touch
company/saas/site" -- reduces accidental secret exposure in commits/diffs
without requiring full container sandboxing.

New primary location: ~/.config/synthetic-enterprise/ (outside the git
working tree entirely, 700-permissioned directory, 600-permissioned files).
The OLD in-tree background/.env.* path is kept as a FALLBACK during the
transition, not removed outright -- CLAUDE.md's own "concurrent writers on
this one working tree" reality means daemon processes launched before this
change picked up will still have old code in memory until their own next
restart (R2); a hard cutover with no fallback risks a simultaneous outage
across the 6 daemons that share this exact dependency (the SPOF the
PRODUCTION_READINESS_EVIDENCE_PASS.md audit already named). Once every
consumer has been confirmed running the new-location-aware code for a
real cycle, the in-tree copies can be deleted for a true hard cutover --
tracked as a follow-up, not assumed done by this commit alone.
"""
from __future__ import annotations

from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

# ── Authority secrets that must NEVER reach a model-facing process ──────────────
# DIRECTOR_RULING_HMAC_GAP_OPTION_1 (2026-07-23). SE_WAKE_HMAC_KEY is the SYMMETRIC
# key that signs director-authority wake/ntfy messages; whoever can verify can also
# SIGN. A spawned `claude -p` worker (or any model-facing fork/sub-agent) that
# inherited it via os.environ.copy() could forge a director_ntfy ruling with a VALID
# signature (director_authority_channels.py's LIVE GAP). The worker needs only
# SE_NTFY_TOPIC to SEND ordinary NTFYs — never the wake key to SIGN. So this set is
# stripped from EVERY model-facing spawn env (worker_tick, autonomous_runner,
# build_executor, director_twin, worker_seat). Verification stays daemon-side
# (ntfy_responder / gate check), which reads the key from its OWN process env, not a
# spawned copy. Class-fix (R10): every spawner calls scrub_model_facing_env(), so a
# new spawn path can be checked against one enumerable list, not re-audited ad hoc.
MODEL_FACING_FORBIDDEN_SECRETS = frozenset({"SE_WAKE_HMAC_KEY"})


def scrub_model_facing_env(env: dict) -> dict:
    """Remove every authority-signing secret from `env` IN PLACE and return it, so a
    model-facing child process cannot mint a forged director-authority signature.

    FAIL-CLOSED by construction: pop-with-default never raises on an absent key, and
    the forbidden set is the SOLE source of truth — adding a secret here strips it
    from all spawners at once. The child keeps everything else (SE_NTFY_TOPIC etc.)
    so it can still SEND ordinary NTFYs; it simply cannot SIGN."""
    for name in MODEL_FACING_FORBIDDEN_SECRETS:
        env.pop(name, None)
    return env

NEW_SECRETS_DIR = Path.home() / ".config" / "synthetic-enterprise"
OLD_SECRETS_DIR = PROJECT_DIR / "background"


def resolve_secret_file(filename: str) -> Path:
    """Return the new (out-of-tree) path if it exists there, else fall back
    to the old in-tree path. `filename` is e.g. ".env.ntfy" or
    ".env.file-api"."""
    new_path = NEW_SECRETS_DIR / filename
    if new_path.is_file():
        return new_path
    return OLD_SECRETS_DIR / filename


def load_secret_env(filename: str = ".env.ntfy", *, only=("SE_NTFY_TOPIC",),
                    environ=None) -> list[str]:
    """Load NAMED `KEY=VALUE` lines from a secret file into the environment, WITHOUT overwriting
    anything already set. Returns the names it set (never the values). Never raises.

    WHY A TOOL NEEDS THIS (2026-09-01). `background/ntfy_utils` raises at IMPORT time when
    `SE_NTFY_TOPIC` is unset -- deliberately, so a daemon dies at start rather than discovering
    its only channel is dead at the moment it needs it. The consequence nobody had met until
    landings became notifications: **`background.notify` is not importable at all outside a
    daemon's environment**, including for a DEFERRED notification that never touches the wire.

    `tools/surgical_land` is run by hand, by every lane, from ordinary shells that never sourced
    `start_worker.sh`. So its landing announcement imported `background.notify`, raised, and was
    swallowed by the guard that exists to stop a notifier failing a landing -- a producer that was
    structurally unable to produce and structurally unable to say so. That is the same shape as
    the three unwired mechanisms it was written to report, arriving in the reporting of them.

    It lives HERE rather than in `ntfy_utils` because this module already owns *where secrets
    live*, and because `ntfy_utils` raises before any code in it can run. `start_worker.sh` does
    the same job in shell; this is the same act for a Python caller, not a second policy.

    NEVER OVERWRITES an existing value: a caller that has already been given a topic keeps it, so
    this can never redirect a live daemon's channel. Values are read and set, never logged or
    returned -- the names are enough for a caller that wants to say what it loaded.

    AN ALLOWLIST, NOT THE WHOLE FILE, and the first draft of this function got that wrong. Reading
    `.env.ntfy` wholesale also loads `SE_WAKE_HMAC_KEY` -- the authority-SIGNING key that
    `MODEL_FACING_FORBIDDEN_SECRETS` above exists to keep out of exactly this kind of process. A
    caller that wants to announce a landing needs the TOPIC and nothing else, so `only` names what
    it needs and the forbidden set is refused on top of that whatever any caller asks for. A helper
    that hands out more authority than its caller asked for is a worse defect than the silence it
    was written to fix.
    """
    import os
    env = os.environ if environ is None else environ
    loaded: list[str] = []
    try:
        text = resolve_secret_file(filename).read_text(encoding="utf-8")
    except OSError:
        return loaded
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        key, sep, value = line.partition("=")
        key = key.strip()
        if not sep or not key or key in env:
            continue
        if key in MODEL_FACING_FORBIDDEN_SECRETS:
            continue          # never, whatever `only` says -- the forbidden set is the floor
        if only is not None and key not in only:
            continue
        env[key] = value.strip().strip('"').strip("'")
        loaded.append(key)
    return loaded
