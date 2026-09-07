"""The work landed. It landed under a DIFFERENT NAME, and the row that was drawn never heard.

THE DEFECT, measured on the live ledger 2026-09-07. Two Lane 0 items were drawn separately at
04:11 and 04:41, worked together, and landed in ONE commit -- `ee3498cc0`, at origin/main -- bound
to a THIRD id, `two-of-three-drawn-focus-items-were-finished-and-never-left-the-working-tree`. The
two rows that were actually DRAWN kept `first_drawn_at` populated against a null `last_landing_at`,
so `drawn_without_landing` went on naming both to every orientation, under the heading that tells
the next seat to check `git status` before starting anything new. Re-running the ordinary route
refused them, correctly and uselessly:

    bound NOTHING to the-lane-0-chain-counter-...: it is NOT CLAIMED

TWO STORES, AND THE REFUSAL BELONGED TO ONE OF THEM. `record_landing` is gated on the CLAIMS
store, where "not claimed" is right -- there is no deadline left to inform. The DRAW LEDGER is a
different store with a different question, it survives release by construction, and it is the one
the orientation reads. `sweep_stale` empties the first at 100 minutes, so by the time this shape
exists -- finish late, land under a name that reads better -- the only route to the second was
already shut. The ledger could not tell "never landed" from "landed under another name", and every
future orientation would re-open work that was done.

MUTATIONS (each must fire, and which test catches it):
  (a) drop the `when <= first_drawn` guard -- `..._A_LANDING_THAT_PREDATES_THE_DRAW_IS_REFUSED`;
  (b) drop the `other_id == focus_id` guard -- `..._AN_ID_CANNOT_LEND_ITSELF_A_LANDING`;
  (c) drop the lender's `last_landing_at` check (credit from any row) --
      `..._A_ROW_WITH_NO_LANDING_CANNOT_LEND_ONE`;
  (d) drop the "was never drawn" guard (mint a row for any id) --
      `..._AN_ID_THAT_WAS_NEVER_DRAWN_IS_NOT_A_ROW_TO_CREDIT`;
  (e) stop writing `landed_under` -- `..._THE_ROW_CARRIES_THE_REASON_IT_HAS_NO_LANDING_OF_ITS_OWN`;
  (f) return "" on every path (report success always) -- the partition control goes red on all
      four refusal legs at once;
  (g) write the claims store as well / take a claim -- `..._IT_TAKES_NO_CLAIM_AND_MOVES_NO_DRAW`.

THE PARTITION CONTROL IS FIRST, AND IT IS ONE STATEMENT OVER FIVE OUTCOMES. A function that
refused EVERYTHING passes all four refusal legs written separately, and this project has entered
that trap through three different doors in one afternoon. So the credit and the four refusals are
asserted together, against one ledger.
"""
from __future__ import annotations

import json

from background import delivery_lane as dl

#: The two real draws and the real landing, read from
#: `docs/observability/.delivery_lane_claims.draws.json` on 2026-09-07.
CHAIN_COUNTER = "the-lane-0-chain-counter-reads-1-across-four-consecutive-continuation-draws"
DD_CONTROLS = "six-dd-level-collection-controls-are-red-at-head-and-are-still-red-at-this-orientation"
LANDED_UNDER = "two-of-three-drawn-focus-items-were-finished-and-never-left-the-working-tree"
CHAIN_COUNTER_DRAWN_AT = 1788750686.9329503
DD_CONTROLS_DRAWN_AT = 1788752487.427198
#: `ee3498cc0`'s own commit timestamp, and the four paths it touched.
EE3498CC0_AT = 1788766836.0
EE3498CC0_PATHS = ["background/delivery_lane.py", "background/seat_continuation.py",
                   "tests/background/test_a_self_issued_handoff_chain_yields_to_focus.py",
                   "tests/simulation/test_dd_level_collection_book.py"]


def _ledger(tmp_path, rows: dict):
    store = tmp_path / "claims.json"
    store.write_text("{}", encoding="utf-8")
    dl._ledger_path(store).write_text(json.dumps(rows), encoding="utf-8")
    return store


def _rows(store):
    return json.loads(dl._ledger_path(store).read_text(encoding="utf-8"))


