#!/usr/bin/env python3
"""Generate `site/data/capabilities_door.json` — the feed behind the Capabilities tab.

WHAT THE TAB ANSWERS (brief §4): *how far along is this, really?* The world and the
supplier side by side, each in two columns — **now** and **next** — and honest about what
does not exist yet, because "absence stated plainly is credibility, not weakness". The
2026-08-18 revision added the third section: **the interface inventory**, every seam
between world and supplier, which of them are typed doorways today, and which real
counterparty each swaps to at go-live. The brief calls that the strongest architectural
claim the project has, because **the wall is the go-live seam** — switching a simulated
endpoint for a real one is the launch, not a rewrite.

THE SPLIT THIS MODULE MAKES, AND WHY (the R-A precedent, from the sibling generator
`generate_capabilities_json.py`): **prose is curated, status is derived.**

Every capability below carries hand-written reader-facing prose and a list of the work
items it rests on. The prose is static because it describes what the code does, not a
run-dependent fact. The STATUS is never static: it is computed from those items' actual
recorded levels through `site/moap_stage.compute_stage`, the same Live/Building/Planned
rule the model-on-a-page diagram uses, so this tab cannot claim a maturity the record does
not carry, and it moves on its own when the record moves.

WHY THE PROSE IS CURATED RATHER THAN READ FROM THE RECORD. The work items' own names are
written in this project's internal voice — "point-in-time blindfold at the source", "M2
entry gate", "R5-compliant alerting", "the coupled-triad AGEING dimension". Brief §6.2
forbids that vocabulary on a public page, and §6.7 makes plain English a design constraint
rather than a preference. Rendering the names raw would be the fastest way to build the tab
and would fail the brief on its first line. So each entry is written for a reader who has
never met this project, and the internal id is kept only as the citation that makes the
claim checkable.

FAIL-CLOSED (R15). A capability citing a work item that does not exist RAISES rather than
rendering with a missing status — a phantom citation is the defect `--citations` already
polices in the map, and it must not reach a published page. An empty register, an
unreadable map feed, or an unreadable wall report all raise. There is no degraded mode in
which this writes a plausible page from nothing.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
SITE = PROJECT / "site"
if str(SITE) not in sys.path:
    sys.path.insert(0, str(SITE))
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from moap_stage import BUILDING, LIVE, PLANNED, compute_stage  # noqa: E402

MAP_FEED = SITE / "data" / "maturity_map.json"
INTERFACES = PROJECT / "company" / "interfaces"
OUT_PATH = SITE / "data" / "capabilities_door.json"


class CapabilitySourceUnavailable(RuntimeError):
    """A source this page rests on could not be read. NOT an empty page."""


# ── The curated register ──────────────────────────────────────────────────────
# (reader-facing name, one plain-English line, [work item ids it rests on])
# The ids are the citation. `_status_for` raises if any of them is not in the record.

WORLD: list[tuple[str, str, list[str]]] = [
    ("Weather that behaves like weather",
     "A joint temperature, wind and solar signal that persists the way real weather does — "
     "cold snaps last for days rather than flickering — with regional variation that still "
     "adds up to the national picture.",
     ["W1_3_national_weather_signal", "W1_4_regional_weather_field"]),
    ("Prices that come out of physics, not out of a distribution",
     "Demand is built from weather and buildings; supply is stacked in merit order; the price "
     "is what falls out. Nothing samples a price curve directly.",
     ["W1_6_physics_price_signal"]),
    ("Ten years of real settlement data, revealed in order",
     "Nearly a decade of actual half-hourly GB settlement records, released to the simulation "
     "in the order they happened, so nothing inside can see a day that has not arrived.",
     ["W1_reveal_over_time"]),
    ("Buildings with real thermal behaviour",
     "Each home is modelled as a physical fabric with heat loss and thermal mass, which is why "
     "a cold week shows up differently in a well-insulated flat and a draughty semi.",
     ["W1_11_fabric_physics_core", "W1_12_premise_trace_generator"]),
    ("Households with hidden lives",
     "Income, essential costs, life events — job loss, illness, a new child — and the choice "
     "between paying and heating. All of it hidden from the supplier, as it is in reality.",
     ["W2_4_household_budget", "W2_5_life_event_stream", "W2_7_willingness_classification",
      "W2_8_self_rationing"]),
    ("Business customers that fail like businesses",
     "Sector shocks, insolvency and late payment behaviour that differ from a household's, "
     "because a struggling company does not miss a bill the way a struggling family does.",
     ["W2_6_sme_distress_twin"]),
    ("The price cap as a real constraint",
     "Ofgem's cap binds what can be charged rather than sitting in a lookup table, and it "
     "changes within the year the way the real one does.",
     ["W3_1_price_cap_binding", "W3_1b_intra_year_price_cap_granularity"]),
    ("The industry's own settlement timetable",
     "Volumes are not final on the day. They are trued up over months, on the real schedule.",
     ["W3_2_settlement_timetable"]),
    ("Banking and payment rails",
     "Direct Debit collection modelled end to end — the bank, the acquirer, and the ways a "
     "collection actually fails.",
     ["W5_1_banking_payment_rails"]),
    ("Futures beyond the real record",
     "Worlds that run past the end of the real data, so the supplier can be tested against "
     "conditions that have not happened yet.",
     ["W1_2_generate_futures"]),
]

SUPPLIER: list[tuple[str, str, list[str]]] = [
    ("Bills that add up",
     "Every line — unit rate, standing charge, VAT, the non-commodity costs — computed and "
     "checked to foot, with the arithmetic itself under a control that can fail.",
     ["D1_bill_correctness", "F6_bill_integrity_structural"]),
    ("Estimated bills, and the correction when the read arrives",
     "Bills built on an estimate when no meter read exists, then rebilled against the truth "
     "when it turns up — including when a customer leaves mid-cycle.",
     ["D3_catchup_rebilling"]),
    ("Three clocks kept straight",
     "What happened physically, what was billed, and what was settled are three different "
     "dates, and the supplier reconciles all three per bill rather than pretending they agree.",
     ["D2_three_clocks"]),
    ("Money matched to the right account",
     "A payment arrives against a party, an account and an agreement. Allocating it correctly "
     "— including when the amount is ambiguous — is its own machinery.",
     ["D5_account_hierarchy_payments"]),
    ("Telling can't-pay from won't-pay",
     "The supplier infers, from payment behaviour alone, whether an arrears case is hardship "
     "or choice — and it is allowed to get this wrong, which is the point.",
     ["C9_cantpay_wontpay_classifier", "C7_life_event_detection"]),
    ("Noticing a customer who has stopped heating their home",
     "A perfect payment record with collapsing consumption is a warning sign, not a good "
     "customer. The supplier detects it from the data it can actually see.",
     ["C10_self_rationing_detection"]),
    ("Weather-normalised demand",
     "Working out how much of a change in consumption was the weather and how much was the "
     "customer — an inference, from observations, that can be wrong.",
     ["C13_weather_normalisation"]),
    ("A real set of books",
     "Double-entry ledger, management accounts, and one reconciled definition of revenue used "
     "on every surface that reports it.",
     ["E1_ledger_double_entry", "E2_revenue_reconciliation", "E4_supplier_reporting_standard"]),
    ("Hedging, and the margin it explains",
     "Forward cover bought against the book, and a year-over-year bridge that accounts for "
     "where the margin actually went.",
     ["B1_margin_bridge", "B3_hedge_tariff_alignment"]),
    ("Its own regulatory obligations, tracked",
     "A register of what the licence requires, checked against what the supplier is doing, "
     "with the physical-harm duties treated as the serious ones.",
     ["F3_obligations_register", "F7_obligations_register_coverage"]),
    ("Carbon measured on three ledgers",
     "Customer, portfolio and grid carbon accounted separately — the measurement the whole "
     "premise rests on.",
     ["E5_carbon_three_ledger"]),
    ("A pricing engine",
     "Building a tariff forward from the cost stack — wholesale, losses, network, policy — "
     "rather than inheriting a price.",
     ["EP3_pricing_engine_late_truth"]),
    ("The collections journey, end to end",
     "Missed payment, reminder, dunning ladder, arrangement, and the point where a debt is "
     "handed on.",
     ["EP4_collections_journey"]),
    ("Settlement true-ups on the real timetable",
     "Following a volume from initial settlement through each reconciliation run, and taking "
     "the financial consequence each time it moves.",
     ["EP5_settlement_true_ups"]),
]

# The counterparty each seam swaps to at go-live. Every entry cites the work item that
# holds that adapter, so the claim "we know what this becomes" is checkable rather than
# aspirational — and every one of them is honestly at the bottom of its scale today.
# READINESS, not a flat "Planned" (director, 2026-08-18: "the seams are not equally planned
# -- DUIS has had its real published spec read, the others haven't. Show readiness honestly").
#
# Three independent axes, because they answer different questions and one of them can be
# strong while another is nothing:
#   ACCESS   what it takes to connect AT ALL -- OPEN / SANDBOX / GATED, quoted from
#            docs/design/EP19_COUNTERPARTY_QUALIFICATION_REGISTER.md, whose whole point is
#            that a gated-counterparty list with no denominator cannot say what fraction of
#            the wall is blocked.
#   SPEC     whether the REAL published specification has been read, and cited. `None` means
#            not read, and most of these are None. This is the axis the director noticed.
#   STATUS   the derived Live/Building/Planned, unchanged, which stays Planned for all eight.
#
# `spec` claims are checkable: each names the in-repo record that holds the reading, and
# test_capabilities_door asserts every cited path exists. A citation that rots fails.
GO_LIVE_SEAMS: list[dict] = [
    {"area": "Settlement and market data", "who": "Elexon Insights (BMRS)",
     "what": "Half-hourly settlement, system prices and the balancing mechanism.",
     "access": "OPEN", "gate": "None. Published openly, no qualification of any kind.",
     "spec": None, "ids": ["EP7_adapter_elexon_insights"]},
    {"area": "Smart metering", "who": "DCC (DUIS service requests)",
     "what": "Reading a meter, changing a tariff, operating the supply switch remotely.",
     "access": "GATED", "gate": "Accession to the Smart Energy Code, SMKI certificates, and CIO/UIT testing.",
     "spec": {"what": "DUIS v5.3 (18 Mar 2025, 543 pages) read at clause level, with its XML schema",
              "where": "docs/design/simplifications/EP8_adapter_dcc_duis.yaml"},
     "ids": ["EP8_adapter_dcc_duis"]},
    {"area": "Consented meter access", "who": "n3rgy / DCC Other User",
     "what": "Half-hourly consumption for a customer who has given consent.",
     "access": "SANDBOX", "gate": "Exercisable today through a consented-access provider, without qualifying.",
     "spec": None, "ids": ["EP9_adapter_n3rgy_consented_metering"]},
    {"area": "Gas industry systems", "who": "Xoserve / UK Link (CDSP)",
     "what": "Gas registration, meter points and the reconciliation the UNC requires.",
     "access": "GATED", "gate": "A signed Data Services Contract / UK Link User Agreement; parts need shipper status.",
     "spec": None, "ids": ["EP10_adapter_uk_link_xoserve"]},
    {"area": "Payment collection", "who": "GoCardless (Bacs bureau)",
     "what": "Presenting Direct Debits and receiving the failures back.",
     "access": "SANDBOX", "gate": "A bureau route has a free sandbox; direct Bacs needs a sponsoring bank and a Service User Number.",
     "spec": None, "ids": ["EP11_adapter_gocardless_bacs"]},
    {"area": "Switching", "who": "CSS (electricity) and RGMA/SPAA (gas)",
     "what": "Gaining and losing customers to other suppliers.",
     "access": "GATED", "gate": "Eligibility under the Retail Energy Code, confirmed by its Code Manager.",
     "spec": None, "ids": ["EP12_adapter_css_rec_switching"]},
    {"area": "Carbon intensity", "who": "NESO Carbon Intensity API",
     "what": "The grid's actual carbon content, half-hour by half-hour.",
     "access": "OPEN", "gate": "None. Free, no key.",
     "spec": None, "ids": ["EP13_adapter_carbon_intensity"]},
    {"area": "Published cost stack", "who": "Ofgem and network operator files",
     "what": "Cap levels, network charges and policy costs, ingested as the published files they are.",
     "access": "OPEN", "gate": "None. Published as spreadsheets rather than as an interface.",
     "spec": None, "ids": ["EP14_adapter_published_cost_stack"]},
]

QUALIFICATION_REGISTER = PROJECT / "docs" / "design" / "EP19_COUNTERPARTY_QUALIFICATION_REGISTER.md"

# ── The supplier use-case register ────────────────────────────────────────────
# DIRECTOR_RULING_SUPPLIER_USE_CASE_REGISTER_AND_SIM_FIDELITY_2026-09-06, decision 4:
# publish the register "as 'what a supplier can do with this world', each item carrying its
# SIM-native test and its current status: *testable now / waits on [plain-English condition]*",
# and explicitly "no atom names, no phase labels".
#
# WHAT MAKES THIS DIFFERENT FROM THE TWO REGISTERS ABOVE, and why it needed its own shape.
# `WORLD` and `SUPPLIER` answer "how mature is this thing we built". This one answers a
# question the ruling puts at the centre: **what could a supplier be SCORED on here, and
# against what hidden truth**. So every entry carries `test` — the counterfactual it is
# graded against — because the ruling's §0 is the reason these are worth listing at all:
# "any product built on attribution ... can be scored against hidden truth before it meets
# a real customer".
#
# THE STATUS RULE, AND WHY IT IS PER-TRUTH RATHER THAN PER-ENTRY. A use case is testable
# exactly when every piece of world-truth it is scored against actually exists. So `needs`
# is a list of (plain-English truth, work item) pairs, and the status is derived from the
# items' recorded levels by the SAME rule the rest of this page uses. Naming the truths
# separately is what lets the page say *which* one is missing in the reader's language
# rather than emitting a bare "not yet" — the ruling asked for a plain-English condition,
# and a condition assembled from the items that are actually below target cannot go stale
# the way a hand-written one would. When an item reaches target it drops out of the
# sentence on its own.
#
# A `None` WORK ITEM IS THE HONEST CASE, NOT A PLACEHOLDER. The ruling's §2 found truths
# with no work behind them at all — the prospect pool, the hedging risk envelope. Those
# carry `None`, they are reported separately as `unmodelled`, and they can never satisfy
# the status rule. Writing them as some nearly-related item would be the failure this
# project files as a placeholder that looks like an answer; leaving them out entirely would
# let an item read "testable now" while the truth it is scored against does not exist.
USE_CASES: list[dict] = [
    # ── Gate 1 — pays ────────────────────────────────────────────────────────
    {"gate": "Whether they pay", "ref": "1.1",
     "name": "Debt and cash flow modelled per home",
     "what": "Provisioning built up home by home, with the rules for how a payment clears "
             "against old and new charges made explicit, and a debt trajectory per home so "
             "that beating the forecast is something a manager can actually be measured on.",
     "test": "Does the predicted arrears trajectory match what truly happened, and how fast "
             "and how accurately was hardship told apart from choice?",
     "needs": [
         ("whether a household genuinely cannot pay or is choosing not to",
          "W2_9_segment_debt_tnc"),
         ("how a household's payment behaviour actually arises",
          "W2_11_payment_behaviour_source"),
         ("money matched to the right account and agreement",
          "D5_account_hierarchy_payments"),
         ("the order in which a payment clears old and new charges",
          "W2_31_people_phase1_the_physical_layer_stands_alone"),
     ]},
    {"gate": "Whether they pay", "ref": "1.2",
     "name": "Spotting a household going cold",
     "what": "Consumption falling below what the building's physics says the home needs in "
             "cold weather is not a thrifty customer; it is someone going without heat.",
     "test": "How many are found and how many false alarms — and the false alarm that "
             "matters is an empty house mistaken for a cold occupant.",
     "needs": [
         ("households that go without heat rather than spend", "W2_8_self_rationing"),
         ("the supplier's own attempt to spot it from what it can see",
          "C10_self_rationing_detection"),
     ]},
    {"gate": "Whether they pay", "ref": "1.3",
     "name": "Prepayment offered well rather than imposed",
     "what": "Moving a customer who can pay but will not onto prepayment, screened for "
             "vulnerability first and designed with credit that carries them over a weekend.",
     "test": "Bad debt by meter type, holding payment method and financial stress constant — "
             "and the share of cases the vulnerability screen stops.",
     "needs": [
         ("whether a household is unwilling or unable", "W2_7_willingness_classification"),
         ("one consistent reading of who counts as vulnerable",
          "C32_one_obligation_one_vulnerability_scorer"),
     ]},
    # ── Gate 2 — stays ───────────────────────────────────────────────────────
    {"gate": "Whether they stay", "ref": "2.1",
     "name": "Budget billing from the home's own physics",
     "what": "Forecasts from the building rather than from a national average profile, a "
             "monthly payment that is right from the first month, and a mode where the "
             "customer names the bill they want and is shown the levers that reach it.",
     "test": "Forecast accuracy by house type against the truth, and what accurate, "
             "controllable bills do to bill shock, arrears onset and leaving.",
     "needs": [
         ("how a building actually loses and stores heat", "W1_11_fabric_physics_core"),
         ("cold spells that persist the way real ones do",
          "W1_22_cold_spell_persistence_and_cross_cell_synchrony"),
         ("a first monthly payment sized to a seasonal year",
          "D_opening_dd_seasonal_sizing"),
         ("the cash-flow shape a seasonal bill produces", "DD_seasonal_cashflow_physics"),
         ("whether a household acts on a prompt about its own bill",
          "W2_25_people_phase2_shape_and_attitudes"),
     ]},
    {"gate": "Whether they stay", "ref": "2.2",
     "name": "Not heating an empty house",
     "what": "Reading occupancy from the meter's own signature — base load only, no evening "
             "peak, weekday regularity, gaps that look like holidays — and setting back the "
             "heating automatically, with anything sharper strictly opt-in.",
     "test": "Detection accuracy and false alarms against the truth, never setting back on "
             "inference alone for anyone who might be vulnerable.",
     "needs": [
         ("how many people live in a home and how that shapes its use",
          "W2_13_occupancy_consumption_volume_shape"),
         ("when a home is genuinely occupied, half hour by half hour",
          "W2_25_people_phase2_shape_and_attitudes"),
     ]},
    {"gate": "Whether they stay", "ref": "2.3",
     "name": "The property as the customer, not the occupant",
     "what": "A record of a home's energy physics that outlives whoever lives there: quotes "
             "prepared before anyone applies, sign-up at the meter rather than the person, "
             "and the final bill actually collected when they leave.",
     "test": "Cost to onboard, accuracy of the first monthly payment, final bills collected, "
             "and whether the meter point is retained across a change of occupant.",
     "needs": [
         ("how a building actually loses and stores heat", "W1_11_fabric_physics_core"),
         ("what happens to debt when the occupant changes",
          "W2_12_change_of_tenancy_debt_physics"),
         ("people moving home, and the shocks that come with it",
          "B7_customer_state_layer_moves_and_shocks"),
     ]},
    {"gate": "Whether they stay", "ref": "2.4",
     "name": "Comparison against genuinely similar homes",
     "what": "Similar homes chosen by building physics rather than by postcode, so the "
             "comparison is fair rather than merely local.",
     "test": "The change each nudge produces by segment, measured against what that same "
             "household would have done untouched.",
     "needs": [
         ("how a building actually loses and stores heat", "W1_11_fabric_physics_core"),
         ("how much of a change was the weather and how much the customer",
          "C13_weather_normalisation"),
         ("a cost comparison shaped to the customer rather than averaged",
          "B5_shaped_cost_benchmark_value_add"),
     ]},
    {"gate": "Whether they stay", "ref": "2.5",
     "name": "Targets and streaks on money, carbon and timing",
     "what": "Goals and progress on all four of money, carbon, shifting load and efficiency — "
             "offered to those who want them, and deliberately not regressive, so the free "
             "steps score as richly as the ones that cost thousands.",
     "test": "Behaviour that actually changed against behaviour merely reported differently, "
             "by segment — and whether the saving rebounds later.",
     "needs": [
         ("how often a message can be repeated before it stops working",
          "H23_frame_saturation_draw_marker"),
         ("whether a household responds to a game, and whether the saving rebounds",
          "W2_25_people_phase2_shape_and_attitudes"),
     ]},
    # ── Gate 3 — the margin bet ──────────────────────────────────────────────
    {"gate": "The margin bet", "ref": "3.1",
     "name": "Buying energy against the homes actually supplied",
     "what": "The shape of what the supplier buys forward derived from how its own homes "
             "respond to cold, region by region, instead of from an industry average profile.",
     "test": "Volume risk and shape error measured on a deliberately cold practice book, and "
             "how the position survives a crisis year.",
     "needs": [
         ("regional weather that adds up to the national picture",
          "W1_21_the_cells_and_the_level_coverage_curve"),
         ("cold spells that persist the way real ones do",
          "W1_22_cold_spell_persistence_and_cross_cell_synchrony"),
         ("forward cover measured against what was sold", "B3_hedge_tariff_alignment"),
         ("published forward prices to test the buying against",
          "G15_forward_curve_series_to_backtest_hedging_by_physics"),
     ]},
    {"gate": "The margin bet", "ref": "3.2",
     "name": "Tariffs between fully fixed and fully variable",
     "what": "A fixed price for part of the expected volume, with caps, floors and a "
             "weather-linked element, so stability is sold to those who value it at a price "
             "that reflects what it costs to provide.",
     "test": "What the promise costs in a cold year, across the weather distribution and the "
             "home's own sensitivity to it — and whether customers understood what they bought.",
     "needs": [
         ("the price ceiling and when it binds", "W3_1_price_cap_binding"),
         ("how much a household values a stable bill",
          "W2_25_people_phase2_shape_and_attitudes"),
         ("weather drawn as a distribution rather than replayed",
          "W1_24_weather_phase3_the_drivers_that_wait_on_a_population"),
     ]},
    {"gate": "The margin bet", "ref": "3.3",
     "name": "Automated buying inside a set risk limit",
     "what": "Timing and shaping the energy purchase automatically, and using batteries and "
             "vehicles with permission — always inside a limit set by the board, never as a "
             "speculative position on the book.",
     "test": "Value captured against the limit, with a 2021-style tail survivable by "
             "construction rather than by luck.",
     "needs": [
         ("published forward prices to test the buying against",
          "G15_forward_curve_series_to_backtest_hedging_by_physics"),
         ("a risk limit set by the board, which is the board's alone to set", None),
     ]},
    {"gate": "The margin bet", "ref": "3.4",
     "name": "Running cheaply enough that the saving is the product",
     "what": "Operating at a fraction of the overhead the price ceiling allows for, so that "
             "most of the contribution per account survives to be shared.",
     "test": "Cost per account measured honestly against what the market actually clears at.",
     "needs": [
         ("what it costs this supplier to serve an account", "B2_opex_cost_to_serve"),
         ("how often a household makes contact, and through which channel",
          "W2_25_people_phase2_shape_and_attitudes"),
     ]},
    # ── Gate 4 — value-add ───────────────────────────────────────────────────
    {"gate": "Value beyond the bill", "ref": "4.1",
     "name": "Advice costed for the actual building",
     "what": "Solar, batteries, vehicles, insulation, flow temperature and timing, each "
             "costed from this home's own measured behaviour rather than from a brochure.",
     "test": "Did the promised saving actually arrive — and how much of it was the advice "
             "rather than the household drifting there anyway?",
     "needs": [
         ("how a building actually loses and stores heat", "W1_11_fabric_physics_core"),
         ("homes changing on their own, with no prompting",
          "W2_24_housing_phase3_houses_change_on_their_own_timeline"),
         ("whether a household acts on advice it is given",
          "W2_26_people_phase3_the_residual_and_the_change"),
     ]},
    {"gate": "Value beyond the bill", "ref": "4.2",
     "name": "Taking a share of what is actually saved",
     "what": "Payment as a share of the saving, measured against the home's own physics "
             "baseline. The mission's create-then-share, sold as a contract — and credible "
             "only once the baseline method has been proved against hidden truth.",
     "test": "The error distribution of the baseline itself, and whether value was created "
             "before it was divided.",
     "needs": [
         ("how much of a change was the weather and how much the customer",
          "C13_weather_normalisation"),
         ("how a building actually loses and stores heat", "W1_11_fabric_physics_core"),
         ("whether a household acts on advice it is given",
          "W2_26_people_phase3_the_residual_and_the_change"),
     ]},
    {"gate": "Value beyond the bill", "ref": "4.3",
     "name": "Diagnosing the building from the meter",
     "what": "A change in how much energy a home needs per degree of cold is a boiler "
             "degrading, insulation failing, or a thermostat being fought over.",
     "test": "Detection against the true timeline of what changed in the house and when.",
     "needs": [
         ("the gap between what the supplier believes about a building and its truth",
          "H_GAP_fabric_belief_truth_gap"),
         ("homes changing on their own, with no prompting",
          "W2_24_housing_phase3_houses_change_on_their_own_timeline"),
     ]},
    {"gate": "Value beyond the bill", "ref": "4.4",
     "name": "Flexibility, with permission",
     "what": "Controlling vehicles, batteries and heat pumps where the customer has agreed, "
             "and sharing the revenue that flexibility earns.",
     "test": "Value captured per class of asset, and how many customers consent — noting "
             "that solar alone stays uneconomic unless paired.",
     "needs": [
         ("markets that pay for shifting load", "W1_9_dsr_flex_markets"),
         ("where vehicles and heat pumps actually are", "W1_10_ev_heatpump_geography"),
         ("a consented route to a customer's own meter",
          "EP9_adapter_n3rgy_consented_metering"),
         ("whether a household will let its heating be controlled",
          "W2_25_people_phase2_shape_and_attitudes"),
     ]},
    {"gate": "Value beyond the bill", "ref": "4.5",
     "name": "A bill split into what each thing cost",
     "what": "Heating, hot water, the car and everything else separated out, the way a bank "
             "app separates spending.",
     "test": "Accuracy of the split against the true consumption of each asset.",
     "needs": [
         ("consumption broken down by what used it, not just the total",
          "W2_18_the_housing_joint_the_sample_and_the_ceiling"),
         ("the same breakdown on the people side rather than a total",
          "W2_31_people_phase1_the_physical_layer_stands_alone"),
     ]},
    {"gate": "Value beyond the bill", "ref": "4.6",
     "name": "Carbon as a product beside the money",
     "what": "Each home's carbon measured against what the grid was actually emitting half "
             "hour by half hour, a carbon budget beside the money one, and shifting use into "
             "the cleaner hours.",
     "test": "Carbon actually saved against what that household would have emitted anyway, "
             "and how much use genuinely moved.",
     "needs": [
         ("carbon kept on three separate ledgers", "E5_carbon_three_ledger"),
         ("a live route to what the grid is emitting", "EP13_adapter_carbon_intensity"),
         ("ten years of what the grid emitted, lined up with the settlement record",
          "G14_half_hourly_grid_carbon_intensity_aligned_to_settlement"),
     ]},
    {"gate": "Value beyond the bill", "ref": "4.7",
     "name": "Knowing what a customer is worth before bidding for them",
     "what": "Worth estimated from what is legitimately observable at a quote — the area, the "
             "building, the payment method, the meter — so that acquisition is bid by expected "
             "value; and each question ranked by how much the answer sharpens the estimate, "
             "so 'advice for three answers' is a designed exchange rather than a form.",
     "test": "The estimate at the quote against what the customer truly turned out to be worth.",
     "needs": [
         ("what a customer is worth over three horizons", "EP1_clv_three_horizon"),
         ("which channel a customer actually arrived through",
          "C12_channel_attribution_analytics"),
         ("a pool of prospective homes that are not yet customers", None),
         ("how a household behaves at the point of quoting",
          "W2_25_people_phase2_shape_and_attitudes"),
     ]},
]


def _levels(feed: Path = MAP_FEED) -> dict[str, dict]:
    try:
        payload = json.loads(feed.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise CapabilitySourceUnavailable(f"map feed unreadable: {e}") from e
    atoms = payload.get("atoms")
    if not atoms:
        raise CapabilitySourceUnavailable("map feed carries no work items")
    return {a["id"]: a for a in atoms if a.get("id")}


def _status_for(ids: list[str], levels: dict[str, dict]) -> str:
    """Live / Building / Planned, computed from the cited items' recorded levels.

    Raises on a citation that resolves to nothing: a published page asserting the maturity
    of a work item that does not exist is the phantom-citation defect, and it is worse here
    than in the map because a reader cannot check it.
    """
    missing = [i for i in ids if i not in levels]
    if missing:
        raise CapabilitySourceUnavailable(
            f"capability cites work item(s) absent from the record: {missing}"
        )
    # `compute_stage` takes {current, target} — its own vocabulary, not the feed's field
    # names. Mapped here rather than renamed there: that function is the shared derivation
    # the diagram and the coherence gate both call, and this tab does not get to reshape it.
    return compute_stage([
        {"current": levels[i]["level_current"], "target": levels[i]["level_target"]}
        for i in ids
    ])


def _entries(register, levels, index: dict[str, str] | None = None,
             evidence: dict | None = None) -> list[dict]:
    index, evidence = index or {}, evidence or {}
    out = []
    for name, blurb, ids in register:
        out.append({
            "name": name, "what": blurb, "status": _status_for(ids, levels), "rests_on": ids,
            "evidence": _evidence_for(ids, index),
            "checks": _checks_for(ids, evidence),
        })
    return out


TESTABLE_NOW = "Testable now"


def use_case_entry(case: dict, levels: dict[str, dict]) -> dict:
    """One register row, with its status DERIVED from the truths it is scored against.

    The rule, and it is the whole point of the row: a use case is testable exactly when
    every piece of world-truth its SIM-native test needs is AT TARGET. `compute_stage` is
    called per truth rather than once over the list because the reader is owed the specific
    condition, not a bare verdict -- and asking it per item means this page keeps using the
    shared Live/Building/Planned rule rather than growing a second opinion about what
    "finished" means.

    Fail-closed, twice over:
      * a truth citing a work item absent from the record RAISES (the phantom citation
        `_status_for` already refuses -- a register that cannot be checked is worse than no
        register, because a reader has no way to catch it);
      * a truth carrying NO work item can never be at target, so it can only ever hold an
        item back. That is deliberate: the ruling found truths with nothing behind them at
        all, and the failure mode to design out is an item reading "testable now" while the
        hidden truth it claims to be scored against does not exist.
    """
    missing = [wid for _, wid in case["needs"] if wid and wid not in levels]
    if missing:
        raise CapabilitySourceUnavailable(
            f"use case {case['ref']} is scored against work item(s) absent from the "
            f"record: {missing}"
        )
    waiting, unmodelled = [], []
    for truth, wid in case["needs"]:
        if wid is None:
            unmodelled.append(truth)
        elif _status_for([wid], levels) != LIVE:
            waiting.append(truth)
    blocking = unmodelled + waiting
    return {
        "gate": case["gate"], "ref": case["ref"], "name": case["name"],
        "what": case["what"], "test": case["test"],
        "testable_now": not blocking,
        "status": TESTABLE_NOW if not blocking else "Waits on " + _condition(blocking),
        "waits_on": waiting,
        "unmodelled": unmodelled,
        "rests_on": [wid for _, wid in case["needs"] if wid],
        "needs_total": len(case["needs"]),
        "needs_met": len(case["needs"]) - len(blocking),
    }


def _condition(blocking: list[str]) -> str:
    """The plain-English condition the ruling asked for, assembled from the truths that are
    actually missing. Never a stored sentence: a hand-written condition would still read
    "waits on the carbon data" the day after the carbon data landed."""
    if len(blocking) == 1:
        return blocking[0]
    return ", ".join(blocking[:-1]) + " and " + blocking[-1]


def use_case_register(levels: dict[str, dict]) -> dict:
    rows = [use_case_entry(c, levels) for c in USE_CASES]
    gates: list[dict] = []
    for row in rows:
        if not gates or gates[-1]["gate"] != row["gate"]:
            gates.append({"gate": row["gate"], "items": []})
        gates[-1]["items"].append(row)
    return {
        "entries": rows,
        "gates": gates,
        "tally": {
            "testable_now": sum(1 for r in rows if r["testable_now"]),
            "waiting": sum(1 for r in rows if not r["testable_now"]),
            "unmodelled_truths": len({t for r in rows for t in r["unmodelled"]}),
        },
    }


def typed_seams(interfaces: Path = INTERFACES) -> list[dict]:
    """The seams that already exist as typed doorways, read from their own docstrings.

    Derived, never listed here: a hand-kept inventory of seams would be wrong the first
    time one was added. A module whose docstring opens `Seam:` is declaring itself one.
    """
    import ast

    if not interfaces.is_dir():
        raise CapabilitySourceUnavailable(f"no interfaces directory at {interfaces}")
    seams = []
    for path in sorted(interfaces.glob("*.py")):
        if path.name == "__init__.py":
            continue
        try:
            doc = ast.get_docstring(ast.parse(path.read_text(encoding="utf-8"))) or ""
        except (OSError, SyntaxError):
            continue
        first = " ".join(doc.split("\n\n")[0].split())
        if not first:
            continue
        seams.append({"module": path.stem, "describes": first[:220]})
    if not seams:
        raise CapabilitySourceUnavailable("no typed seams found — the walk returned nothing")
    return seams


def wall_position() -> dict:
    """The wall's own measured position, from the register that already polices it."""
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "tools.wall_crossing_dispositions", "--json"],
            cwd=str(PROJECT), capture_output=True, text=True, timeout=180,
        )
        report = json.loads(proc.stdout)
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        raise CapabilitySourceUnavailable(f"wall report unavailable: {e}") from e
    for key in ("measured_crossings", "rows", "unexamined"):
        if key not in report:
            raise CapabilitySourceUnavailable(f"wall report missing {key!r}")
    return {
        "live_crossings": report["measured_crossings"],
        "direct": report.get("direct_crossings"),
        "indirect": report.get("indirect_crossings"),
        "examined": report["rows"],
        "cut": (report.get("by_disposition") or {}).get("cut"),
        "owed": (report.get("by_disposition") or {}).get("owed"),
        "unexamined": report["unexamined"],
    }


