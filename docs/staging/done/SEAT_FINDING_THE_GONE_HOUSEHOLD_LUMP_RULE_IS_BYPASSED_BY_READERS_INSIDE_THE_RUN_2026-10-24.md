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

## The fix, landed (2026-10-24, before its grade)

`LivePaymentTriad.close_account(household, final_bill_due)` is told **as the run closes the
account**: from `_notify_registration_loss` (every departure, on its effective date) and where a home
move that did not follow us closes the account. The final bill's due date is the 28th of the month
of the last day supplied, the same day `_post_month_bill` uses (`_bill_due_on`), so nothing is looked
ahead. `_after_final_bill` reads the told date (the later of it and any bill actually posted), and
the cut in `_cross_settlement` sits under the forced path too. `close_accounts` at the end stays the
backstop and now adds to the set instead of replacing it.

Named limit: a departure dated the 1st to the 3rd of a month has a final bill due on the previous
28th, before the departure is known; a reader in those few days can still cross a lump dated after
that 28th. The counter shows any such residue.

Found on the way: at settlement budget 0 the run's memory curve extrapolates to a negative peak
(-1,995 MB), which the box queue reads as an undeclared weight and refuses for ever, so the s.1a
probe could not start. `_box_admission` now prices an off-curve budget at the class weight.

Controls: `test_a_closure_told_as_it_happens_cuts_lumps_a_reader_forces_mid_run` (mutation: the
told closure stored nowhere, red), `test_the_run_tells_the_queue_at_each_departure_and_unfollowed_move`
(mutation: the departure call removed, red), and
`test_a_budget_below_the_curves_anchor_is_priced_at_the_class_weight` (mutation: the raw peak
passed, red).

**Graded (2026-10-25), in `debt_realism_three_world_fidelity_gaps.md` s.1a:** with the switch on, 0 late lumps cross (was 12) and 14 are lost at close; write-offs per pound billed 0.665% to 0.725% (+0.060 points, GBP 562), the off arm unchanged to the penny. Cause 1 is graded and worth about a ninth of the off level. Still open: the 0.15% baseline, being re-read at `3f09d17e4`.

## Done (2026-10-25)

Both open questions are answered. The rule acts inside the run (`75a84091a`), graded in
`5ed67fe06`: 0 late lumps cross with the switch on, and cause 1 is worth +0.060 points (0.665% to
0.725%). The second question, the baseline, is settled in s.1a: the same probe at the 12 Oct head
`3f09d17e4` reads 0.151% (GBP 874.44, the recorded figure). So the code moved and the measure did
not. The "5–7x under" headline was true of that world only; it is corrected beside each place it
stood (s.1 and the bad-debt knowledge topic; `bad_debt_provisioning.md`'s is owed behind the
settlement-ceiling red, `SEAT_FINDING_THE_SETTLEMENT_CEILING_JOURNAL_LEG_HAS_ARMED..._2026-10-25.md`,
with its corrected copy at `/var/tmp/closed_arrears_runs/bad_debt_provisioning.corrected.md`). Left open, and not this
finding's: which commits in `3f09d17e4..42b9da490` raised the same book's write-offs 4.4-fold
(bisection on the same probe), and the mix-adjusted comparison of s.1.
