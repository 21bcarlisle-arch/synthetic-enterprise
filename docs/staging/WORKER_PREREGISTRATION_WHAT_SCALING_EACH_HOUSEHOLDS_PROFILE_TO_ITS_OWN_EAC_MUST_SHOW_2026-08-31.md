**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery direction, 2026-08-31

# Pre-registration — what scaling each household's profile to its own EAC must show

**Filed before the code change.** Predictions written here first; the result is appended below in
its own section and nothing above it is ever edited.

## The defect, re-measured on this tree rather than quoted

The delivery brief cites 125 paired households. I did not trust a figure from another run
(`a_cited_baseline_may_come_from_a_different_run`), so I re-measured on the live drawn population at
`fd8c78303`, over the accounts this change can reach: **resi, profile class 1, legacy demand
provider, carrying a declared `eac_kwh`** — 141 such accounts in the book, of which 133 had been
acquired by 2024 and 79 by 2019. Annual settled kWh is the integral of the shape function
`run_phase2b` actually hands to settlement, summed over every day of the year.

| | 2019 (n=79) | 2024 (n=133) |
|---|---|---|
| drawn EAC — median | 2,481.5 | 2,506.1 |
| drawn EAC — IQR | 1,720.0 – 3,619.0 | 1,734.1 – 3,619.1 |
| drawn EAC — p90/p10 spread | **2.428** | **2.421** |
| settled kWh — median | 4,902.2 | 4,917.6 |
| settled kWh — IQR | 3,921.8 – 4,902.2 | 3,934.1 – 4,917.6 |
| settled kWh — p90/p10 spread | **1.310** | **1.250** |
| Spearman rho(drawn EAC, settled kWh) | **−0.0733** | **−0.0016** |
| median settled ÷ median drawn | 1.976 | 1.962 |

**The world states a household's annual consumption and settlement never hears it.** rho of −0.0016
on 133 accounts is not a weak signal, it is the absence of one. The settled IQR's lower quartile
sits *exactly* on 3,934.1 kWh, which is the PC1 Group Average Demand annualised for 2024 — the
national average customer, unmodified, is the modal household in this book.

**Why this is rung 3 in the canon's terms** (`DIRECTOR_CANON_WORLD_VALIDATION_LADDER_2026-08-31.md`):
consumption is the largest single driver of bill, margin and CLV, and if it carries no household
signal then no belief about a household can beat a belief about the mean. The ladder says a rung 3
failure is repaired *downward* — by giving individuals the rationale they lack — and the rationale
here already exists and is simply not wired: `population_draw._draw_one` draws `eac` from the
published Ofgem TDCV band and `to_customer_dict` renders it, and on the legacy route it reaches
pricing and hedging only. **It never reaches the volume.**

## The change, in one sentence

`sim.profile_class_1.load_pc1_shape` returns the **absolute** Group Average Demand series in kWh
(~3,921 kWh annualised); normalise it to that year's own annual total and multiply by the
household's own `eac_kwh` before the weather/occupancy/asset layer runs — which is the settlement
convention (profile coefficient × EAC), not a new idea.

**Scope, stated because it is narrower than "every account":** profile class 1 (domestic
unrestricted) accounts carrying a declared `eac_kwh`. **Not** the two PC3 SME accounts — PC3 is a
non-domestic profile and the same repair there is a separate question with its own evidence, filed
as owed rather than folded in. **Not** the half-hourly-metered accounts, whose volume is a real meter
read. **Not** the fabric-driven premises, whose level is set by their fabric on purpose (W1_11's own
pre-commitment says so in terms).

**What is deliberately NOT changed, and this is where my prediction departs from the brief's.** The
brief expects billed volume to fall ~1.8×, which is what happens if the whole settled total is
forced to equal the EAC. I am not doing that. The additive overlays — degree-day heating load, EV
charging, ASHP uplift — are *absolute physical quantities in kWh*, not proportions of a baseline,
and dividing them by the household's EAC would make an EV charge less on a small-consumption
account, which is false. So EAC sets the **base profile's level** and the physical overlays continue
to stack on top of it. The consequence is that a household's settled total is its EAC times its
multiplicative overlays plus its additive ones, and therefore **need not equal its EAC** — which is
also true of a real EAC, a backward-looking estimate the meter is free to disagree with.

**This is a CORRECTION, not a curriculum choice, and it errs against us.** Billed volume falls and
revenue falls with it. That direction is the tell that it is not being done to enlarge our own
result (`internal_consistency_is_not_a_fidelity_argument_for_a_world_change_that_enlarges_your_own_experiment`).

