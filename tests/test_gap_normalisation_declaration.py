"""ATOM D44 -- what `raw_gap` and `g0` MEAN on a published gap entry.

H27 EXPERT HOUR #28 (2026-08-13). `background/gap_metric.py`'s own docstring
states ONE relation between the three fields it publishes --
`gap = raw_gap / g0` -- and enumerated exactly ONE exempt family (ageing).
Measured on the live ledger the public Proof door serves: 11 of 14 pairs satisfy
it and THREE DO NOT, all three the same unenumerated family
(`detection_measures`, D11), where `g0 = 0.5` is the no-skill SCORE on the
headline's own scale and `raw_gap` is ONE of the two averaged directions.

The reader got both readings of the same field:
  * W2_11<->D5   `raw 0.000` beside a nonzero headline -- the miss direction
    really is zero and the WHOLE score is the other one (false flags on
    truly-succeeded invoices). Reads as "the company's own error is nil".
  * W2_8<->C10   `raw 0.361` against a published 0.199; raw/g0 = 0.723, 3.6x.

THE KIND IS DECLARED, NEVER DERIVED. A kind inferred from whether
`gap == raw/g0` holds would classify every entry correctly by construction and
could never fire on the case it exists for -- the fail-OPEN direction of this
same mistake. So the declaration is made at the construction site and CHECKED
against the arithmetic there, and every mutation below is a defect that could
be written today, not a restatement of the declaration.

R15: each test names the defect it pins and asserts the control FIRES on it;
the last section asserts the control is not always-red (the real scorers
construct clean, and a fully-declared ledger audits empty).
"""
from __future__ import annotations

import json

import pytest

from background.gap_metric import (
    NORMALISATION_FINDING_COMPONENT_SHADOWS,
    NORMALISATION_FINDING_DIVISOR_BROKEN,
    NORMALISATION_FINDING_FALSE_DIVISOR,
    NORMALISATION_FINDING_NONE_NOT_HEADLINE,
    NORMALISATION_FINDING_REFERENCE_MISMATCH,
    NORMALISATION_FINDING_UNDECLARED,
    NORMALISATION_FINDING_UNKNOWN_KIND,
    NORMALISATION_KINDS,
    GapResult,
    audit_ledger_normalisation,
    detection_measures,
    load_gap_ledger,
)


# --------------------------------------------------------------------------- #
# THE WRITE SIDE -- an undeclared or mis-declared entry cannot be constructed.
# --------------------------------------------------------------------------- #
def test_an_entry_that_declares_no_kind_cannot_be_written():
    """THE DEFECT THAT SHIPPED. `detection_measures` joined the ledger on
    2026-08-09 with g0=0.5 and raw_gap = one of two directions, under a module
    that had stated `gap = raw_gap / g0` since A6, and nothing objected."""
    with pytest.raises(ValueError, match="declares no normalisation kind"):
        GapResult(metric="detection", gap=0.0834, raw_gap=0.0, g0=0.5,
                  baseline="b", components={"missed_failure_rate": 0.0})


def test_a_declared_divisor_whose_arithmetic_is_false_cannot_be_written():
    with pytest.raises(ValueError, match="is not raw_gap/g0"):
        GapResult(metric="detection", gap=0.0834, raw_gap=0.0, g0=0.5,
                  baseline="b", normalisation="divisor")


def test_a_reference_kind_must_say_why_there_is_no_divisor():
    """An exemption without a stated reason is how the first one sat unseen."""
    with pytest.raises(ValueError, match="no `normalisation_reason`"):
        GapResult(metric="detection", gap=0.0834, raw_gap=0.0, g0=0.5,
                  baseline="b", normalisation="reference",
                  raw_gap_is="missed_failure_rate: one direction",
                  components={"missed_failure_rate": 0.0})


def test_a_reference_kind_must_say_what_raw_gap_actually_is():
    with pytest.raises(ValueError, match="no `raw_gap_is`"):
        GapResult(metric="detection", gap=0.0834, raw_gap=0.0, g0=0.5,
                  baseline="b", normalisation="reference",
                  normalisation_reason="balanced headline",
                  components={"missed_failure_rate": 0.0})


def test_a_reference_kind_must_name_a_component_that_exists():
    """Prose alone about `raw_gap` would be unfalsifiable -- which is the state
    this whole check exists to leave. The named key must be findable by the
    reader, in the components the same door renders."""
    with pytest.raises(ValueError, match="is not in components"):
        GapResult(metric="detection", gap=0.0834, raw_gap=0.0, g0=0.5,
                  baseline="b", normalisation="reference",
                  normalisation_reason="balanced headline",
                  raw_gap_is="missed_failure_rate: one direction",
                  components={"false_flag_rate": 0.1668})


