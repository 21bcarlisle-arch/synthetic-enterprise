**Knowledge:** price-cap

# A time-of-use tariff needs the household's choice, not its meter

K8 page for items 5 and 6 of
`docs/staging/SEAT_FINDING_SVT_BILLS_ABOVE_THE_CAP_ARE_TWO_DEFECTS_NOT_A_GRADING_ARTEFACT_2026-10-23.md`.
Written 24 Oct 2026. The question: **may a supplier put a household on a multi-register (time-of-use)
tariff it did not contract for, because the meter allows it?** What the rules say, what is not
published (GAP), and which choice the build makes.

## What the rules say

**1. A Multi-Register Tariff is a contract, not a meter (SLC 28AD, SLC 1).** Quoted verbatim in
`docs/domain_artefact_library/regulatory/slc_28ad_multi_register_cap_test.md`: a Multi-Register
Metering Arrangement "includes any contractual arrangement whereby the Domestic Customer is charged on
the basis of Time of Use Rates (regardless of the metering equipment employed)", and a Multi-Register
Tariff is "a Tariff whereby a Domestic Customer incurs Charges for Supply Activities on the basis of"
one. The definition reads from the charging arrangement to the tariff. A smart meter that *can* record
by time band does not put its household on a Multi-Register Tariff. The tariff the household is
charged under does that. 28AD.3/.4 then grade the tariff against the benchmark of its own type.

**2. A default tariff must resemble what the household already had (SLC 1, 2017).** Ofgem,
*Notice of modifications and reasons: default tariffs for domestic customers at the end of fixed-term
contracts* (electricity, 10 Oct 2017, ofgem.gov.uk/system/files/docs/2017/10/notice_of_modifications_and_reasons_-_default_tariffs_for_domestic_customers_at_the_end_of_fixed-term_tariffs_electricity.pdf,
fetched 24 Oct 2026). A rollover tariff must be "similar in nature to the customer's current tariff,
taking into account their characteristics and preferences (eg in respect of tariff type, online
account management, meter type and payment method)". The defined term "Relevant Fixed Term Default
Tariff" carries the same test: "terms and conditions that are ... similar in nature to the existing
Fixed Term Supply Contract for that Domestic Customer, including in respect of ... their current
Relevant Meter Type", and it must be no dearer than the "Relevant Cheapest Evergreen Tariff". So the
rollover follows the household's current tariff type. It does not follow what the meter could do.

**3. Billing a ToU pair off sub-daily reads needs explicit consent (SLC 47).** Ofgem,
*SLC 47 statutory notice* (Sept 2022, ofgem.gov.uk/sites/default/files/2022-09/SLC%2047%20Notice.pdf,
fetched 24 Oct 2026; marked-up text, old and new paragraph numbers both shown). 47.6: the licensee "must
not ... obtain any Electricity Consumption Data which relates to a period of less than one month",
subject to exceptions. Daily data (47.7/47.8) may be obtained after notice unless the customer objects.
Data for "a period of less than one day" (47.10/47.11) needs Notice "that the licensee requires the
Domestic Customer's consent", and "the Domestic Customer has given their explicit consent". The billing
exception, 47.9(b), covers a single period since the last billing date and is not a half-hourly
series. A ToU pair priced per half-hour, as this build settles it, reads half-hourly data. Without
the household's explicit consent the supplier may not obtain that data for billing.
`docs/market_research/smart_meter_hh_data_consent_2026.md` already separates this billing regime
from the settlement opt-in that MHHS retires.

**4. Deemed contracts.** A deemed contract is 28AD-capped like the SVT (28AD's Relevant 28AD Customer
definition). This build settles it on its own single-rate path (`simulation/hedged_settlement.run_deemed_term`).

## What is not established (GAP)

- **GAP: register-based ToU without half-hourly data.** A SMETS2 meter can hold time-of-use registers
  the supplier configures, read monthly. On that route SLC 47's sub-daily consent may not apply. No
  published rule found says a supplier may or may not configure ToU registers on a default tariff a
  household did not choose. Rule 2 already points against it.
- **GAP: the verbatim definition of "Relevant Meter Type"** in the current consolidated SLC 1. From
  practice, it separates single-rate from Economy 7/10 and other multi-rate arrangements. It is not
  quoted here.
- **GAP: uptake.** What share of smart-metered households, offered a ToU pair with a fix, would take
  it. The build assumes a household that accepts a fix quoted as a ToU pair has chosen ToU. That is
  this supplier's product shape (`company/pricing/tou_desk.py`), and how many households would accept
  it is unmeasured.
- **Practitioner check, not yet asked:** whether any GB supplier rolls smart single-rate households
  onto a ToU default. No published source says one does. Under K4 this goes to the director only if
  someone shows it matters.

## The choice the build makes

**A default-tariff term is single-rate whatever the meter. A term is ToU only where the household
took a product quoted as ToU (a fix) and the meter allows it.** `tou_desk.offers_tou(customer, *,
tariff_type)` refuses ToU for `DEFAULT_TARIFF_TYPES` (`svt`, `deemed`, the same tuple the cap invariant
reads). `tariff_type` is required, so no caller can reach ToU by leaving it out. The renewal chain
reads the same predicate, so a smart home's default tariff is graded against the single-rate cap and
its fix against the multi-register cap (28AD.3/.4).

Before 24 Oct 2026, every term of a smart-metered home was settled as a 1.5×/0.79× pair revenue-neutral
at 30/70, the default included. On run `8b6fea024` that reaches the 127 actual-read accounts, and 501
default-tariff bills that did not reproduce their term's struck rate. The household-ceiling invariant
graded 59 of them as over the cap, but they were a pair struck at the cap and are lawful at their split.

**Item 6, each register's rate on a ToU invoice.** After the fix every ToU bill is on a chosen term.
A bill that carries one `Anytime` register at the blended rate still cannot be checked by its household.
What the build does about that is recorded in the finding's item 6.