def evidence_index(mapping: Path = SITE / "data" / "moap_node_atoms.json") -> dict[str, str]:
    """work item id -> the evidence page anchor that carries its record.

    Director, 2026-08-18: "the page says its states are computed, not typed; a sceptic
    should be able to get from 'Bills that add up' to the thing that proves it in one click."
    The evidence page already renders, per architecture node, the cited artefacts, the tests
    and the level record for every work item under it. This reverses that mapping so a
    capability can link straight to the node that holds its proof. Derived from the same file
    the diagram uses; a capability whose work is under no node simply gets no link, rather
    than a link that goes somewhere plausible and wrong.
    """
    try:
        payload = json.loads(mapping.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise CapabilitySourceUnavailable(f"node mapping unreadable: {e}") from e
    nodes = payload.get("nodes") or []
    if not nodes:
        raise CapabilitySourceUnavailable("node mapping carries no nodes")
    out: dict[str, str] = {}
    for node in nodes:
        for wid in node.get("atoms") or []:
            out.setdefault(wid, node["id"])
    return out


# THE LINKS ARE OFF, AND THIS IS THE DECISION (director, 2026-08-18: "the evidence links land
# a reader in the machine's own vocabulary ... how and when is yours, including deciding this
# shouldn't ship until Evidence is rewritten"). They are off.
#
# The destination renders a raw work-item id, a maturity level, a lane name, a loop stage and
# repo file paths -- every one of them on section 6.2's forbidden list, reached FROM a public
# tab. The link satisfied the letter of "route to evidence" and broke the rule the brief rests
# on, and it did something worse than fail: it told a reader, in one click, that they are not
# the audience. A dead link teaches distrust; this taught exclusion.
#
# What ships instead is JUSTIFICATION IN PLAIN WORDS, on the claim itself: how many
# independent automated checks stand behind it and when they last ran. That is what a sceptic
# actually asks -- "how do you know?" -- answered without teaching anyone a vocabulary. The
# readable record is minted as SITE12_evidence_a_reader_can_use and the links come back when
# it lands, pointing at something written for the person reading it.
_EVIDENCE_LINKS_SHIP = False


def _evidence_for(ids: list[str], index: dict[str, str]) -> str | None:
    """Deliberately None until the evidence surface is written for a reader (SITE12).

    Kept as a function rather than deleted so the decision is one flag with its reasoning
    beside it, and so the control that asserts every emitted link resolves stays live for the
    day they return.
    """
    if not _EVIDENCE_LINKS_SHIP:
        return None
    for wid in ids:
        if wid in index:
            return f"../evidence/#w-{wid}"
    return None


def _checks_for(ids: list[str], evidence: dict) -> dict | None:
    """How many independent automated checks stand behind a claim, and when they last ran.

    Derived from the published evidence data -- the same source the machine-facing page uses,
    read for the one number a reader wants rather than rendered as a record. None where the
    work is not covered by that data at all, which is itself said on the page.
    """
    # `test_files` and `test_functions` are COUNTS in this feed, not lists. Summing them over
    # the cited work items is right for functions and an over-count for files where two items
    # share a file, so only the function count is published -- an inflated file count on a page
    # about honesty would be a poor place to be sloppy.
    seen, funcs = set(), 0
    for node in evidence.get("nodes") or []:
        for atom in node.get("atoms") or []:
            aid = atom.get("id")
            if aid in ids and aid not in seen:
                seen.add(aid)
                value = atom.get("test_functions")
                funcs += value if isinstance(value, int) else 0
    if not seen or not funcs:
        return None
    return {"checks": funcs, "covered": len(seen), "of": len(ids),
            "last_run": (evidence.get("suite") or {}).get("timestamp")}


def scale(customers: Path = SITE / "data" / "customers.json",
          dashboard: Path = SITE / "data" / "dashboard.json") -> dict:
    """How big the book is — the gap the Live/Planned columns cannot show.

    Director, 2026-08-18: "The book is twenty customers and the page never says so. Nineteen
    items marked Live read as near-complete while scale — the biggest honest gap — is
    invisible."

    THIS FUNCTION DOES NOT PICK A NUMBER WHEN ITS SOURCES DISAGREE, and today they do: the
    live customer feed says one thing and the break-even analysis another. Publishing one and
    dropping the other would be exactly the figure-reconciliation defect a prior review
    already found on this site (two bad-debt figures, 129x apart, feeding the same doors with
    no bridge). Both are published, with their sources, and the disagreement is stated as the
    open gap it is. Fail-closed: no readable source raises rather than omitting scale, since a
    page that quietly stops mentioning its size is the failure this section exists to prevent.
    """
    figures = []
    try:
        c = json.loads(customers.read_text(encoding="utf-8"))
        if isinstance(c.get("customer_count"), int):
            figures.append({"value": c["customer_count"], "basis": "accounts in the live customer feed",
                            "source": "site/data/customers.json", "as_of": c.get("generated")})
    except (OSError, ValueError):
        pass
    try:
        d = json.loads(dashboard.read_text(encoding="utf-8"))
        n = ((d.get("b2_taxonomy") or {}).get("break_even_analysis") or {}).get("current_book_size")
        if isinstance(n, int):
            figures.append({"value": n, "basis": "book size used by the break-even analysis",
                            "source": "site/data/dashboard.json", "as_of": (d.get("build") or {}).get("simulation_window")})
    except (OSError, ValueError):
        pass
    if not figures:
        raise CapabilitySourceUnavailable("no readable source for the size of the book")
    values = sorted({f["value"] for f in figures})
    return {
        "figures": figures,
        "agree": len(values) == 1,
        "low": values[0], "high": values[-1],
        "real_world": "A real GB supplier serves hundreds of thousands to millions of homes.",
    }


def _git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(PROJECT),
                             capture_output=True, text=True, timeout=30)
        return (out.stdout or "").strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