def test_a_reference_kind_whose_named_component_carries_a_different_number_fires():
    with pytest.raises(ValueError, match="!= raw_gap"):
        GapResult(metric="detection", gap=0.0834, raw_gap=0.0, g0=0.5,
                  baseline="b", normalisation="reference",
                  normalisation_reason="balanced headline",
                  raw_gap_is="missed_failure_rate: one direction",
                  components={"missed_failure_rate": 0.42})


def test_a_reference_kind_with_a_zero_g0_is_refused():
    """`reference` means g0 is the score a blind rule attains. 0 is not one --
    that shape is `none`, and letting it pass would make the two kinds
    indistinguishable in exactly the field a reader divides by."""
    with pytest.raises(ValueError, match="not a score a blind rule attains"):
        GapResult(metric="detection", gap=0.0834, raw_gap=0.0, g0=0.0,
                  baseline="b", normalisation="reference",
                  normalisation_reason="balanced headline",
                  raw_gap_is="missed_failure_rate: one direction",
                  components={"missed_failure_rate": 0.0})


def test_a_reference_headline_cannot_outlive_an_undefined_direction():
    """If the named direction has no population (None), the balanced headline
    must be undefined too. A live headline beside a direction that does not
    exist is the fail-open reading of a two-direction measure."""
    with pytest.raises(ValueError, match="cannot survive a direction"):
        GapResult(metric="belief", gap=0.4, raw_gap=0.0, g0=0.5,
                  baseline="b", normalisation="reference",
                  normalisation_reason="balanced headline",
                  raw_gap_is="undercall_rate: one direction",
                  components={"undercall_rate": None})


def test_an_un_normalised_kind_must_publish_a_zero_g0():
    """So no reader can divide by it."""
    with pytest.raises(ValueError, match="An un-normalised measure publishes g0"):
        GapResult(metric="ageing", gap=1.2, raw_gap=1.2, g0=0.5,
                  baseline="b", normalisation="none",
                  normalisation_reason="ordered space, no baseline",
                  raw_gap_is="the headline itself")


def test_an_un_normalised_kind_whose_raw_is_not_the_headline_fires():
    with pytest.raises(ValueError, match="is not the headline"):
        GapResult(metric="ageing", gap=1.2, raw_gap=0.4, g0=0.0,
                  baseline="b", normalisation="none",
                  normalisation_reason="ordered space, no baseline",
                  raw_gap_is="the headline itself")


def test_an_unknown_kind_word_is_refused_rather_than_treated_as_a_divisor():
    with pytest.raises(ValueError, match="declares no normalisation kind"):
        GapResult(metric="detection", gap=0.1, raw_gap=0.05, g0=0.5,
                  baseline="b", normalisation="normalised")


# --------------------------------------------------------------------------- #
# THE MEASURED FINDING, as a structural property rather than a live pin.
# --------------------------------------------------------------------------- #
def test_the_balanced_detection_headline_can_be_all_of_the_direction_raw_gap_is_not():
    """The shape the door was rendering as `raw 0.000` beside a live score: a
    company that misses NOTHING and false-flags plenty. `raw_gap` is 0.0 and the
    entire headline is the direction it does not carry -- so a reader applying
    `gap = raw_gap / g0` reads 0.000 where the truth is a wrongful-dunning
    exposure. Structural, not a pin on today's numbers."""
    truth = {"i1", "i2"}
    universe = {"i1", "i2"} | {f"n{i}" for i in range(8)}
    flagged = truth | {"n0", "n1"}            # every true failure caught, 2 wrong
    res = detection_measures(truth_set=truth, flagged_set=flagged, universe=universe)

    assert res.raw_gap == 0.0, "no true failure missed"
    assert res.gap is not None and res.gap > 0.0, "but the headline is not zero"
    assert res.normalisation == "reference"
    # ALL of the headline is the direction `raw_gap` is not.
    assert res.gap == pytest.approx(res.components["false_flag_rate"] / 2.0)
    # And the relation the module docstring states is FALSE for this entry --
    # which is the whole reason the kind has to be declared.
    assert res.gap != pytest.approx(res.raw_gap / res.g0)
    # The declaration points the reader at the number that is actually moving.
    assert res.raw_gap_is.startswith("missed_failure_rate")
    assert "false_flag_rate" in res.normalisation_reason


