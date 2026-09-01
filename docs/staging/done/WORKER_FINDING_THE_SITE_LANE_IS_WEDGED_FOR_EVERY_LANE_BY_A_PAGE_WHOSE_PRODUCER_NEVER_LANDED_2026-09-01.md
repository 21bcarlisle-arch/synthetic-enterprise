# [WORKER FINDING] The site lane is wedged for every lane by a page whose producer never landed

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted
**Found:** 2026-09-01, by having a bill-shock commit refused twice by a red in a file it does not
touch, in a lane it has nothing to do with.

## Class registration

Belongs to `publish_gate_and_wedge`. It also matches `uncommitted_and_orphaned_work` — the
stalled work is the cause, the wedge is the subject — and the wedge is what a reader needs to find.

**Not BLOCKING, deliberately.** It wedges commits, which is urgency, not severity: no instrument
here is untrustworthy and no published figure is claimed wrong by *this* document. The
published-figure half is already carried by
`WORKER_FINDING_A_PUBLISHED_CAPTURE_WAS_PRODUCED_BY_CODE_THAT_WAS_NEVER_COMMITTED_2026-08-31`,
which is still open — this is that defect wedging a different lane's publish. Grading my own
blocker BLOCKING and freezing a lane I do not own is the anti-pattern `background/
finding_severity.py` names in its own clause 2.

## The symptom

`python3 -m tools.surgical_land` refuses any commit whose pathspec contains a `generate_*_data`
producer, `site/data`, or a site-consumed ledger — the site lane's broad trigger — with:

    site/test_the_baseline_comparison_reaches_the_reader.py::
      test_the_level_on_the_page_is_the_one_the_measuring_tool_REPORTS
    AssertionError: the tool measures 2017 at 14.00% and the page does not carry it
    1 failed, 519 passed, 31 skipped

**And the same test passes in the working tree, alone and in the full `site/` suite:
527 passed, 31 skipped.** A red that appears only inside the gate and never in front of the person
trying to fix it is the worst shape a blocker can take.

## Why it is green in the tree and red in the gate

The gate runs the **working-tree test file** against the **tree the commit would create**. The
departure-level lane has three artefacts uncommitted, and they are only consistent with each other:

| artefact | state | what it holds |
|---|---|---|
| `simulation/departure_level_anchor.py` | **uncommitted** | `YEAR_LEVEL_ANCHOR` refitted on the two-route capture; 2016/2022/2025 deliberately absent |
| `site/data/value_arms.json` | **uncommitted** | the page rendered from those new anchors |
| `site/test_the_baseline_comparison_reaches_the_reader.py` | **uncommitted** | the new control asserting the page carries what the tool reports |

In any commit tree that does not contain all three, the **old** anchors are read (2017 solves to
14.00%) while the **old** page is served (which carries no 14.00%), and the **new** test — taken
from the working tree — sees the disagreement and fires. It is behaving exactly as designed. The
inconsistency it names is real; it just is not reachable by the lane that trips over it.

**So the control is right and the tree is wrong.** The three files must land together or not at all,
and until they do, every other lane's site-touching commit is refused for a reason it cannot fix.

## What this cost, measured rather than asserted

Two full `surgical_land` cycles on the bill-shock definition split, each ~4 minutes of gate, both
refused on this. The split itself was green throughout: `tests/tools/` 36 passed, the full `site/`
suite 527 passed in the working tree, `tests/design/` + the static ratchet 130 passed.

## Why the wedged lane must not simply land the three files

Adopting them would sweep another lane's claim into a bill-shock commit, and those anchors **move
the published departure level** — a headline figure with its own pre-registration
(`SEAT_FINDING_THE_DEPARTURE_LEVEL_UNIONED_ONTO_ACCOUNT_YEARS_AND_2022_HAS_NO_LEVER_2026-08-31`) and
its own finding still in the queue. Two published figures moving in one commit is unattributable,
which is the rule the bill-shock work is being split across three commits to obey. Landing them
under a message about bill shock would also misattribute the work to the wrong lane and the wrong
reasoning.

**The right owner is the departure-level lane, and the action is small for them and unsafe for
anyone else: land those three paths as one pathspec.**

## The staleness, which is the part that makes it a blocker rather than a race

- `site/test_the_baseline_comparison_reaches_the_reader.py` — last written **2026-08-31 17:26**
- `simulation/departure_level_anchor.py` — last written **2026-08-31 20:14**

Nineteen to twenty-one hours, with the lane's own finding filed and unactioned. This is not work in
flight that will clear on its own; it is a stalled lane holding a gate every other lane has to pass
through. `process_run`'s own publish gate runs `tests/` only and never `site/`, so **the daemon
keeps publishing straight past it** — which is why the tree has stayed in this state for a day
without anything noticing.

## What is owed

1. **The departure-level lane lands its three paths as one commit.** That clears the wedge.
2. **A commit that regenerates a page must land the code that generated it, in the same commit.**
   This is the third instance of that shape in two days. `site/data` committed by `process_run`
   while its producer sits uncommitted is the mechanism, and it is structural, not careless.
3. **Not done here**, and deliberately: this document records the blocker and names its owner. It
   does not clear it, because clearing it means landing another lane's published-figure change.