## Predictions, filed before the run

**P1 — LEVEL. Median settled kWh in 2024 falls from 4,917.6 to between 2,900 and 3,400, a fall of
1.45× to 1.70×.** Reasoning, written out so it can be wrong in public: the median household's
overlay factor today is 4,917.6 ÷ 3,921 = 1.254; applying that to a drawn median of 2,506 gives
~3,143. The band is set by the additive overlays being a larger *fraction* of a smaller base.
*Refuted if the median lands outside [2,900, 3,400].* **I expect to be nearer the bottom of the band
than the brief's ~1.8×, and I am recording the disagreement rather than quietly adopting the
brief's figure.**

**P2 — SPREAD. The settled p90/p10 spread in 2024 rises from 1.250 to above 2.00, and lands BELOW
the drawn spread of 2.421.** Above 2.00 because the drawn EAC spread now passes through; below 2.421
because the additive overlays compress it from both ends. *Refuted if it stays under 2.00 — the
level moved but the household variation did not — or if it exceeds 2.421, which would mean the
overlays are amplifying rather than compressing and I have the sign of the interaction wrong.*

**P3 — RANK CORRELATION. Spearman rho(drawn EAC, settled kWh) in 2024 rises from −0.0016 to above
+0.90.** This is the prediction the whole change exists for. Not +1.0: the overlays reorder
neighbouring households. *Refuted if rho lands below +0.90.* **If rho comes out at exactly +1.0 that
is also a finding and an unwelcome one** — it would mean the physical overlays have no ordering
effect at all, i.e. the household's fabric and occupancy stopped mattering, and I would have traded
one missing dimension for another.

**P4 — THE COMPANY'S EAC ERROR SHRINKS, AND ITS SIGN FLIPS FROM SYSTEMATIC TO NOISE.**
`_company_eac_estimate` re-estimates from the account's own billing records, so today it converges
on ~4,900 kWh while the world's statement about that household is ~2,500 — the company is not
mis-estimating, it is correctly measuring a quantity the world never linked to the household. After
the change the company's estimate and the drawn EAC are estimates of the same thing, so the median
signed error should collapse from roughly +96% toward the overlay factor, and its *dispersion across
households* should stop being dominated by one shared constant. *Refuted if the median absolute
error does not fall by at least half.*

**P4 IS NOT MEASURED IN THIS INCREMENT AND I AM SAYING SO BEFORE THE RESULT, NOT AFTER.** It needs a
full `run_phase2b`, which does not fit this invocation. It is filed as a prediction with a named
debt, and the result section will say **OWED**, not "confirmed". A prediction whose measurement is
deferred is not a prediction that passed.

**P5 — REVENUE AND MARGIN FALL, and net margin worsens.** Volume falls ~1.5× on 141 of 146
electricity accounts; revenue is roughly proportional and fixed costs are not. *Refuted if revenue
holds or rises*, which would mean the change did not reach the book. **Filed as the unflattering
half, in advance, because it is the number that will be quoted back.** Nothing may be tuned to bring
the old figures back — that is the same pre-commitment W1_11 made when the fabric switch moved
volumes, and for the same reason.

## The repairs that are NOT allowed whatever the result

1. **Re-scaling the TDCV bands so the settled median lands where it used to.** That fits the world's
   own statement to an artefact of the national average and destroys the quantity being measured.
2. **Forcing the settled total to equal the EAC by dividing the additive overlays too.** It would
   make P3 read +1.0 by construction — the rank correlation would then be a tautology and could no
   longer fail (`R15: TAUTOLOGY`).
3. **Normalising against a single hardcoded 3,921 constant instead of the profile's own annual
   total for the year in question.** The GAD annual total moves year to year with the season and
   day-type calendar (3,904.2 in 2022, 3,921.8 in 2019 and 2025); a frozen divisor would smuggle a
   ±0.5% year effect into every household's level and attribute it to nothing.
4. **Widening the scope to PC3 or to the fabric premises to make an aggregate look better.**

## What done means, since no exit test is written for this

Three things, and a landed increment is not "the run got greener":

1. The shape function reaching settlement, for a PC1 legacy-route account, has an annual base
   integral equal to that account's `eac_kwh` — mutation-provable, and the control is keyed to that
   **property** rather than to today's median.
2. rho(drawn, settled) is published as a measured number with the population it was measured on, and
   the pre-change reading of −0.0016 is kept beside it.
3. P4 and P5 are stated as OWED with what would settle them, rather than left unmentioned.
