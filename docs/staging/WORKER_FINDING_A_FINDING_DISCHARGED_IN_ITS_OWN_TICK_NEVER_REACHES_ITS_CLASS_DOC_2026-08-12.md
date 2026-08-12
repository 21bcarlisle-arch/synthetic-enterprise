# [WORKER-FINDING] A finding repaired in the tick that filed it never reaches its class document's cost

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-12, building the RUNG-1c BLOCKING draw (the exoneration field).
**Disposition:** QUEUED per SELF_INTERRUPT_DISCIPLINE — nothing is blocked, no published figure
moves, and the class documents are correct as rendered. Filed, not fixed on sight.
**Rank:** backlog. Promote when a class document's cumulative-cost argument is next used to
justify a repair, because that is the number this defect understates.

## Observed, with evidence

`background/finding_classes.py::derive_memberships` (line ~456) excludes a RECORDED document
from the class population, with a stated and good reason:

> a RECORDED document is a landed record with nothing owed, so it has no repair to argue and
> no cost to add. Folding reports of FIXES into a class of DEFECTS would inflate every
> instance list with work already done.

`archived_instances()` then re-admits the ones that were consolidated before they were archived —
"named by the existing class document AND present in the archive".

Both halves are right, and between them is a gap. **Observed this tick:** with
`WORKER_FINDING_A_REFUTATION_SCORES_AS_EVIDENCE_IN_THE_WEDGE_CITATION_2026-08-12.md` live in the
root and unclassified as to discharge, `--check` reported `publish_gate_and_wedge instances=25`
and named it `UNCONSOLIDATED`. Adding its `**Discharged:**` line — a true statement, its repair
had landed — took the count to **24** and it was never written into
`CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md`. It is now in `done/`, so `archived_instances()`
cannot re-admit it either: that path requires the class document to already name it, and nothing
ever did.

## The property that breaks

The two rules compose into: **a finding is recorded in its class only if it survives unrepaired
long enough to be rendered.** The window is one `--render` invocation.

That inverts what the class document is for. Its "Cumulative cost, measured from the instances'
own recorded evidence" section exists to argue that a class is worth a structural repair. This
finding cost **two consecutive priority-zero draws** — a real, recorded, class-shaped cost — and
contributed zero to that argument precisely because it was fixed promptly. The faster the class
is repaired instance by instance, the cheaper the class looks, and the weaker the case for the
structural fix. Same shape as
`feedback_a_severity_header_states_what_the_hour_found_not_what_it_left`, reflected: there, a
lane's blocker set could only GROW; here, a class's cost can only UNDERCOUNT.

## Why the two obvious diagnoses are wrong

- **Not "stop excluding RECORDED".** The exclusion's own reasoning holds — a class document is an
  argument for an unbuilt repair, and listing landed fixes among open defects would inflate every
  instance list. Reverting it re-creates the defect it was written to close.
- **Not "render before discharging".** That makes the record depend on the order two edits happen
  in within one tick, which is not a property anything can check and not one a future author will
  know. It also creates an incentive to delay a true discharge in order to be counted, which is
  the worst possible thing to reward.

## Recommendation

Separate the two questions the population currently answers at once: **who is an instance of this
class** (a historical fact, permanent) from **what is still owed** (a live state). Concretely,
have `derive_memberships` admit a RECORDED document to a `discharged_instances` list rendered in
its own section — counted in cumulative cost, excluded from the repair argument and from the
BLOCKING derivation. The class document then says "N instances, M still owed", which is the
sentence its cost section is actually trying to make.

The mutations that must fail, both directions: discharge an instance and assert the class's
cumulative-cost figure is **unchanged**; and assert the class's derived severity and its
still-owed count **do** drop. A repair that moved the cost figure would have re-created the
inflation the current exclusion exists to prevent.

## Not the cause of anything published

**Observed:** no published figure reads a class document's instance count — `--check` passes at
this commit (0 failures), and the five class documents render identically apart from this
document's own absence. The defect is in what the project can prove about its own history, not in
any customer-facing or financial number.

## Related, already recorded

- `feedback_a_severity_header_states_what_the_hour_found_not_what_it_left`
- `feedback_a_rendered_documents_derived_severity_is_a_snapshot_nothing_re_reads`
- `feedback_a_new_finding_archived_before_its_class_doc_is_rendered_is_invisible` — the same
  invisibility reached by archiving rather than by discharging; that one was closed by rendering
  first, which is exactly the ordering dependence this finding argues is not a fix.
