**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# One item lands twice, on origin and on the shared HEAD, and the shared checkout forks

*Console seat, 2026-10-07, from the triage of the delivery seat's carried "what it got wrong" items
(`docs/direction/wrong_triage.yaml`). Carried as `one-item-lands-twice-on-origin-and-the-shared-head`,
55 listings since 2026-09-30.*

## The defect

An item reaches origin through `surgical_land`, and the same change is also committed locally on
the shared checkout's HEAD, with different bytes. The two copies conflict, `origin_reconcile`
refuses the fast-forward, and the shared checkout forks. While it is forked, every daemon runs code
that origin has replaced, and the publisher refuses with `behind_origin`.

- 2026-09-30: four pairs in one stretch.
- 2026-10-01: `75df9efdf` after `d77ff33d5`.
- 2026-10-07: `17f75226a` and `f07af3845` (W2_20 and W2_21 at L1) were local commits on the shared
  HEAD and on no remote, while `067493aa4` carried both to origin. The fork stood from 07:50 until
  `d8c139a1f` merged it at 10:21. In that time the 09:21 orientation ran the old direction-record
  code (`d1b8da5fd`).

## Why the existing proposal does not cover it

`SEAT_PROPOSAL_WHAT_FORCES_THE_MERGES_ON_MAIN_MEASURED_AND_WHAT_TO_CHANGE_2026-10-04` deals with
abandoned working copies that hold the fast-forward. This is a different writer: a lane that
commits on the shared checkout itself.

## What done means

A commit on the shared checkout's HEAD that does not come from the reconciler or the publisher is
refused, with a message naming `surgical_land` as the door. Or, if some daemon needs that path,
its commits are listed, and an item already on origin under a receipt is never re-committed
locally. The control is a fixture shared checkout where a plain `git commit` must be refused.