# EVERY GAP NAMES THE WORK THAT CLOSES IT (director, 2026-08-18: "a gap with no plan beside
# it is a confession; a gap with a plan is a roadmap ... if something is missing and genuinely
# isn't on the plan, that's the finding -- put it on the plan").
#
# The plan status is DERIVED from those items' own records, never written here: whether work
# exists, whether it is drawable now or waiting, and what it is waiting on. What is NOT
# derived is a date, and that is deliberate rather than lazy -- this project's own law says
# dates are forecasts and the exit test is the only gate, so a date on this page would be the
# one number a reader would take as a promise. "What it is waiting on" is the honest answer to
# "when", and it is checkable.
GAP_PLAN: dict[str, list[str]] = {
    "book": ["PB3_book_growth_as_earned_outcome"],
    "counterparties": ["EP19_counterparty_qualification_paths", "EP20_go_live_cutover_analysis"],
    "unproven": ["SITE12_evidence_a_reader_can_use"],
    "fidelity": ["G1_fidelity_grid_scorer", "G2_fidelity_evidence_ledger",
                 "G3_fidelity_inspection_chain"],
}


def plan_for(ids: list[str], levels: dict[str, dict]) -> dict:
    """What the record says about the work that closes a gap: is it planned, is it drawable,
    what is it waiting on. Fail-closed -- an id that resolves to nothing raises, because a gap
    claiming a plan that does not exist is worse than a gap admitting it has none."""
    missing = [i for i in ids if i not in levels]
    if missing:
        raise CapabilitySourceUnavailable(
            f"a gap cites work that is not in the record: {missing} -- put it on the plan or "
            "stop claiming it is planned"
        )
    items = [levels[i] for i in ids]
    started = [i for i in items if i["level_current"] > 0]
    drawable = [i for i in items if i.get("loop_stage") in ("build", "harden")]
    waiting_on: list[str] = []
    for item in items:
        for dep in item.get("depends_on") or []:
            if dep in levels and levels[dep]["level_current"] < levels[dep]["level_target"]:
                waiting_on.append(dep)
    if drawable:
        when = "being worked on now"
    elif waiting_on:
        when = "waiting on earlier work to finish first"
    else:
        when = "planned and queued, not started"
    return {
        "planned": True, "items": len(items), "started": len(started),
        "drawable_now": bool(drawable), "when": when,
        "waiting_on_count": len(set(waiting_on)),
    }


