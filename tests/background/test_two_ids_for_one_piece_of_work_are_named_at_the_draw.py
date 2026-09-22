"""Two ids for one piece of work were undetectable at the draw, and cost two seat turns twice.

THE DEFECT (2026-09-17, measured on this lane's own draws). `era5-pull-the-last-23-cells-in-two-
passes-an-hour-apart` and `era5-pull-the-last-23-in-book-weather-cells-after-the-quota-resets` were
drawn concurrently against the same 23 cells. The rival landed `7d9eabe49` at 07:24 and this seat
re-derived the same premise from a two-commit-stale worktree minutes later.

THE DISPOSITION HALF ALREADY WORKED and is not what is tested here: `--landed-under` credits one id
with another's landing, and it correctly REFUSED, because the rival landed BEFORE the draw. What had
no question anywhere was the DRAW, where the collision was still cheap. Both items cited commits
that were genuine ancestors of origin/main, so `premise_note` passed them both in silence. The tell
that actually caught it was `ps`, read for an unrelated reason, which is not a mechanism.

KEYED TO THE PROPERTY, NEVER TO TODAY'S IDS OR THE LIVE STORES. The property is: **a draw whose
subject is already in somebody else's hands says so in the dispatch.** Every id below is synthetic
and every store is a tmp_path; the one live thing asked is `git ls-files`, and the paths it is asked
about are this repository's own at any commit. The 2026-09-17 pair appears once, in
`..._THE_PAIR_THAT_COST_TWO_TURNS`, as the shape the rule has to catch and not as data it is tuned
to -- its two ids are rebuilt from tokens the fixture ledger has never seen.

MUTATIONS (each must fire, and which test catches it). All SIXTEEN were RUN on 2026-09-17, one at
a time, in a `git archive` extract given its own index — the extract needs one, because
`_paths_named_in` joins against `git ls-files` and without it the path leg is silently dead and the
two path controls below fail at every commit. Every one of them reddened at least the test named.
Eight of the sixteen — c, d, e, f, j, k, n, o — were re-run independently later the same day by
monkeypatch rather than by editing, and all eight fired again. Two of that eight fired only after
the SIMULATION was corrected, and both slips were in the flattering direction, so they are written
down here: patching `_ledger_path` to blind the `named_paths` read (d) also moved where the fixture
WRITES the vocabulary, so the mutation changed nothing; and passing a one-store list for (o) raised
`IndexError` out of the fixture, which is not the control refusing. Blind the second store at READ
time and strip the field at READ time — a mutation that the fixture follows is not a mutation:
  (a) return `{}` from `rival_claims` always -- the partition control reds (this is the defect);
  (b) drop the subject leg -- `..._THE_PAIR_THAT_COST_TWO_TURNS` and the partition control red;
  (c) drop the path leg -- the partition control reds;
  (d) read only `rec["paths"]` and not the ledger's `named_paths` -- the partition control reds,
      because at draw time neither claim has landed and `named_paths` is the only path either has;
  (e) lower `_RIVAL_TOKEN_COUNT` to 1 -- `..._ONE_SHARED_WORD_IS_A_TOPIC_AND_NOT_A_DUPLICATE` reds;
  (f) drop the rarity ceiling, so any shared token counts -- the same test reds, because the pair
      it uses shares four ordinary words the fixture ledger is full of;
  (g) stop excluding the item's own id -- `..._AN_ITEM_IS_NEVER_ITS_OWN_RIVAL` reds;
  (g2) stop excluding its pre-2026-09-16 TRUNCATED twin -- the same test reds, and it is listed
      separately because the two exclusions are one line apart and each passes the other's test;
  (h) stop excluding stale claims -- `..._A_DEAD_CLAIM_IS_NOT_A_RIVAL` reds;
  (i) call `claims_mod.sweep` instead of `stale_claims` -- `..._THE_CHECK_DOES_NOT_SWEEP` reds;
  (j) drop `_informative` -- `..._A_SHARED_ROOM_IS_TRAFFIC_AND_NOT_DUPLICATION` reds;
  (k) drop `_VOCABULARY_FLOOR` -- `..._A_LEDGER_TOO_YOUNG_TO_JUDGE_RARITY_SAYS_NOTHING` reds;
  (l) let an unreadable store raise -- `..._THE_CHECK_NEVER_TAKES_THE_DRAW_DOWN` reds;
  (m) take the vocabulary from the live ledger instead of the passed store -- the young-ledger
      control reds, because the live ledger is always over the floor;
  (n) compose the doorbell without `rival_note` -- `..._THE_DISPATCH_CARRIES_THE_CHECK` reds;
  (o) read one claim store instead of both -- the partition control reds, because one of its four
      rivals is held by the OTHER writer.

THE PARTITION CONTROL IS FIRST AND IT IS ONE STATEMENT OVER FOUR READINGS. A `rival_claims` that
answered `{}` to everything passes every per-leg test ever written for it, and this lane has walked
into that trap through three separate doors in one afternoon. So words-only, paths-only, both and
neither are asserted together against one pair of stores.
"""
from __future__ import annotations

