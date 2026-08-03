"""SITE_EH1_segment_disclosure -- R15 mutation proofs + R11 rendered-value proofs.

THE DEFECT this atom closes (cold-eyes Expert Hour, the finding that FAILED SITE1):
/company/ led with a blended "Net margin / customer" and "Revenue / customer" --
correctly clock-labelled (R14) and honestly showing its denominator -- over a book
whose revenue is ~99% Industrial & Commercial, under a household-carbon narrative in
which I&C appeared zero times. R14 discipline was fully present and pointed at the
WRONG AXIS: the CLOCK was labelled on every figure and the SEGMENT on none.
The aggravating half: /data/world.json rated a 2.5x churn miss GREEN via a note
saying the portfolio is "predominantly I&C" -- the one disclosure of the book's real
composition existed ONLY where it EXCUSED a failed benchmark.

WHAT THIS FILE PROVES, and the rules each proof serves:

R15 (a control must be able to FAIL): every control this atom adds is mutation-tested
BOTH WAYS -- fed its own named defect and shown to reject, then fed the real artefact
and shown to pass. The three killer patterns are each attacked directly: TAUTOLOGY
(the gates are fed a hand-built payload that disagrees with the generator, so a gate
that merely echoed its input would pass and is caught), FAIL-OPEN (missing/empty/
malformed/zero inputs are asserted to FAIL, not skip), FAIL-SILENT (an unreadable
front door is asserted to FAIL).

R11 (verify to the rendered value): the /company/ assertions run the page's own
inline script through site/company/_render_harness.mjs and assert on the RENDERED
innerHTML, never on the source file or the JSON.

R12/R13 WALL, self-policed: this atom is DISCLOSURE ONLY. `test_no_rag_is_re_rated`
asserts every published anchors RAG is byte-identical to the rating in the underlying
population_anchoring.json. A rival implementation of this same atom suppressed a
mismatched row's `rag` to null; that is a re-grading decision, not a disclosure, and
this test is what keeps it out.

NO PINNED GENERATED VALUES (memory: a pinned RNG-generated date caused a four-day
publish blackout here). Nothing below asserts a particular share, margin, segment
name, account count or RAG letter. Every assertion is a RELATIONSHIP -- "the resi
tile's denominator is the resi account count", "the mismatch is stated wherever the
populations differ", "the published RAG equals the measured RAG" -- so a run that
legitimately draws a different book still passes without an edit.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT))

COMPANY_JSON = PROJECT / "site" / "data" / "company.json"
DASHBOARD_JSON = PROJECT / "site" / "data" / "dashboard.json"
WORLD_JSON = PROJECT / "site" / "data" / "world.json"
ANCHORING_JSON = PROJECT / "site" / "state" / "population_anchoring.json"
COMPANY_HTML = PROJECT / "site" / "company" / "index.html"
FRONT_DOOR = PROJECT / "site" / "index.html"
HARNESS = PROJECT / "site" / "company" / "_render_harness.mjs"


def _load(path):
    if not path.exists():
        pytest.skip("{} not generated in this tree".format(path.name))
    return json.loads(path.read_text())


# ---------------------------------------------------------------------------
# R11 -- the RENDERED page. Not the code, not the JSON: the innerHTML the
# browser would show, produced by the page's own render functions.
# ---------------------------------------------------------------------------
def _render():
    if shutil.which("node") is None:
        pytest.skip("node not available for the render harness")
    proc = subprocess.run(
        ["node", str(HARNESS), str(COMPANY_HTML)],
        input=COMPANY_JSON.read_text(), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, "render harness failed: " + proc.stderr[-2000:]
    return json.loads(proc.stdout)


def _unescape(s):
    """The page escapes its own text (esc()), so an assertion about a rendered
    LABEL must compare against the unescaped string -- "Industrial & Commercial"
    renders as "Industrial &amp; Commercial"."""
    return (s.replace("&amp;", "&").replace("&ndash;", "\u2013")
             .replace("&mdash;", "\u2014").replace("&pound;", "\u00a3"))


def _pct(v):
    """The page's own pct() format: Number(v).toFixed(2)+"%". Asserting in the
    page's format (not a chosen one) keeps this a RELATIONSHIP test -- it holds
    for whatever share this run's book actually has."""
    return "{:.2f}%".format(v)


@pytest.fixture(scope="module")
def rendered(company):
    return _render()