def gaps(world: list[dict], supplier: list[dict], seams: list[dict], book: dict,
         levels: dict[str, dict]) -> list[dict]:
    """The gaps the two columns above CANNOT show — never a re-list of what they already do.

    Director, 2026-08-18: the section "is a verbatim re-list of the supplier's four Next
    items, and it omits the world's own gap (the price cap) — so the section that promises to
    state gaps plainly is both duplicative and incomplete."

    Both halves of that are fixed by changing what the section is FOR. It no longer filters
    the entries by status (which is what made it a copy, and what made its filter arbitrary
    enough to drop a Building item). It carries the things no capability row can express:
    how small the book is, what is half-built rather than absent, and the fact that nothing
    here has ever met a real counterparty. Each is derived, so the section cannot go stale
    while the columns move.
    """
    out: list[dict] = []

    size = f"{book['low']}" if book["agree"] else f"{book['low']}–{book['high']}"
    out.append({
        "plan": plan_for(GAP_PLAN["book"], levels),
        "title": f"The book is {size} customers",
        "what": (
            f"Everything on this page is true of a supplier with {size} accounts. "
            + book["real_world"]
            + " Scale is the largest single gap between this and a real energy retailer, and "
            "nothing above will tell you that, because every item can be genuinely built at "
            "this size."
            + ("" if book["agree"] else
               " The project's own feeds do not currently agree on the exact figure — "
               + ", ".join(f"{f['value']} ({f['basis']})" for f in book["figures"])
               + " — and that disagreement is itself unreconciled.")
        ),
    })

    part_built = [e for e in world + supplier if e["status"] == BUILDING]
    if part_built:
        out.append({
            # The plan for a part-built capability is the capability itself: it is on the map,
            # it has a target above where it sits, and that is what "next" in the column means.
            "plan": {"planned": True, "items": len(part_built), "started": len(part_built),
                     "drawable_now": True, "when": "being worked on now", "waiting_on_count": 0},
            "title": "Half-built, not absent",
            "what": ("Listed above as coming next, which understates it: these exist and work "
                     "in part, and are not finished. " +
                     "; ".join(f"{e['name']} — {e['what'][:90].rstrip('. ')}" for e in part_built) + "."),
        })

    if not any(s["status"] == LIVE for s in seams):
        read = [s for s in seams if s.get("spec")]
        out.append({
            "plan": plan_for(GAP_PLAN["counterparties"], levels),
            "title": "Nothing here has ever spoken to a real counterparty",
            "what": (
                f"All {len(seams)} connections to the real industry are unbuilt, so every figure "
                "on this site comes from a simulated world. "
                + (f"One specification has been read in earnest ({read[0]['counterparty']}); "
                   f"the rest rest on secondary research that says to verify it before building."
                   if read else "None of their specifications has been read in earnest yet.")
            ),
        })

    unproven = [e for e in world + supplier if e["status"] == LIVE and not e["evidence"]]
    if unproven:
        built = [e for e in world + supplier if e["status"] == LIVE]
        out.append({
            "plan": plan_for(GAP_PLAN["unproven"], levels),
            "title": "No claim on this page yet links to a record a reader could use",
            "what": (
                "Every item marked as built should be traceable to what makes it so. The "
                "records exist, and they are written for whoever maintains this project -- "
                "internal identifiers, maturity levels, file paths -- so sending a reader to "
                f"them would satisfy the letter of the request and teach nothing. {len(unproven)} "
                f"of {len(built)} built capabilities have no published record at all, because "
                "the evidence pages are generated from the architecture diagram and it covers a "
                "fraction of the work. Rather than link to the machine's own notes, each claim "
                "below states in plain words what checks it. A record written for a reader is "
                "on the plan and is the next thing built here."
            ),
        })

    out.append({
        "plan": plan_for(GAP_PLAN["fidelity"], levels),
        "title": "This page cannot tell you whether the simulation is right",
        "what": ("It reports what has been built and how far, not whether the world it models "
                 "behaves like the real one. That is a different question, it is measured "
                 "elsewhere in this project against real market history, and the measurement "
                 "publishes its own worst failures. A capability list is the wrong place to "
                 "answer it -- but it is answered."),
    })
    return out


