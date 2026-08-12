# WORKER FINDING — an archived finding left a copy in the room it left, and the doorbell kept ringing

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-12, worker tick, drawing lane `C_customer_ops`'s two live BLOCKING findings.
**Class:** the record outruns the code's inverse — the record LAGS the work, and the queue is
the thing that lags.
**Rank requested:** backlog. Nothing published is wrong; the cost is drawn attention, which is
the resource this project treats as scarce.

## Observed, with evidence

The tick was woken with two BLOCKING findings in `C_customer_ops`, drawn ahead of the general
queue under RUNG 1c / OPS12 clause 3:

- `WORKER_FINDING_ARREARS_RAG_IS_FAIL_OPEN_ON_A_MISSING_LEDGER_2026-08-09.md`
- `WORKER_FINDING_THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE_2026-08-10.md`

**Both were already closed.** Each had a copy in `docs/staging/done/` carrying a full,
correct DISPOSITION section written by an earlier tick — including, for the naive-arm
finding, a population-level measurement of the correction's direction that this tick did
not have and would have duplicated. The arrears fix had landed at `d32992b60`; the
naive-arm fix was built but only partly committed (see below).

The doorbell fired because a **stale copy of each was still sitting in the staging root**.
The scanner reads the root; the archive is invisible to it; a finding present in both
places is drawn forever.

Census of the class at the time of the draw — five files present in BOTH `docs/staging/`
and `docs/staging/done/`:

| file | root copy | verdict |
|---|---|---|
| `WORKER_FINDING_ARREARS_RAG_IS_FAIL_OPEN…` | untracked | byte-identical prefix of the archived copy |
| `ADVISOR_FINDINGS_CLAUDE_MD_DECAY_AUDIT_2026-08-07` | untracked | byte-identical (96/96 lines) |
| `WORKER_FINDING_THE_PRINTED_FOOTING_CONTROL…` | untracked | byte-identical (87/87 lines), *and* a staged R100 rename of the same file sat uncommitted in the shared index |
| `WORKER_FINDING_THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE` | **tracked** | superseded — the archived copy has the disposition, the root copy does not |
| `WORKER_FINDING_THE_ATOMS_OWN_RECORD_STORE_IS_ONE_ENTRY_FROM_ITS_CAP_2026-08-11` | **tracked** | **the root copy is NEWER** — see §"not touched" |

Four were removed this tick. Two shapes produced them: an archive done with `cp` rather
than `git mv` (the tracked ones), and an untracked finding written to the root while a
separate archived copy already existed (the untracked ones — these never appear in a diff,
so no commit review could have caught them).

## The second-order damage, which is the part worth the finding

`tests/company/policy/test_policy_field_consumption.py` — the CLASS control closing the
naive-arm finding — was committed at `e3d992363`, an auto-process run-complete sweep. The
mechanism it imports was not: HEAD's `company/policy/decision_policy.py` contained **zero**
occurrences of `active_policy`, so `from company.policy.decision_policy import
active_policy, policy_scope` was an ImportError at collection time. **HEAD was red**, and
had been since that commit.

That is this project's catalogued *a control committed without its mechanism reds HEAD*.
What is new is the causal chain: the finding LOOKED open (root copy), so the earlier tick's
completed work looked incomplete, so nothing pushed the half-landed mechanism over the line,
and a broad auto-process `git add` took the test file alone because it was the only path in
that lane the sweep happened to see. **A stale queue entry is not inert — it hid a red HEAD
behind a finding everyone believed was still open.**

Landed this tick at `c4a20ec77`.

## Why the obvious control is not the right one

"Assert no basename appears in both `docs/staging/` and `docs/staging/done/`" is a two-line
test and it would have fired on all five. It is worth having. But on its own it is the
FAIL-SILENT shape from this project's own catalogue: it fires at *commit* time, and three of
the five root copies were **untracked**, so a pre-commit control would never have seen them.
The scanner that draws the doorbell reads the filesystem; the control must read the same
filesystem, on the same schedule, or it checks a different population than the one that
causes the harm (`feedback_a_harnesss_convenience_chose_the_controls_subject`).

**Recommended, and what I would take:** put the check where the draw happens —
`background/supervisor.py`'s staging scan already stats every root file; have it refuse to
raise a doorbell for a basename that also exists under `done/`, and emit the pair as a
maintenance item instead. That way the control's subject is exactly the scanner's subject,
it covers untracked files for free, and a duplicate costs one log line rather than a drawn
tick. Pair it with the commit-time test for the tracked half, which catches the `cp`-instead-
of-`git mv` shape at the moment it is introduced.

Both halves need the R15 both-ways proof: create a duplicate, assert the doorbell is not
raised and the maintenance item IS.

## Not touched, deliberately (SELF_INTERRUPT_DISCIPLINE)

`WORKER_FINDING_THE_ATOMS_OWN_RECORD_STORE_IS_ONE_ENTRY_FROM_ITS_CAP_2026-08-11.md` is the
one duplicate left in place. Its two copies are **not** equal and the root one is the newer:
the root copy carries the `**Severity:** LATENT · **Lane:** H_harness` header that OPS9 added
to every finding, and the archived copy does not. So the archived copy predates OPS9's stamp,
which means the archive is missing the machine-readable severity OPS9 exists to guarantee —
a different defect from the one this finding is about, in a lane that is not the drawn one,
and resolving it means deciding whether that finding is in fact closed. Left whole for
whoever draws it rather than half-merged by a tick that has not read its subject.

## Also queued, unrelated, surfaced by the new AST scan

`saas/reporting/annual_report.py:7713` — invalid escape `churn\_estimate` inside an f-string.
A `SyntaxWarning` today, an error in a future Python. Not fixed on sight.

---
## DISPOSITION (2026-08-12, worker tick) — CLOSED, census now zero

Drawn as a named publish-gate WEDGE SUSPECT. **It was not the cause.** The wedge was
`tests/company/test_phase_ob_settlement_reconciliation.py::TestRAGThresholds::
test_zero_monthly_revenue_is_green` — a test still pinning the fail-open that `2abb973c2`
had correctly closed — plus two more reds hidden behind the gate's `-x`. Fixed at
`33592d8d1`. Recorded here so this finding is not drawn as a suspect a third time.

The finding's OWN class is now closed. Its census named five files in both rooms; four
were cleared that tick, and the fifth (`..._RECORD_STORE_IS_ONE_ENTRY_FROM_ITS_CAP_...`)
is cleared at `6b3b36591`: the root copy was the archived text plus the OPS9 severity
header a later tick had added, so the header moved onto the archived copy and the root
copy went. Re-run of the census on today's tree: **zero files in both rooms.**

The deletion was verified present at HEAD (`git ls-tree`), not in the worktree — a
pathspec commit has silently dropped a staged deletion here before, leaving a file in
both rooms while every filesystem control read clean.
