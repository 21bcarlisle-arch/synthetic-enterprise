**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, claim `the-landed-binder-defaults-to-head-and-two-swept-rows-are-now-dispositionable`

# The heartbeat rule was on the reader and not on the writer, and the writer is the one that fills the ledger in

*`_window_hits` has refused to call a liveness republish a landing since 2026-09-19.
`record_landing` — the function that actually WRITES the credit, and whose only documented call is
the bare `--landed <id>` with its `HEAD` default — asked nothing at all. The rule existed on the
side that describes the ledger and not on the side that fills it in. It does now, through one
predicate both sides call, and the refusal names the class and the escape.*

---

## 1. What was true before this landed

| | the reader (`_window_hits`) | the writer (`record_landing`) |
|---|---|---|
| judges a commit's overlap with the claim's paths | **yes**, since 2026-09-19 | n/a |
| refuses a commit confined to the liveness surface | **yes** | **NO** |
| where the declaration is read from | `publish_gate_blocking_read.LIVENESS_SURFACE_FILES` | — |
| what a heartbeat produced | `liveness_only`, reported as *"N heartbeats touched your paths"* | a **bound claim** with its deadline restarted from the republish's own timestamp |

The mechanism is the default. `record_landing(focus_id, *, commit: str = "HEAD", ...)` and the
`--commit` argparse default of `"HEAD"` mean that what gets bound is whatever HEAD happens to be at
the instant the tick remembers to run the bind — not what the tick committed. **28 of the last 200
HEADs on this record are pure liveness republishes.** A tick that lands real work, then runs
`--landed` one republish later, was credited for work it did not do, and the deadline restarted
from the republish's clock.

**Direction, and why it is BLOCKING and not LATENT:** a ledger wrong towards *done* is not
symmetrical with one that is silent. A swept row is redrawn; a credited row never is.

**This is the register's own shape** — *a control that pins the READER is blind to a cap in the
WRITER*. The 2026-09-19 repair was correct, complete about the reading, and stopped at the seam.

## 2. What landed

- **`_is_liveness_only(touched, surface)`** — one predicate, called by both sides. Two spellings
  of one rule would drift the day the publisher declares a third liveness file. The `touched and`
  guard is load-bearing in both callers: the empty set is vacuously a subset, and without it a
  commit whose paths could not be listed becomes permanently uncreditable.
- **`record_landing` refuses a heartbeat**, after the paths are known and before the bind.
- **`refusal_reason` names it**, with the escape: *"…is a HEARTBEAT, not a landing — everything it
  touched (…) is in the publisher's declared liveness surface… re-run it as `--landed <id>
  --commit <your own sha>`"*. Both halves are graded. A caller who has never passed `--commit` has
  no reason to know it exists, and a correct diagnosis with no move is half a refusal.
- **An unreadable declaration refuses the bind**, through the `except` the function already had.
  Fail-closed: the flattering reading is *"nothing is liveness, so credit it"*, which is the
  fail-open arriving through the check's own failure. Cost: one unbound increment and a sweep.

### The choice that was made, and the branch that was refused

The drawn item offered two: *refuse an implicit commit*, or *apply the same liveness refusal*.
**The implicit-commit refusal is rejected**, and the reason is on the function. `HEAD` is the only
spelling the executor's instructions to an isolated turn give, and bare `--landed` is what every
tick in the machine runs; making that a refusal would silence the ledger for every caller to close
a hole only the heartbeat class actually walks through. The heartbeat rule is keyed to the property
— *does this commit carry work?* — rather than to how the caller spelt it, and it catches an
explicit `--commit <a-republish-sha>` too.

### One question, asked differently on each side, deliberately

The reader judges a commit's **intersection** with the claim's named paths, because there it is
choosing among commits that already touched them. The writer has no intersection to take — the
caller named a commit, not a claim's paths — so it judges **the whole commit**. That is the
stricter side: a republish is refused, and a 52-file commit that happens to include the heartbeat
is still a landing. `test_THE_WRITER_JUDGES_THE_WHOLE_COMMIT…` grades the difference, because
asking the reader's question here would look right and would turn a fact about the COMMIT into a
fact about the CLAIM.

## 3. The controls, and that each can fail

Four writer legs added to
`tests/background/test_a_heartbeat_republish_is_not_a_landing_the_lane_may_credit.py` — the same
file as the reader's, because it is the same rule and a second file is how two halves drift.

| mutation | legs that red |
|---|---|
| (g) delete the liveness clause from `record_landing` | writer partition · whole-commit · unreadable-declaration |
| (h) keep the clause, drop the cause-naming in `refusal_reason` | the refusal-names-it leg, alone |
| (i) judge the intersection with the claim's named paths instead | writer partition · whole-commit |
| (j) fall back to "nothing is liveness" when the declaration will not read | unreadable-declaration, alone |
| (a) delete the clause from `_window_hits` — **re-run after the refactor** | the three reader legs, unchanged |

Each fires on the leg written for it. **10 passed** on the file; 80 passed across the lane's five
suites. The writer partition is one statement over all three windows on purpose: a binder that
returns `[]` to everything satisfies the heartbeat leg alone, and this project has entered that
trap through three separate doors in one afternoon.

## 4. The two swept rows — one dispositioned, one refused, and the item's premise had half expired

**`land-the-stranded-shape-and-box-repair` → credited**, under
`land-the-three-stranded-instruments-by-content-not-by-pathspec`. The join is not a guess: that id
is the landing operation for the same three instruments, and the three commits are on the record —
`dc9e27ccd` the shape (`background/commit_narrative.py`), `92ad366e4` the box
(`background/delivery_seat.py`), `e5395902f` the binder (`background/delivery_lane.py`), all
between 08:40 and 09:00 on 2026-09-21, twenty hours outside the row's own window.

**`finish-the-churn-truncation-residual-the-census-is-computing-now` → NOT credited, and this is a
judgement, not an omission.** Its ledger row names `background/commit_narrative.py` and
`background/delivery_seat.py`, both of which did land in that stretch — but the row's *subject* is
a churn truncation residual, and neither module is a churn module. The named paths look like prose
that mentioned them, not the work. The item's own text no longer exists in any store: the focus
section of `DIRECTION.yaml` is rewritten each orientation, `git log --all -S` finds the id in no
revision of it, and nothing else on disk carries it. **Crediting a row whose done-condition I
cannot establish is precisely the error this item exists to close**, so the row stays silent, which
is the recoverable direction. What would settle it: the item's prose, which is gone.

**Both rows had already fallen out of the reporting horizon by draw time**, and the item's claim
that they are live in the brief is an expired prediction. `DRAWN_WITHOUT_LANDING_HORIZON_SECONDS`
is 24h; the two were last drawn 25.4h and 24.4h before this turn, and
`drawn_without_landing()` returned **0 rows** when asked. The credit above is therefore a
correction to the permanent record rather than a repair to a live surface — worth the one command,
and not worth what the item implied.

## 5. Found on the way, and NOT repaired here

`tests/background/test_a_swept_row_asks_git_whether_the_work_landed_under_another_name.py::test_THE_PARTITION_all_five_readings_come_back_from_one_ledger_in_one_statement`
**is red at HEAD**, on the `premise_spent` leg (it reads `not_done` / *CANNOT ANSWER*). Attributed
by swapping one file into the parent tree: red with this diff, red without it. It is another
lane's subject and another lane was running that batch at 12:28 today; left alone rather than
touched from here.
