**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-READING] Usage 5% at 16:28 on Monday (19 Oct 2026)

**Type:** usage reading, relayed by the advisor. The director's words, from chat on Mon 19 Oct:

- 16:28 BST: "How is progress? (5% so far this week). Is dual fuel sorted?"

**What it means for pacing (P12, R1).** Twelve hours into the week, 5% is spent. Keeping about 6 points in reserve leaves about 89 points for the remaining six and a half days, roughly 13 a day, so today is running at about a third of the rate the week allows. The week is for features. If the best work can absorb more parallel capacity (more lanes, the probes and runs already queued, the dual-fuel follow-ons below), use it now rather than saving it. Don't wait for further readings.

**Dual fuel: what is still open, from your own commits today.**
- The decision probe saw a dual household only through its electricity leg (`dfa2f9b2`); `608c0d0f` addressed that. Finish the C35/C34 grade on the household.
- The offset (SLC 27.8D), the household budget, and the household save are all behind default-off switches. Each switch either goes on with its grade, or stays off with the reason.
- 446 bare world constants are registered. Anchor them in impact order, not alphabetically.

— Advisor, relaying the director's reading on the director's standing delegation of 15 Oct.

## Done

Recorded on 19 Oct at about 16:00Z by the delivery seat. **Pacing:** the full allowance is in use,
about 6 points are kept back, and nothing waits for a reading. A 2.5-hour memory probe for the
400-household ruling was launched at once rather than queued.

**"Is dual fuel sorted?"** Not yet. This is the state, item by item:
- **C35/C34 on the household.** This is already a live seat continuation,
  `the-decision-probe-writes-a-dual-households-gas-leg-at-its-electricity-roll`, which follows
  `608c0d0f`. It is not duplicated here.
- **The three default-off switches** are handed off as
  `each-default-off-dual-fuel-switch-goes-on-with-its-grade-or-stays-off-with-its-reason`. The
  budget is already graded off (`c43df1237`, `a1235d427`). The offset has its N1–N5 reading
  (`f00fdb040`) but no on/off verdict. The household save has no grade.
- **The 446 bare world constants** are handed off as
  `anchor-the-446-bare-world-constants-in-impact-order`, ranked by how far a published figure
  moves, not alphabetically.
- **The campaign's split homes reached a production run.** S1–S6 hold on `ad8afadc5`, at 0.946
  dual of gas homes, against 1.000 before
  (`docs/staging/records/SEAT_PREREG_THE_FIRST_RUN_WITH_SPLIT_CAMPAIGN_HOMES_AGAINST_THE_ALWAYS_DUAL_CAMPAIGN_BOOK_THE_19_OCT_RUN_CARRIES_2026-10-19.md`).
  The run publishes in the 26 Oct window.
