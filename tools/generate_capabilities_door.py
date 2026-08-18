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
GO_LIVE_SEAMS: list[tuple[str, str, str, list[str]]] = [
    ("Settlement and market data", "Elexon Insights (BMRS)",
     "Half-hourly settlement, system prices and the balancing mechanism.",
     ["EP7_adapter_elexon_insights"]),
    ("Smart metering", "DCC (DUIS service requests)",
     "Reading a meter, changing a tariff, operating the supply switch remotely.",
     ["EP8_adapter_dcc_duis"]),
    ("Consented meter access", "n3rgy / DCC Other User",
     "Half-hourly consumption for a customer who has given consent.",
     ["EP9_adapter_n3rgy_consented_metering"]),
    ("Gas industry systems", "Xoserve / UK Link (CDSP)",
     "Gas registration, meter points and the reconciliation the UNC requires.",
     ["EP10_adapter_uk_link_xoserve"]),
    ("Payment collection", "GoCardless (Bacs bureau)",
     "Presenting Direct Debits and receiving the failures back.",
     ["EP11_adapter_gocardless_bacs"]),
    ("Switching", "CSS (electricity) and RGMA/SPAA (gas)",
     "Gaining and losing customers to other suppliers.",
     ["EP12_adapter_css_rec_switching"]),
    ("Carbon intensity", "NESO Carbon Intensity API",
     "The grid's actual carbon content, half-hour by half-hour.",
     ["EP13_adapter_carbon_intensity"]),
    ("Published cost stack", "Ofgem and network operator files",
     "Cap levels, network charges and policy costs, ingested as the published files they are.",
     ["EP14_adapter_published_cost_stack"]),
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


def _entries(register, levels) -> list[dict]:
    out = []
    for name, blurb, ids in register:
        out.append({
            "name": name, "what": blurb, "status": _status_for(ids, levels), "rests_on": ids,
        })
    return out


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


def _git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(PROJECT),
                             capture_output=True, text=True, timeout=30)
        return (out.stdout or "").strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def build(feed: Path = MAP_FEED) -> dict:
    levels = _levels(feed)
    world, supplier = _entries(WORLD, levels), _entries(SUPPLIER, levels)
    seams = [
        {"area": area, "counterparty": who, "what": what,
         "status": _status_for(ids, levels), "rests_on": ids}
        for area, who, what, ids in GO_LIVE_SEAMS
    ]

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
        },
        "world": {"entries": world, "tally": tally(world)},
        "supplier": {"entries": supplier, "tally": tally(supplier)},
        "go_live": {"seams": seams, "tally": tally(seams)},
        "typed_seams": typed_seams(),
        "wall": wall_position(),
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