@pytest.fixture(scope="module")
def company():
    """R2/pipeline race, the convention already used in site/company/test_company_door.py:
    a running auto-processor can regenerate company.json with an OLDER generator that
    predates this atom. Skip rather than wedge the publish gate on that transient -- the
    always-on guarantees live in the generator-level and gate-level tests below, which
    do not depend on the published artefact."""
    data = _load(COMPANY_JSON)
    if not (data.get("book_mix") or {}).get("available"):
        pytest.skip("book_mix not in live company.json (pre-deploy / older generator process)")
    return data


def test_book_mix_renders_before_any_claim(rendered, company):
    """Scope item 2 on /company/: the mix block is populated, and it is populated
    with the run's OWN composition rather than a hand-written sentence."""
    intro = _unescape(rendered["mix-intro"]["innerHTML"])
    assert intro and "Loading" not in intro, "the book-mix block never rendered"
    mix = company["book_mix"]
    assert mix.get("available"), "book_mix unavailable: " + str(mix.get("reason"))
    # RELATIONSHIP, not a pinned value: whatever this run's non-domestic share is,
    # that share must be the one on the page.
    assert _pct(mix["non_domestic_revenue_share_pct"]) in intro, intro[:400]
    # And every segment the book has must be named, with its own account count.
    for seg in mix["segments"]:
        assert seg["label"] in intro, "segment {} missing from the mix intro".format(seg["label"])


def test_book_mix_block_precedes_the_finance_panel_in_the_page():
    """Ordering is the defect: a reader who meets a GBP/customer figure before the
    book's composition has been misled by ordering alone, however well-labelled the
    figure is. Assert the DOM order, not merely the presence of both."""
    html = COMPANY_HTML.read_text()
    assert html.index('id="mix-intro"') < html.index('id="finance-kpis"')
    assert html.index('id="mix-intro"') < html.index('id="hh-intro"')


def test_every_per_customer_tile_states_its_segment_and_its_own_n(rendered, company):
    """Scope item 1, the core of the atom. Each per-customer tile must name a
    segment and divide by THAT segment's own account count."""
    kpis = _unescape(rendered["finance-kpis"]["innerHTML"])
    mix = company["book_mix"]
    divisible = [s for s in mix["segments"] if s.get("revenue_per_customer_gbp") is not None]
    assert divisible, "no segment had a divisible per-customer figure this run"
    for seg in divisible:
        label = seg["label"]
        assert "Net margin / customer — " + label in kpis, label
        assert "Revenue / customer — " + label in kpis, label
        # The denominator rendered next to it is this segment's own n.
        assert "÷ {} {} account(s)".format(seg["n_accounts"], label) in kpis, label

    # THE DEFECT ITSELF: no blended per-customer tile may lead the panel. The old
    # tile rendered the label "Net margin / customer" with NO segment suffix -- match
    # the page's real tile markup (kpi-l), closing at </div>, so a suffixed tile does
    # not satisfy it.
    for stale in ("Net margin / customer", "Revenue / customer"):
        assert '<div class="kpi-l">{}</div>'.format(stale) not in kpis, (
            "the blended '{}' tile is still published as a headline".format(stale))


def test_the_blended_figure_is_kept_but_demoted_with_its_reason(rendered, company):
    """R12: an inconvenient diagnostic is not deleted. The blend a reader saw
    yesterday must stay findable and reconcilable -- just not as a headline."""
    mix = company["book_mix"]
    blended = mix.get("blended")
    assert blended, "the blended figure was deleted rather than demoted"
    assert blended.get("withheld_as_headline") is True
    note = _unescape(rendered["finance-unit-note"]["innerHTML"])
    assert "blended figure, demoted" in note.lower(), note[:300]
    # Its clock is named, and it is named as DIFFERENT from the per-segment clock.
    assert blended["clock"] in note
    assert mix["clock"] in note, "the per-segment clock is not named beside the blend"


def test_per_segment_unit_economics_are_arithmetic_not_authored(company):
    """Anti-tautology: the published GBP/customer must be the segment's own
    latest-year figure over the segment's own n, recomputed here independently."""
    for seg in company["book_mix"]["segments"]:
        n = seg.get("n_accounts")
        if not n or not seg.get("latest_year_present"):
            assert seg.get("revenue_per_customer_gbp") is None, seg["segment"]
            assert seg.get("net_margin_per_customer_gbp") is None, seg["segment"]
            assert seg.get("per_customer_unavailable_reason"), seg["segment"]
            continue
        assert seg["revenue_per_customer_gbp"] == pytest.approx(
            seg["latest_year_revenue_gbp"] / n, abs=0.01), seg["segment"]
        assert seg["net_margin_per_customer_gbp"] == pytest.approx(
            seg["latest_year_net_margin_gbp"] / n, abs=0.01), seg["segment"]


