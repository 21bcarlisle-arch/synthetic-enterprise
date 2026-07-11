"""Director input log -- docs/staging/in_progress/DIRECTOR_INPUT_LOG.md (P2,
Lane H, advisor-staged 2026-07-11). Channel-tagged, HMAC-verified log of
every input reaching this session, mirrored to the PRIVATE
synthetic-enterprise-ops repo (background/ops_repo.py) rather than this
(public) repo -- the doc's own PRIVACY AMENDMENT.

Built in direct response to this session's own mid-turn/NTFY provenance-
ambiguity incident (docs/observability/ntfy-mirror.md, 2026-07-11
~10:58-12:00 UTC entries): several messages arrived wrapped as "the user
sent a new message while you were working", with no way to tell whether
that was a live console paste or an NTFY-relayed message. `classify_and_log_
message()` below is the actual mechanism that resolved it in hindsight -- a
suspicious 4x-repeated flood turned out to carry a VALID HMAC signature
(background/ntfy_utils.py's sign_wake_message()/verify_wake_message()
format, `text|timestamp|hexhmac`), meaning it genuinely passed through the
real NTFY-to-dispatcher relay pipeline. That's a fact no amount of eyeballing
the message shape could have established; this module makes it checkable
mechanically, every time, rather than by hand once.

HONEST SCOPE LIMIT (researched via the claude-code-guide agent before
building, 2026-07-11): the doc's own premise names `window-live` and
`window-queued-midturn` as separate channel tags, citing "the user-prompt
lifecycle hook from the adoption sprint" as "the known-good mechanism --
deterministic, unskippable". That premise does not hold under Claude Code's
actual `UserPromptSubmit` hook: its documented payload has no field
distinguishing a fresh-turn prompt from a message queued mid-tool-execution
and delivered later (no origin/source field, no queue-status field), and no
other documented hook event covers mid-turn-queued input either. Rather than
fake a distinction the harness genuinely does not expose, both collapse into
one `window` channel tag here -- honestly scoped, not silently claiming
DoD's "one test entry per channel tag, including a mid-turn queued paste" if
the harness cannot actually produce that distinction. Filed as a real gap:
a `origin` field on UserPromptSubmit's payload would close it; not
something this repo can build (it's the CLI's own schema).
"""
from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

from background.ntfy_utils import NTFY_TOPIC, WAKE_HMAC_KEY, verify_wake_message
from background.ops_repo import OPS_REPO_DIR, commit_and_push, ops_tree_lock
from background.secret_scrub import scrub

LOG_FILE = OPS_REPO_DIR / "director_input_log.md"
MAX_LOG_ENTRIES = 5000

ChannelTag = Literal[
    "window", "ntfy", "comments-box", "supervisor-wake", "watcher-wake",
    "advisor-staged", "unknown-unverified",
]

_SIGNED_SUFFIX_RE = re.compile(r"^(?P<text>.*)\|(?P<ts>\d{9,})\|(?P<hex>[0-9a-fA-F]{64})$", re.DOTALL)

_HEADER = (
    "# Director Input Log\n\n"
    "Every input reaching an agent turn, channel-tagged and (where a wake-relay "
    "signature is present) HMAC-verified against SE_WAKE_HMAC_KEY. Secret-scrubbed "
    "via background/secret_scrub.py (correlatable hash-prefix redaction -- see "
    "docs/staging/in_progress/DIRECTOR_INPUT_LOG.md, the public repo, for the design "
    "doc). This repo is PRIVATE: personal/operational content may flow unredacted, "
    "but raw secrets (topic, HMAC key, signatures) are still never written verbatim.\n\n"
)


def has_signed_suffix(text: str) -> bool:
    return bool(_SIGNED_SUFFIX_RE.match(text))


def _hmac_status(text: str) -> Optional[bool]:
    """None = no signature present to check at all (e.g. a plain console
    paste). True/False = a `...|ts|hexhmac` suffix was present and did/did
    not verify against SE_WAKE_HMAC_KEY."""
    if not has_signed_suffix(text):
        return None
    if not WAKE_HMAC_KEY:
        return None
    return verify_wake_message(text, max_age_seconds=10**9) is not None


def classify_channel(raw_text: str, hmac_status: Optional[bool]) -> ChannelTag:
    """Infer the channel tag from a signed wake payload's recognisable
    bracket tag, or default to the two well-defined fallbacks: a signature
    that's present but INVALID is the loud, adversarial case
    ("unknown-unverified" -- never silently trusted or silently dropped);
    no signature at all defaults to "window" (the only channel with no
    signature scheme, per the scope-limit note above)."""
    if hmac_status is False:
        return "unknown-unverified"
    if hmac_status is True:
        if "[STAGING WATCHER" in raw_text:
            return "watcher-wake"
        if "[SUPERVISOR" in raw_text:
            return "supervisor-wake"
        if "[DISPATCHER" in raw_text:
            return "ntfy"
        return "supervisor-wake"  # signed but no recognised bracket -- still a genuine internal relay
    return "window"


def classify_and_log_message(raw_text: str, channel_hint: Optional[ChannelTag] = None) -> None:
    """Classify one raw inbound message (or use `channel_hint` when the
    caller already knows its own channel unambiguously, e.g.
    ntfy_responder.py calling this for an inbound NTFY message) and append
    it to the log."""
    hmac_status = _hmac_status(raw_text)
    channel = channel_hint if channel_hint is not None else classify_channel(raw_text, hmac_status)
    append_entry(channel, raw_text, hmac_verified=hmac_status)


def append_entry(
    channel: ChannelTag, content: str, direction: str = "in",
    hmac_verified: Optional[bool] = None,
) -> None:
    """Append one scrubbed, timestamped, channel-tagged entry and push to
    the private ops repo. V1 commits+pushes per call rather than batching
    (real message volume here is low; batching is a straightforward future
    optimisation, not correctness-load-bearing). Rotates at MAX_LOG_ENTRIES.

    Same test-isolation guard as background/ntfy_mirror.py's
    append_mirror_entry() (2026-07-09 tmux-leak-class incident): never
    write to the real log, or push, during a pytest run."""
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    hmac_str = "valid" if hmac_verified is True else "invalid" if hmac_verified is False else "n/a"
    scrubbed = scrub(content, known_secrets=[NTFY_TOPIC, WAKE_HMAC_KEY]).replace("\n", " ")
    entry = f"- [{ts}] [{channel}] [{direction}] [hmac:{hmac_str}] {scrubbed}"

    with ops_tree_lock():
        existing = LOG_FILE.read_text(encoding="utf-8") if LOG_FILE.is_file() else ""
        entries = (
            [line for line in existing.split("\n\n", 2)[-1].splitlines() if line.strip()]
            if existing.startswith("# Director Input Log") else []
        )
        entries.append(entry)
        entries = entries[-MAX_LOG_ENTRIES:]

        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOG_FILE.write_text(_HEADER + "\n".join(entries) + "\n", encoding="utf-8")

        commit_and_push(["director_input_log.md"], "director input log entry")
