**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B13_a_dual_fuel_household_is_one_account_across_both_fuels`

*Triage, 20 Nov 2026 (supplier batch 3, docs/staging/SEAT_RECORD_TRIAGE_OF_THE_SUPPLIER_FINDINGS_BATCH_3_2026-11-20.md): **real (med)**. The riding leg still answers its own fix offer (run_phase2b.py:5205-5215); only a save crosses fuels. B13 sits closed at L2 with this open in its own comment (maturity_map_closed.yaml:4946). Needs B13 reopened or a new atom. Knowledge gap: yes (K4).*

# A dual household's two fuels answer their anniversary offers apart, so the household can sit on a fix for gas and the default for electricity

Found while taking B13 to L2 (seat, 26 Oct). On the B13 walked run (phase 4c to 2017-12-31, the
once-per-stint default-tariff letter and the woken re-fix on), 10 of the households that re-fixed
their electricity on contact had a gas renewal offer dated the same day their electricity stint
began, still unanswered when the electricity re-fixed. SYN-2016-023 is the worked case. Both legs
reached their anniversary on 2017-01-17. The electricity declined its fix and rolled to the default.
The gas leg answered its own offer afterwards, at its own pop (`_declined_on_the_riding_leg`), and
declined too.

The decline-and-stay rule (`DECLINE_A_FIX_ABOVE_THE_DEFAULT`) is read per leg, against each fuel's
own default. Nothing ties the two answers, so a household can accept one fuel's fix and decline
the other's. The 24 Oct basics ruling, as B13 carries it, is that a dual household acts once
across both fuels. B13 L2 builds that for a fix taken on contact. It does not build it for the
anniversary offer. The re-fix refuses by name where the gas offer is unanswered (10 households in
this window), which understates the household's side (F11).

**Not measured.** How many dual households in a full window end up on a fix for one fuel and the
default for the other. Whether a real supplier's dual renewal is ever answered per fuel is a
practitioner question (K4). Published practice sells the dual fix as one product
(`home_moves.md` §8.7).

**Proposal.** The household answers its anniversary once, on its decision leg, and the riding leg
takes the same answer. The control is the B13 file's re-fix test, which would then move these 10
households' gas instead of refusing them.