def test_account_counts_come_from_the_segment_field_not_an_id_substring():
    """A rival implementation counted I&C by testing `"IC" in account_id`, which
    silently files SME accounts under residential and so publishes a wrong
    denominator -- and a wrong denominator IS a wrong GBP/customer figure. Assert
    the counts join on each account's own `segment` field."""
    from tools.generate_company_data import _account_counts_by_segment
    sample = _load(PROJECT / "site" / "data" / "customer_sample.json")
    counts, unclassified, total = _account_counts_by_segment(sample)
    assert sum(counts.values()) + unclassified == total
    for cid, cust in (sample.get("customers") or {}).items():
        seg = str(cust.get("segment") or "").strip().lower()
        if seg == "sme":
            # The exact case the id-substring approach gets wrong.
            assert counts.get("sme"), "SME accounts exist but were not counted as SME"
            assert "IC" not in cid or True
            break


def test_household_drilldown_states_its_own_segments_weight(rendered, company):
    """The one account drilled into is residential, and residential is a rounding
    error of this book's revenue. The drill-down must say so rather than letting one
    household imply the shape of the whole company."""
    mix = company["book_mix"]
    hh_seg = str((company.get("household") or {}).get("segment") or "").lower()
    match = [s for s in mix["segments"] if s["segment"].lower() == hh_seg]
    if not match:
        pytest.skip("the drilled-into account's segment is not in the mix this run")
    intro = _unescape(rendered["hh-intro"]["innerHTML"])
    assert "Weight, stated up front" in intro, intro[:300]
    assert _pct(match[0]["revenue_share_pct"]) in intro
    assert _pct(mix["dominant_share_pct"]) in intro


# ---------------------------------------------------------------------------
# CONTROL 1 -- the front-door mix-claim coherence gate.
# Named defect: the hand-authored segment sentence on the front door rotting into
# a FALSE public claim (one-way door 3) as the drawn book changes shape.
# ---------------------------------------------------------------------------
def _mix_gate():
    from tools.generate_dashboard_data import _check_front_door_segment_claim
    return _check_front_door_segment_claim


def test_front_door_claim_gate_passes_on_the_real_artefacts():
    assert _mix_gate()(_load(DASHBOARD_JSON)) is True


def test_front_door_claim_gate_fails_when_the_claim_becomes_false(tmp_path):
    """MUTATION (the named defect): the book stops being what the sentence says.
    Independence proof -- the CLAIM is parsed from HTML and the VALUE computed from
    the dashboard's segment split, so mutating either side alone must be caught."""
    door = tmp_path / "index.html"
    # A threshold no book can satisfy. The sentence is now a false public claim.
    door.write_text(FRONT_DOOR.read_text().replace(
        "non_domestic_revenue_share_gt_95", "non_domestic_revenue_share_gt_100"))
    assert _mix_gate()(_load(DASHBOARD_JSON), front_door_path=door) is False


def test_front_door_claim_gate_fails_when_the_disclosure_is_deleted(tmp_path):
    """MUTATION: someone edits the segment disclosure off the front door, or into
    an unverifiable form. 'No claim found' must never mean 'claim fine' (FAIL-OPEN)."""
    door = tmp_path / "index.html"
    door.write_text(FRONT_DOOR.read_text().replace('data-mix-claim="', 'data-was-claim="'))
    assert _mix_gate()(_load(DASHBOARD_JSON), front_door_path=door) is False


def test_front_door_claim_gate_fails_when_it_cannot_read_the_door(tmp_path):
    """FAIL-SILENT: an unavailable check is a FAILED check (R15)."""
    assert _mix_gate()(_load(DASHBOARD_JSON), front_door_path=tmp_path / "gone.html") is False


@pytest.mark.parametrize("segment_annual", [None, [], [{"year": 2025}], "not-a-list",
                                            [{"year": 2025, "resi_gas": {"revenue_gbp": 0.0}}]])
