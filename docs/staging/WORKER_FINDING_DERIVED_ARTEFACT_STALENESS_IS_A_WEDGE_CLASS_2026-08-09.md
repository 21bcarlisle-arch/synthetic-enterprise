# [WORKER FINDING] A derived artefact nothing regenerates is a standing wedge generator (2026-08-09)

**Severity:** LATENT · **Lane:** H_harness

**Found during:** `DIRECTOR_PRIORITY_UNWEDGE_AND_ALARM_TEETH` draw 1 (unwedge), causes 3–5.
**Disposition:** instances FIXED and committed (`96bdad98a`); the CLASS is QUEUED, not fixed on
sight (SELF_INTERRUPT_DISCIPLINE). Per R10 an absurdity-class defect cannot close on an
instance fix, and three of this episode's five causes were the same class.

## Observed, with evidence

The episode's causes 1–2 were fixed by the previous tick
(`WORKER_FINDING_SECOND_WEDGE_CAUSE_LANDED_AFTER_THE_FIRST_2026-08-09`). With those green, the
gate ran further and stopped at three more:

| # | Red test | Cause |
|---|---|---|
| 3 | `test_forward_attachment_register::test_live_tree_has_no_violations` | `docs/design/FORWARD_ATTACHMENT_LEDGER.md` stale: 2 `fabricated_entry` + 5 `missing_entry` |
| 4 | `test_pull_forward_proposal::test_live_rendering_is_current` | `docs/design/PULL_FORWARD_PROPOSALS.md` stale — **and untracked** |
| 5 | `test_seat_guard_daemons::test_every_main_entrypoint_is_guarded` | `pull_forward_proposal.py`, `staging_archive_policy.py` unguarded |

Causes 3 and 4 are both **derived artefacts**: `background/forward_attachment_register.py
--write` and `python3 -m background.pull_forward_proposal --write` regenerate them from the
maturity map plus the `**Advances:**` declarations in `docs/staging/**`. Both regenerated
cleanly with zero hand-editing — nothing was *wrong*, only *stale*.

**What moved the derivation:** one finding archived staging → `staging/done/` (an ordinary,
required staging-protocol act) and three findings staged the same day. That is it. Routine
staging hygiene silently invalidates a committed artefact that a blocking test checks.

## Why it is a class, not three instances

1. **The regeneration step exists but has no caller.** Both modules ship a `--write` CLI and a
   blocking `--check` test. Nothing in the publish path, the pre-commit gate, or the staging
   archive path runs `--write`. The derived artefact is therefore correct only for as long as
   nobody touches `docs/staging/` — and touching `docs/staging/` is the machine's normal
   metabolism. This is a control whose *precondition* is violated by ordinary operation.
2. **The trigger and the artefact are in different hands.** The act that invalidates the
   ledger (archive a finding) is in `staging_archive_policy.py`; the act that repairs it is in
   `forward_attachment_register.py`. Neither knows about the other. Any future derived-from-
   staging artefact inherits the same hole by default, so the count only grows.
3. **`-x` makes the class invisible one cause at a time.** The gate reports the first red only,
   so three same-class causes presented as three unrelated incidents across three ticks.

## What closing it looks like (the drawable half)

A **register of derived artefacts** — (module, `--write` entrypoint, `--check` entrypoint,
rendered path) — with two consumers:

* the publish path (and/or the staging-archive path) regenerates every registered artefact
  before running the gate, so a staging move can no longer wedge publishing; and
* one test asserts the register is COMPLETE — every `docs/design/*.md` written by a
  `--write` CLI appears in it. Without that, the register is a fail-open index and the next
  derived artefact is simply absent from it (cf. `feedback_index_is_a_fail_open_control`).

R15 note: the completeness test must be mutated by *adding* a derived artefact and confirming
the register reds, not merely by checking today's two entries resolve.

## Not asserted

* Whether regeneration belongs in the publish path or the archive path — both are defensible
  and the choice wants a design pass, not a guess. Deciding that inside this finding would be
  the accretion `OPERATIONAL_COHERENCE_DESIGN_PASS` forbids.
* How many derived artefacts exist beyond these two. Not enumerated — that enumeration IS the
  register, i.e. the work.

## Adjacent, separately drawable

`docs/design/PULL_FORWARD_PROPOSALS.md`, `background/pull_forward_proposal.py`,
`tests/background/test_pull_forward_proposal.py`, `company/billing/credit_balance_control.py`
and its test were all **untracked** in the shared working tree while measuring green locally —
the third recorded instance of "untracked build passes local-green". All are committed in
`96bdad98a`. The recurrence says the existing local-green discipline is prose, not mechanism:
the gate measures the working tree, so it can be green on files that do not exist at HEAD.

— Worker finding, 2026-08-09, during the director-priority unwedge.
