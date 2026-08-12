# [WORKER-REPORT] OPS10 — five class documents now hold fifty-one instances, and a check keeps holding them (2026-08-12)

**Severity:** RECORDED · **Lane:** H_harness · **Status:** the consolidation is landed and
its check is green; two limitations are named at the foot and nothing else is owed.

**Atom:** `OPS10_finding_class_consolidation` **L0 → L2**, self-certified into
`gate_authorizations.jsonl` (R16). Deliverable 2 of the WORK THIS CREATES block in
`DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE_2026-08-12`, clause 1.

## What landed

`background/finding_classes.py` derives class membership from the staging root and renders
five class documents. `tests/background/test_finding_classes.py` holds 26 named tests.

    docs/staging/CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md         21 instances  BLOCKING
    docs/staging/CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md      17 instances  BLOCKING
    docs/staging/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md   6 instances  LATENT
    docs/staging/CLASS_MEASUREMENTS_THAT_MIRROR_2026-08-12.md        5 instances  BLOCKING
    docs/staging/CLASS_NO_CALLER_AND_NEVER_RUNS_2026-08-12.md        2 instances  LATENT

Staging root: **130 → 83** `*.md`. 51 individuals `git mv`'d to `docs/staging/done/`
(**archived, never deleted** — the ruling's own word), one resurrected duplicate removed
after proof (below), five class documents added.

The ruling counted ~46 documents in five families by eye. The derivation finds 51 and
disagrees per family — 21 v ~18 gate, 17 v ~9 controls, 5 v ~7 mirrors, 2 v ~5 no-caller.
Each class document prints **both** numbers, his beside mine, so the disagreement is on the
page rather than silently resolved in my favour. The largest gap is `controls that cannot
fail`, where the derivation catches "blind", "disarmed", "silenced" and "swallowed" as the
same family; anyone who thinks that is too wide can read the instance list and say so.

## The five exit criteria, each against its evidence

**(1) Five documents, every instance named by filename.** Rendered from the derivation, so
the list is not typed by hand. `--check` re-derives and fails on any live finding that
belongs to a class and is missing from its list.

**(2) Archived, and the archive verified to HOLD.** `--check` asserts, per named instance,
that it exists in `docs/staging/done/` **and** does not exist in the root. The resurrection
class (`WORKER_FINDING_ARCHIVED_STAGING_PATHS_ARE_RESURRECTED_ON_THE_SHARED_TREE_2026-08-10`)
is this move's known failure mode on this tree, so the check names it as `RESURRECTED` and
`ARCHIVE MISSING` respectively, and `test_check_fails_when_a_superseded_instance_is_back_in_
the_root` proves that half fires. The landing itself used `tools.surgical_land`, because the
same finding's second-order defect is that **a pathspec commit silently downgrades a staged
rename to an add** if the old path returns inside the gate window.

**(3) Membership is DERIVED and re-checkable.** Nothing is hand-listed: the population is a
glob of the root, minus machine doorbells, class documents, externally-authored documents
and RECORDED records. A sixteenth instance filed next week is reported as `UNCONSOLIDATED`
by name — `test_check_names_a_live_finding_that_belongs_to_a_class_and_is_not_listed`, with
MUTATION D proving the report can be silenced and killing that test when it is.

**(4) Cumulative cost MEASURED from artefacts.** The gate/wedge class carries **162.5
recorded episode-hours** across 10 of its 21 instances, largest single episode **60h**;
uncommitted/orphaned carries 7.0h; controls-that-cannot-fail 25.0h; mirrors and no-caller
carry **0 hours traced**, printed as zero with an explicit note that this is a statement
about those instances' measurement and **not** a prose estimate offered in its place.

Three narrowings, each because the first draft was wrong in a way this project has already
filed against itself:
* a number is only a cost when a cost word sits within 70 characters of it — otherwise the
  ruling's own 72-hour ageing threshold bills itself to a class as damage;
* fenced code blocks are stripped first — the first draft billed a pasted pytest line
  (`assert '-1 day(s) old'`) as one day of damage;
* each instance contributes **its own largest** figure, so a finding that states its episode
  twice (`31h`, then `the 25h window inside it`) is not billed twice.
The headline is deliberately named *recorded episode-hours*, not *hours lost*: two findings
can describe the same outage from different angles, so the sum is over documents. Every
figure prints with its filename and the sentence it came from.

**(5) One name, one number.** The printed count and the rendered list come from the same
object in the same call, so they cannot disagree at write time; `--check` then re-reads the
written file and compares the printed integer with the length of the list it parses back.
MUTATION B replaces the printed count with the ruling's own estimate and kills
`test_the_printed_count_equals_the_instance_list_length`.

## R15, four mutations, each killing a named test

Mutants load from a **copy** of the module under a fresh name, with a uniqueness assertion
on every anchor (editing a source file mid-pytest corrupts `inspect.getsource`; a
same-length mutation can survive its own restoration through the `.pyc` cache — both filed
here).

| mutation | what it does | test it kills |
|---|---|---|
| A | removes the lane guard | `test_a_member_in_another_lane_is_refused_consolidation` |
| B | prints the ruling's estimate as the count | `test_the_printed_count_equals_the_instance_list_length` |
| C | drops the cost-context requirement | `test_a_number_with_no_cost_word_near_it_is_not_a_cost` |
| D | silences the UNCONSOLIDATED report | `test_check_names_a_live_finding_that_belongs_to_a_class_and_is_not_listed` |

The RELEASE half is tested too (R11, no orphan transitions):
`test_check_passes_on_a_completed_consolidation` — a consolidation done properly goes green,
so the check is not a control that is only ever red.

## Two refusals worth reading, because consolidation is a way to LOSE findings

**The lane guard.** Severity is lane-scoped (OPS9; OPS11's refusal acts per lane). Archiving
a BLOCKING `D_billing_metering` finding into an `H_harness` class document would leave the D
lane with no live blocker — laundering it out of existence under someone else's lane. A
member whose lane differs is refused, stays live in the root, and is named in a *Refused
consolidation — out of lane* section of the class document. Two documents were refused this
way. A member with **no readable lane** is refused on the same rule, fail-closed.

**The class inherits the MAXIMUM severity of its members.** Three of the five class
documents are BLOCKING because their members are. Consolidation reduces the document count;
it must not reduce the severity, or clause 2's refusal quietly loses its subject.

Externally-authored documents (`ADVISOR_*`, `DIRECTOR_*`) are classified for information but
**never** consolidated or archived by this tool. Clause 5 of the same ruling exists because
four advisor documents sat unopened for a week; folding one into a class document would be
that silence with a mechanism behind it.

## One resurrected ghost found while doing this — observed, with evidence

`WORKER_FINDING_THE_WEDGE_ALARM_IS_DISARMED_BY_RUNS_THAT_PUBLISH_NOTHING_2026-08-10.md`
existed in **both** the root and `done/`. The archived copy is the canonical one: it was
closed on 2026-08-11 by `a2d7510e2` and archived in `8582eb6ce`, and it carries a CLOSED
section the root copy lacks. Line-by-line, the root copy contained **nothing** the archived
copy lacks except the severity header OPS9 added to it during yesterday's pass — i.e. a
pre-closure copy that came back after archiving, and was then classified BLOCKING by the
severity pass, which had no way to know it was a ghost.

So one of OPS9's 29 `H_harness` blockers was **an already-closed finding wearing a fresh
header**. I removed the root copy (never blindly: the subset proof above ran first) and
carried a `RECORDED` header onto the archived canonical copy citing its closure commit.
`H_harness` BLOCKING is 28, not 29.

**The class this belongs to is one this consolidation already lists**: the resurrection
finding is an instance of `uncommitted_and_orphaned_work`, and it now has a measured
consequence — a resurrected copy does not just re-ring the doorbell, it re-enters the
severity census as a live blocker in a lane whose level-raises OPS11 is about to refuse.
Queued per SELF_INTERRUPT_DISCIPLINE rather than fixed on sight; the writer is still
unidentified and the machine is not blocked.

## What this does NOT do

* **The check has one caller: the suite.** `test_the_live_staging_root_consolidation_holds`
  runs `--check` against the real root, so a full run catches drift. But the pre-commit gate
  selects tests by changed-path name stem, and a commit touching only `docs/staging/**` maps
  to no test (a filed finding of this project's own). A staging-only commit can therefore
  land drift that the next full run reports. Wiring `--check` into the daily digest belongs
  to `OPS14` (the aged-staging digest atom), not here — an operational mechanism added to
  patch a symptom, outside the design that owns it, is the accretion `OPS1` forbids.
* **Nothing refuses anything.** Class documents carry severity and lane; `OPS11` and `OPS12`
  are the mechanisms that act on them, and both are minted, unbuilt, and depend on OPS9.
* **The remaining root documents are not triaged.** 84 `*.md` with this report in it: five
  class documents, one machine doorbell, and 78 classifiable documents of which **72 match
  no class at all** and 6 match one but are out of population — the two out-of-lane
  refusals, two `ADVISOR_*` documents, and two `WORKER_REPORT_*` records carrying RECORDED.
  Unclassed is a real answer and not a backlog: the ruling clustered five families, not all
  111 documents.