# --------------------------------------------------------------------------- #
# THE POPULATION CONTROL -- the ledger on disk, not the code that writes it.
# --------------------------------------------------------------------------- #
def _declared_entry(**over):
    entry = {
        "twin_atom_id": "CX", "metric": "detection",
        "gap": 0.0834, "raw_gap": 0.0, "g0": 0.5,
        "normalisation": "reference",
        "normalisation_reason": "balanced headline; g0 is the no-skill score",
        "raw_gap_is": "missed_failure_rate: one of two directions",
        "components": {"missed_failure_rate": 0.0, "false_flag_rate": 0.1668},
    }
    entry.update(over)
    return entry


def test_a_fully_declared_ledger_audits_clean():
    """NOT ALWAYS-RED."""
    ledger = {
        "W_ref": _declared_entry(),
        "W_div": _declared_entry(gap=0.4, raw_gap=0.2, g0=0.5,
                                 normalisation="divisor",
                                 normalisation_reason="", raw_gap_is="",
                                 components={}),
        "W_none": _declared_entry(gap=1.2, raw_gap=1.2, g0=0.0,
                                  normalisation="none",
                                  normalisation_reason="ordered space",
                                  raw_gap_is="the headline itself",
                                  components={}),
    }
    assert audit_ledger_normalisation(ledger) == []


def test_the_audit_reports_an_entry_that_declares_nothing():
    """FAIL-CLOSED. A pre-D44 producer's entry is a finding, never a pass --
    an unreadable basis is not a correct one."""
    entry = _declared_entry()
    entry.pop("normalisation")
    found = audit_ledger_normalisation({"W": entry})
    assert [f["finding"] for f in found] == [NORMALISATION_FINDING_FALSE_DIVISOR]

    clean = _declared_entry(gap=0.4, raw_gap=0.2, g0=0.5, components={})
    clean.pop("normalisation")
    found = audit_ledger_normalisation({"W": clean})
    assert [f["finding"] for f in found] == [NORMALISATION_FINDING_UNDECLARED]


def test_the_audit_separates_undeclared_from_actively_misleading():
    """The two are not the same defect: an undeclared entry whose numbers happen
    to divide leaves the reader unable to CHECK; one whose numbers do not divide
    has already told them something false."""
    a = _declared_entry(gap=0.4, raw_gap=0.2, g0=0.5, components={})
    a.pop("normalisation")
    b = _declared_entry()
    b.pop("normalisation")
    found = {f["world_atom_id"]: f["finding"]
             for f in audit_ledger_normalisation({"W_ok": a, "W_bad": b})}
    assert found["W_ok"] == NORMALISATION_FINDING_UNDECLARED
    assert found["W_bad"] == NORMALISATION_FINDING_FALSE_DIVISOR


def test_the_audit_fires_on_each_declared_kind_that_lies():
    cases = {
        "W_div": (_declared_entry(gap=0.9, raw_gap=0.2, g0=0.5,
                                  normalisation="divisor",
                                  normalisation_reason="", raw_gap_is="",
                                  components={}),
                  NORMALISATION_FINDING_DIVISOR_BROKEN),
        "W_ref": (_declared_entry(components={"missed_failure_rate": 0.42}),
                  NORMALISATION_FINDING_REFERENCE_MISMATCH),
        "W_none": (_declared_entry(gap=1.2, raw_gap=0.4, g0=0.0,
                                   normalisation="none",
                                   normalisation_reason="ordered",
                                   raw_gap_is="the headline itself",
                                   components={}),
                   NORMALISATION_FINDING_NONE_NOT_HEADLINE),
        "W_huh": (_declared_entry(normalisation="normalised"),
                  NORMALISATION_FINDING_UNKNOWN_KIND),
    }
    for world, (entry, expected) in cases.items():
        found = audit_ledger_normalisation({world: entry})
        assert [f["finding"] for f in found] == [expected], world


def test_the_audit_does_not_die_on_a_malformed_entry():
    """FAIL-SILENT is the third killer pattern: a checker that raises on the
    population it grades stops grading it."""
    found = audit_ledger_normalisation({
        "W_str": _declared_entry(gap="n/a", raw_gap=None, g0=0.5),
        "W_nul": None,
        "W_lst": [1, 2, 3],
    })
    assert [f["finding"] for f in found] == [NORMALISATION_FINDING_UNDECLARED]