def _real_ledger(tmp_path):
    """The 2026-09-07 shape: two drawn rows with no landing, one row holding the landing."""
    return _ledger(tmp_path, {
        CHAIN_COUNTER: {"first_drawn_at": CHAIN_COUNTER_DRAWN_AT,
                        "last_drawn_at": CHAIN_COUNTER_DRAWN_AT},
        DD_CONTROLS: {"first_drawn_at": DD_CONTROLS_DRAWN_AT,
                      "last_drawn_at": DD_CONTROLS_DRAWN_AT},
        LANDED_UNDER: {"first_drawn_at": 1788766630.6734242,
                       "last_drawn_at": 1788766630.6734242,
                       "last_landing_at": EE3498CC0_AT,
                       "last_landing_paths": list(EE3498CC0_PATHS)},
        "drawn-but-nothing-lends-it-anything": {"first_drawn_at": CHAIN_COUNTER_DRAWN_AT,
                                                "last_drawn_at": CHAIN_COUNTER_DRAWN_AT},
    })


def test_THE_PARTITION_one_pair_is_credited_and_four_are_refused_each_naming_itself(tmp_path):
    """One ledger, five outcomes, one control: a function that refuses everything must go red.

    Every refusal is asserted as NON-EMPTY *and* the credit as EMPTY, in the same statement, so
    neither "always refuse" nor "always allow" can survive. The reasons are checked for their
    distinguishing word rather than verbatim, so the message can be improved without pinning the
    control to today's wording.
    """
    store = _real_ledger(tmp_path)
    credited = dl.note_landing_under(CHAIN_COUNTER, LANDED_UNDER, path=store)
    never_drawn = dl.note_landing_under("an-id-nobody-ever-drew", LANDED_UNDER, path=store)
    itself = dl.note_landing_under(CHAIN_COUNTER, CHAIN_COUNTER, path=store)
    empty_lender = dl.note_landing_under(DD_CONTROLS, "drawn-but-nothing-lends-it-anything",
                                         path=store)
    absent_lender = dl.note_landing_under(DD_CONTROLS, "an-id-nobody-ever-drew", path=store)
    assert credited == "", credited
    assert "never drawn" in never_drawn, never_drawn
    assert "cannot lend itself" in itself, itself
    assert "NO landing" in empty_lender, empty_lender
    assert "never drawn" in absent_lender, absent_lender


def test_A_LANDING_THAT_PREDATES_THE_DRAW_IS_REFUSED_it_is_somebody_elses_work(tmp_path):
    """The same rule as `--landed`, and asserted as a MOVE across the boundary.

    An absence-only leg would pass on a function that refused every pair. So one ledger carries
    two lenders that differ ONLY in whether their landing is newer than the draw, and both
    answers are asserted together.
    """
    drawn = 1_000_000.0
    store = _ledger(tmp_path, {
        "drawn-once": {"first_drawn_at": drawn, "last_drawn_at": drawn},
        "landed-before-the-draw": {"first_drawn_at": drawn - 7200, "last_drawn_at": drawn - 7200,
                                   "last_landing_at": drawn - 1, "last_landing_paths": ["a.py"]},
        "landed-after-the-draw": {"first_drawn_at": drawn - 7200, "last_drawn_at": drawn - 7200,
                                  "last_landing_at": drawn + 1, "last_landing_paths": ["b.py"]},
    })
    stale = dl.note_landing_under("drawn-once", "landed-before-the-draw", path=store)
    assert "predates the draw" in stale, stale
    assert _rows(store)["drawn-once"].get("last_landing_at") is None
    assert dl.note_landing_under("drawn-once", "landed-after-the-draw", path=store) == ""
    assert _rows(store)["drawn-once"]["last_landing_at"] == drawn + 1


def test_AN_ID_CANNOT_LEND_ITSELF_A_LANDING_which_would_be_the_free_eraser(tmp_path):
    """Self-credit is the fail-open shape: any drawn row could clear its own missed reading.

    Asserted with a row that HAS a landing, so the refusal cannot be coming from the empty-lender
    guard one line below it -- two sequential guards, and the first one answering is exactly how
    this project has had a mutation survive before.
    """
    drawn = 1_000_000.0
    store = _ledger(tmp_path, {
        "has-its-own-landing": {"first_drawn_at": drawn, "last_drawn_at": drawn + 7200,
                                "last_landing_at": drawn + 3600, "last_landing_paths": ["a.py"]},
    })
    refusal = dl.note_landing_under("has-its-own-landing", "has-its-own-landing", path=store)
    assert "cannot lend itself" in refusal, refusal


def test_A_ROW_WITH_NO_LANDING_CANNOT_LEND_ONE_so_the_credit_is_a_join(tmp_path):
    """What makes this trustworthy is that BOTH halves are already facts in the ledger.

    The caller chooses only which pair. A lender with no landing is the shape that would turn
    this into an assertion by the caller, and it is refused.
    """
    store = _real_ledger(tmp_path)
    refusal = dl.note_landing_under(CHAIN_COUNTER, "drawn-but-nothing-lends-it-anything",
                                    path=store)
    assert "NO landing" in refusal, refusal
    assert "last_landing_at" not in _rows(store)[CHAIN_COUNTER]


