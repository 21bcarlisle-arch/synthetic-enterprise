"""A CREDENTIAL ARRIVING BY NTFY NEVER REACHES THE WORKING TREE.

THE DIRECTOR, 2026-08-27, authorising this after declining to rotate the token that prompted
it: *"the instance is harmless, the class isn't. Anything I send over ntfy landing verbatim in
the repo will eventually bite us with something that matters, and being careful once doesn't
close it."*

THE INSTANCE. A live Cloudflare API token sat in `docs/staging/done/DIRECTOR_CONSOLE_2026-08-20.md`,
three lines below the director's own sentence saying it was not in the repo. It got there the
ordinary way: he typed it into a console note, `ntfy_responder._write_to_staging` wrote the
message verbatim, and a later archive commit carried it. Nothing malfunctioned. **The leak path
IS the normal path**, which is exactly why a careful human at one end cannot close it.

WHY THE EXISTING SCRUBBERS DO NOT COVER THIS, checked rather than assumed:

  * `background/secret_scrub.scrub` matches `\\b[0-9a-fA-F]{32,}\\b` -- hex digests -- plus a
    caller-supplied list of KNOWN secret values. A Cloudflare API token is 40 characters of
    mixed-case alphanumerics with `_-`; it is not hex, and it was not on any known list. It
    would have sailed through.
  * `background/ntfy_mirror.scrub_secrets` targets the outbound public mirror, not inbound.
  * `background/doorbell_redaction` is about internal work-order text reaching a person, the
    opposite direction.

So this is a new detector, and it BORROWS `secret_scrub._correlatable_hash` for its placeholder
rather than inventing a second convention: two occurrences of the same real secret still produce
the same marker, so anyone reading the tree can correlate without the value existing there.

THE SHAPE OF THE GUARD, and why it is a guard: `doorbell_redaction`'s doctrine applies verbatim
-- the rule lives on the ONE channel every writer passes through, so no future call site has to
remember it. Inbound text reaches the tree by THREE routes, not one, and fixing only the obvious
one is the instance fix this was explicitly not to be:

  1. `_write_to_staging` -> `docs/staging/from_rich_*.md`  (the known route)
  2. `_quarantine`       -> `docs/staging/quarantine/*.md` (a flood message, preserved in full)
  3. `log()`             -> `docs/observability/ntfy-responder-log.md` (`message[:60]` -- and a
     40-character token comfortably fits inside sixty characters)

REDACTS, NEVER DROPS. A message carrying a credential is still an instruction, and refusing it
would delete the director's steer to punish its contents. The credential is replaced; every
other character survives.

THE PRECISION PROBLEM, WHICH IS THE WHOLE DESIGN, and which this seat has already got wrong
once. On 2026-08-26 a `[A-Za-z0-9_-]{40,}` sweep over a document replaced EIGHT strings when one
was a secret -- base64 blobs, digests and long identifiers all look alike to a length test. A
redactor that mangles the director's words is not a safer redactor; it corrupts direction, which
is the more expensive failure. So detection is three tiers, in descending confidence:

  A. **Named families with anchored prefixes** (`sk-ant-`, `ghp_`, `AKIA`, `xoxb-`, JWTs, PEM
     blocks). A prefix match is near-certain and needs no entropy argument.
  B. **Label-anchored values** -- `token=`, `api_key:`, `Bearer ` -- where the surrounding text
     declares what the value is. The anchor does the work, so the value pattern can stay loose.
  C. **Bare high-entropy runs**, for the credential family nobody has enumerated yet -- the
     Cloudflare case. This is the tier that mis-fired before, so it is gated three ways at once
     rather than on length alone: the charset admits no `/`, `.` or whitespace (so paths, URLs
     and prose are out), the run must mix upper, lower AND digits (so a 40-character git SHA and
     a lowercase `test_some_long_name` are out), and its Shannon entropy must clear
     `_MIN_ENTROPY_BITS`. Prose does not contain 32-character unbroken mixed-case alphanumeric
     runs; credentials are made of nothing else.

AND WHEN IT DOES MIS-FIRE, THE DIRECTOR IS TOLD. `redact()` returns what it removed, and the
responder says so on the reply channel. A silent redactor that ate one word of an instruction
would be indistinguishable from the director having not written it -- the same
looks-like-work-in-progress failure as a waiter with no subject. He can restate; he cannot
restate what he was never told had gone.

THE RAW MESSAGE IS NOT DESTROYED. It is written outside the working tree, under
`secrets_location.NEW_SECRETS_DIR`, so a false positive is recoverable by a human at the console
and a true positive is still not in git. Out-of-tree is the existing convention for this repo's
secrets and is reused rather than re-decided.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path

from background.secret_scrub import _correlatable_hash
from background.secrets_location import NEW_SECRETS_DIR

#: Where the unredacted inbound message is kept. Out of tree by construction -- it is derived
#: from the secrets root, not from PROJECT_DIR, so no future refactor of the repo layout can
#: quietly move it back inside the thing it must stay outside of.
RAW_DIR = NEW_SECRETS_DIR / "inbound_raw"

#: Shannon entropy floor, in bits per character, for a TIER C bare run. A 40-character
#: Cloudflare token measures around 5.0; `aaaaaaaa...` measures 0; a repetitive identifier like
#: `TEST_VALUE_TEST_VALUE_TEST_VALUE_ABC123` sits near 3.4. Set at 3.6 so the pathological
#: low-entropy shapes fall out while every real credential clears it comfortably -- the floor is
#: a second opinion on top of the charset and case-mix gates, not the only one.
_MIN_ENTROPY_BITS = 3.6

#: Minimum length for a TIER C bare run. Cloudflare API tokens are exactly 40; AWS secret access
#: keys are 40; a git SHA is 40 too, which is why length alone was never going to be enough.
_MIN_BARE_RUN = 32


def shannon_entropy(text: str) -> float:
    """Bits per character. Zero for a single repeated character, ~6 for random base64."""
    if not text:
        return 0.0
    counts = Counter(text)
    n = len(text)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


# ---------------------------------------------------------------------------
# TIER A -- named families
# ---------------------------------------------------------------------------
# Ordered most-specific first: `sk-ant-` must be tried before a generic `sk-`, or an Anthropic
# key would be reported as the wrong family. The families are named in the placeholder, so
# getting the order wrong would put a WRONG fact in the tree rather than merely a vague one.
_TIER_A: tuple[tuple[str, re.Pattern], ...] = (
    ("private_key_block", re.compile(
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
        re.DOTALL)),
    ("anthropic_api_key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{16,}")),
    ("openai_api_key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9]{32,}")),
    ("github_token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("aws_access_key_id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")),
)

# ---------------------------------------------------------------------------
# TIER B -- label-anchored values
# ---------------------------------------------------------------------------
# The LABEL carries the confidence, so the value pattern is deliberately loose. Group 1 is
# everything up to and including the separator and is preserved verbatim: redacting the word
# "token" as well would make the sentence unreadable and hide WHAT was removed.
_TIER_B = re.compile(
    r"(?i)"
    r"((?:api[_\- ]?key|apikey|access[_\- ]?token|auth[_\- ]?token|bearer|password|passwd|"
    r"secret|token)\s*(?:[:=]|\s)\s*[\"']?)"
    r"([A-Za-z0-9_\-./+=]{12,})"
    r"([\"']?)")

# ---------------------------------------------------------------------------
# TIER C -- bare high-entropy runs
# ---------------------------------------------------------------------------
# No `/`, no `.`, no whitespace: paths, URLs, hostnames, version strings and ordinary prose are
# excluded by the CHARSET before entropy is even considered. What remains is the shape a
# credential has and almost nothing else does.
_TIER_C = re.compile(r"\b[A-Za-z0-9_-]{%d,}\b" % _MIN_BARE_RUN)


def _looks_like_a_credential(run: str) -> bool:
    """The three-way gate for TIER C. Each clause exists to exclude a real thing that a bare
    length test caught on 2026-08-26.

    A 40-character git SHA has no uppercase. A screaming-snake constant has no lowercase. A
    long `test_a_thing_that_does_something` has no digit. A credential normally has all three,
    and anything that also clears the entropy floor is not a word.
    """
    if not (any(c.isupper() for c in run) and any(c.islower() for c in run)
            and any(c.isdigit() for c in run)):
        return False
    return shannon_entropy(run) >= _MIN_ENTROPY_BITS


def _placeholder(family: str, value: str) -> str:
    return "[REDACTED:{}:{}]".format(family, _correlatable_hash(value))


def redact(text: str) -> tuple[str, list[str]]:
    """Return `(redacted_text, families_found)`.

    `families_found` is what the caller tells the director: one entry per occurrence, carrying
    family NAMES and never values -- a notification saying which credential family was removed
    is useful; one quoting the credential would move the leak from the repo to the phone.
    """
    if not text:
        return text, []

    # One entry per OCCURRENCE, not per distinct family: the director is told how many strings
    # went, and two tokens in one message is a different message from one.
    found: list[str] = []

    def _note(family: str) -> str:
        found.append(family)
        return family

    for family, pattern in _TIER_A:
        text = pattern.sub(lambda m, f=family: _placeholder(_note(f), m.group(0)), text)

    def _tier_b(match: re.Match) -> str:
        value = match.group(2)
        # Do not re-redact a TIER A placeholder that happens to follow the word "token".
        if value.startswith("[REDACTED:"):
            return match.group(0)
        return match.group(1) + _placeholder(_note("labelled_secret"), value) + match.group(3)

    text = _TIER_B.sub(_tier_b, text)

    def _tier_c(match: re.Match) -> str:
        run = match.group(0)
        if not _looks_like_a_credential(run):
            return run
        return _placeholder(_note("high_entropy_token"), run)

    text = _TIER_C.sub(_tier_c, text)
    return text, found


def was_redacted(original: str, redacted: str) -> bool:
    """Mirrors `doorbell_redaction.was_redacted` so callers of either guard read the same."""
    return original != redacted


def summarise(families: list[str]) -> str:
    """One sentence for the reply channel. Empty when nothing was removed, so a caller can use
    it directly as an `if` -- an unconditional "0 secrets redacted" note on every message is the
    unchanging-status NTFY that R5 forbids."""
    if not families:
        return ""
    return ("NOTE: {} redacted from that message before it was written to the repo ({}). "
            "The raw message is out of tree at {}. If that ate something you meant to send, "
            "it was a false positive -- resend it and say so.".format(
                "1 credential-shaped string was" if len(families) == 1
                else "{} credential-shaped strings were".format(len(families)),
                ", ".join(sorted(set(families))),
                RAW_DIR))


def preserve_raw(message: str, stamp: str) -> "Path | None":
    """Write the unredacted message OUTSIDE the working tree, and return where.

    A redactor with no recovery path turns every false positive into lost direction. This is
    the recovery path, and it lives under the repo's existing out-of-tree secrets root rather
    than in a location invented here -- `secrets_location.NEW_SECRETS_DIR` is already where
    this project agrees credentials live.

    0o700 on the directory and 0o600 on the file: a plaintext credential store readable by
    every account on the box would be a worse hole than the one being closed.

    THE `guard_live_ledger_write` CALL IS NOT BOOKKEEPING. It is a no-op today, deliberately:
    `RAW_DIR` is derived from the secrets root and sits outside the published-record directory,
    so the guard returns the path unchanged. What it does is FIRE THE DAY THAT STOPS BEING TRUE.
    `test_the_raw_directory_is_outside_the_working_tree` asserts the invariant statically; this
    asserts it at the moment of writing, so a refactor that moved the secrets root inside the
    tree would be refused under test rather than quietly start committing credentials.

    NEVER RAISES on the ordinary failures. This runs on the inbound path, and an unwritable home
    directory must not stop the director's message being staged -- the redaction has already
    happened by then, so failing here costs recoverability, while raising would cost the
    instruction itself. The guard's own refusal is deliberately NOT caught: it only fires in a
    test process against a live record path, which is a defect to surface, not to survive.
    """
    from background.live_ledger_guard import guard_live_ledger_write
    path = guard_live_ledger_write(
        RAW_DIR / "from_rich_RAW_{}.md".format(stamp), writer="inbound_secret_redaction.preserve_raw")
    try:
        RAW_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
        path.write_text(message)
        path.chmod(0o600)
        return path
    except OSError:
        return None
