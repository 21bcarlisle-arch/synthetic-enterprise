"""Egress allowlist -- Option 2 floor, part (b) (2026-07-11, director
in-console authorization, absorbing docs/design/
HARNESS_BEST_PRACTICE_ASSESSMENT.md's own recommendation: "a network egress
allowlist scoped just to the already-named external endpoints... rather
than full container isolation").

HONEST SCOPE LIMIT, checked before building rather than assumed: true
OS-level egress enforcement (iptables/nftables DROP rules) requires root.
This machine's `rich` user genuinely has sudo group membership, but
CLAUDE.md's own `.claude/hooks/block_sudo.py` hook deliberately bans sudo
for THIS agent regardless of the underlying account's real permission --
that is a standing safety control (HARNESS_BEST_PRACTICE_ADOPTION.md item
1b), and bypassing it to build this would be exactly the class of
safety-control violation this session has been careful about throughout.
So this is an APPLICATION-LEVEL allowlist, not a kernel-level one: it
cannot stop a raw syscall or a compromised process making a direct
connection outside Python. What it DOES do: any code that routes its
outbound requests through `check_allowed()` (or the `guarded_request()`
wrapper below) gets a real, enforced check against the named endpoints
this project actually needs, catching accidental or unintended requests
from code written in this repo.

TRUE OS/container-level enforcement (the part this can't provide) is
registered as part of H3/the Hardened profile's Epoch-5 NFR blocker
(docs/design/maturity_map.yaml) -- that profile's whole design (Pattern C+:
container, unreadable creds, audit, RBAC) puts network policy at the
container boundary, which is the correct layer for real enforcement, not
a host-level iptables edit this agent would need a banned sudo call to make.

Adoption note: this module provides the mechanism; retrofitting every
existing network call site (WebFetch tool internals, curl invocations,
requests calls scattered across simulation/tools/background) to route
through it is NOT done by this commit -- that would be a large, separate
refactor. Honestly registered as a follow-up, not silently claimed complete.
"""
from __future__ import annotations

from urllib.parse import urlparse

# The named endpoints this project actually needs (docs/design/
# HARNESS_BEST_PRACTICE_ASSESSMENT.md's own list, not re-derived):
# Elexon, NESO, Open-Meteo, the Tailscale File API, github.com, npm/pip
# registries. Suffix-matched so subdomains (api.github.com, raw.
# githubusercontent.com) are covered without listing every one.
ALLOWED_HOST_SUFFIXES: tuple[str, ...] = (
    "elexon.co.uk",
    "elexonportal.co.uk",
    "neso.energy",
    "nationalgrideso.com",
    "open-meteo.com",
    "taila062fa.ts.net",  # this project's own Tailscale tailnet (the File API)
    "github.com",
    "githubusercontent.com",
    "pypi.org",
    "pythonhosted.org",
    "npmjs.org",
    "registry.npmjs.org",
    "ntfy.sh",
    "localhost",
    "127.0.0.1",
)


class EgressBlocked(Exception):
    """Raised by guarded_request() when a target host isn't on the
    allowlist. Deliberately a distinct exception type (not a bare
    ValueError) so callers can catch/handle it specifically."""


def check_allowed(url: str) -> bool:
    """True if `url`'s hostname matches (or is a subdomain of) one of
    ALLOWED_HOST_SUFFIXES. Case-insensitive; a bare hostname with no
    scheme is accepted too (urlparse still extracts it correctly for the
    common `host:port` and `host/path` shapes this project's own targets use)."""
    parsed = urlparse(url if "//" in url else f"//{url}")
    host = (parsed.hostname or "").lower()
    if not host:
        return False
    return any(host == suffix or host.endswith("." + suffix) for suffix in ALLOWED_HOST_SUFFIXES)


def guarded_request(method_fn, url: str, *args, **kwargs):
    """Call `method_fn(url, *args, **kwargs)` (e.g. `requests.get`) only if
    `url` passes check_allowed(); raises EgressBlocked otherwise, before
    any network call is attempted."""
    if not check_allowed(url):
        raise EgressBlocked(
            f"Egress blocked: {url!r} is not on the allowlist "
            f"(ALLOWED_HOST_SUFFIXES in background/egress_allowlist.py)."
        )
    return method_fn(url, *args, **kwargs)
