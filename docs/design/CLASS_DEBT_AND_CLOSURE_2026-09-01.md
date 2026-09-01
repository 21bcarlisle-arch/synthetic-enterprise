# Class debt: what the registers cost, what closes them, and whether they are one class

*Delivery seat, 2026-09-01, answering the director's instruction of the same morning.*

---

## 1. What was wired

`background/finding_classes.py` has rendered a cumulative cost into each class register since
2026-08-12 and **nothing read it**. `background/staging_rooms.py` classified every `CLASS_*`
document as `KIND_REFERENCE`, which is in `NOT_WORK`, so a register was dropped from the queue
before rank was ever considered. A cost nobody reads and an artefact that cannot be drawn are one
defect seen from two ends, and the register's own `no_caller_and_never_runs` class is its name.

`background/class_debt.py` reads the cost, and `work_queue()` now splices accruing registers into
the draw at **rank 35 — between a decomposed mint (30) and an individual finding (40)**. The
argument is the ruling's own: *"a class with a live instance list is the artefact that can win a
draw; twenty siblings filed separately cannot."* A finding is one instance of something; an
accruing class is what generates such findings.

**Why the registers were reference until now, and why that is not being reversed.** A standing
register cannot be a queue item, because it is re-rendered in place and never actioned-and-archived
— while all six sat in the work channel the root could never reach zero, which is how that folder
reached 49 items. That argument turns entirely on a register having **no exit**. A register now has
one: a `## Disposition` section recording a decision about the class. A register with a current
decision is reference and is dropped exactly as before. **It drains by being decided, never by being
consumed**, so the root can still signal "drained".

That is also what keeps this a decision rather than a rule. Nothing in the module computes whether a
class *should* be closed. It computes what a class has cost, decides only whether that cost has been
**looked at**, and puts the un-looked-at ones in front of the work they are taxing.

---

## 2. The debt, measured

| Class | n | measured | episode-hours | persisted-days | commits-on-top | same-day pairs | last 7d |
|---|---:|---:|---:|---:|---:|---:|---:|
| `publish_gate_and_wedge` | 55 | 15 | 322.9 | 17.42 | 1,676 | 134 | 8 |
| `controls_that_cannot_fail` | 26 | 1 | 25.0 | 4.00 | 1,775 | 50 | 2 |
| `uncommitted_and_orphaned_work` | 20 | 2 | 31.0 | 0.00 | 1,561 | 11 | 5 |
| `no_caller_and_never_runs` | 8 | 0 | 0.0 | 14.00 | 1,676 | 1 | 3 |
| `figures_on_a_superseded_clock` | 3 | 0 | 0.0 | 0.00 | 72 | 1 | 3 |
| `measurements_that_mirror` | 7 | 0 | 0.0 | 0.00 | 1,300 | 4 | 1 |

**118 instances when the table was measured, 119 by the time it landed — the twentieth `uncommitted_and_orphaned_work` instance arrived during this pass and is described below. 18 of them — 15% — record any duration at all.** Every cost figure above is a
floor on that basis.

**The three units are never added, and `commits-on-top` is not summable across classes either**:
six classes were open simultaneously, so the same commit sits under all six and a total would count
the tree six times.

### What the old cost measure was blind to, and how that was established

The director's instruction said the recorded cost is too low because it counts each instance in
isolation. It is, and there was a second reason underneath it.

`cost_evidence`'s vocabulary — `wedge|outage|stall|blackout|starved|…` — is the **availability**
vocabulary, which is the publish-gate class's own vocabulary. So it measured loudest on the class it
was written from (15 of 55) and read **0.0 on three of six classes**, none of which was free. A cost
measure that reads its own subject back is `measurements_that_mirror`, committed by the instrument
used to rank it.

A second term now reads how long the instances say a **wrong state persisted**. Its clearest result:
`no_caller_and_never_runs` goes from *0.0 hours* to **14 persisted-days** — *"`resource_headroom`
sat unwired for nine days"*, *"the code/artefact gap was unguarded again for five days"*. On the old
measure it sorted last of the drawable classes.

