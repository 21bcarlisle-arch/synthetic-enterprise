"""A dispatch claims the id the doorbell's own `--landed` instruction names, not the first
`--landed <word>` anywhere in the text.

THE DEFECT (measured 2026-10-16). The Lane 0 item
`the-draw-ledger-credits-by-the-items-work-not-by-path-overlap` says in its own WHAT "the same
binding delivery_lane --landed writes". `_DISPATCHED_ID.search` took the first match, so the
dispatch claimed and stamped a ledger row named `writes`, and the item's real id was never claimed:
its `--landed` bound nothing and the draw could hand it out again while its tick held it.

The rare branch is asserted in the same statement: a text carrying only a bare `--landed <id>`
(no instruction form) still resolves, so the preference cannot be a parser that refuses
everything else.
"""
from __future__ import annotations

from background import delivery_lane as dl

REAL_ID = "an-item-whose-prose-quotes-the-flag"


def _doorbell(prose: str, focus_id: str) -> str:
    return (f"LANE 0 DELIVERY -- WORK: {prose} IMMEDIATELY AFTER EACH COMMIT, run "
            f"`python3 -m background.delivery_lane --landed {focus_id}`: that binds the paths.")


def test_THE_INSTRUCTION_OUTRANKS_PROSE_and_a_bare_flag_still_resolves():
    quoted = _doorbell("Count it landed only on the binding delivery_lane --landed writes.", REAL_ID)
    plain = _doorbell("Nothing in this prose quotes the flag.", REAL_ID)
    bare = f"hand-written note: run --landed {REAL_ID} after the commit"

    assert (dl._dispatched_id(quoted) == REAL_ID
            and dl._dispatched_id(plain) == REAL_ID
            and dl._dispatched_id(bare) == REAL_ID
            and dl._dispatched_id("no flag here") is None), (
        dl._dispatched_id(quoted), dl._dispatched_id(plain), dl._dispatched_id(bare))


def test_CLAIM_DISPATCHED_MINTS_THE_REAL_ID(tmp_path):
    store = tmp_path / "claims.json"
    quoted = _doorbell("Count it landed only on the binding delivery_lane --landed writes.", REAL_ID)
    assert dl.claim_dispatched(quoted, path=store) == REAL_ID
    assert dl.held_at_dispatch(quoted, stores=[(store, 6000.0)]) == f"{REAL_ID} in claims.json"
