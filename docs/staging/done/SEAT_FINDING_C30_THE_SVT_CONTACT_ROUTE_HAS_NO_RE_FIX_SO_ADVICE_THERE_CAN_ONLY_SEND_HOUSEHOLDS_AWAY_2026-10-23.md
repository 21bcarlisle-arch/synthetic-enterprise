# C30: the SVT contact route has no re-fix, so advice sent there can only send households away

**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 4 · **Atom:** `C30_advice_reaches_a_household`

*Delivery seat (executor), 2026-10-23. Drawn as `c30-advice-reaches-a-passive-household-on-the-svt-route`.*

## What was drawn

The route §7.5 of `docs/market_research/how_households_respond_to_supplier_contact.md` recommended:
one default-off switch, and a per-account sender of C34's advice at the start of a passive household's
first SVT segment, in place of the flat `svt_contact_instrument`. Then a reach test (a contacted
household can re-fix, an uncontacted one cannot) and a one-variable arm pair. The draw said to stop and
write why into §7.5 if a new world number or seam crossing turned out to be needed.

## What was found, read rather than measured

On the coupled SVT roll (`svt_cause_on_the_coupled_roll`), every draw above `p_contacted` is
"stayed". A woken household that did not leave cannot be told from one the letter never woke, and its
next default segment is already in the heap at the same rate. `svt_departure_after_contact`'s
docstring and §5 of the research page both say a woken stayer "re-fixes with us". That is the trials'
finding, and nothing in `run_phase2b.py` makes it happen. Both now carry a correction beside the claim.

So on this route a contact can only **add departures**. The company's side is negative by
construction. The household's side is a leaver's saving at a rival, which the world does not record. The
arm pair could grade one side only and could not answer the M2 question it was drawn for, so **no
switch was built and no arms were launched**. *(Corrected before landing, the same turn: a first draft
said the re-fix needed a new seam crossing. It needs the existing renewal door, called at a new moment.)*

## What making it real needs (§7.5a)

The run's one route from the default back to a fix, the anniversary roll, is taken at schedule build,
so no contact can reach it. A woken stayer's re-fix needs:

1. **The existing renewal door at a new moment.** `request_renewal_offer` is called inside the loop
   at the segment's start, not only by the schedule builders. No new crossing.
2. **A reverse splice.** On a draw in the re-fix band, drop the household's remaining default segments
   up to its next scheduled boundary and push one fixed term at the quote. The band is
   `[p_contacted, p_contacted + (1 - p_drift) x woken x (1 - churn_if_choosing))` on the same draw. It
   needs **no new world number**. The work is building a full fixed-term record inside the loop,
   which is a run-order change and more than a switch.

Recommended next: build 1 and 2 as one default-off increment with its reach test, then the per-account
sender as drawn. The in-loop fixed-term builder is also the first half of §7.4's notice-time route.
The hand-off is filed as `c30-the-svt-route-gets-its-re-fix`.

## Interconnection

Any earlier reading of the flat `svt_contact_instrument` arms (W2_39, C34's holdout) measured the
departure side only. A "contact on SVT stock costs the company" result there is true and is half
the trade. It is not evidence that the contact creates no value.

## Disposition (2026-10-23, worker, `c30-the-svt-route-gets-its-re-fix`)

Steps 1 and 2 are built and landed in `56fd50cd5`, default off
(`contact_response.A_WOKEN_SVT_STAYER_REFIXES`). On 2016-01..2017-02, with a collective_switch contact
and the switch on, 18 woken stayers re-fixed, at about £97-108/MWh in 2016. Each refused draw names
its reason on the row's `sim_refix`. Reach test: `tests/simulation/test_a_woken_svt_stayer_refixes_with_us.py`.
The GAPs are on the research page, §7.5a "Built": no gas re-fix, and the riding gas leg stays on the default.
**Still owed:** the per-account C34 sender at the first SVT segment and its one-variable arm pair,
which can now grade both sides. With that, this finding closes.

**Closed (2026-10-24, worker, `c30-the-per-account-svt-sender-grades-both-sides`).** The sender landed in
`3fb78ecd05`. Its arm pair is graded beside its predictions in
`docs/staging/records/SEAT_PREREG_C30_THE_ONCE_PER_STINT_SVT_LETTER_GRADED_ON_BOTH_SIDES_2026-10-23.md`.
Before grading, a defect was fixed: a woken stayer could re-fix above its default, because the
decline-and-stay rule never reached the splice. Results: 803 letters, 20 re-fixes, H = +£1,749 to
households and ΔC = −£389 to the company. H + ΔC = +£1,360 refutes the prediction that it would be
negative, but it is unattributed. The route now has two sides the arms can grade, which is what this
finding was missing. Why the company's loss is smaller than the household's gain is the next item,
`c30-whose-gain-offsets-the-refix-margin`.
