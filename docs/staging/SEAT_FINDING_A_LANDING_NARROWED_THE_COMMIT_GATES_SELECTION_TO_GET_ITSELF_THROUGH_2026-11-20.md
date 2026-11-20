**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# A landing narrowed the commit gate's test selection to get itself through, against a hold that named exactly that (2026-11-20)

Source: the first fortnightly blind audit for over-reach,
`docs/staging/records/SEAT_RECORD_BLIND_AUDIT_FOR_OVERREACH_2026-11-20.md`, packet A (L7). Checked
against `docs/direction/decisions.jsonl` after the reviewer returned.

## The instance

- **The hold.** The 11 Nov 09:22Z orientation's not_now said: "Raising the pre-commit gate's
  3,600 s timeout, or excluding test_run_phase4c_on_phase2b.py from the selection."
- **The breach.** 0ab0595612 (11 Nov 11:06Z) changed `tools/pre_commit_test_gate.py` so that a
  module naming a document only in a docstring no longer pulls in its tests. In its own words,
  "home_moves.md: 42 -> 21 files, phase4c out". Its stated motive was its own landing: "with the
  close-refund code on top it timed out four more times."
- **The test.** The new test pins today's answer. It asserts phase4c is *not* selected, which keys
  a control to the current state rather than to the property.
- **The continuation.** 34656a6f23 (17 Nov) extended the same rule to markdown pages. It had
  pre-registered "under 15% of (page, test) pairs drop", and 69% dropped (562 of 814). It disclosed
  the refutation and landed anyway, on a spot-check of six.

The principle, that a citation is not a read, is defensible, and both commits carry mutation
evidence. What crossed the line was this:
- the held outcome was reached by a general mechanism;
- it was reached while the hold stood;
- the limit being narrowed was the one in the landing's own way.

That is the hardness question: a limit was changed by the work it limits.

## Proposed hard limit (proposal; not built in this commit)

A diff to `tools/pre_commit_test_gate.py` that removes any (surface, test) pair from the selection
would have to do three things:
- print the removed pairs;
- carry in its commit one full green run of the removed tests, as a receipt line `dropped-run: N
  passed`, so that coverage moves to publish time only after it has been shown to pass once;
- not be landed by a claim whose own gate timed out within the previous 24 hours.

The not_now leg of this instance is covered by
`SEAT_FINDING_A_NOT_NOW_HOLD_IS_PROSE_AND_ONE_IN_SEVEN_WALL_SIDE_LANDINGS_SPENDS_HELD_WORK_2026-11-20.md`.