import json
import time

import pytest

from background import delivery_lane as dl
from background import seat_work_in_hand as claims_mod

#: A file this repository tracks at every commit, in a room NO claim owns. The path leg is a join
#: against `git ls-files`, so an untracked spelling would make every path assertion below vacuous.
OWNED_PATH = "background/delivery_lane.py"
SECOND_OWNED_PATH = "background/seat_work_in_hand.py"

#: Tracked, and under a prefix `claims_mod.SHARED_BY_DESIGN` declares. Asserted, not assumed --
#: if that list is ever narrowed, the shared-room control must red rather than quietly test nothing.
SHARED_ROOM_PATH = "docs/reports/ANNUAL_REPORT.md"

#: Enough remembered draws for "rare across the ledger" to mean anything. Deliberately built from
#: words the test's own rival ids never use, so a token the pair shares is rare BECAUSE the pair
#: shares it and not because the ledger is empty.
FILLER_WORDS = (
    "settlement tariff hedge renewal ledger dashboard invoice meter forecast cohort "
    "margin carbon levy standing supplier register canon envelope oracle ratchet "
    "publisher worktree promoter reconciler doorbell alarm harness verifier auditor "
    "clock basis rung stratum leg floor ceiling window disposition residue "
    "sample quantile spread bound estimate refusal witness grader partition seam"
).split()


def _filler_ids(count: int) -> list[str]:
    """`count` distinct synthetic ids, each using two filler words and nothing the pair uses."""
    out = []
    for i in range(count):
        a = FILLER_WORDS[i % len(FILLER_WORDS)]
        b = FILLER_WORDS[(i * 7 + 3) % len(FILLER_WORDS)]
        out.append(f"fix-the-{a}-so-the-{b}-holds-{i}")
    return out


@pytest.fixture()
def stores(tmp_path):
    """A delivery store and a seat store, each with its own draw ledger, neither of them live."""
    delivery = tmp_path / "delivery_claims.json"
    seat = tmp_path / "seat_claims.json"
    for store in (delivery, seat):
        store.write_text("{}")
        dl._ledger_path(store).write_text("{}")
    return [(delivery, float(dl.CLAIM_STALE_SECONDS)),
            (seat, float(claims_mod.STALE_AFTER_SECONDS))]


def _hold(store, work_id, *, claimed_at, paths=None):
    claims = json.loads(store.read_text())
    claims[work_id] = {"claimed_at": float(claimed_at), "note": "", "paths": list(paths or [])}
    store.write_text(json.dumps(claims))


def _remember(store, work_id, *, named_paths=None, drawn_at=0.0):
    """Put an id in the draw ledger — which is where the vocabulary and `named_paths` come from."""
    ledger = json.loads(dl._ledger_path(store).read_text())
    row = {"first_drawn_at": float(drawn_at), "last_drawn_at": float(drawn_at)}
    if named_paths is not None:
        row["named_paths"] = list(named_paths)
    ledger[work_id] = row
    dl._ledger_path(store).write_text(json.dumps(ledger))


def _stock_the_vocabulary(store, extra=()):
    for work_id in _filler_ids(dl._VOCABULARY_FLOOR + 20):
        _remember(store, work_id)
    for work_id in extra:
        _remember(store, work_id)


NOW = 1_700_000_000.0


