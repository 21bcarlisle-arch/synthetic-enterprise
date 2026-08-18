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


def _entries(register, levels, index: dict[str, str] | None = None) -> list[dict]:
    index = index or {}
    out = []
    for name, blurb, ids in register:
        out.append({
            "name": name, "what": blurb, "status": _status_for(ids, levels), "rests_on": ids,
            "evidence": _evidence_for(ids, index),
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


def _evidence_for(ids: list[str], index: dict[str, str]) -> str | None:
    """The per-work-item anchor on the evidence page, or None.

    None is a real answer and is rendered as one. The evidence page derives from the
    architecture diagram's node mapping, which covers 46 of the record's 314 work items, so
    a capability resting on work that is on no node has NOTHING PUBLISHED that proves it.
    Linking such a capability to the evidence page's front would be a link that looks like
    proof and is not, which is the defect a prior review already found on this site (ten
    citations styled as live links, pointing at a 404).
    """
    for wid in ids:
        if wid in index:
            return f"../evidence/#w-{wid}"
    return None


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


def gaps(world: list[dict], supplier: list[dict], seams: list[dict], book: dict) -> list[dict]:
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
            "title": "Half-built, not absent",
            "what": ("Listed above as coming next, which understates it: these exist and work "
                     "in part, and are not finished. " +
                     "; ".join(f"{e['name']} — {e['what'][:90].rstrip('. ')}" for e in part_built) + "."),
        })

    if not any(s["status"] == LIVE for s in seams):
        read = [s for s in seams if s.get("spec")]
        out.append({
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
            "title": f"{len(unproven)} of {len(built)} built capabilities have nothing published that proves them",
            "what": (
                "Every item marked as built above should link to the record that makes it so. "
                f"{len(unproven)} do not, because the evidence pages are generated from the "
                "architecture diagram, and the diagram covers a fraction of the work: "
                + ", ".join(e["name"] for e in unproven)
                + ". Their records exist in the project's own files; they are not published. "
                "Said here rather than hidden by pointing the links somewhere plausible."
            ),
        })

    out.append({
        "title": "This page cannot tell you whether the simulation is right",
        "what": ("It reports what has been built and how far, not whether the world it models "
                 "behaves like the real one. That is a different question with its own evidence, "
                 "and a capability list is the wrong place to answer it."),
    })
    return out


def build(feed: Path = MAP_FEED) -> dict:
    levels = _levels(feed)
    index = evidence_index()
    world, supplier = _entries(WORLD, levels, index), _entries(SUPPLIER, levels, index)
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
            "evidence_map": "site/data/moap_node_atoms.json",
            "scale": "site/data/customers.json + site/data/dashboard.json",
        },
        "world": {"entries": world, "tally": tally(world)},
        "supplier": {"entries": supplier, "tally": tally(supplier)},
        "go_live": {"seams": seams, "tally": tally(seams),
                    "access_tally": {a: sum(1 for s in seams if s["access"] == a)
                                     for a in ("OPEN", "SANDBOX", "GATED")}},
        "typed_seams": typed_seams(),
        "wall": wall_position(),
        "scale": book,
        "gaps": gaps(world, supplier, seams, book),
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
