"""The one named, seeded RNG substream derivation (SP2_2_rng_substream_primitive, C-S2).

Every stochastic mechanism in the world draws from its own ``random.Random``,
derived as a pure function of (namespace, name, base_seed). A new draw in one
subsystem can then never consume from, or shift, any other subsystem's stream.

The key is ``f"{namespace}::{name}::{base_seed}"`` -- byte-identical to the
formula the Formula-B modules each carried privately
(``docs/design/RNG_SUBSTREAM_PRIMITIVE_DISCOVER.md`` section 2), so moving a
Formula-B module onto this function moves none of its draws. Formula A
(``base_seed:name``, no namespace) and Formula C (single colon) modules DO move
when migrated; that is a deliberate baseline break owed its own re-pin.

Why the namespace may not contain ``:`` while the name may. Existing names
already carry ``::`` (``"payment_event::3"``, ``"away::2024"``) and re-keying
them would move draws. The encoding stays injective anyway: with a colon-free
namespace the FIRST ``::`` ends the namespace, and ``str(int)`` never contains a
colon so the LAST ``::`` starts the seed; the name is whatever lies between.
An empty namespace is refused rather than falling back to an unnamespaced key --
that fallback is the exact Formula-A collision the primitive exists to close.
"""

from __future__ import annotations

import hashlib
import random


def substream_key(namespace: str, name: str, base_seed: int) -> bytes:
    """The bytes hashed for one substream; refuses a key that could collide."""
    if not isinstance(namespace, str) or not namespace:
        raise ValueError(
            "substream namespace must be a non-empty str -- an unnamespaced "
            "key can collide with another subsystem's stream (C-S2)"
        )
    if ":" in namespace:
        raise ValueError(
            f"substream namespace {namespace!r} contains ':' -- the first '::' "
            "must end the namespace or two (namespace, name) pairs can share a key"
        )
    if not isinstance(name, str):
        raise TypeError(f"substream name must be a str, got {type(name).__name__}")
    if isinstance(base_seed, bool) or not isinstance(base_seed, int):
        raise TypeError(
            f"substream base_seed must be an int, got {type(base_seed).__name__} -- "
            "a non-int seed's str() may contain ':' and break the key's injectivity"
        )
    return f"{namespace}::{name}::{base_seed}".encode("utf-8")


def substream(namespace: str, name: str, base_seed: int) -> random.Random:
    """An ISOLATED ``random.Random`` for mechanism ``name`` of subsystem ``namespace``.

    Seeded from the first 8 bytes (big-endian) of SHA-256 over
    ``substream_key`` -- a stable digest, never Python's per-process-salted
    ``hash()``, so replay holds across processes.
    """
    digest = hashlib.sha256(substream_key(namespace, name, base_seed)).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))