def test_ALL_FOUR_READINGS_ARE_REACHABLE_AND_NEITHER_LEG_ANSWERS_FOR_THE_OTHER(stores):
    """The partition, in one statement. A check that says `{}` to everything passes every leg test
    below and is exactly the defect; a check that says "rival" to everything is the noise that
    trains a reader to skip the line. Both are refused here."""
    delivery, seat = stores[0][0], stores[1][0]
    # EACH RIVAL SHARES ITS OWN PAIR OF RARE WORDS WITH `mine` AND NOT WITH THE OTHERS. A word all
    # three used would be in three ids, which is over the rarity ceiling by construction -- the
    # first draft of this fixture failed for exactly that reason, and it is the right refusal.
    mine = "resume-the-quisset-fenwick-crawl-and-refill-the-halvard-bracken-store"
    words_only = "restart-the-quisset-fenwick-pass-tonight"
    paths_only = "make-the-promoter-stop-guessing-which-room-it-is-in"
    both = "rebuild-the-halvard-bracken-index-in-one-go"
    neither = "give-the-invoice-basis-line-its-own-clock"

    _stock_the_vocabulary(delivery, extra=[mine, words_only, both, neither])
    _remember(delivery, paths_only, named_paths=[OWNED_PATH])
    _remember(delivery, both, named_paths=[SECOND_OWNED_PATH])
    for work_id in (paths_only, both, neither):
        _hold(delivery, work_id, claimed_at=NOW - 60)
    # HELD BY THE OTHER WRITER. The two stores are the interactive seat's and this lane's, and the
    # pair that collided on 2026-08-31 was one item held by a tick and the other by a session, so a
    # check that read one store would be blind to exactly the shape it exists for.
    _hold(seat, words_only, claimed_at=NOW - 60)

    item = {"id": mine,
            "what": f"Re-run the crawl. The reader is {OWNED_PATH} and the store is "
                    f"{SECOND_OWNED_PATH}.",
            "why": "the last pass stopped at the quota"}
    found = dl.rival_claims(item, now=NOW, stores=stores)

    assert set(found) == {words_only, paths_only, both}, found
    assert any("distinctive words" in r for r in found[words_only])
    assert not any("already holds" in r for r in found[words_only])
    assert any("already holds" in r for r in found[paths_only])
    assert not any("distinctive words" in r for r in found[paths_only])
    assert len(found[both]) == 2, found[both]


def test_THE_PAIR_THAT_COST_TWO_TURNS_IS_NAMED_BEFORE_EITHER_LANE_SPENDS_A_TURN(stores):
    """The 2026-09-17 shape, end to end: two ids, two live claims, NEITHER having landed anything,
    and the note has to come out of the draw-time information alone."""
    delivery = stores[0][0]
    mine = "era5-pull-the-last-23-cells-in-two-passes-an-hour-apart"
    rival = "era5-pull-the-last-23-in-book-weather-cells-after-the-quota-resets"

    _stock_the_vocabulary(delivery, extra=[mine, rival])
    _hold(delivery, rival, claimed_at=NOW - 900)  # no paths: it has landed nothing yet

    note = dl.rival_note({"id": mine, "what": "pull the last 23 cells", "why": "coverage"},
                         now=NOW, stores=stores)

    assert "DUPLICATE-WORK CHECK" in note
    assert rival in note
    assert "era5" in note and "pull" in note
    assert "--landed-under" in note and "--release" in note
    assert "not a refusal" in note, "a refusal would have to be right about which; a note need not"


def test_ONE_SHARED_WORD_IS_A_TOPIC_AND_NOT_A_DUPLICATE(stores):
    """Two items on one subject are the ordinary case in this lane — a finding and its repair, a
    floor and the promotion waiting on it. The rule has to be able to stay quiet about them."""
    delivery = stores[0][0]
    mine = "resume-the-quisset-crawl-for-the-outstanding-tiles"
    rival = "give-the-quisset-reader-a-clock-of-its-own"

    _stock_the_vocabulary(delivery, extra=[mine, rival])
    _hold(delivery, rival, claimed_at=NOW - 60)

    assert dl.rival_claims({"id": mine, "what": "", "why": ""}, now=NOW, stores=stores) == {}


def test_AN_ITEM_IS_NEVER_ITS_OWN_RIVAL_UNDER_EITHER_SPELLING(stores):
    """`draw()` claims BEFORE it composes, so the item is always in the store by the time this
    runs; and an id carrying a decimal still has a truncated twin from before 2026-09-16."""
    delivery = stores[0][0]
    mine = "the-third-arm-separates-fewer-quisset-accounts-in-p6s-2.45-percent"
    truncated = "the-third-arm-separates-fewer-quisset-accounts-in-p6s-2"

    _stock_the_vocabulary(delivery, extra=[mine, truncated])
    _hold(delivery, mine, claimed_at=NOW - 10, paths=[OWNED_PATH])
    _hold(delivery, truncated, claimed_at=NOW - 10, paths=[OWNED_PATH])

    item = {"id": mine, "what": f"the subject is {OWNED_PATH}", "why": ""}
    assert dl.rival_claims(item, now=NOW, stores=stores) == {}


