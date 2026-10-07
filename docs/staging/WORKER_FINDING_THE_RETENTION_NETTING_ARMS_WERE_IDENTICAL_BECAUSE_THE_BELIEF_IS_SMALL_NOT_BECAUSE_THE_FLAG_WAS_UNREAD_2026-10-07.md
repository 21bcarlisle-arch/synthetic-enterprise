# The 06:04 retention-netting arms were identical because the belief is small, not because the flag went unread

**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 4 · **Atom:** `C29_decisions_stop_being_lookup_tables`

*Worker, 2026-10-07 10:10 BST. Disposition of `the-retention-netting-reaches-code-and-its-arms-differ`: RELEASED,
the work is the live delivery seat's (pid 1038428, worktree /var/tmp/se-seat-executor), which at 09:46 was
landing it through `surgical_land` as `DecisionPolicy.retention_nets_default_belief`, with its arm pair queued
in /var/tmp/se-retguard-arms behind pid 415593. Building it a second time would collide with that landing.*

## The item's first question, answered from the bytes

The item said the on/off arms in `~/.cache/seat_lane0_20261007_retguard/` "tested nothing" and asked why the
on-arm's `dataclasses.replace(CURRENT_POLICY, retention_nets_bad_debt_belief=True)` ran at all.

- **Where the field came from:** the arms ran with `PYTHONPATH=/tmp/wt_retguard_2826265`, a worktree at
  `bfe428ef6` with UNCOMMITTED edits to `company/policy/decision_policy.py:181` (the field),
  `company/interfaces/growth_desk.py` (`retention_expected_bad_debt`) and `simulation/run_phase2b.py:2865-2870`
  (the call site). That is why no ref contains the name. The first on-attempt died on the run's policy-scope
  check; the rerun completed.
- **The flag WAS read.** On the on-arm, 73 of 73 guard passes carry a non-None `expected_bad_debt`. On the
  off-arm the count is 0. The guard's protected value is netted (SYN-2016-001: 176.31 + 27.5 - 7.40 = 196.42).
- **Why the decisions did not move:** the netted belief is a few percent of the margin, and the protected value
  dwarfs the offer cost. Here are the POOR/CRITICAL guard passes (margin / netted bad debt / protected value):
  SYN-2016-001 CRITICAL 176.3/7.40/196.4 · SYN-2016-013 CRITICAL 87.8/4.89/110.4 ·
  PROS-2016-0098 CRITICAL 2275.9/76.76/2226.6 · SYN-2016-067 POOR 612.8/25.71/614.6 · SYN-2016-002 POOR
  80.3/3.95/103.9. The highest bad-debt/margin ratio on the book is 0.089. The smallest protected value is
  £98.06. Offer costs run from £5.93 to £357.25. No offer is withdrawn: 73 offers each side
  (POOR 8, CRITICAL 3), totals identical (bad debt 18,309.60, net 242,278.08).

So P2 and P4 of that pre-registration failed for a stated reason, and the run itself was sound. The company's
learned default belief by arrears state, as read at the term start, is too small to bind. That matches the
landing seat's own estimate that an offer is withdrawn only above about an 18% belief, against a 2% prior.

## What this means for the arm pair now queued

Unless the landed version reads a materially larger belief (it nets the belief off revenue rather than margin,
which raises the term by roughly revenue/margin), **predict before it runs that the new pair is also
identical or near-identical on POOR/CRITICAL offers.** If so, the fix that stops the transfer is not "net the
expected bad debt". Two other routes are open. One is to ask whether the default belief for an account already
in arrears is itself too low; a CRITICAL account carrying a 3-4% expected loss is a reading to check with the
director against how the trade prices a debtor. The other is a guard that refuses a discount to an account in
arrears outright, which is a policy and not a valuation. This is the odd-against-the-industry reading
CLAUDE.md says to raise, not build on.
