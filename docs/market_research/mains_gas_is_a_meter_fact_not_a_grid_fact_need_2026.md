**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** W2_20_mains_gas_is_drawn_not_inferred_from_the_heating_system

**Knowledge:** none -- the housing knowledge page is deliverable 4 of the housing ruling and is not
yet written. This is one of the anchored rows it will be built from; the declaration is replaced
when the page lands.

# "Off gas" is a fact about a meter, not about the grid — and half of all flats read as off gas

**Measured 2026-09-06**, delivery seat, `W2_20`. Source: DESNZ NEED `anon2026_50k.csv`, the same
50,000 dwellings the floor-area anchor came from. Raw stays out of the repo.

---

## What the ruling asked for, and what the data actually is

Housing ruling §3.1 wants heating system and fuel drawn "including **no mains gas**". Neither the
`DrawnPremise` nor the `Household` carries any gas field today, so off-gas is currently *inferred*
from the heating system — backwards, because a property with no gas supply has no gas system to
choose.

NEED has `MAIN_HEAT_FUEL`. **It is DERIVED, and DESNZ says so in its own metadata:**

> A property is assumed to be using gas as its main heating fuel if (and only if) it has a gas
> meter matched to it *and* that gas meter has a consumption of at least 1,000 kWh for any of the
> latest 3 years.

So `MAIN_HEAT_FUEL = 2` bundles three different worlds: no gas supply at all; a gas supply with no
meter matched to this dwelling; and a matched meter used for under 1,000 kWh in three years.

## The measurement that settles what it means

| | share "not gas" | n |
|---|---:|---:|
| **Flat** | **50.3%** | 11,910 |
| Detached | 15.5% | 7,777 |
| Bungalow | 15.0% | 3,968 |
| End terrace | 7.2% | 4,309 |
| Semi detached | 6.6% | 12,592 |
| Mid terrace | 6.5% | 9,444 |
| **All** | **19.1%** | 50,000 |

**Half of all flats cannot be off the gas grid.** Flats are overwhelmingly urban, and the grid runs
past them. What the flag is picking up is that no individual gas meter is matched to the dwelling —
electric heating, or a communal/district system metered at the building rather than the flat.

The genuinely off-grid stock is visible where you would expect it and at a plausible size: detached
at 15.5% and bungalow at 15.0%, which is rural oil and LPG.

## So the attribute to draw is not "off grid"

It is **"has a mains gas supply at this meter point"** — which is the fact a supplier actually
holds, actually bills, and actually sees. A supplier does not know whether the main runs under the
street; it knows whether it has a gas meter point for this customer. Drawing the observable is both
the more honest quantity and the one the company can be measured against later.

Labelling this attribute "off grid" would be a definitional error of the kind that has been
expensive here before — a concept nobody defined, then differenced and published. **It is named
`has_mains_gas_supply` for that reason, and this page is the reason.**

## What this source cannot settle

The validity flag `GasValFlag2024` is meant to say *why* a reading is absent — `O` = missing or not
yet connected, `L` = below 1,000 kWh. Within the "not gas" population it resolves almost nothing:

    (blank)  8,660   90.6%
    L          451    4.7%   connected, low user
    O          444    4.6%   missing / not connected

**90.6% are blank**, so the decomposition does not separate "no supply" from "no matched meter".
The arithmetic bound this permits — 18.2% ≤ off-grid ≤ 19.1% — is therefore **not a real bound on
grid connection**, only on this dataset's own flag, and it is recorded here so nobody quotes it as
one. The true off-grid share needs a different source (the published count of properties not
connected to the gas network) and is a **registered gap**, not a number.
*Corrected 2026-10-07: the gap is closed by the published comparator below, which turned out
to be a meter fact as well.*

## What to draw

- `has_mains_gas_supply`, drawn conditional on property type, with the marginals above.
- The existing heating-system marginals must not move as a side effect. If drawing supply first
  changes them, that is a fidelity finding decided blind to P&L — not a fix to be absorbed.
- The 1,000 kWh floor is DESNZ's operational threshold, not a physical one. A household with a gas
  supply and genuinely tiny use exists and must remain drawable; it simply cannot be counted here.

## Lineage

Same file as the floor-area anchor, so these two rows share a source. That validates neither
against the other, and neither may validate the SIM's consumption — NEED already anchors the
high-tail gas figure, so a check of SIM gas against NEED after fitting to NEED would be a
tautology. Validation needs different lineage.

## The published comparator (2026-10-07, W2_20)

DESNZ, *Subnational electricity and gas consumption statistics, Great Britain, 2023*, section 3.4,
p.25: **"Across Great Britain in 2023, an estimated 16 per cent of domestic properties were not
connected to the gas grid, a similar proportion to 2015."** Regions run from North East 7% to South
West 24%. Inner London is 26% and Outer London 14%.

**How DESNZ counts it:** "the difference between the number of properties and the number of
domestic gas meters in each area". So this figure is **also a meter fact** and the right comparator
for `has_mains_gas_supply`. Inner London at 26% is the same flats effect NEED shows. DESNZ says
it is an **underestimate**: meters under 73,200 kWh/yr are counted as domestic, including small
commercial ones.

That gives a bracket from two sources. DESNZ's 16% is a floor. NEED's raw 19.1% is a ceiling,
because it also counts low users and meters NEED could not match to an address. **The world's
drawn share: 17.0% (n=6,000, seed 42) and 16.3% (n=4,000, seed 20261007)**, both inside it. Held by
`tests/simulation/test_the_mains_gas_marginal_recovers_the_published_off_grid_share.py`. That test
also refuses the heating-inferred share (8.6%), and both mutations are red: folding supply into
heating, and negating the flag.

**Lineage, stated:** DESNZ and NEED both come from the gas meter registers. The bracket shows the
joint has not drifted from the meter data. It is not independent validation.

**What it exposes, and not fixed here:** `heating_system` is still drawn independently of the
supply flag. As a result, **15.3% of drawn homes have an individual gas boiler and no gas supply**.
The heating weights also renormalise over the stock left after dropping oil, LPG and district heat,
so the world draws gas boilers at 90.7%, above the 83% supply share. That means "connection comes
first, then the heating system" cannot hold while both marginals stay where they are. Filed as
`docs/staging/SEAT_FINDING_W2_20_A_SIXTH_OF_DRAWN_GAS_BOILERS_HAVE_NO_GAS_SUPPLY_2026-10-07.md`.
