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

---

# THE RESULT — P1, P2 and P3 ALL REFUTED. The repair works and every number I predicted about it was wrong.

*Appended 2026-08-31 after the measurement. Nothing above this line has been edited.*

Same instrument, same population, same years as the pre-change table: the annual integral of the
shape function `run_phase2b` hands to settlement, over the resi/PC1/legacy-provider accounts
carrying a declared `eac_kwh`. One variable changed — the base profile's level.

| | 2019 (n=79) before → after | 2024 (n=133) before → after |
|---|---|---|
| settled kWh — median | 4,902.2 → **2,630.6** | 4,917.6 → **2,669.5** |
| settled kWh — IQR | 3,921.8–4,902.2 → 2,028.6–3,842.7 | 3,934.1–4,917.6 → 2,030.4–3,769.9 |
| settled p90/p10 spread | 1.310 → **2.664** | 1.250 → **2.749** |
| Spearman rho(drawn, settled) | −0.0733 → **+0.8691** | −0.0016 → **+0.8845** |
| median settled ÷ median drawn | 1.976 → **1.060** | 1.962 → **1.065** |

| prediction | outcome |
|---|---|
| **P1** median settled 2024 lands in [2,900, 3,400] | **REFUTED** — 2,669.5. The fall is **1.842×**, not the 1.45–1.70× I derived |
| **P2** settled spread rises above 2.00 **and** below 2.421 | **REFUTED on the second clause** — 2.749, *above* the drawn spread |
| **P3** rho rises above +0.90 | **REFUTED** — +0.8845, short by 0.0155 |
| **P4** company EAC error at least halves | **OWED** — needs a full `run_phase2b`; not measured, not claimed |
| **P5** revenue and margin fall | **OWED** — same reason. Volume fell 1.84× on 133 of 146 electricity accounts, so the direction is not in doubt; the magnitude is unmeasured and is not being quoted |

## Why P1 was wrong, which is the part worth reading

I predicted the fall from the median household's overlay factor: 4,917.6 ÷ 3,934.1 = 1.254, applied
to a drawn median of 2,506 gives ~3,143. **The arithmetic is fine and the quantity is not a
quantity.** Before the change the settled distribution was nearly constant — p10 3,934.1, median
4,917.6, p90 4,917.6 — so its median was picking out the *modal overlay multiplier* (the EPC band D
1.25), not a median household. After the change the ordering is set by the EAC, so the median is a
median-EAC household carrying whatever overlay it happens to have. **The two medians are medians of
different things**, and dividing one by the other was exactly the mistake this project's own rule
warns about: say out loud what each number counts before dividing them.

**The brief's ~1.8× was right and my correction of it was wrong.** I recorded the disagreement in
advance and it went against me. Worth noting: the other lane that drew this same item independently
(see the finding below) filed the *same* 2,900–3,400 band from the *same* reasoning, so this is a
reproducible error in how the two of us read the pre-change distribution, not a slip.

## Why P2 was wrong, and it is the one with a live question attached

I said the additive overlays would compress the spread below the drawn 2.421. They do not — the
settled spread came out **wider** than the drawn one, 2.749. The reason is that the multiplicative
overlays (occupancy volume factor, EPC band) vary across households roughly independently of the
EAC, and independent multiplicative variation *adds*: it cannot compress. The additive terms pull
the other way and lose.

**Whether 2.749 is more faithful than 2.421 is an open question and I am not claiming it is.** It is
the honest consequence of composing two independent household descriptions, and the reason it is
open is the same double-description problem the other lane names: the drawn EAC and the EPC band are
two statements about one household's consumption, drawn on separate substreams, and nothing
reconciles them. Filed as owed. **What is not open is the direction**: a settled spread of 1.250 on
a drawn spread of 2.421 was the world flattening its own households.

## Why P3 landing at +0.8845 rather than +1.0 is the good half

The pre-registration recorded that rho = +1.0 would be an unwelcome result — it would mean the
physical overlays stopped ordering households at all, trading one missing dimension for another.
+0.8845 says the household's own annual statement now sets the level *and* its fabric, occupancy and
assets still move it around that level. The prediction is refuted; the property it was reaching for
holds.

## Filed BEFORE P4 is measured, because it bears on P4 and on nothing above

On a drawn account, `eac_kwh` is the world's own draw (`population_draw._draw_one`, Ofgem TDCV band)
rendered into the supplier's roster **verbatim** by `SyntheticCustomer.to_customer_dict`. So the
world's statement and the supplier's declaration are one object, and driving settled volume from it
makes the company's EAC re-estimation partly self-referential in a way it was not before — W1_11's
own docstring reads the declared EAC as the company's *belief* for exactly this reason.

**P4 must therefore be scored knowing that some of any improvement is self-inflicted.** What keeps
it from being a pure tautology is that settled volume is not the declaration: occupancy, EPC band,
heating system and assets move a household away from it, which is precisely the 2.749-vs-2.421 gap
above. The structural repair — a world-side true EAC and a supplier-side declaration that may
differ, with a read error between them — is **OWED** and is the next atom on this thread. Recorded
here rather than in the result table because it changes how P4 is read and P4 has not been read yet.

## What landed, and what did not

Landed: the level, the control, and this reading. `simulation/demand_model.eac_scaled_shape_fn` +
`profile_annual_kwh`, wired at both `_weather_adjusted_shape_fn` call sites through one
`_base_profile_eac` decision, with `tests/simulation/test_the_drawn_eac_sets_the_settled_level.py`
keyed to the property.

**Not landed, and named rather than left quiet:**

1. **P4 and P5** — both need a full `run_phase2b`, which did not fit this invocation.
2. **PC3 / the two SME accounts.** I scoped this to the domestic profile class and pre-registered
   that scope. The other lane pre-registered the *wider* scope with the better argument — *"fixing
   the resi instance and leaving the SME one is fixing an instance, not a class"* — which is this
   project's own rule. **Their argument wins and I am not adopting it here**, because changing the
   intervention after filing the pre-registration and before publishing its result is the thing the
   discipline exists to prevent. It is theirs to land, on their pre-registration, and this is the
   pointer.
3. **A mutation proof of the new controls.** `process_run_complete` was live in this shared tree
   while the work was done, and mutating a shared module under a running hook chain manufactures a
   red in another lane's gate. The controls are structurally able to fail — the unlevelled arm is
   exercised as its own test beside the levelled one, and
   `test_the_level_is_applied_exactly_once_on_the_path_the_book_settles_on` goes red on a second
   normalisation — but **"able to fail" is not "proven to fail" and I am not claiming the latter.**