def test_AN_ID_THAT_WAS_NEVER_DRAWN_IS_NOT_A_ROW_TO_CREDIT_and_no_row_is_minted(tmp_path):
    """A credit is about a DRAW. Minting a row here would put a never-drawn id in the ledger."""
    store = _real_ledger(tmp_path)
    before = set(_rows(store))
    refusal = dl.note_landing_under("an-id-nobody-ever-drew", LANDED_UNDER, path=store)
    assert "never drawn" in refusal, refusal
    assert set(_rows(store)) == before


def test_THE_ROW_CARRIES_THE_REASON_IT_HAS_NO_LANDING_OF_ITS_OWN(tmp_path):
    """`landed_under` is the one-line reason, and the paths come from the lender.

    Without the field the credited row is indistinguishable from a row that landed under its own
    name, and an audit of why an item left the missed list has nothing to follow.
    """
    store = _real_ledger(tmp_path)
    assert dl.note_landing_under(CHAIN_COUNTER, LANDED_UNDER, path=store) == ""
    row = _rows(store)[CHAIN_COUNTER]
    assert row["landed_under"] == LANDED_UNDER
    assert row["last_landing_at"] == EE3498CC0_AT
    assert row["last_landing_paths"] == sorted(EE3498CC0_PATHS)
    assert dl.last_landing(CHAIN_COUNTER, path=store) == (EE3498CC0_AT, sorted(EE3498CC0_PATHS))


def test_IT_TAKES_NO_CLAIM_AND_MOVES_NO_DRAW_it_writes_one_store(tmp_path):
    """The credit is a record, not a re-issue: no deadline starts and the draw instants stand.

    A version that took a claim would hand the id back out to the deadline machinery long after
    anyone was working it, and a version that moved `first_drawn_at` would erase the evidence the
    row is about.
    """
    store = _real_ledger(tmp_path)
    claims_before = store.read_text(encoding="utf-8")
    assert dl.note_landing_under(DD_CONTROLS, LANDED_UNDER, path=store) == ""
    assert store.read_text(encoding="utf-8") == claims_before
    row = _rows(store)[DD_CONTROLS]
    assert row["first_drawn_at"] == DD_CONTROLS_DRAWN_AT
    assert row["last_drawn_at"] == DD_CONTROLS_DRAWN_AT


def test_THE_CREDITED_ROW_LEAVES_THE_MISSED_LIST_AND_THE_UNCREDITED_ONE_STAYS(tmp_path):
    """The whole point, end to end, and asserted as a DIFFERENCE over one ledger.

    `drawn_without_landing` is what the orientation reads. Before the credit it names both real
    rows; after it, only the one that was not credited. Asserting the after-state alone would
    pass on a reader that had stopped reporting anything.
    """
    store = _real_ledger(tmp_path)
    # AFTER the landing and INSIDE the reader's 24h horizon of the two 04:11/04:41 draws. A `now`
    # a full day past the landing is a day and a half past the draws, and the horizon drops both
    # rows -- which reads as the credit working while nothing has been credited.
    now = EE3498CC0_AT + 6 * 3600
    assert now - CHAIN_COUNTER_DRAWN_AT < dl.DRAWN_WITHOUT_LANDING_HORIZON_SECONDS
    # Both real rows are named, and the lender is not -- it landed inside its own window.
    before = [r["id"] for r in dl.drawn_without_landing(now=now, path=store)]
    assert CHAIN_COUNTER in before and DD_CONTROLS in before, before
    assert LANDED_UNDER not in before, before
    assert dl.note_landing_under(CHAIN_COUNTER, LANDED_UNDER, path=store) == ""
    after = [r["id"] for r in dl.drawn_without_landing(now=now, path=store)]
    assert CHAIN_COUNTER not in after, after
    assert DD_CONTROLS in after, "only the credited row moves; the other is still genuinely missed"


def test_AN_UNWRITABLE_LEDGER_READS_AS_A_REFUSAL_never_as_a_silent_success(tmp_path):
    """Fail CLOSED here, unlike `drawn_without_landing`, and the direction is the whole point.

    The reader fails open because a brief with twenty other keys must not go down for one store.
    This is a WRITE whose answer the caller prints, and a success reported over a store that did
    not change is the one answer that would train the next seat to stop checking.
    """
    store = tmp_path / "claims.json"
    store.write_text("{}", encoding="utf-8")
    dl._ledger_path(store).write_text("{ this is not json", encoding="utf-8")
    refusal = dl.note_landing_under(CHAIN_COUNTER, LANDED_UNDER, path=store)
    assert refusal, "an unreadable ledger must not report a credit"
