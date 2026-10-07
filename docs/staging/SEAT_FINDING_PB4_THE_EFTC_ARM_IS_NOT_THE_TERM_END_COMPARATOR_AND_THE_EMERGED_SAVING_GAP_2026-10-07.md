# PB4: the EFTC control arm is not the term-end comparator, and the emerged saving gap by engagement

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity` · **Claim:** `pb4-closes-the-fixed-term-end-refix-share` (Lane 0)

Closes or files the two open disqualifiers from PB4's blind Expert Hour (`789083280`): D1 (the
world's re-fix share at a fixed-term end against Ofgem's EFTC control arm) and D4 (the emerged
pattern on the page).

## Premise, re-measured at draw

The duplicate claim the draw named is this draw's own write. No rival `surgical_land` or seat is
working PB4. `789083280` is the Expert Hour itself; nothing since has touched D1 or D4.
PB4's row still reads FAIL held at L2.

## D1: FILED, NOT THE COMPARATOR. No re-fit.

The trial report was re-fetched and text-extracted on 2026-10-07: Ofgem, *End of Fixed Term
Communications Trial*, September 2019. The control arm's population is defined by three
selections. Each one moves the internal (re-fix) share in a known direction.

1. **It conditions out the early re-fixers.** §3.4 excludes "customers who had already switched to a
   new tariff". §5.3 says plainly what that removes: *"The customers involved in the EFTC trial were
   those who remained on a fixed tariff a few days before it was due to expire. Many of the
   customers on these same tariffs will have already made an active choice to switch to a new
   tariff before this point."* The report does not publish that excluded count.
   - The control arm's 14% internal is therefore re-fixing among those who had not yet re-fixed.
   - The world's 31% is re-fixing among all households reaching a term end.
   - These are different quantities, and the trial's figure is a **lower bound** on the term-end
     re-fix share. The world's 31% is the unconditional share; it is consistent with the trial
     for any pre-emptive re-fix share of about 20% or more.
2. **One large incumbent, chosen for inertia.** §3.13–3.14: the supplier was shortlisted because
   its roll-over-onto-SVT rate was above average. Mean tenure was 17 years (§4.7). The world's
   households at a term end are a small supplier's customers, all acquired by switching. That is
   the opposite selection.
3. **The trial's own tenure gradient points the world's way.** Fig. 4.6, control arm, by tenure:
   - 5 years or under: 20%
   - 5–10 years: 20%
   - 10–15 years: 20%
   - 15–20 years: 10%
   - over 20 years: 8%

   The world's book sits at the short end, or below it.
4. Six-week window; prepayment excluded (§3.4, §3.7). The supplier's own 2018 baseline was 16%
   within 30 days of tariff end, internal and external together (§3.5).

The external legs agree: the world sends 4.5% out, against the trial's 6%.

**Verdict.** Re-fitting the world's re-fix share to 14% would fit it to an inert incumbent's
not-yet-acted residue. The world would move off the record, not onto it. D1 does not show the
world's re-fix share to be twice the published one, because no published figure for that
quantity exists. The 35% active anchor is still what `svt_rates_active_passive_2016_2025.md` §4
says it is: a structural inference, not directly cited. This finding does not promote it.

**What would close it.** The unconditional split at a fixed-term end for a small supplier's
recently switched book. That is the same unpublished instrument (Ofgem's 2019 roll-over RFI, by
supplier) that `first_renewal_departure_rate_small_gb_supplier.md` already names as the director's
third-side question. It is one question, not a new one.

## D4: pre-registration, written before the capture was read

**Subject.** The world's own renewal decisions at real inputs, from one `capture_departure_factors`
run of the current HEAD. These are the arguments and the outcome of every `roll_lifecycle_event`.

**Definitions.**
- *Engagement group*: the household's persistent archetype (`engagement_level_for_customer`), read
  as world-side truth for an evidence surface only.
- *Saving*: `price_differential_vs_market_reference`, the fraction by which this supplier's offer
  sits above the market reference the household faces. Positive means leaving saves money.
- *Leave*: `event_type == "churned"`.
- *The world's own probability*: `realized_churn_probability`, reported beside the realised count
  because it carries far less noise than the dice.

**Bands, fixed before the read:** no saving (differential <= 0), up to 5%, 5-15%, over 15%. A cell with
fewer than 10 decisions is shown as too few to read.

**Predictions** (written 2026-10-07, before any row was read):
- **P1.** In every saving band where both groups have at least 10 decisions, the active archetype's
  mean realised probability of leaving is above the disengaged archetype's.
- **P2.** The gap between active and disengaged widens as the saving grows. Passive rollers are
  capped at 0.10 (`PASSIVE_CHURN_CAP`), so their curve flattens while the active curve does not.
- **P3.** On realised counts, the two groups' 95% Wilson intervals overlap in most bands. One run of
  this book cannot resolve the gap by dice alone.
- **P4.** The ratio of disengaged to active mean probability is well above the ratio of their
  `P(active)`, 0.20/0.50 = 0.4. The reason is that passive rollers still leave, up to the cap.

## D4: result. ON THE PAGE, AND THE PATTERN IS NOT REPRODUCED

**The capture.** One run of `tools/capture_departure_factors` at `bebf42253`, default seed, reduced
to `docs/reports/pb4_departure_factors.json`. It holds 75 renewal-roll decisions (71 on the resi
book) and 1,777 SVT drift decisions.

**The definition was wrong before the read, and the read is what showed it.** 72 of the 75 renewal
rows carry no passive cap, so they are households that LOOKED. A household that does not look never
reaches `roll_lifecycle_event`. It goes onto the default tariff and can leave only through the SVT
drift roll. The band x archetype table pre-registered above would therefore have measured
"leaving, given looking". The world draws that independently of the archetype, and the table would
have been captioned "who leaves at the end of a deal". It is not published. What is published
instead covers both routes per archetype, plus a pooled read by saving over the households that
looked.

| Archetype | Households | Reached the roll | Left there (world p) | SVT drift p / cap period | SVT left / SVT-year (counted) | Expected departures / household | Counted |
|---|---|---|---|---|---|---|---|
| active | 56 | 55 | 0.338 | 0.0247 | 0.121 | **0.61** | 0.55 |
| passive | 42 | 11 | 0.407 | 0.0272 | 0.179 | **0.48** | 0.57 |
| disengaged | 25 | 5 | (n=5) | 0.0229 | 0.054 | **0.60** | 0.36 |

Households that looked, by saving on offer:
- no saving: 52 decisions, 14 left, world p 0.348
- up to 5%: n=7
- 5% to 15%: n=8
- over 15%: n=4

The last three are each too few to read.

**Verdict.** The separated model does NOT reproduce "low-engagement households switch less". Its
built-in engagement effect is real but sits only at the renewal gate: who looks (55 of 56 active
against 5 of 25 disengaged). On the default tariff, `departure_risks.svt_inertia_hazard` takes
years-on-SVT and the market year and nothing else. Every archetype therefore drifts off it at the
same world probability (0.023 to 0.027 per cap period). That route carries most of the world's
departures (61% at C1b; the docstring says so). So over the run a disengaged household is
**expected** to leave as often as an active one (0.60 against 0.61).

> **Superseded on the page, 2026-10-07, by the re-capture on `beb4f8533`'s world.** The table and
> verdict above describe the engagement-blind world at `bebf42253` and are kept as written. Since
> `beb4f8533` the SVT drift carries the sourced engagement gradient (`SVT_INERTIA_DISENGAGED_RATIO`,
> 0.54, Ofgem CMOL 2017). The re-capture was taken at `85ddd37d8` plus that change only (graded in
> `WORKER_FINDING_PB4_THE_SVT_DRIFT_ENGAGEMENT_GRADIENT_IS_WIRED_AND_THE_PREDICTION_HOLDS_2026-10-07.md`).
> It now sits in `docs/reports/pb4_departure_factors.json`, with 71 resi renewal decisions and
> 1,764 SVT decisions.
>
> | Archetype | SVT drift p / cap period (was) | SVT-years (was) | Expected departures / household (was) | Counted (was) |
> |---|---|---|---|---|
> | active | 0.0288 (0.0247) | 124.2 (124.2) | **0.654** (0.61) | 0.55 (0.55) |
> | passive | 0.0309 (0.0272) | 113.1 (117.1) | **0.522** (0.48) | 0.57 (0.57) |
> | disengaged | 0.0138 (0.0229) | 112.7 (111.5) | **0.397** (0.60) | 0.32 (0.36) |
>
> Disengaged against active expected departures is now **0.607**, against 0.98 before. The pattern
> is reproduced in direction: a disengaged household is expected to leave about 0.6 times as often as
> an active one. The renewal-roll leg did not move, so the whole change comes through the drift.
> The page's verdict sentence is now computed from the feed's ratio instead of being fixed prose.
> P4's "about 1.0" is therefore superseded on the page. P1 to P3 are unchanged, because they read the
> renewal roll and the bands, and neither moved.

The counted column (0.36 against 0.55) looks like the published pattern, but it is dice. The SVT
leg's 6 departures against about 13 expected is the whole gap. A reader of realised counts alone
would have closed D4 on noise.

**The "on a given saving" leg cannot be read on this run.** 52 of 71 looked decisions had no
saving on offer, and the other 19 split into cells under 10.

**Predictions, graded beside themselves:**
- **P1 REFUTED** (where readable): pooled over bands, active 0.338 is below disengaged 0.414 (n=5)
  and passive 0.407, given looking. The test was mis-aimed at a quantity the world sets equal by
  construction.
- **P2 REFUTED / UNREADABLE**: passive rollers barely reach the capped roll (3 of 75 rows). Their
  departures go through the SVT route, so the cap is not where the gap would show, and no band
  beyond "no saving" reaches n=10.
- **P3 CONFIRMED**, and more strongly than written: three of four saving bands are unreadable even
  pooled across archetypes.
- **P4 REFUTED as framed**: the passive leg does not leave through the 0.10 cap. It leaves through
  the archetype-blind SVT drift, which is why the expected-departure ratio of disengaged to active
  is about 1.0, not "well above 0.4".

## What is owed, and where

1. **World (W2 / PB4 BUILD): the SVT drift is engagement-blind.** The 0.20 / 0.10 annual anchors
   are population figures for SVT holders. Spreading them by archetype needs a sourced gradient:
   how much less a long-default, never-switched household drifts than a recently lapsed fixer.
   That source is not in the tree. Knowledge first: this is a research pass before any multiplier,
   and the code should carry `None` with its reason until then. The years-on-SVT split already
   carries part of it, since disengaged households average 2.6 SVT years against 1.4 for active
   ones. Not enough to show.
2. **The term-end split (D1)**: the director's third-side question already on file in
   `first_renewal_departure_rate_small_gb_supplier.md`.
3. **Saving gradient among lookers**: 52 of 71 looked decisions sat at no saving. One run cannot
   read the gradient. A multi-seed capture, about 20 minutes per seed, is the instrument if the
   SVT fix lands.

**PB4's level is NOT recorded.** It stays L2. The remaining blocker is (1), plus re-taking the
Expert Hour after it.
