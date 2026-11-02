**Knowledge:** the-customer-needs-framework

# Stated against revealed preference, and defaults: the gap is not a multiplier, and a default buys enrolment rather than response (2026-11-02)

This is page 5 of the customer-needs domain as `docs/design/THE_KNOWLEDGE_BASE_STRUCTURE.md` §4 ranks it. It answers
the 30 Oct corpus steer (`docs/staging/advisor/DIRECTOR_STEER_BUILD_THE_CUSTOMER_KNOWLEDGE_CORPUS_AND_PROPOSE_THE_NEXT_SIM_ADDITIONS_2026-10-30.md`),
Ask 1 and both addenda. It guards every other page in the domain: most of them rest on what households *said*.

Grades as on the sister pages: **D** derived by us from primary data, **P** reported in a primary publication by the
body holding the data, **S** a secondary summary, **A** an assumption with a range.

**Sides.** World: how large a drawn household's response is, given what a survey says. Supplier: what a stated
answer (a quote form, a preference centre, a survey it runs) is worth as a predictor. A household's *intention* is
hidden truth; its *stated answer* and its *later action* are both observable to a supplier that asks and then records.

No predictions were filed before these sources were read. Every figure below was read first.

## 0. Three things that are each called "the stated-revealed gap"

They must not be read as one number.

| # | What is compared | Same people? | What it measures |
|---|---|---|---|
| G1 | Survey willingness in some studies against sign-up in other studies | **No** | How far a survey level overstates a market level, confounded with country, tariff and year |
| G2 | Intention against later behaviour, same people | Yes | How much of behaviour intention predicts |
| G3 | A contrast between groups when stated against the same contrast when revealed, same survey | Yes, same waves | Whether a survey's *differences between households* survive into what they do |

A world parameter is usually a contrast (G3) or a response size, not a level. That is the reading that matters most
here, and it is the one the packs did not have.

## 1. G1: the "3-5×" figure (P, ratios D)

Source: Nicolson, Fell and Huebner (2018), 66 uptake measures from 27 studies in six countries; extract in
`data/lake/nicolson_tou_uptake_review_2018/table3_uptake_by_factor_extract.csv` (the PDF re-fetched today hashes
the same as the lake's record).

The sister page (`the_gb_natural_experiments_that_pin_the_weights_2026-11-02.md` §3) already corrected the packs'
"3-5×" to "about 2× to 5×, depending on the statistic". This page goes one step further, and **corrects that too**:

- **The ratio divides two numbers from different populations.** The survey measures are "most of which were run on
  nationally representative samples of British energy bill payers"; the commercial measures are those "most of
  which are offered in the US" (p.283). A median of GB surveys over a median of US sign-ups is not a conversion
  rate of anyone. The paper's own "five times" is this ratio.
- **The paper's regression gives an offset, not a multiplier.** With study fixed effects, "uptake measures elicited
  from surveys are consistently estimated as being between 28% and 36% points higher than uptake to commercially
  available TOU tariffs or tariffs people were able to sign up to in trials" (p.282). That is additive: 28-36
  percentage points, P.
- **Trial recruitment against commercial sign-up is not a significant difference** (p = 0.490, p.282), so the
  1.6×-3× "against trial recruitment" readings on the sister page are not a separate gap.

**Corrected:** a stated ToU willingness overstates sign-up by about 30 percentage points on this evidence, not by
a factor. Applied as a factor, a 36% survey becomes 7-18%; applied as an offset it becomes 0-8%. Neither is a GB
revealed rate. **Graded A, with that range, for any GB opt-in ToU uptake**; the paper's own bracket is 1% to 43%.

## 2. G2: intention against behaviour, same people (P)

- Armitage and Conner (2001), 185 studies: the theory of planned behaviour (intention plus perceived control)
  accounts for **27%** of the variance in behaviour, and **11 points more** when behaviour is self-reported than
  when it is observed. The packs' "about 28%, cited by Fell et al." is **corrected to 27%**, and to the source.
- Webb and Sheeran (2006), 47 experiments that changed intention: a medium-to-large change in intention
  (d = 0.66) produced a small-to-medium change in behaviour (**d = 0.36**). About half of an induced change in
  intention reaches behaviour (0.36 / 0.66 = 0.55, D, on a ratio of standardised effects).

Neither is energy-specific. They bound how much a supplier can learn from asking: a stated answer is a weak
predictor of one household's action, and a self-reported action (CIM's C4, below) overstates the link.

## 3. G3: contrasts between households, CIM Waves 3-6 (D)

Source: `revealed_switching_by_age_and_arrears_and_the_needs_tables_in_cim_waves_4_6_2026-11-02.md` §3, which reads
Ofgem's Consumer Impact Monitor tables. Intent to switch supplier in the next three months against reported
switching to a new supplier in the past six months (twelve in Wave 3); the windows differ, so only contrasts compare.

| Contrast | Survives into behaviour, Waves 4-6 (revealed over intent) |
|---|---|
| Youngest against oldest band | about **a fifth** (0.2, 0.3, 0.1) |
| Behind on bills against no difficulty | about **half** (0.6, 0.5, 0.5) |

