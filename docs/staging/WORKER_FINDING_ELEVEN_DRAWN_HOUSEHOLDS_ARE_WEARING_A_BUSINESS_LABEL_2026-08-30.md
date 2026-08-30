**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# Eleven drawn households are wearing a business label, and three separate red controls are all reporting it

**Found:** 2026-08-30, dispositioning the HEAD red census the director named. Three of the six
failures the census returned are one defect, and none of them says so — each control sees the
corner of it that falls in its own lane.

## The measurement

`simulation.run_phase2b.CUSTOMERS`, 258 accounts, of which 13 carry `segment` in
`("SME", "I&C")`. Eleven of those thirteen map to a **residential** property type:

| account | fuel | acquisition | property_type | annual volume |
|---|---|---|---|---|
| SYN-2016-005 | electricity | synthetic_draw | semi_detached | 2,631 kWh |
| SYN-2016-013 | electricity | synthetic_draw | semi_detached | 2,666 kWh |
| SYN-2016-015 | electricity | synthetic_draw | semi_detached | 2,606 kWh |
| SYN-2016-023 | electricity | synthetic_draw | semi_detached | 3,627 kWh |
| SYN-2016-034 | electricity | synthetic_draw | semi_detached | 2,551 kWh |
| SYN-2016-040 | electricity | synthetic_draw | semi_detached | 1,744 kWh |
| SYN-2016-003 | gas | synthetic_draw | semi_detached | 6,306 kWh |
| SYN-2016-012 | gas | synthetic_draw | semi_detached | 14,748 kWh |
| SYN-2016-014 | gas | synthetic_draw | semi_detached | 9,664 kWh |
| SYN-2016-044 | gas | synthetic_draw | semi_detached | 9,237 kWh |
| SYN-2016-054 | gas | synthetic_draw | semi_detached | 9,458 kWh |

**Every one is a drawn account, every one is a semi-detached house, and every one consumes a
household's worth of energy.** Ofgem's typical domestic consumption values are 2,700 kWh
electricity and 11,500 kWh gas; these sit either side of both. For contrast, the two accounts
that are genuinely non-domestic are the hand-authored founders C5 and C6, at 15,000 and 45,000
kWh of electricity — five and seventeen times a household.

An SME that uses less electricity than a typical house is not an SME. The label is wrong; the
household underneath it is fine.

## The three controls, and why none of them could name the defect

| red control | what it sees |
|---|---|
| `tests/simulation/test_phase_b_life_events::test_real_roster_business_segment_never_residential` | a business account in a residential dwelling — closest to the truth, and names one account |
| `tests/company/pricing/test_the_support_bound_is_domestic::test_the_non_domestic_share_under_a_domestic_bound_stays_small` | 8 of 150 electricity accounts (5.3%) priced under a bound derived from the Ofgem DOMESTIC cap |
| *(see the companion finding)* | the segment dial moves the residential book — a DIFFERENT defect that presents in the same area |

**The pricing control's reading is inverted by this, and that is worth stating plainly.** It
reports that 5.3% of the priceable book is non-domestic and is being priced under a domestic
bound. Six of those eight accounts are domestic households. So the domestic bound is CORRECT for
them and the alarm is firing on a labelling error rather than on a pricing error. The remaining
two are C5 and C6, which are genuinely non-domestic — and 2 of 150 is 1.3%, which is the share
that control was presumably shaped around.

That distinction matters because the two repairs point in opposite directions: fix the labels and
the pricing control goes green with nothing changed about pricing; "fix" the pricing and you have
built a non-domestic bound for six houses.

## What this does to the tariff-type determination — it strengthens it

`DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` argued that the SME carve-out *"covers two
accounts and cannot carry the change"*, on a census that found 220 of 222 electricity accounts
residential. Today's roster shows 8 of 150 non-domestic, which at first reading weakens that
argument from 1% to 5%.

**It does not, and the measurement is the reason.** Six of the eight are domestic households with
a wrong label, so the genuine non-domestic count is still two. The determination's conclusion —
that the domestic statistic governs and the SME carve-out cannot carry a book-wide change — holds
on the corrected census, and holds for a better reason than the one available when it was written.

Recorded here because I am building C1 on that determination, and a finding that appears to
undercut the foundation of work in flight has to be resolved rather than noted.

## What is owed

The draw assigns `segment` independently of the dwelling and the volume it generates. Either it
should draw a genuine non-domestic account (non-residential property type, business-scale
consumption, a business tariff structure and a broker acquisition channel) or it should not
produce business segments at all and leave the two founder SMEs as the only ones.

**Recommendation: the second, for now.** A GB domestic supplier's book is what this project
models; the brief of 2026-08-30 is entirely about households; and a synthetic SME that is a house
in a costume adds no fidelity while breaking three controls and inverting a fourth's reading.
Drawing real SMEs is a genuine piece of world-building with its own anchor requirements (business
consumption profiles, broker commission as a per-kWh trail, 1–3 year contracts) and belongs on the
roadmap, not in a label.

Not done here (SELF_INTERRUPT_DISCIPLINE): it changes the composition of the live book, so it
moves published figures and needs its own pre-registration and one-variable run. It was found
while dispositioning someone else's red census, which is the definition of on-the-way-past.

## The falsifier that is already there

`test_real_roster_business_segment_never_residential` is the right control, keyed to the property
rather than to a count, and it is currently red for the right reason. It should go green because
the labels were fixed, and never because the assertion was relaxed.