def build(feed: Path = MAP_FEED) -> dict:
    levels = _levels(feed)
    index = evidence_index()
    try:
        evidence = json.loads((SITE / "data" / "evidence.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise CapabilitySourceUnavailable(f"evidence data unreadable: {e}") from e
    world = _entries(WORLD, levels, index, evidence)
    supplier = _entries(SUPPLIER, levels, index, evidence)
    seams = [
        {"area": s["area"], "counterparty": s["who"], "what": s["what"],
         "access": s["access"], "gate": s["gate"], "spec": s["spec"],
         "status": _status_for(s["ids"], levels), "rests_on": s["ids"],
         "evidence": _evidence_for(s["ids"], index)}
        for s in GO_LIVE_SEAMS
    ]
    book = scale()

    def tally(rows):
        return {s: sum(1 for r in rows if r["status"] == s) for s in (LIVE, BUILDING, PLANNED)}

    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_commit": _git_commit(),
        "sources": {
            "record": "site/data/maturity_map.json",
            "status_rule": "site/moap_stage.py (Live / Building / Planned)",
            "seams": "company/interfaces/*.py docstrings",
            "wall": "tools/wall_crossing_dispositions.py",
            "access_class": "docs/design/EP19_COUNTERPARTY_QUALIFICATION_REGISTER.md",
            "use_case_register": (
                "docs/staging/done/DIRECTOR_RULING_SUPPLIER_USE_CASE_REGISTER_AND_SIM_"
                "FIDELITY_2026-09-06.md"
            ),
            "evidence_map": "site/data/moap_node_atoms.json",
            "scale": "site/data/customers.json + site/data/dashboard.json",
        },
        "world": {"entries": world, "tally": tally(world)},
        "supplier": {"entries": supplier, "tally": tally(supplier)},
        "use_cases": use_case_register(levels),
        "go_live": {"seams": seams, "tally": tally(seams),
                    "access_tally": {a: sum(1 for s in seams if s["access"] == a)
                                     for a in ("OPEN", "SANDBOX", "GATED")}},
        "typed_seams": typed_seams(),
        "wall": wall_position(),
        "scale": book,
        "gaps": gaps(world, supplier, seams, book, levels),
    }


def generate(out: Path = OUT_PATH, feed: Path = MAP_FEED) -> dict:
    payload = build(feed)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":  # pragma: no cover - operator convenience
    p = generate()
    print(f"wrote {OUT_PATH.relative_to(PROJECT)}: "
          f"{len(p['world']['entries'])} world, {len(p['supplier']['entries'])} supplier, "
          f"{len(p['go_live']['seams'])} go-live seams, {len(p['typed_seams'])} typed seams, "
          f"{p['wall']['live_crossings']} live crossings")