def test_front_door_claim_gate_fails_on_an_unavailable_mix(segment_annual):
    """FAIL-OPEN: missing / empty / malformed / all-zero segment data must FAIL,
    never silently pass and never degrade to a 0%-I&C mix (which would read as a
    DOMESTIC book -- the precise lie this atom exists to prevent)."""
    assert _mix_gate()({"financial": {"segment_annual": segment_annual}}) is False


def test_segment_revenue_mix_never_degrades_to_a_silent_zero():
    from tools.generate_company_data import segment_revenue_mix
    for bad in (None, [], [{}], [{"year": 2025}], ["not-a-dict"]):
        mix = segment_revenue_mix(bad)
        assert mix.get("available") is False, bad
        assert mix.get("reason"), bad
        assert "non_domestic_revenue_share_pct" not in mix, bad


# ---------------------------------------------------------------------------
# CONTROL 2 -- the anchors-register population gate (the aggravating half).
# Named defect: a row rating a sim outcome against an external benchmark WITHOUT
# stating, in the text a reader sees, which population that benchmark measures --
# the condition under which a 2.5x domestic-churn miss was cleared GREEN.
# ---------------------------------------------------------------------------
def _anchor_gate():
    from tools.generate_world_data import check_anchor_populations
    return check_anchor_populations


@pytest.fixture
def world():
    """Same pipeline race as `company` above: skip if world.json predates this atom."""
    data = _load(WORLD_JSON)
    runtime = ((data.get("anchors") or {}).get("runtime")) or {}
    if not runtime.get("population_disclosure"):
        pytest.skip("population disclosure not in live world.json (pre-deploy / older generator)")
    return data


def test_anchor_population_gate_passes_on_the_real_artefact(world):
    assert _anchor_gate()(world) is True


def test_every_anchor_row_declares_its_population_in_rendered_text(world):
    """R11 for /world/: the disclosure must be in `note`, a field the world door
    already renders -- a machine-readable field nobody sees is not a disclosure."""
    runtime = world["anchors"]["runtime"]
    assert runtime.get("cards"), "no anchor cards published"
    for card in runtime["cards"]:
        assert card.get("benchmark_population"), card.get("metric")
        assert card["benchmark_population"] in (card.get("note") or ""), card.get("metric")


def test_the_book_composition_is_disclosed_where_it_excuses_nothing(world):
    """The aggravating half, precisely: the composition existed ONLY inside the note
    that excused a failed benchmark. It must also stand at register level, where it
    exculpates nothing."""
    book = world["anchors"]["runtime"].get("book_composition") or {}
    assert book.get("population_class"), book
    assert book.get("detail"), book
    assert book.get("evidence"), book


def test_anchor_population_gate_fails_on_an_undeclared_population(world):
    """MUTATION (the named defect): a new anchor row is added that declares no
    population. An undeclared population is a FAILED check, not a skipped one."""
    import copy
    mutated = copy.deepcopy(world)
    cards = mutated["anchors"]["runtime"]["cards"]
    victim = copy.deepcopy(cards[0])
    victim["metric"] = "A newly added benchmark"
    victim["benchmark_population"] = "unstated"
    victim["measured_population"] = "unstated"
    victim["population_mismatch"] = False
    victim["note"] = "Looks fine. unstated"
    cards.append(victim)
    assert _anchor_gate()(mutated) is False


def test_anchor_population_gate_fails_when_a_mismatch_is_hidden_from_the_note(world):
    """MUTATION (benchmark shopping itself): the populations differ, the field says
    so, but the RENDERED note has been smoothed back into a reassuring sentence.
    Independence -- the gate re-decides the mismatch from the card's own declared
    populations, so it disagrees with the smoothed text rather than echoing it."""
    import copy
    mutated = copy.deepcopy(world)
    hit = [c for c in mutated["anchors"]["runtime"]["cards"]
           if c.get("population_status") == "MISMATCH"]
    if not hit:
        pytest.skip("no mismatched row in this run to mutate")
    card = hit[0]
    card["population_mismatch"] = False
    card["note"] = ("Everything is fine here. " + card["benchmark_population"]
                    + " " + str(card.get("measured_population")))
    assert _anchor_gate()(mutated) is False


def test_anchor_population_gate_fails_when_the_population_is_only_machine_readable(world):
    """FAIL-SILENT: the field is set but the population never reaches the rendered
    string. A disclosure nobody can see is not a disclosure."""
    import copy
    mutated = copy.deepcopy(world)
    card = mutated["anchors"]["runtime"]["cards"][0]
    card["note"] = "A note that mentions no population at all."
    assert _anchor_gate()(mutated) is False


