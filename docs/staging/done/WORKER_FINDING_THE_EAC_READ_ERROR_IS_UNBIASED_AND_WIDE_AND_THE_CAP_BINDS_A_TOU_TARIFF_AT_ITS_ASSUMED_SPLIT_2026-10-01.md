**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# The registry EAC's error against next year's use is unbiased and wide, and the cap binds a ToU tariff at its assumed split

Claim `size-the-registry-eac-read-error-from-the-published-record`. This is knowledge only; no
world change was made. The document is
`docs/market_research/how_far_a_settled_eac_sits_from_next_years_use.md`, and the
pre-registration with its results is in `records/`.

## The three answers

**1. Read error: there is a sourced distribution, and the split by meter type is a named gap.**
DESNZ states that NEED's per-dwelling electricity is the industry's own AA (~80%) or EAC (~20%).
Across 330,884 consecutive-year pairs, the next year's figure over this year's has:
- median 1.000, so no bias, which matches Elexon Issue 23's 2006 conclusion;
- median |Δ| **0.147**, p90 **0.58**;
- a 0.31 share moving by more than 25%.

For homes where gas is not the main heating fuel, the nearest proxy for E7/storage, it is wider:
median 0.179, p90 0.71.

**The world's zero read error sits at the far edge of what is published.** Even a home on gas
heating has a median 14% gap between one industry year and the next. The spread bundles real
household change, change of occupier, and estimate-to-actual corrections. The world already makes
the first of these (weather), so this is **not** a calibration target as it stands. Nothing
published splits it by smart, traditional or E7, and the practitioner question is put in the doc.

**2. The cap binds a multi-register tariff at its assumed split, not at the realised rate**
(draft SLC 28AD.4, .29, .31, .34).
- An E7 tariff is tested at 42/58 against the Economy 7 benchmark.
- Any other ToU tariff is tested at the supplier's declared historic average split.

So the five ToU first bills above the flat ex-VAT cap are not breaches by that fact. **The flat
cap is the wrong comparator for them.** The in-force text was not read, because the URL
redirected; this needs checking before anything is keyed to the wording.

**3. 28 MWh is plausible, and 41 MWh is unrefuted but out of the record's reach.**
- DESNZ censors domestic electricity at 25 MWh.
- 5.93% of the drawn class sits above that.
- NEED's gas-heated twin class burns a median of 21–27 MWh of gas, with p90 34–42 MWh.

The open question is the opposite one: NEED's non-gas homes in that class have a median of only
4.5 MWh. **Does the world heat direct-electric homes to a gas home's standard?** The practitioner
question is put in the doc.

## Handed on, not done here

- **A pre-registered world item** to give the registry EAC a read-error term. It first decides
  which of the four bundled components the world does not already produce. The seat should draw
  this before the bill-shock swap
  (`SEAT_CONTINUATION_SWAP_THE_WORLDS_BILL_SHOCK_BASE_ONTO_THE_EXPERIENCED_SHOCK_2026-10-01.md`)
  carries the zero-error tenure gradient into churn.
- **Re-key any ToU-cap comparison** to the E7 benchmark at the tariff's assumed split.
