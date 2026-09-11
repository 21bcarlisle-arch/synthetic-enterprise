**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, origin-fork reconciliation

# The sign bar was invented twice, once on each side of the fork, and converging it provably cannot clear the blocker

**Filed 2026-09-11 by the delivery seat on a scheduled tick**, holding
`the-fork-is-one-conflicted-file-and-it-holds-the-selection-legs-two-homes`. It **corroborates and
extends** — it does not correct —
`SEAT_FINDING_THE_FORKS_MERGED_FEED_REPUBLISHES_A_SENTENCE_ITS_OWN_RECORD_CALLS_WITHDRAWN_AND_THE_TWO_SIGN_HOMES_DISAGREE_2026-09-11.md`
(same seat, earlier tick), whose §4 decision not to land the merge I independently reached and
agree with.

**RECORDED and not BLOCKING on purpose.** The blocker is already held BLOCKING by the finding
above. A second BLOCKING document on one subject doubles a lane hold without adding a constraint,
and this project already pays for holds keyed to documents rather than to defects.

---

## 0. What this tick adds, stated first

The earlier finding established *that* the two sign homes disagree and *that* they are two
quantities with one name. It left one question open in its "what is next" §1: *"One of the two
blocks must stop answering 'can the sign be stated', or the reconciliation must be widened."*

Four things are new here:

1. **The mechanism of the bar drift has a name: parallel invention across the fork.** Neither side
   changed the other's; each side independently minted its own answer to "what is the bar", and
   the merge carries both. §2.
2. **Converging the bar cannot clear the blocker, and this is now measured rather than argued.**
   Both homes were re-graded against *both* bars. The disagreement is invariant to the bar. §3.
3. **Three controls are red on the merged tree, not one, and all three share ONE cause** — a cause
   that is neither side's code. §4.
4. **The fork has grown again**: 34 ahead / 32 behind at `794ecb716`, against 26/31 when the
   earlier finding was written and 21/24 when the item was drawn. The five conflicted paths are the
   same five. §1.

## 1. The five paths are stable; the divergence is not

Re-measured this tick at `HEAD 794ecb716`, merge base `8dd060194`, read-only:

```
$ git rev-list --count HEAD..origin/main   ->  32   (behind)
$ git rev-list --count origin/main..HEAD   ->  34   (ahead)
$ git merge-tree --write-tree HEAD origin/main   -> 2773c3f70  (rc=1)
  docs/staging/records/SEAT_PREREGISTRATION_…_2026-09-11.md   (add/add)
  simulation/net_new_acquisition.py                            (content)
  site/data/value_arms.json                                    (content)
  tests/tools/test_generate_value_arms_data.py                 (content)
  tools/pre_commit_test_gate.py                                (content)
```

| when | ahead | behind | conflicted paths |
|---|---|---|---|
| item drawn (2026-09-10) | 21 | 24 | 1 *(as then believed)* |
| earlier finding, this morning | 26 | 31 | 5 |
| **this tick** | **34** | **32** | **5** |

**All four non-feed resolutions were re-derived independently in a fresh worktree
(`/var/tmp/se-lane0-merge-20260911c`, locked) before the earlier finding was read, and they agree
with it path for path** — including folding the chooser *into* `settle_within_budget` rather than
choosing a side, and keeping both pre-registrations in one file. Two independent passes reaching
the same four resolutions is the strongest evidence available that this part is settled and should
not be re-litigated on a third tick. The bytes are preserved outside the repo at
`/var/tmp/lane0-resolve-20260911/`.

*Method note, against my own process:* I re-derived all of this before reading the staging finding
that already held it. The doorbell listed that file. **Orienting on staging is cheaper than any
measurement it contains** — that is the cost this tick paid, and it is the reason it is written
down here rather than absorbed.

## 2. The bar was invented twice, and neither side deleted the other's

This is the part the earlier finding recorded as an outcome (2.0 against 2.306) without the
mechanism. The mechanism is that **both sides answered the same question from scratch**:

```
                              HEAD (794ecb716)          origin/main
SEMS_TO_STATE_A_SIGN = 2.0    ABSENT                     PRESENT  (tools/run_value_cycle_ab.py:5015)
def sems_to_state_a_sign(n)   PRESENT                    ABSENT
def distance_to_a_sign(...)   ABSENT                     PRESENT
```

`git log -S "SEMS_TO_STATE_A_SIGN = 2.0" 8dd060194..HEAD` returns **nothing**: HEAD never carried
the constant and therefore never removed it. This is not one side retiring the other's constant —
it is two lanes minting two answers to one legal question in the same week, on two sides of a fork
neither could see across.

The two answers are the normal approximation and the exact small-sample point:

```
SEMS_TO_STATE_A_SIGN        = 2.0     (a written-down constant, same for every family size)
sems_to_state_a_sign(9)     = 2.30600 (two-sided t at 0.025 each side, 8 d.o.f.)
sems_to_state_a_sign(12)    = 2.20099
sems_to_state_a_sign(30)    = 2.04523
```

**And the constant reaches the merged feed through a DEFAULTED PARAMETER, which is why nothing
caught it.** `distance_to_a_sign(mean, stdev, n, sems_needed: float = SEMS_TO_STATE_A_SIGN)` — and
all three call sites take the default:

```
tools/run_value_cycle_ab.py:5317        distance_to_a_sign(
tools/run_value_cycle_ab.py:5600        distance_to_a_sign(
tools/generate_value_arms_data.py:6954  distance_to_a_sign(
```

No call site passes a bar. A default argument is the one place a constant can outlive its own
retirement without appearing in any caller's diff — so `generate_value_arms_data.py` can carry the
comment *"THE SIGN BAR COMES FROM THE RUN PRODUCER, NOT FROM A LITERAL HERE … imported rather than
re-spelled so the two cannot drift apart again"* (line 145) and still publish the literal, in the
same module, on the same page, in the same run.

## 3. Converging the bar provably cannot clear the blocker — both homes against both bars

This is the measurement that decides the earlier finding's open §1, and it is the reason the
obvious repair is the wrong one. **Before changing a constant two figures disagree across, grade
both figures against both values of it.**

| | `sems_from_zero` | vs bar **2.0** | vs bar **2.306** |
|---|---|---|---|
| `error_bar.selection_leg` | **2.8518** | stateable | **stateable** |
| `current_world.selection_leg.distance_to_a_sign` | **1.7865** | not stateable | **not stateable** |

**The verdicts disagree under BOTH bars.** Converging the constant — whichever way — changes
neither cell that matters. The disagreement is invariant to the bar, so it is not a bar
disagreement at all: the two blocks are computed over **different seed families** (the error-bar
run's and the floor run's), and their scalars differ by 60%.

This independently re-confirms, on this fork's own numbers, the rule already landed at `03e9acfb4`
(*the sign disagreement is invariant to the bar, so converging the constant cannot clear the
fork*). It is worth restating because the bar drift in §2 is the **visible** defect and fixing it
is the move a reader of §2 alone would make — and it would leave the blocker exactly where it is
while looking like progress.

**So the bar drift in §2 is a real defect and a SEPARATE one.** It should be fixed — a defaulted
constant contradicting its own module's comment is the "one question, several implementations"
shape this project names as its most expensive — but fixing it **must not be reported as clearing
the fork**, and no control should be keyed to it doing so.

## 4. Three controls are red on the merged tree, and one cause explains all three

The earlier finding reported one failing control. The whole file, run on the merged tree this
tick: **3 failed, 195 passed (203s)**.

```
FAILED test_the_withdrawn_sentence_is_kept_beside_the_reading_that_replaced_it
FAILED test_a_remedy_whose_OTHER_HALF_IS_EMPTY_is_refused_and_not_rounded_to_zero_percent
FAILED test_a_control_arm_that_is_not_the_pages_current_run_is_STATED_and_not_left_to_inference
```