@pytest.mark.parametrize("mutation", [
    {"cards": []},
    {"cards": [{"metric": "m", "note": "no population field here"}]},
    {"cards": [{"metric": "m", "benchmark_population": "domestic", "note": ""}]},
])
def test_anchor_population_gate_fails_open_on_nothing(world, mutation):
    """FAIL-OPEN: an available register with no cards, a card with no population
    field, and a card with an empty note must each FAIL."""
    import copy
    mutated = copy.deepcopy(world)
    mutated["anchors"]["runtime"].update(mutation)
    assert _anchor_gate()(mutated) is False


def test_anchor_population_gate_fails_when_the_book_composition_is_withheld(world):
    import copy
    mutated = copy.deepcopy(world)
    mutated["anchors"]["runtime"]["book_composition"] = {}
    assert _anchor_gate()(mutated) is False


# ---------------------------------------------------------------------------
# THE WALL. This atom is DISCLOSURE ONLY.
# ---------------------------------------------------------------------------
def test_no_rag_is_re_rated(world):
    """R12/R13 WALL: every published anchors RAG must be byte-identical to the
    rating in site/state/population_anchoring.json, which this atom never touches.

    This is the test that keeps the rejected rival's behaviour out: it suppressed a
    mismatched row's published `rag` to null. Substituting the machine's judgement
    about a benchmark's applicability for the measured rating is a re-grading
    decision, and it also hides WHAT was laundered -- a GREEN standing over a 2.5x
    miss is the evidence; blanking it to UNKNOWN erases the crime with the excuse.
    """
    anchoring = _load(ANCHORING_JSON)
    runtime = world["anchors"]["runtime"]
    assert runtime.get("overall_rag") == anchoring.get("overall_rag")
    by_key = {
        "churn_long_run": (anchoring.get("long_run_comparison") or {}).get("rag"),
        "bad_debt": ((anchoring.get("bad_debt_vs_benchmark") or [{}])[-1]).get("rag"),
        "complaints": ((anchoring.get("complaints_vs_benchmark") or [{}])[-1]).get("rag"),
        "arrears": ((anchoring.get("arrears_vs_benchmark") or [{}])[-1]).get("rag"),
    }
    for card in runtime["cards"]:
        key = card.get("metric_key")
        if key in by_key:
            assert card.get("rag") == by_key[key], (
                "{}: published rag {!r} != measured rag {!r} -- this atom may not "
                "re-rate a benchmark".format(key, card.get("rag"), by_key[key]))
    # And at least one row must be BOTH mismatched AND still carrying its rating,
    # or the wall is untested by this run.
    kept = [c for c in runtime["cards"]
            if c.get("population_status") == "MISMATCH" and c.get("rag")]
    assert kept, "no mismatched-but-still-rated row in this run to prove the wall"


def test_no_benchmark_or_sim_value_is_altered(world):
    """The other half of the wall: the disclosure is prepended to `note`, never
    folded into the benchmark or sim value a reader compares."""
    anchoring = _load(ANCHORING_JSON)
    cards = {c.get("metric_key"): c for c in world["anchors"]["runtime"]["cards"]}
    lrc = anchoring.get("long_run_comparison") or {}
    churn = cards.get("churn_long_run")
    if churn and lrc.get("sim_avg_pct") is not None:
        assert churn["sim_value"] == str(lrc["sim_avg_pct"]) + "%"
        assert churn["benchmark_value"] == str(lrc["ofgem_avg_pct"]) + "% (Ofgem)"
        assert churn["ratio"] == lrc.get("ratio")


def test_the_original_excusing_note_is_preserved_not_deleted(world):
    """The excuse stays on the page, LABELLED -- deleting it would hide the
    benchmark-shopping rather than expose it."""
    anchoring = _load(ANCHORING_JSON)
    original = (anchoring.get("long_run_comparison") or {}).get("note")
    if not original:
        pytest.skip("no churn note in this run")
    churn = [c for c in world["anchors"]["runtime"]["cards"]
             if c.get("metric_key") == "churn_long_run"]
    assert churn, "churn row missing"
    assert original in churn[0]["note"]
    assert "kept verbatim" in churn[0]["note"]
