"""Tests for the forward-attachment register (atom FUT1_attach_forward_hook,
DIRECTOR_RULING_FUTURE_COMMITMENT_SETS_2026-08-08 §2 + WORK-THIS-CREATES #5).

The R15 shape the atom's own origin note names is *a ledger that renders whatever it is told*
— so the tests that matter here are the MUTATION tests on `verify_rendering()`: a fabricated
row must fail it, a dropped row must fail it, and the honest rendering must pass it while the
derivation is provably non-empty (the vacuity guard — an empty ledger agrees with an empty
rendering for free, and that agreement would mean nothing).

The second class of test is RE-DERIVABILITY: delete the declaration from the source doc and
the row must disappear. An attachment that survives the deletion of its own declaration is
stored, not derived, which is the defect.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

from background import forward_attachment_register as far

PROJECT = Path(__file__).resolve().parent.parent.parent


# --------------------------------------------------------------------------- fixtures

FAKE_MAP = [
    {"id": "EP16_anchored_generators", "title": "Generated worlds", "lane": "W1_market_weather",
     "epoch": 4, "level_current": 0, "level_target": 3, "loop_stage": "idle"},
    {"id": "EP4_collections_journey", "title": "The collections road", "lane": "C_customer_ops",
     "epoch": 2, "level_current": 0, "level_target": 3, "loop_stage": "idle"},
]


@pytest.fixture
def tree(tmp_path):
    """A miniature project tree: a map, a finding that declares, and a doc that does not."""
    (tmp_path / "docs/design").mkdir(parents=True)
    (tmp_path / "docs/staging").mkdir(parents=True)
    (tmp_path / "docs/design/maturity_map.yaml").write_text(yaml.safe_dump(FAKE_MAP))
    (tmp_path / "docs/staging/WORKER_FINDING_THING_2026-08-08.md").write_text(textwrap.dedent("""\
        # [WORKER-FINDING] a thing (2026-08-08)

        **Advances:** EP16_anchored_generators — the anchor is gas-shaped.

        Body prose that mentions advances in passing but declares nothing.
        """))
    (tmp_path / "docs/design/D6_SOMETHING_DISCOVER.md").write_text(textwrap.dedent("""\
        # D6 — a discover mint

        **Advances:** EP4_collections_journey — misdated debt.
        """))
    return tmp_path


def _derive(tree):
    return far.derive(root=tree, map_path=tree / "docs/design/maturity_map.yaml")


# --------------------------------------------------------------------------- derivation

def test_declaration_is_derived_from_the_doc(tree):
    d = _derive(tree)
    assert d["violations"] == []
    assert set(d["ledger"]) == {"EP16_anchored_generators", "EP4_collections_journey"}
    e = d["ledger"]["EP16_anchored_generators"][0]
    assert e["source"] == "docs/staging/WORKER_FINDING_THING_2026-08-08.md"
    assert e["date"] == "2026-08-08"
    assert e["kind"] == "finding"
    assert e["note"] == "the anchor is gas-shaped."
    assert d["ledger"]["EP4_collections_journey"][0]["kind"] == "discover"


def test_deleting_the_declaration_deletes_the_row(tree):
    """RE-DERIVABILITY. The row exists because the finding says so — and only while it says so."""
    doc = tree / "docs/staging/WORKER_FINDING_THING_2026-08-08.md"
    assert "EP16_anchored_generators" in _derive(tree)["ledger"]
    doc.write_text(doc.read_text().replace("**Advances:** EP16_anchored_generators — ", ""))
    after = _derive(tree)
    assert "EP16_anchored_generators" not in after["ledger"]
    assert after["violations"] == []


def test_one_declaration_can_name_several_atoms(tree):
    doc = tree / "docs/staging/WORKER_FINDING_THING_2026-08-08.md"
    doc.write_text(doc.read_text().replace(
        "**Advances:** EP16_anchored_generators",
        "**Advances:** EP16_anchored_generators, EP4_collections_journey"))
    d = _derive(tree)
    assert len(d["ledger"]["EP4_collections_journey"]) == 2
    assert d["violations"] == []


# --------------------------------------------------------- fail LOUD, never silently drop

def test_unknown_atom_is_a_violation_not_a_silent_drop(tree):
    """A typo'd or invented id must not vanish — the whole point is that the declaration is
    checked against the map, so a declaration that attaches to nothing is visible."""
    doc = tree / "docs/staging/WORKER_FINDING_THING_2026-08-08.md"
    doc.write_text(doc.read_text().replace("EP16_anchored_generators", "EP16_anchored_generatorz"))
    d = _derive(tree)
    assert d["ledger"] == {"EP4_collections_journey": d["ledger"]["EP4_collections_journey"]}
    assert [v for v in d["violations"]
            if v["kind"] == "unknown_atom" and v["detail"] == "EP16_anchored_generatorz"]


def test_empty_declaration_is_a_violation(tree):
    (tree / "docs/staging/EMPTY_2026-08-08.md").write_text("# x\n\n**Advances:**\n")
    assert [v for v in _derive(tree)["violations"] if v["kind"] == "empty_declaration"]


def test_malformed_token_is_a_violation(tree):
    (tree / "docs/staging/BAD_2026-08-08.md").write_text("# x\n\n**Advances:** ep!!, EP4_collections_journey\n")
    d = _derive(tree)
    assert [v for v in d["violations"] if v["kind"] == "malformed_token" and v["detail"] == "ep!!"]
    # the valid sibling on the same line still attaches — one bad token does not eat the line
    assert any(e["source"].endswith("BAD_2026-08-08.md") for e in d["ledger"]["EP4_collections_journey"])


def test_declaration_payload_stops_at_end_of_line(tree):
    """The unbounded-field-parser class: a declaration must not swallow the rest of the doc.
    Here the very next line names a real atom in prose — it must NOT become an attachment."""
    (tree / "docs/staging/BOUND_2026-08-08.md").write_text(
        "# x\n\n**Advances:** EP16_anchored_generators\nEP4_collections_journey is discussed below.\n")
    d = _derive(tree)
    sources = {e["source"] for e in d["ledger"].get("EP4_collections_journey", [])}
    assert "docs/staging/BOUND_2026-08-08.md" not in sources


def test_absent_map_makes_every_id_unknown_rather_than_accepted(tmp_path):
    """FAIL DIRECTION: an unreadable map is a FAILED check, not a pass that accepts anything."""
    (tmp_path / "docs/staging").mkdir(parents=True)
    (tmp_path / "docs/staging/F_2026-08-08.md").write_text("**Advances:** EP16_anchored_generators\n")
    d = far.derive(root=tmp_path, map_path=tmp_path / "nope.yaml")
    assert d["ledger"] == {}
    assert [v for v in d["violations"] if v["kind"] == "unknown_atom"]


# ------------------------------------------------------- R15: the control must be able to fail

def test_honest_rendering_verifies(tree):
    d = _derive(tree)
    assert d["entries"], "vacuity guard: the fixture must produce attachments"
    assert far.verify_rendering(far.render_markdown(d), d) == []


def test_mutation_fabricated_row_fails_verification(tree):
    """THE NAMED DEFECT: a ledger that renders whatever it is told. A row nobody declared is
    added to the rendering; the control must fire."""
    d = _derive(tree)
    rendered = far.render_markdown(d)
    assert far.verify_rendering(rendered, d) == [], "vacuity guard: unmutated must pass"
    poisoned = rendered + (
        "\n## EP4_collections_journey\n"
        "- `2026-08-08` · `docs/staging/A_DOC_THAT_NEVER_DECLARED_ANYTHING.md` (finding) — invented\n"
    )
    v = far.verify_rendering(poisoned, d)
    assert [x for x in v if x["kind"] == "fabricated_entry"
            and x["source"] == "docs/staging/A_DOC_THAT_NEVER_DECLARED_ANYTHING.md"], v


def test_mutation_dropped_row_fails_verification(tree):
    """The other direction: a rendering that quietly omits a real declaration is equally wrong
    — accretion that does not surface is the homelessness the ruling exists to end."""
    d = _derive(tree)
    rendered = far.render_markdown(d)
    truncated = "\n".join(
        ln for ln in rendered.splitlines()
        if "WORKER_FINDING_THING_2026-08-08.md" not in ln)
    v = far.verify_rendering(truncated, d)
    assert [x for x in v if x["kind"] == "missing_entry"
            and x["atom_id"] == "EP16_anchored_generators"], v


def test_mutation_reattributed_row_fails_verification(tree):
    """A real source moved under the wrong atom heading is BOTH a fabrication and a miss —
    the pair (atom, source) is what is verified, not the mere presence of the path."""
    d = _derive(tree)
    rendered = far.render_markdown(d).replace("## EP16_anchored_generators", "## EP4_collections_journey")
    kinds = {x["kind"] for x in far.verify_rendering(rendered, d)}
    assert kinds == {"fabricated_entry", "missing_entry"}


def test_missing_rendering_is_a_failed_check_not_a_pass(tree):
    problems, _ = far.check(root=tree, map_path=tree / "docs/design/maturity_map.yaml",
                            ledger_md=tree / "docs/design/NOT_WRITTEN.md")
    assert [p for p in problems if p["kind"] == "rendering_missing"]


def test_written_rendering_round_trips(tree):
    d = _derive(tree)
    md = tree / "docs/design/FORWARD_ATTACHMENT_LEDGER.md"
    md.write_text(far.render_markdown(d))
    problems, derived = far.check(root=tree, map_path=tree / "docs/design/maturity_map.yaml",
                                  ledger_md=md)
    assert derived["entries"], "vacuity guard"
    assert problems == []


def test_an_annotation_only_drift_is_stale_though_every_PAIR_is_intact(tree):
    """THE ORACLE'S OWN DEFECT, pinned (2026-08-10, eighth publish wedge, `b2f0fc8f8`).

    The repair landed in `check()` with no test of its own, so the one thing standing between
    that class and its fourth recurrence was the blocking test it exists to agree with. The
    real drift was an atom's level/stage annotation moving after an ordinary map edit, every
    `(atom_id, source)` pair unchanged — invisible to `verify_rendering`, which is the
    staleness oracle `background/derived_artefact_register.py` drives, and red for 98 gate
    cycles at `test_live_rendering_is_current`.

    BOTH halves are asserted, because the pair-level silence is what made the oracle blind:
    the pair check must stay quiet (this drift is not its subject) and `check()` must refuse
    anyway. Revert `check()` to pairs-only and this test fails.
    """
    d = _derive(tree)
    md = tree / "docs/design/FORWARD_ATTACHMENT_LEDGER.md"
    honest = far.render_markdown(d)
    drifted = honest.replace("L0→L3 · idle_", "L2→L3 · harden_")
    assert drifted != honest, "vacuity guard: the fixture must carry the annotation being drifted"
    md.write_text(drifted)

    assert far.verify_rendering(drifted, d) == [], (
        "vacuity guard: the drift must be INVISIBLE to the pair-level check, or this test is "
        "not standing where the oracle was blind")

    problems, derived = far.check(root=tree, map_path=tree / "docs/design/maturity_map.yaml",
                                  ledger_md=md)
    assert derived["entries"], "vacuity guard"
    assert [p for p in problems if p["kind"] == "stale_rendering"], problems


# ------------------------------------------------------------------ the live tree (WTC #5)

def test_live_tree_has_no_violations():
    problems, derived = far.check()
    assert problems == [], problems
    assert derived["entries"], "vacuity guard: the live ledger must not be empty"


@pytest.mark.parametrize("atom_id,source_fragment", [
    # WORK-THIS-CREATES #5: the two forward-findings of 2026-08-08, retro-attached.
    ("EP16_anchored_generators", "WORKER_FINDING_L1_TEXTURE_BAND_IS_GAS_SHAPED_2026-08-08"),
    ("EP17_varied_population_draw", "WORKER_FINDING_L1_TEXTURE_BAND_IS_GAS_SHAPED_2026-08-08"),
    ("EP4_collections_journey", "D6_PAYMENT_AGEING_GAP_VALIDITY_DISCOVER"),
])
def test_the_two_forward_findings_are_attached(atom_id, source_fragment):
    ledger = far.derive()["ledger"]
    assert atom_id in ledger, f"{atom_id} has accreted nothing"
    assert any(source_fragment in e["source"] for e in ledger[atom_id]), ledger[atom_id]


def test_live_rendering_is_current():
    """The committed ledger must equal a fresh derivation — a stale rendering is the stored-
    not-derived defect wearing a generated-file header."""
    derived = far.derive()
    assert far.LEDGER_MD_PATH.read_text() == far.render_markdown(derived), (
        "the committed ledger and the source docs disagree — a declaration was added, edited, "
        "or its doc was moved (archiving a finding into docs/staging/done/ changes its cited "
        "path). Fix: python3 -m background.forward_attachment_register --write"
    )
