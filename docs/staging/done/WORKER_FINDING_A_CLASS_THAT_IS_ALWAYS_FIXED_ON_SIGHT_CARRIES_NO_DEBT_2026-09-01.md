# [WORKER FINDING] A class that is always fixed on sight carries no debt, and the draw ranks on the wrong count

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS10_finding_class_consolidation`
**Found:** 2026-09-01, filing two RECORDED findings against `no_caller_and_never_runs` and watching
the class count not move. Not fixed here — it changes the draw order, so it needs its own
pre-registration.

## Class registration

Belongs to `measurements_that_mirror`. The debt measure reproduces the consolidation population
rather than deriving its own, and the two questions are not the same question.

## The exclusion, which is correct where it was written

`finding_classes.derive_memberships` drops RECORDED documents from every class population, and says
why:

> *"A class document exists to argue one repair against one cumulative cost; a RECORDED document is
> a landed record with nothing owed, so it has no repair to argue and no cost to add. Folding reports
> of FIXES into a class of DEFECTS would inflate every instance list with work already done."*

For **consolidation** that is right and I would not change it. A class register that swallowed fix
reports would archive them under a defect heading and claim to supersede work that is finished.

## The question it is being read for is a different one

`background/class_debt.py` — shipped this morning, on the director's brief — derives its population
from the same `derive_memberships`, so it inherits the exclusion. And its question is not "what is
unrepaired". His words:

> *"A recurring class doesn't cost N times one instance; it invalidates whatever was built on top of
> it in between."*

**Recurrence includes every instance that was fixed on sight.** A class that recurs twenty times and
is repaired each time within the hour is the strongest possible case for a class-level fix (R10) and
currently reads as zero debt: every one of those twenty is RECORDED, so none of them counts. The
measure runs perfectly and answers a question nobody asked — which is the shape recorded in
`feedback_answers_to_questions_nobody_asked`, and `a correct refusal is not a population` is the
other half of it.

Both findings I filed tonight are exactly that: three unwired mechanisms inside one module, fixed in
the turn, contributing nothing to the class whose whole subject is unwired mechanisms.

## Measured, so the size of it is not a guess

Class registers versus what the same classifier finds in `docs/staging/done/` and the registers do
not already list:

| class | register instances | in archive, DECLARED | in archive, title-match only |
|---|---:|---:|---:|
| publish_gate_and_wedge | 56 | 0 | 42 |
| controls_that_cannot_fail | 27 | 2 | 22 |
| uncommitted_and_orphaned_work | 21 | 0 | 38 |
| measurements_that_mirror | 7 | 1 | 10 |
| no_caller_and_never_runs | 8 | 0 | 6 |
| figures_on_a_superseded_clock | 3 | 0 | 1 |
| **total** | **122** | **3** | **119** |

**And the draw order changes.** `class_debt.order_key` leads with the instance count. On these
numbers `uncommitted_and_orphaned_work` (21 → 59) overtakes `controls_that_cannot_fail` (27 → 51),
which is a swap in the ranked list the seat is supposed to draw from.

## What is NOT established, and why this is a finding rather than a change

**116 of the 119 match by TITLE, not by declaration.** A deliberate fold into a register is a
stronger claim than a title regex, and I have not shown that title-matching an archived document is
sound enough to count as an instance. It might over-match badly. So the direction is clear (the
recurrence count is materially understated, roughly 2×) and the exact figure is not, and I am not
going to substitute one for the other on the strength of a regex — that is
`check a substituted quantity's range before its distribution`.

## What would close it

1. **Two populations, named apart.** `derive_memberships` keeps its RECORDED exclusion for
   consolidation; `class_debt` derives a RECURRENCE population that includes fixed instances. One
   question each, neither borrowing the other's refusal.
2. **Establish whether a title match is an instance.** Sample the 119 by hand against their class
   definitions and report the false-positive rate before any count uses them. If it is high, the
   recurrence population is the DECLARED set only and the answer is to make declaration the norm.
3. **A pre-registration first**, because it re-orders the draw: state what the ranking will be
   before recomputing it, and keep the prediction beside the result.

## CORRECTION 2026-09-02 — the draw order does NOT change, and I made the error this finding names

The director asked for the 116 title-matched archives to be sampled before folding them. Sampling
them refuted my own headline claim.

**What I did wrong.** I counted every archived document a classifier puts in a class. I did not
apply the exclusions `derive_memberships` applies to the live root: externally-authored documents
(advisor pointers, director rulings) and self-clearing alarm documents are OUT OF POPULATION by the
register's own rules. Applying them removes **39 of 127** — 10 externally authored, 29 alarms.

That is `a correct refusal is not a population`, committed inside the finding whose subject is a
correct refusal being read as a population. I had the rule in front of me and applied it to one
population and not the other.

**The corrected measurement**, register count → recurrence count:

| class | register | + archive | recurrence |
|---|---:|---:|---:|
| publish_gate_and_wedge | 56 | 30 | 86 |
| controls_that_cannot_fail | 27 | 24 | 51 |
| uncommitted_and_orphaned_work | 21 | 19 | 40 |
| measurements_that_mirror | 8 | 8 | 16 |
| no_caller_and_never_runs | 8 | 6 | 14 |
| figures_on_a_superseded_clock | 3 | 1 | 4 |

**The order is identical.** My claim that `uncommitted_and_orphaned_work` (21 → 59) would overtake
`controls_that_cannot_fail` (27 → 51) came from the uncorrected 59; the corrected figure is 40, and
51 stays ahead. Tested for sensitivity by additionally excluding `WORKER_REPORT_*` documents
(reports ABOUT a class rather than instances OF it, which the hand sample showed to be the main
residual error): 73 / 51 / 39 / 14 / 13 / 4 — **still identical**.

**Hand sample, 25 of the candidates, judged against their class definitions.** Of the 18 that
survive the rule-based exclusions, 4–5 are genuinely wrong — around 25%, and they fall into two
nameable kinds: a REPORT about a class counted as an INSTANCE of it, and two plain
misclassifications (one document about a guard landing without callers matched
`publish_gate_and_wedge` on the phrase "publish gate" when its actual subject is
`no_caller_and_never_runs`).

## What survives, and it is the part that mattered

The defect is real and unchanged: `class_debt` inherits the RECORDED exclusion, so a class repaired
on sight N times reads as zero debt. `no_caller_and_never_runs` took **three** instances on
2026-09-01 and **three more** on 2026-09-02, every one of them RECORDED, and its count moved by zero.

What changes is the JUSTIFICATION, because "it re-orders the draw" is now known to be false on this
corpus. The real consequence is narrower and sharper, and it does not depend on ordering at all:
**`REOPEN_AFTER_INSTANCES` keys on the instance count.** An understated count means an acceptance
that should have been re-opened by recurrence is not — which is precisely the failure the re-arm rule
exists to prevent, and it is the one that reversed my own decision on this register a day ago.

## What this finding does not claim

Not that the debt register is wrong to exist or that this morning's build was misconceived — the
accrual, the three cost terms and the order key all stand. Not that the RECORDED exclusion is a
defect; it is correct for its own question. The claim is that **one population is answering two
questions, and only one of them is the question it was built for.**