**Extended.** The stated-revealed gap is not one shrink factor applied to every household. It shrinks some
differences much more than others. A world that draws a response from a stated survey contrast overstates the age
difference about five-fold and the arrears difference about two-fold. That is the reason the needs pages grade a
stated contrast as a direction, never as a size.

## 4. Defaults: enrolment and response are separate quantities (P, ratios D)

Source: Fowlie et al. (2017, published 2021), a randomised experiment at the Sacramento Municipal Utility District
in which the same critical-peak (CPP) and time-of-use (TOU) prices were offered either as an opt-in or as a default.
Extract in `data/lake/fowlie_default_effects_smud_2017/headline_rates_extract.csv`.

| Quantity | Opt-in | Default (opt-out) | Ratio (D) |
|---|---|---|---|
| Enrolled | about 20% | over 90% (under 5% opted out) | about 4.5× |
| Peak cut per **enrolled** household, CPP event days | 0.664 kWh | 0.323 kWh | opt-in 2.1× |
| Peak cut per **enrolled** household, TOU, event-day hours | 0.473 kWh | 0.136 kWh | opt-in 3.5× |
| Peak cut per **enrolled** household, TOU, ordinary peaks | 0.288 kWh | 0.105 kWh | opt-in 2.7× |
| Peak cut per **offered** household, CPP event days | 0.130 kWh | 0.299 kWh | default 2.3× |

- **Confirmed:** the default effect is very large (the sister page's 83%/26% from Nicolson's three opt-out measures
  is consistent with a randomised 90%+/20%).
- **Extended, and it changes a supplier result.** The households a default adds (the paper's "complacents", about
  75% of the population) do respond, but each cuts its peak by about a third to a half of what an active chooser
  cuts. A default raises the *total* response because it enrols so many more, while each defaulted household is worth
  less per head. A world in which a defaulted household responds like a chooser overstates a default product's
  value per account two- to three-fold. A world in which it does not respond at all understates the total.
- **Not GB.** One US utility, summer peaks with air conditioning. GB has no published randomised default on a
  domestic tariff (sister page §3). The **direction** (defaulted responders respond less per head) is P and is the
  belief to carry; the **size** is A, range one-third to one-half of a chooser's response, until a GB source exists.

## 5. What this changes

**World.**
- No response size is drawn from a stated survey level. Where a level is all that exists, it is an A with the
  section 1 range.
- A between-household contrast taken from a stated survey is a direction, shrunk toward zero by a factor that differs
  by contrast (section 3), until a revealed contrast exists.
- A household enrolled by default and one that chose carry different response sizes (section 4). One response
  parameter for both is the error to avoid.

**Supplier.**
- A stated answer the supplier collects predicts little of one household's action (section 2). The supplier's method
  (M4) should learn from what households do once offered, not from what they say.
- Defaulting is the largest single lever on enrolment the evidence shows. Its value must be graded per enrolled
  household *and* per offered household, because the two point opposite ways.

## 6. Graded against the advisor's packs

| Pack claim | Verdict |
|---|---|
| Stated ToU willingness 36%, trial 12%, commercial 7% (Nicolson) | **Confirmed** as medians. The means are 37/23/17 |
| "3-5×" stated-revealed gap | **Corrected**: different populations divided; the paper's fixed-effects estimate is an offset of 28-36 points |
| Intention explains about 28% of behaviour (via Fell) | **Corrected** to 27%, Armitage and Conner (2001), and 11 points lower for observed behaviour |
| Opt-out enrolment approaches 100% | **Confirmed**, and **extended**: defaulted households respond about a third to a half as much per head (Fowlie) |

## 7. Gaps

- **GAP-SR1:** no GB randomised default on a domestic tariff. The per-head response of a defaulted GB household is
  an A.
- **GAP-SR2:** no GB study links one household's stated answer to its later supplier record. Section 2 is
  international and not energy-specific.

## Sources

- Nicolson, M., Fell, M. and Huebner, G. (2018). Consumer demand for time of use electricity tariffs: a systematized
  review. *Renewable and Sustainable Energy Reviews* 97, 276-289. https://discovery.ucl.ac.uk/10054779/7/Nicolson_1-s2.0-S1364032118306257-main.pdf
- Fowlie, M., Wolfram, C., Spurlock, C.A., Todd, A., Baylis, P. and Cappers, P. (2017). Default effects and
  follow-on behavior. NBER WP 23553. https://www.nber.org/system/files/working_papers/w23553/w23553.pdf
  (*Review of Economic Studies* 88(6), 2021).
- Armitage, C.J. and Conner, M. (2001). Efficacy of the theory of planned behaviour: a meta-analytic review.
  *British Journal of Social Psychology* 40, 471-499.
- Webb, T.L. and Sheeran, P. (2006). Does changing behavioral intentions engender behavior change? *Psychological
  Bulletin* 132(2), 249-268.
- Ofgem, Consumer Impact Monitor, Waves 3-6, as read on the sister page.
