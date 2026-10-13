**Severity:** LATENT · **Lane:** W4_the_wall · **Epoch:** unassigned · **Atom:** `unminted`
**What:** the in-loop annual DD review is fed settled revenue at TRUE kWh, where the supplier holds only its estimated bills · claim `dd4b-in-loop-bill-basis-tail-and-probe-placebo`
**Status:** measured 2026-10-13 on `f200-low` (200 founders, budget 0); remedy not built. Evidence in `records/SEAT_PREREG_DD4B_AT_THE_IN_LOOP_REVIEW_LOW_AND_HIGH_2026-10-12.md`, "The content tail, explained"

# The in-loop DD review is told true consumption, not the supplier's estimated bills

`simulation/dd_review_in_loop.py` builds the review's bills from the loop's monthly settled revenue,
grossed up at VAT. In this world that revenue is priced at the meter's TRUE consumption. The company's
review door (`annual_dd_review_view`) then sizes the household's DD from it. A real supplier reviewing
a household with estimated reads holds its own issued bills, estimates included, not the true volume.

**Size, on `f200-low`.** 135 of 847 reviews differ from the post-loop chain (the supplier's own bills)
by more than 5% on volume alone. In 111 of them the true-up lands in a later window. In 24 (8
households) it never lands. `C7`'s estimates run at a fifth of true use for 42 months, so the in-loop
review is told 3.8 times what the supplier ever billed. Through the chain, 365 of 847 reviews end up
with a different current DD.

**Why it is LATENT, not BLOCKING.** No figure published as the supplier's own knowledge reads the
in-loop chain: the published census is the post-loop one. What the in-loop chain drives is the WORLD's
DD4b response, which is correctly the world's. The defect is in what the household is said to have been
TOLD: a supplier could not have told it that amount.

**A second, separate defect the census exposed.** `C7` has a smart meter and 42 consecutive estimated
bills with no forced catch-up. Look for the parked atom on read-cadence and catch-up rules before
minting one.

**Remedy (not built).** The in-loop review should take the supplier's own bill for the month, from the
same `SimulatedReadFeed` and assembly door `build_monthly_bills` uses, with the move-in void and
unnamed months attributed as the post-loop bills attribute them, or both re-attributed together. Then
"the in-loop chain is the post-loop chain" holds on content, and a control can assert it: matched
reviews' spend equal to the penny, not just keys equal.