def test_every_kind_word_the_audit_accepts_is_one_a_writer_can_declare():
    """The two vocabularies are the same object -- a kind the audit tolerates
    but no writer can produce (or the reverse) is a seam with two truths."""
    for kind in NORMALISATION_KINDS:
        entry = _declared_entry(normalisation=kind, gap=0.4, raw_gap=0.4,
                                g0=(0.0 if kind == "none" else 0.5),
                                normalisation_reason="r",
                                raw_gap_is=("missed_failure_rate: d"
                                            if kind == "reference" else "h"),
                                components={"missed_failure_rate": 0.4})
        if kind == "divisor":
            entry["gap"], entry["raw_gap"] = 0.8, 0.4
        found = audit_ledger_normalisation({"W": entry})
        assert found == [], f"{kind}: {found}"


# --------------------------------------------------------------------------- #
# THE LIVE LEDGER -- the artefact the public door actually serves.
# --------------------------------------------------------------------------- #
def test_the_live_ledger_is_graded_and_its_state_is_reported_not_assumed():
    """CHARACTERIZATION (R12 -- a diagnostic, not a target). Every live entry
    predates D44, so every one is a finding today and this test does not pretend
    otherwise. What it pins is that the audit REACHES the live artefact and that
    no entry is silently skipped -- when runs re-measure with declaring writers,
    the findings drain and this test still passes.
    """
    ledger = load_gap_ledger()
    assert ledger, "the live coupled gap ledger is unreadable or empty"
    found = audit_ledger_normalisation(ledger)
    graded = {f["world_atom_id"] for f in found} | {
        k for k, v in ledger.items()
        if isinstance(v, dict) and v.get("normalisation") in NORMALISATION_KINDS
    }
    assert graded == set(ledger), (
        "an entry was neither found nor cleanly declared -- the audit skipped it"
    )
    # The finding classes present must be ones the audit can name.
    assert {f["finding"] for f in found} <= {
        NORMALISATION_FINDING_UNDECLARED, NORMALISATION_FINDING_FALSE_DIVISOR,
        NORMALISATION_FINDING_DIVISOR_BROKEN,
        NORMALISATION_FINDING_REFERENCE_MISMATCH,
        NORMALISATION_FINDING_NONE_NOT_HEADLINE,
        NORMALISATION_FINDING_UNKNOWN_KIND,
        # H27 Hour #30 -- and this one FIRES on the live ledger today, which is
        # what makes this population control non-vacuous.
        NORMALISATION_FINDING_COMPONENT_SHADOWS,
    }


def test_the_json_shape_the_door_reads_carries_the_declaration():
    """The door cannot re-derive the relation from the numbers, so it has to
    travel with them (R11: what the reader is handed, not what the writer knew)."""
    res = detection_measures(
        truth_set={"i1"}, flagged_set={"i1", "n0"},
        universe={"i1", "n0", "n1", "n2"})
    entry = res.to_ledger_entry("D5_account_hierarchy_payments")
    assert entry["normalisation"] == "reference"
    assert entry["raw_gap_is"].startswith("missed_failure_rate")
    assert entry["normalisation_reason"]
    json.dumps(entry)  # ledger-serialisable


# --------------------------------------------------------------------------- #
# THE RESERVED-NAME COLLISION (atom D44, H27 Expert Hour #30)
#
# THE DEFECT, measured on the artefact the public door serves. `to_dict` emits
# `components` as a SIBLING of the declared fields, and the door renders both in
# one row: the basis line off the entry-level `normalisation`, and every
# `components` key by name inside the disclosure headed "Components &
# measurement basis". On `site/data/proof.json` row `W2_9_segment_debt_tnc` that
# rendered `basis UNDECLARED` beside `normalisation: majority-class prevalence`
# -- one word, two fields, opposite readings, and the free-text side is not in
# NORMALISATION_KINDS.
#
# R10: closed as a CLASS, not as three instances. The reserved set is DERIVED
# from GapResult's own fields, so a field added to the contract tomorrow is
# reserved the same day.
# --------------------------------------------------------------------------- #
def test_the_reserved_set_is_derived_from_the_contract_not_transcribed():
    """INDEPENDENCE (R15). A hand-typed list would drift the moment a field was
    added; this asserts the guard's subject IS the dataclass."""
    import dataclasses

    from background.gap_metric import reserved_component_keys

    assert reserved_component_keys() == {
        f.name for f in dataclasses.fields(GapResult)
    }
    # And it genuinely covers the field the live defect was on.
    assert {"normalisation", "raw_gap", "g0", "gap"} <= reserved_component_keys()


