**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** W2_18_the_housing_joint_the_sample_and_the_ceiling

**Knowledge:** none -- the housing knowledge page is deliverable 4 of the housing ruling and is not
yet written. This is the gap measurement that has to exist before it can say anything true; it will
be cited by that page and this declaration replaced when the page lands.

# The housing joint, phase 1: what the premise draw already carries, and the four things it does not

**Measured 2026-09-05**, delivery seat, as the first step of `W2_18` under the director's stage-1
sequencing. Every figure below came from drawing a population and reading the objects, not from
reading the ruling's own account of the gaps.

---

## Why this was measured before anything was built

The housing ruling opens by saying the existing premise draw "stands" and names the gaps it wants
closed. That account is the advisor's, and CLAUDE.md's rule is that a closed atom's ground gets
opened before it is built on — which is exactly what nearly cost us a duplicate change-of-tenancy
build this morning.

`python3 tools/closed_atom_delivery.py --prior-art <ground>` on the housing subjects returns
substantial prior art, and all of it is live:

| Closed atom | Verdict | Reaches |
|---|---|---|
| `W1_11_fabric_physics_core` | DELIVERED | `simulation/fabric_physics.py`, `fabric_demand_path.py` — imported |
| `W2_2_population_draw` | DELIVERED | `simulation/population_draw.py` — imported |
| `C14_thermal_parameter_inference` | DELIVERED | `simulation/premise_population.py` — imported |
| `W1_12_premise_trace_generator` | DELIVERED | `simulation/premise_trace.py` — imported |
| EPC register | *no closed atom names it* | **new ground** |

So phase 1 EXTENDS four live modules and opens one genuinely new source. Anything here that forks a
parallel premise generator is the defect, not the deliverable.

## What a drawn premise carries today

`draw_population()` returns `SyntheticCustomer`, whose `premise` is a `DrawnPremise` of five fields
— `premise_id`, `epc_band`, `epc_lodged`, `meter_cadence_days`, and a `household`. That `Household`
carries twenty:

    battery_kwh, bedrooms, boiler_age, build_era, customer_id, epc_rating, ev_charger_kw,
    has_battery, has_driveway, has_ev, has_smart_meter, has_solar, heating_system, income_stress,
    insulation, property_type, roof_aspect, smart_meter_install_year, solar_install_year, solar_kwp

And `fabric_physics` already computes, per premise, `heat_loss_coefficient_kw_per_k` and
`mass_time_constant_hours` — so **fabric heat loss and thermal mass, two of the ruling's §3.1 list,
are built and live.** Off-street parking (`has_driveway`) and roof orientation (`roof_aspect`) are
there too.

## The four things it does not carry

Checked against the drawn record itself, not against mention counts — a grep for a name is blind to
whether the thing is an attribute, and counting mentions is how three separate measurements went
wrong earlier today:

| §3.1 quantity | On the drawn record? | Note |
|---|---|---|
| **Floor area** | **No** | The ruling's own gap: it rests on an unpublished bedrooms table. `bedrooms` is drawn; area is not derived from it. The EPC register is the anchor named for closing this. |
| **Roof area, pitch, flat-vs-house** | **No** | Only `roof_aspect` (orientation) exists. The ruling expects roof geometry beyond flat-vs-house and orientation to be a REGISTERED GAP rather than a number, so this is where that entry goes. |
| **Mains gas / off-gas** | **No** | No field on either record. "Heating system and fuel including no mains gas" needs the fuel to be drawn, not inferred from the heating system. |
| **Current settings** | **No** | Flow temperature, heating and hot-water schedules, thermostat set-point. `flow_temp` has **zero occurrences in the whole `simulation/` tree.** |

The last is the one worth flagging to the director: §2.5 makes current settings hidden state
("the free-and-easy rungs' potential depends entirely on where the house is now"), and §2.3 makes
flow-temperature turn-down one of the seven phase-1 levers. Both rest on an attribute that does not
exist anywhere yet, so the ceiling on that lever is currently unstateable rather than merely
uncomputed.

## What this fixes about the ruling's own gap list

The ruling names bungalows-folded-into-detached and the EPC model-versus-metered gap as open. Those
are not re-measured here and stay open on the ruling's word. What this measurement adds is that
**two of the quantities it lists as needed are already built** (fabric heat loss, thermal mass) and
one it does not emphasise — current settings — is the emptiest of the four, with no representation
of any kind.

## What comes next

Floor area from the EPC register, because it is the anchor the ruling names, it is new ground with
no prior art to reconcile, and three of the other gaps are cheaper once a real area exists.