def test_A_DEAD_CLAIM_IS_NOT_A_RIVAL(stores):
    """A claim past its own deadline is work nobody is doing. Reporting it would send every reader
    to check a row the next sweep is about to release."""
    delivery = stores[0][0]
    mine = "era5-pull-the-last-23-cells-in-two-passes-an-hour-apart"
    rival = "era5-pull-the-last-23-in-book-weather-cells-after-the-quota-resets"

    _stock_the_vocabulary(delivery, extra=[mine, rival])
    _hold(delivery, rival, claimed_at=NOW - dl.CLAIM_STALE_SECONDS - 1)

    assert dl.rival_claims({"id": mine}, now=NOW, stores=stores) == {}


def test_THE_CHECK_DOES_NOT_SWEEP(stores):
    """`claims_mod.overlapping_claims` is the nearest existing organ and it sweeps. A read taken to
    compose a doorbell must not change what is claimed, or the draw becomes a writer."""
    delivery = stores[0][0]
    rival = "era5-pull-the-last-23-in-book-weather-cells-after-the-quota-resets"
    _stock_the_vocabulary(delivery, extra=[rival])
    _hold(delivery, rival, claimed_at=NOW - dl.CLAIM_STALE_SECONDS - 1)

    dl.rival_claims({"id": "era5-pull-the-last-23-cells-in-two-passes-an-hour-apart"},
                    now=NOW, stores=stores)

    assert rival in json.loads(delivery.read_text()), "the check released a claim it only read"


def test_A_SHARED_ROOM_IS_TRAFFIC_AND_NOT_DUPLICATION(stores):
    """Every lane writes in `docs/reports/`. An overlap there is two lanes filing, not two lanes
    building the same thing, and reporting it trains the reader to skip the line."""
    assert any(SHARED_ROOM_PATH.startswith(p) for p in claims_mod.SHARED_BY_DESIGN), \
        "this control tests nothing unless its path is in a room the writer calls shared"
    delivery = stores[0][0]
    mine = "publish-the-quisset-figure-with-its-basis"
    rival = "give-the-fenwick-table-a-sample-size-bound"

    _stock_the_vocabulary(delivery, extra=[mine, rival])
    _remember(delivery, rival, named_paths=[SHARED_ROOM_PATH])
    _hold(delivery, rival, claimed_at=NOW - 60)

    item = {"id": mine, "what": f"the figure goes in {SHARED_ROOM_PATH}", "why": ""}
    assert dl.rival_claims(item, now=NOW, stores=stores) == {}


def test_A_LEDGER_TOO_YOUNG_TO_JUDGE_RARITY_SAYS_NOTHING_ABOUT_WORDS_AND_STILL_READS_PATHS(stores):
    """An empty ledger gives every token a count of zero, so an ungated rarity test would call
    every pair of ids rivals. The subject leg stands down; the path leg does not depend on it."""
    delivery = stores[0][0]
    mine = "era5-pull-the-last-23-cells-in-two-passes-an-hour-apart"
    words_only = "era5-pull-the-last-23-in-book-weather-cells-after-the-quota-resets"
    with_path = "give-the-fenwick-table-a-sample-size-bound"

    for work_id in _filler_ids(dl._VOCABULARY_FLOOR - 5):
        _remember(delivery, work_id)
    _remember(delivery, with_path, named_paths=[OWNED_PATH])
    _hold(delivery, words_only, claimed_at=NOW - 60)
    _hold(delivery, with_path, claimed_at=NOW - 60)

    found = dl.rival_claims({"id": mine, "what": f"the subject is {OWNED_PATH}"},
                            now=NOW, stores=stores)
    assert set(found) == {with_path}, found


def test_THE_CHECK_NEVER_TAKES_THE_DRAW_DOWN(stores, tmp_path):
    """It sits inside `doorbell`, which sits inside `draw`, which must never raise into the
    supervisor. An unreadable store yields no note — the behaviour before this existed."""
    broken = tmp_path / "not_json.json"
    broken.write_text("{ this is not json")
    dl._ledger_path(broken).write_text("{ nor is this")

    assert dl.rival_note({"id": "anything-at-all"}, now=NOW, stores=[(broken, 1.0)]) == ""
    assert dl.rival_claims({"id": "anything-at-all"}, now=NOW, stores=[(broken, 1.0)]) == {}


def test_THE_DISPATCH_CARRIES_THE_CHECK_AHEAD_OF_THE_WORK(monkeypatch, stores):
    """A tick that reads the work before it reads the check has already started, which is why
    `premise_note` goes first and why this goes with it."""
    delivery = stores[0][0]
    mine = "era5-pull-the-last-23-cells-in-two-passes-an-hour-apart"
    rival = "era5-pull-the-last-23-in-book-weather-cells-after-the-quota-resets"
    _stock_the_vocabulary(delivery, extra=[mine, rival])
    # REAL WALL CLOCK, because `doorbell` takes no `now` and the staleness read inside will use
    # `time.time()`. A fixed epoch here would make the rival stale and the control vacuous.
    _hold(delivery, rival, claimed_at=time.time() - 60)
    monkeypatch.setattr(dl, "claim_stores", lambda: stores)

    text = dl.doorbell({"id": mine, "what": "pull the last 23 cells", "why": "coverage"})

    assert "DUPLICATE-WORK CHECK" in text
    assert text.index("DUPLICATE-WORK CHECK") < text.index("LANE 0 DELIVERY")
    assert f"--landed {mine}" in text, "the dispatched id must still survive into the text"