def test_a_component_key_that_shadows_an_entry_field_cannot_be_written():
    """THE WRITE SIDE. Every reserved name, not just the one that shipped."""
    from background.gap_metric import reserved_component_keys

    for name in sorted(reserved_component_keys()):
        with pytest.raises(ValueError, match="entry-level field names"):
            GapResult(metric="detection", gap=0.4, raw_gap=0.2, g0=0.5,
                      baseline="b", normalisation="divisor",
                      components={name: "majority-class prevalence"})


def test_the_write_guard_is_not_always_red():
    """NOT A TAUTOLOGY: a components dict that shadows nothing constructs."""
    res = GapResult(metric="detection", gap=0.4, raw_gap=0.2, g0=0.5,
                    baseline="b", normalisation="divisor",
                    components={"normaliser": "majority-class prevalence",
                                "normalisation_absent_reason": "n/a",
                                "minority_class_share": 0.09})
    assert res.components["normaliser"] == "majority-class prevalence"


def test_the_write_guard_runs_before_the_kind_check():
    """ORDER MATTERS. The live offender had NO declared kind, so a guard placed
    after the kind check would never have reached its collision -- the entry
    would raise on the kind and carry the shadow away unreported."""
    with pytest.raises(ValueError, match="entry-level field names"):
        GapResult(metric="detection", gap=0.4, raw_gap=0.2, g0=0.5,
                  baseline="b",  # no `normalisation=` at all
                  components={"normalisation": "majority-class prevalence"})


def test_the_audit_reports_a_shadowing_component_already_on_disk():
    """THE READ SIDE. The write guard cannot reach an entry already serialised
    to JSON -- and the live offender was exactly that. This is the half that
    covers the existing population.

    R15 BOTH WAYS: present -> found; renamed -> gone."""
    from background.gap_metric import NORMALISATION_FINDING_COMPONENT_SHADOWS

    entry = _declared_entry(components={"missed_failure_rate": 0.0,
                                        "false_flag_rate": 0.1668,
                                        "normalisation": "majority-class prevalence"})
    found = audit_ledger_normalisation({"W": entry})
    shadow = [f for f in found
              if f["finding"] == NORMALISATION_FINDING_COMPONENT_SHADOWS]
    assert len(shadow) == 1
    assert "majority-class prevalence" in shadow[0]["detail"]

    entry["components"]["normaliser"] = entry["components"].pop("normalisation")
    assert audit_ledger_normalisation({"W": entry}) == []


def test_the_audit_grades_the_collision_on_an_entry_with_no_declared_kind():
    """THE SHAPE THE LIVE OFFENDER HAD. `W2_9_segment_debt_tnc` carried
    `components['normalisation']` AND no entry-level `normalisation` at all. The
    audit's kind branches all `continue`, so a collision check placed after them
    would report the undeclared kind and stay silent about the shadow -- the
    reader would be told half of what the row is doing wrong."""
    from background.gap_metric import NORMALISATION_FINDING_COMPONENT_SHADOWS

    entry = _declared_entry(gap=0.4, raw_gap=0.2, g0=0.5,
                            components={"normalisation": "majority-class prevalence"})
    entry.pop("normalisation")
    findings = {f["finding"] for f in audit_ledger_normalisation({"W": entry})}
    assert NORMALISATION_FINDING_COMPONENT_SHADOWS in findings
    assert NORMALISATION_FINDING_UNDECLARED in findings

    # Same for an UNKNOWN kind, the other early `continue`.
    entry["normalisation"] = "percentage"
    findings = {f["finding"] for f in audit_ledger_normalisation({"W": entry})}
    assert NORMALISATION_FINDING_COMPONENT_SHADOWS in findings
    assert NORMALISATION_FINDING_UNKNOWN_KIND in findings


def test_no_live_scorer_writes_a_shadowing_component():
    """THE THREE OFFENDERS THIS HOUR FOUND, pinned at their sources so a rename
    back is a red test rather than a door regression."""
    from background.gap_metric import ageing_gap, misapplication_gap

    mis = misapplication_gap(["dom"] * 100 + ["biz"] * 10,
                             ["dom"] * 95 + ["biz"] * 15)
    assert "normalisation" not in mis.components
    assert mis.components["normaliser"] == "majority-class prevalence"

    res = detection_measures(truth_set={"i1"}, flagged_set={"i1", "n0"},
                             universe={"i1", "n0", "n1", "n2"})
    assert "normalisation" not in res.components

    age = ageing_gap(["current", "90+", "30-60", "current"],
                     ["current", "current", "30-60", "60-90"])
    assert "normalisation" not in age.components
    assert "NO NORMALISER" in age.components["normalisation_absent_reason"]
    assert age.normalisation == "none"