*(The earlier finding's "59 other tests passed" indicates a narrower selection, so this is not
established as a degradation — only as a fuller measurement. Said plainly rather than claimed as a
trend.)*

**Each passes on its own side and fails only merged.** Attributed in clean extracts, not assumed:

```
clean HEAD        (/var/tmp/se-attr-head-20260911)    2 passed
clean origin/main (/var/tmp/se-attr-origin-20260911)  2 passed
merged worktree                                        3 failed
```

**The single cause is that the merge changes which run is canonical**, and it is neither side's
code:

```
docs/observability/value_cycle_ab_s1_three_arm.json
  HEAD        generated_at 2026-09-09T13:58:12Z   producing_commit 8b846013e
  origin/main generated_at 2026-09-10T14:04:08Z   producing_commit 9cf9d16ed   (promoted by cf16f724e)
  HEAD-side commits touching it since the base:   NONE
```

Two of the three reds are **HEAD-side controls keyed to accidental properties of the
pre-promotion artefact** — the exact class `cf16f724e` names in its own message (*"the only three
controls it reddened had each borrowed an accidental property of whichever artefact was canonical
that week"*). Origin fixed the three that promotion reddened **on its own side**; it could not see
these, because they did not exist there. The fork is what hid them from the commit that would
otherwise have found them.

The clearest instance, and it names its own defect in its own assertion message:

```python
same = _rerun_block()["baseline_is_the_pages_current_run"]     # reads whatever is canonical today
assert same is True, ("… on a tree where they are byte-identical …")
```

The `same` leg does not construct the case it is testing — it relies on the pinned baseline and the
canonical run *happening* to be the same file this week. The property-keyed spelling is one
argument (`canonical=_load(DEPARTURE_BASELINE)`), which asserts the real property — *when the
page's current run IS the pinned baseline, the flag says so* — and is true under any promotion.
The `moved` leg already constructs its case and is correct as written.

## 5. What I did NOT do, and why

**I did not land the merge.** Same reason as the earlier finding, independently reached: it
publishes to the reader a sentence the feed's own withdrawal record names as withdrawn. The control
refusing it is right.

**I did not fix the sign blocker in the conflict resolution.** It is a producer change to the
most-read page, it needs its own controls mutation-proven, and a bounded tick that rushed it would
be shipping a judgement about what the page may claim under cover of a merge receipt.

**I did not converge the bar to make §2 go away.** §3 is the reason: it would not clear the
blocker, and a repair that looks like the fix without being it is worse than the open defect.

**I did not re-key the three controls in §4.** They are HEAD-side controls and the repair is small
and known (§4 gives the one-argument spelling for the clearest of them), but re-keying a control on
the same tick that lands the merge it refuses removes the only evidence the merge was refused for a
reason. They should be re-keyed in daylight, on HEAD, **before** the merge is attempted again.

## What is next

1. **The sign blocker, unchanged from the earlier finding's §1**, and now with §3 attached so the
   next seat does not spend a tick converging the bar: the headline must fail closed when the
   payload holds more than one readable answer to "can this sign be stated" and they disagree, and
   `_distinguishable_reconciliation` must enumerate every home rather than the two that both read
   `error_bar`. A producer change on HEAD, with its own controls.
2. **Re-key the three controls in §4 to their properties, on HEAD, before re-attempting the merge.**
   They are red only when merged, so the control must be proven against a constructed promotion
   rather than against the tree's current artefact — otherwise the next promotion reds them again.
3. **The bar drift in §2, as its own change**, with the default argument removed so no call site can
   inherit a constant silently. NOT reported as closing the fork (§3).
4. Then the merge relands: the four resolutions are settled, twice, independently
   (`/var/tmp/lane0-resolve-20260911/`), and only the feed needs regenerating against the repaired
   producer — in a real worktree with a `.git`, per the 09-10 finding's §5.