def test_PREMISE_NOTE_STAYS_ON_WHAT_AND_WHY_AND_MUST_NOT_BE_WIDENED_WITH_THE_PATH_DOORS(
        monkeypatch) -> None:
    """THE CHANGE THIS EXISTS TO REFUSE, and it is a change that looks obviously right.

    On 2026-09-22 `path_note` was widened from a hand-rolled `what + why` to the canonical
    `_ITEM_PROSE_KEYS`, because 54 live entries named a tracked path in `done_means`/`note` and
    nowhere else. That left the SAME narrow literal sitting in `premise_note` one screen up,
    looking exactly like the defect just repaired. **Copying the widening there would be wrong,
    and the measurement is why.**

    `premise_note` fires when EVERY commit an item cites has reached origin -- "nothing this item
    points at is still outstanding". `what`/`why` is where an item states what it DEPENDS ON.
    `done_means`/`note` is where it states CRITERIA, ANCHORS and COMPLETION MARKERS, and all
    eleven live entries citing a SHA only in those fields cite one of those three: "Parts TWO and
    THREE are DISCHARGED in commit 96ec173c0", "the census fail-open closed in 37138c44f", "12
    unjudged strings at 9e9f4d994", "producing_commit must read a178b56d6".

    A COMPLETION MARKER HAS ALREADY ARRIVED BY DEFINITION, so folding it into `all arrived` makes
    the condition trivially true and manufactures a spent-premise note for an item whose work has
    not started. That is the false positive `premise_note`'s own docstring designs against, and it
    fires hardest on the six live entries that cite NOTHING in `what`/`why` -- silent today,
    spuriously spent under the widening.

    THE COUNT THAT SAYS OTHERWISE IS THE WRONG RULER, and it is recorded because it was mine:
    widening flips 6 entries to firing against 1 to silent, which reads as a clear gain until you
    ask what each number counts. They are verdict FLIPS, not CORRECT verdicts, and all 6 of the
    gains are false positives.
    """
    arrived = "3d954803e"

    def _fake_git(*args, **_kw):
        # BOTH READS MUST ANSWER, and the first draft of this stub answered only the second.
        # `_cited_commits` confirms each token with `cat-file -e` before `premise_note` asks
        # ancestry, so a stub that refuses `cat-file` yields ZERO cited commits and the door
        # returns "" for the reason the assertion below is testing for -- a control proving its
        # own stub. The `!= ""` leg at the end is what caught it.
        # EVERY sha resolves, and resolves as an ancestor: the completion-marker case exactly,
        # where the citation records work already done.
        if args[:1] == ("cat-file",) or args[:2] == ("merge-base", "--is-ancestor"):
            return ""
        return None

    monkeypatch.setattr(dl, "_git", _fake_git)

    marker_only = {
        "id": "cites-a-completion-marker-and-nothing-else",
        "what": "Add Birmingham and Teesside to the archive sites and re-run derive().",
        "why": "The supply book is 4/6 cell-resolved and W1_14 cannot move until it is 6/6.",
        "done_means": "done means the coverage refresh is landed; the fail-open that hid the "
                      "generator closed in {}.".format(arrived),
    }
    assert dl.premise_note(marker_only) == "", (
        "an item whose only cited commit is a COMPLETION MARKER in `done_means` was reported as "
        "having a spent premise -- the work has not started, and this is what widening "
        "`premise_note` to `_ITEM_PROSE_KEYS` does to six live entries")

    # AND THE DOOR IS NOT SIMPLY DEAD: the same commit cited in `why` as the thing the item waits
    # on must still fire. Without this leg a `premise_note` that returned "" unconditionally would
    # pass the assertion above, which is this file's own stated trap.
    depends_on_it = dict(marker_only, why="Blocked on {}, which is already on origin.".format(
        arrived), done_means="done means the coverage refresh is landed.")
    assert dl.premise_note(depends_on_it) != "", (
        "`premise_note` said nothing about an item whose stated blocker is already an ancestor of "
        "origin/main -- the door is dead and the leg above is passing on its silence")