**The extraction was narrowed by measurement, not by taste, and the wrong drafts are recorded.** A
wide net over "a duration near a damage word" was run against the whole corpus first. It accepted
15 figures of which **7 were wrong**: *"three instances in three days"* is a recurrence rate,
*"forgets a failed collection after three weeks"* is a model parameter, *"predates it by two days"*
is an offset. The two spurious three-week reads alone would have put 42 days on a class with no
measured cost at all and moved it up the draw on nothing. The rule kept is the one syntax that
discriminated cleanly — the duration must be governed by `for` (*"false **for six days**"*, *"served
a frozen artefact **for four days**"*) — which accepts 7 and rejects all 7 known false ones, at the
price of missing real costs written another way (*"repaired eight days earlier"*). **It under-reads
on purpose.** All seven false sentences are pinned in `tests/background/test_class_debt.py` so a
later widening has to defeat them deliberately.

### What could not be counted, said plainly

The director's own example — *eleven hours of outage from two same-day findings interacting* — **is
not derivable from this corpus.** Each document records its own episode; nothing records the
combined one. Summing them would double-count, and a figure for the interaction itself would have to
be invented. What is counted instead is the **opportunity**: 134 same-day instance pairs in the
publish-gate class, 50 in `controls_that_cannot_fail`, 201 across all six. That gives the gap a size
without inventing a number to fill it.

The same applies to the other two examples in the instruction. *A week of A/B results measured on
nine accounts* and *three days on a churn model that could not read its own price* are both
invalidated-work costs; the corpus records them as prose in documents that are not instances of these
classes, and no rule here reaches them.

---

## 3. Per class: what closes it, whether it exists, what it would have caught

Full reasoning is in each register's `## Disposition` section. Summary:

| Class | What closes it | Exists? | Verdict |
|---|---|---|---|
| `publish_gate_and_wedge` | — | **cannot be stated** | **Split first.** It is two families. |
| `controls_that_cannot_fail` | empty-population floor; falsifier requirement | **half** | Build the missing half. |
| `uncommitted_and_orphaned_work` | check past-tense records against commits | **four narrow ones** | Consolidate them to one property. |
| `no_caller_and_never_runs` | reachability check on every control | **fragments** | Prerequisite blocked. |
| `figures_on_a_superseded_clock` | a summary shares its rows' clock | **yes, scoped too narrowly** | **Closest to closable.** |
| `measurements_that_mirror` | instrument's input ≠ its own output | no | **ACCEPTED**, re-opens at 9. |

The four that matter:

**`figures_on_a_superseded_clock` — the mechanism exists and three instances still got past it.**
CLAUDE.md names it: *every financial figure carries its clock*, enforced by the basis gate in
`tools/generate_dashboard_data.py`. All three instances are financial figures published beside a
figure re-summed from mutated rows. The gate is keyed to **that generator's own fields**, and all
three instances are A/B and treasury surfaces that never pass through it. Extending the requirement
from the fields to the **property** is small work and would close the class. This is the best
candidate in the set.

**`uncommitted_and_orphaned_work` — four controls, one property.** Controls of exactly the right
shape landed on 2026-08-18, 08-18, 08-19 and 09-01. Eleven of the twenty instances predate all of
them. The four that arrived afterwards were filed anyway, because **each control is scoped to one
record type** — a discharge, a store's falsifier, a store's symbol, a "What landed" heading — so a
fifth record type is uncovered by construction and nothing says so.

*(Correction, made here rather than quietly: the fourth of those,
`tests/design/test_a_landed_claim_names_an_artefact_that_is_in_a_commit.py`, was UNTRACKED when the
table above was built — a control against unlanded claims that was itself unlanded. Another lane
landed it in `2f7ea8dd4` while this was being written. The observation was true and is no longer.)*

**The twentieth instance arrived during this pass and is the uncovered fifth record type exactly.**
A test file rewritten ahead of an API that was never written took **413 architecture controls out
of collection for nine and a half hours** — not failing, not running — and none of the four
controls is about a test file's imports. Its one-leg control landed with this document
(`tests/architecture/test_a_test_module_imports_a_name_that_exists.py`), which makes **five narrow
controls where the argument above says there should be one.** That is the class demonstrating its
own diagnosis inside a single morning.

**`controls_that_cannot_fail` — the covered half proves itself, the uncovered half has nothing.**
`tests/architecture/test_no_tree_scan_passes_on_an_empty_population.py` (2026-08-27) is real: it
caught a live offender during this very pass (`tests/tools/test_the_door_works_from_a_worktree.py`,
repaired in the same commit). It closes the *subject-emptied* half. For the *verdict-cannot-be-false*
half — *fires on the word nothing*, *swallowed 199 generator crashes*, *fail-open on a full disk* —
**no mechanism exists.** 344 test files carry a `MUTATION` docstring by convention and nothing
refuses a new control that has no falsifier.

**`no_caller_and_never_runs` — blocked on a prerequisite, and this is the useful finding.** The
general mechanism would be a reachability check. The nearest thing to one is the reuse convention —
and `WORKER_FINDING_THE_REUSE_CONVENTION_MANUFACTURES_FALSE_CALLERS_2026-08-28` is **open in the
staging root right now** and says that convention produces callers that do not call. A reachability
control built on it would go green on exactly the population it exists to catch. Establishing what a
real caller is comes first.

---

## 4. Is it one class?

**No. It is one lineage and it should not be consolidated — and the reason is the same reason the
director asked for cumulative cost in the first place.**

The through-line is real and it is broader than he put it. *Something was recording, and nothing was
checking that the record was of the thing it claimed to be* covers, on the titles:

- `measurements_that_mirror` (7/7) — the record is of itself.
- `figures_on_a_superseded_clock` (3/3) — the record is of an older version of its subject.
- `uncommitted_and_orphaned_work` (19/19) — the record says *landed*, *discharged*, *counted*; the
  tree holds nothing. *Three consecutive passes recorded a landing that is in no commit.*
- `no_caller_and_never_runs` (8/8) — the record says a control exists; nothing checked it runs.
- `controls_that_cannot_fail` (~12/26) — the subject-moved half exactly. The fail-open half is a
  near miss: there the record is not *of the wrong thing*, it is **absent and read as a pass**.
- `publish_gate_and_wedge` (~2/3 of 55) — *an OOM kill recorded as a test regression*, *the headroom
  surface publishes a test fixture as the gate's duration*, *the wedge detector fed itself*. The
  other third is gate capacity and topology and is not this shape at all.

So roughly 85 of 118 instances are faces of one thing. **That is a diagnosis, not a register.**

The decisive test is what the parent register would be *for*. A class document exists, in this
project's own words, "to argue one repair against one cumulative cost". The parent has no single
repair: the closures above are a caller census, a git-vs-record check, an input-≠-output check, a
clock check and a population floor. One register holding 118 instances and one cost would argue for
nothing — **consolidating would destroy exactly the property being wired in this morning.** A class
you cannot close is not a class, it is a theme.

What the lineage *does* buy is a prediction, and it is worth more than a merge: **every closure in
the table above has the same shape — compare the record to its subject, and fail when the subject
cannot be read.** Both halves are load-bearing and this project has paid for each separately
(fail-closed-on-unreadable-input; controls keyed to a structure that moved). That shape is the thing
to build to, and it is why `class_debt` carries a dated population floor of its own.

**The consolidation that IS warranted is a split, not a merge.** `publish_gate_and_wedge` is at 55
against the director's count of ~18. Its patterns grew it by naming **mechanisms** rather than a
family (`\btmpfs\b|\boom\b`, `surgical_land`), and it now holds two families with no shared repair.
It ranks first in the draw today partly because it is a catch-all, which makes the split the first
work the new ranking asks for. No instance has been reclassified: moving 55 archived documents on an
unverified boundary would be a larger version of the defect being fixed.

---

## 5. Decisions taken, and what was rejected

**Taken.** Five classes recorded `OPEN` with the next work named. One recorded `ACCEPTED` —
`measurements_that_mirror`, the only class that has stopped recurring — with its cost showing **and
with the fact that the cost is unknown stated in the same breath**: zero of seven instances measured
anything, so 0.0h means *not measured*, never *not costly*. It re-opens automatically at 9
instances.

**Rejected — a cost threshold for entering the draw.** It would need a number picked because a
number was needed. Accrual needs none: two instances in seven days, re-using R10's own bar that one
instance is not a class. The measured consequence is real — `figures_on_a_superseded_clock` has zero
recorded cost and is the fastest-accruing class in the set, and a cost threshold would not have
drawn it.

**Rejected — ordering the classes by cost.** The first draft did, and it put `controls_that_cannot_
fail` (25 hours, 4 days) above `no_caller_and_never_runs` (0 hours, 14 days), because a lexicographic
key over two units silently asserts that any quantity of the first beats any quantity of the second.
That is adding hours to days with the addition hidden inside a sort. **Instances lead instead**: the
count is measured for 100% of the population and every cost term for 15% of it, so a cost-led rank
ranks classes by their measurement habit. Cost orders within a tie and is printed on every row.

**Rejected — summing the persisted-days across classes into a headline.** Different classes, same
episodes in some cases. The per-class figures stand, each traceable to the sentence it came from.

**Open to reversal.** The one place I would expect the director to disagree is rank 35: an accruing
class always outranks an individual finding. The alternative is that cost decides the *band* as well
as the order, which needs a threshold, which is the thing I refused above. If he wants a heavy class
to outrank a mint, or a light one to sit below findings, that is a one-line change to `ORDER`.

---

*Mechanism: `background/class_debt.py`, `background/staging_rooms.py` (rank 35),
`background/finding_classes.py` (disposition carried through a re-render). Proof:
`tests/background/test_class_debt.py`. Read the live table with
`python3 -m background.class_debt`.*
