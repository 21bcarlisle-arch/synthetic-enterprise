"""Correlatable secret scrubbing -- docs/staging/in_progress/DIRECTOR_INPUT_LOG.md's
scrubbing spec: "Secrets (topic names, PINs, tokens, signatures, keys) ->
replaced by sha256-prefix hashes (8 chars) so correlation survives without
disclosure."

Deliberately a SEPARATE function from background/ntfy_mirror.py::scrub_secrets()
rather than a shared rewrite of it: that function's blunt "[hex-scrubbed]" /
"[topic-scrubbed]" placeholders are locked in by its own existing tests
(tests/background/test_ntfy_mirror.py) and its target is the (now-relocating)
public-repo mirror -- changing its output format would be an unrelated,
unrequested behavior change to already-shipped code. The detection logic
(long hex digest, known topic value) is conceptually the same "one place"
the doc asks for; the replacement FORMAT differs by explicit design
requirement (correlatable hash vs blunt redaction), so it lives here as its
own small function instead.
"""
from __future__ import annotations

import hashlib
import re

_HEX_DIGEST_RE = re.compile(r"\b[0-9a-fA-F]{32,}\b")


def _correlatable_hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:8]


def scrub(text: str, known_secrets: list[str] | None = None) -> str:
    """Replace `known_secrets` (e.g. the live NTFY topic, HMAC key) and any
    bare 32+ hex-char run (signatures, content hashes) with
    `[redacted:<8-char-sha256-prefix-of-the-real-value>]` -- two entries
    containing the SAME real secret produce the SAME placeholder, so an
    advisor/reader can correlate occurrences without the value ever being
    disclosed."""
    scrubbed = text
    for secret in known_secrets or []:
        if secret:
            scrubbed = scrubbed.replace(secret, f"[redacted:{_correlatable_hash(secret)}]")

    def _replace_hex(match: re.Match) -> str:
        value = match.group(0)
        return f"[redacted:{_correlatable_hash(value)}]"

    return _HEX_DIGEST_RE.sub(_replace_hex, scrubbed)
