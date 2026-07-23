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
