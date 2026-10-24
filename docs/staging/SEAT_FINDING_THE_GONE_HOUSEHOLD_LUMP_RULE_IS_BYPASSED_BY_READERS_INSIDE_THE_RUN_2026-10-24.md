**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `gone-household-lump-rule-before-after-is-graded` (Lane 0 delivery)

# The gone-household lump rule is bypassed by readers inside the run: 12 of 14 late lumps still cross with it switched on

**What was measured.** The before/after grade of `a8ea44a12`, in
`docs/market_research/debt_realism_three_world_fidelity_gaps.md` s.1a ("Result"). It used 160
founders, settlement budget 0, one seed, and the same code with
`world_payment_truth.GONE_HOUSEHOLD_PAYS_NO_LUMP` set off and then on. Residential write-offs per
pound billed went from 0.665% to 0.671%. Lumps lost at close went from 0 to 2. Lumps crossed after
their closed account's final bill went from 14 to **12**.

**The defect.** The rule acts only on lumps that are still queued when
`LivePaymentTriad.close_accounts` is called. `simulation/run_phase2b.py` calls it once, after the
last bills post, and its comment says this is "before the first reader below forces a crossing".
That is true of the readers after it, but not of the readers inside the run. `arrears_state` and
`receivable` (forced per account), and `default_belief_rate` (forced for every account), run at
renewals throughout the run. Each one crosses every queued lump dated up to its `as_of`, including
a gone household's lump dated after its final bill. By the time the closed set is known, 12 of the
14 lumps have already crossed. The build's counter `settlements_crossed_after_close` exists to make
a late closure visible, and it did: that is how this was found. Its control
(`tests/background/test_a_gone_household_pays_no_lump_after_its_final_bill.py`) tests the queue,
not the run's call order, so it could not see this.

**What it costs.** Cause 1 of the write-off gap is **ungraded**, not refuted. If each of the 12
lumps moves the share as the 2 did, the upper bound is about GBP 330, or 0.035 points on
0.665%. That is an extrapolation from two lumps. The crisis bad-debt validator's floor and the
Capabilities Debt row both wait on this cause.

**A second open question, found by the same run.** The off arm's 0.665% is about 4.4 times the
0.15% (14 cases, 12 Oct) that s.1 uses for "about 5–7x under Centrica". I cannot yet say why. The
code moved for twelve days, and the case unit may differ (cases here are issued bills). The
one-variable check is the same probe (`/var/tmp/closed_arrears_runs/probe2.py`, switch off) at the
commit the 0.15% was read on, or the 0.15%'s own measure read on this book. Until then, the "5–7x"
headline should not be quoted.

**The fix (for the next lane; not built here).** The triad must learn that an account has closed when
the run closes it, not once at the end. A per-account close (or its final bill's due date) is
already known in the run when the household leaves. The cut must also apply in
`_deliver_settlements_through`'s forced path. The control should be keyed to the property, not to
the queue: over a real `run_phase2b` book with the switch on, `crossed_after_close == 0`. The
mutation to prove it is moving the `close_accounts` call back to the end. Then re-run both arms and
grade cause 1 against the same unchanged prediction.

**Method record.** The handoff named
`docs/staging/records/SEAT_RECORD_THE_GONE_HOUSEHOLD_LUMP_RULE_BEFORE_AFTER_IS_QUEUED_2026-10-24.md`
for the method. It is on no ref and not in the shared tree, so it was never landed. The method
above is read from `both_arms.sh` and `probe2.py` themselves.
