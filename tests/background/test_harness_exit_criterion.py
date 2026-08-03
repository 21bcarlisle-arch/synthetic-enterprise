"""HX1_exit_criterion_counter_mechanise — acceptance tests for the harness exit-criterion counter.

The counter (`background/harness_exit_criterion.py`) is itself a CONTROL: it decides
whether harness investment may resume. R15 therefore binds it — a control that cannot
fail is worse than none — so these tests are written to prove it fires BOTH ways, and
the four exit criteria the atom declares each have a named test:

    (1) a SYNTHETIC STALL injected into the primary-state inputs RESETS the counter
        -> test_a_synthetic_stall_resets_the_counter_to_zero
    (2) THREE CLEAN CONTENT ADVANCES with zero stall-class SATISFY it
        -> test_three_clean_advances_satisfy_the_criterion
    (3) the counter is a PURE FUNCTION of primary state, never of tick memory or
        self-report (TAUTOLOGY guard)
        -> test_provenance_prose_cannot_manufacture_an_advance
        -> test_the_same_primary_state_gives_the_same_answer
    (4) NON-FINITE / MISSING inputs REJECT (FAIL-OPEN guard)
        -> test_a_missing_ledger_refuses_rather_than_reading_as_zero_advances and siblings

Everything here builds a synthetic primary state on disk. Nothing reads the real
ledger/map, so the suite does not change its verdict as the project advances.
"""

from __future__ import annotations

import json

import pytest

from background import harness_exit_criterion as hx
from background.harness_exit_criterion import ExitCriterionError

# A stall detector for a span that is genuinely clean, and a fully-covered registry.
# Passing these explicitly is what lets a test reach `satisfied=True`; on the real
# repository today the two UNCOVERED classes HX2 named hold `provable` at False.
CLEAN = dict(stall_detector=lambda since, now: [], uncovered_ids=[], point_kind_ids=[])

PASSES = staticmethod(lambda files: True)


class _Repo:
    """A synthetic primary state: ruling doc, ledger, map, fidelity register, tests."""

    def __init__(self, root):
        self.root = root
        self.ruling = root / "RULING.md"
        self.ledger = root / "gate_authorizations.jsonl"
        self.map = root / "maturity_map.yaml"
        self.fidelity = root / "fidelity.json"
        self.tests = root / "tests"
        self.tests.mkdir()
        self.ruling.write_text("The criterion is ratified. **N = 3.**\n", encoding="utf-8")
        self.fidelity.write_text("{}", encoding="utf-8")
        self._atoms: list[dict] = []
        self._entries: list[dict] = []
        self._t = 1_700_000_000.0

    # -- builders --------------------------------------------------------------
    def atom(self, atom_id, *, lane="W1_market_weather", value_stream="wholesale_to_price"):
        self._atoms.append({"id": atom_id, "lane": lane, "value_stream": value_stream})
        return self

    def advance(self, atom_id, *, level=2, provenance="evidence", at=None, action=None, ts_override=None):
        self._t += 3600.0
        entry = {
            "atom": atom_id,
            "action": action or "LEVEL_UP_SELF_CERTIFIED",
            "level": level,
            "ts": ts_override if ts_override is not None else (at if at is not None else self._t),
            "authorized_by": "agent_self_certified",
            "channel": "self",
            "provenance": provenance,
        }
        self._entries.append(entry)
        return self

    def spec_tied_test(self, atom_id):
        """A test module DECLARING itself this atom's acceptance test (module docstring)."""
        safe = atom_id.lower().replace("-", "_")
        (self.tests / f"test_{safe}.py").write_text(
            f'"""{atom_id} — acceptance."""\n\n\ndef test_it():\n    assert True\n', encoding="utf-8"
        )
        return self

    def incidental_mention(self, atom_id, name="test_unrelated.py"):
        """A test that MENTIONS the atom in a fixture but is not its acceptance test."""
        (self.tests / name).write_text(
            f'"""Something else entirely."""\n\n_FIXTURE = {{"id": "{atom_id}"}}\n\n\n'
            f"def test_other():\n    assert _FIXTURE\n",
            encoding="utf-8",
        )
        return self

    def moved_fidelity_row(self, atom_id, *, lift=2.5, baseline="gas_floor_alone"):
        obj = json.loads(self.fidelity.read_text())
        obj[f"{atom_id}::row"] = {
            "atom_id": atom_id,
            "per_cell_lift": [{"cell": "y2016", "lift": lift, "best_baseline_id": baseline}],
        }
        self.fidelity.write_text(json.dumps(obj), encoding="utf-8")
        return self

    def flush(self):
        import yaml

        self.map.write_text(yaml.safe_dump(self._atoms), encoding="utf-8")
        self.ledger.write_text(
            "".join(json.dumps(e) + "\n" for e in self._entries), encoding="utf-8"
        )
        return self

    # -- the call under test ---------------------------------------------------
    def paths(self):
        return dict(
            ledger_path=self.ledger,
            map_path=self.map,
            fidelity_path=self.fidelity,
            ratification_path=self.ruling,
            tests_root=self.tests,
        )

    def evaluate(self, **kw):
        opts = dict(CLEAN)
        opts.update(kw)
        return hx.evaluate(now=self._t + 3600.0, **self.paths(), **opts)


@pytest.fixture()
def repo(tmp_path):
    return _Repo(tmp_path)


def _three_clean(repo):
    for i in (1, 2, 3):
        atom = f"W1_{i}_thing"
        repo.atom(atom).spec_tied_test(atom).advance(atom)
    return repo.flush()


# ── EXIT CRITERION 2: three clean advances satisfy it ───────────────────────────


def test_three_clean_advances_satisfy_the_criterion(repo):
    v = _three_clean(repo).evaluate(test_runner=lambda files: True)
    assert v.error is None, v.error
    assert v.n_required == 3
    assert v.count == 3, [(a.atom, a.evidence.kind, a.evidence.status) for a in v.advances]
    assert v.provable is True, v.unprovable_reasons
    assert v.satisfied is True
    assert v.decision == "HARNESS_INVESTMENT_MAY_RESUME"


def test_two_clean_advances_do_not_satisfy_it(repo):
    """The counter must not round up: N is the bar, and 2 < 3."""
    for i in (1, 2):
        atom = f"W1_{i}_thing"
        repo.atom(atom).spec_tied_test(atom).advance(atom)
    v = repo.flush().evaluate(test_runner=lambda files: True)
    assert v.count == 2
    assert v.satisfied is False
    assert v.decision == "KEEP_BUILDING_PRODUCT"


def test_a_moved_fidelity_row_is_evidence_on_its_own(repo):
    """The strongest evidence kind needs no test execution at all."""
    for i in (1, 2, 3):
        atom = f"W1_{i}_thing"
        repo.atom(atom).moved_fidelity_row(atom).advance(atom)
    v = repo.flush().evaluate()  # NO test_runner
    assert v.count == 3
    assert v.satisfied is True
    assert {a.evidence.kind for a in v.advances} == {"fidelity_register_row_moved"}


# ── EXIT CRITERION 1: a synthetic stall resets the counter ──────────────────────


def test_a_synthetic_stall_resets_the_counter_to_zero(repo):
    """Inject ONE stall-class event into the span that otherwise satisfies the
    criterion. The counter must drop to zero and name the cause."""
    from background.stall_class_register import StallEvent

    repo = _three_clean(repo)
    baseline = repo.evaluate(test_runner=lambda files: True)
    assert baseline.count == 3 and baseline.satisfied is True

    stall_at = repo._entries[-1]["ts"] + 60.0  # inside the span, after the last advance
    v = repo.evaluate(
        test_runner=lambda files: True,
        stall_detector=lambda since, now: [
            StallEvent("meaningful_progress_gap", stall_at, "synthetic 240 min gap")
        ],
    )
    assert v.count == 0, [(a.atom, a.at) for a in v.advances]
    assert v.satisfied is False
    assert "meaningful_progress_gap" in (v.reset_cause or "")


def test_a_stall_mid_run_restarts_the_run_rather_than_shortening_it(repo):
    """A stall between the second and third advance does not leave a count of 2 — the
    run RESTARTS, so only the advance after the stall survives. Consecutive means
    consecutive; a counter that merely decremented could be walked past by a stall."""
    from background.stall_class_register import StallEvent

    repo = _three_clean(repo)
    mid = repo._entries[1]["ts"] + 60.0
    v = repo.evaluate(
        test_runner=lambda files: True,
        stall_detector=lambda since, now: [StallEvent("meaningful_progress_gap", mid, "mid-span")],
    )
    assert v.count == 1
    assert v.satisfied is False


def test_a_stall_before_the_run_does_not_suppress_a_later_clean_run(repo):
    """The counter is CONSECUTIVE, not all-time: a stall that predates three clean
    advances must not hold the count down forever. Without this the counter could never
    recover and the criterion would be unreachable by construction."""
    from background.stall_class_register import StallEvent

    repo = _three_clean(repo)
    early = repo._entries[0]["ts"] - 60.0
    v = repo.evaluate(
        test_runner=lambda files: True,
        stall_detector=lambda since, now: [StallEvent("meaningful_progress_gap", early, "old")],
    )
    assert v.count == 3
    assert v.satisfied is True


def test_a_stall_at_the_same_instant_as_an_advance_resets_first(repo):
    """Tie-break: a stall stamped at the same second as an advance must be applied
    BEFORE it, so the advance starts a fresh run rather than being swallowed. The
    opposite order would let a simultaneous stall be silently absorbed."""
    from background.stall_class_register import StallEvent

    repo = _three_clean(repo)
    last_advance_ts = repo._entries[-1]["ts"]
    v = repo.evaluate(
        test_runner=lambda files: True,
        stall_detector=lambda since, now: [StallEvent("meaningful_progress_gap", last_advance_ts, "tie")],
    )
    assert v.count == 1, "the final advance should survive as a fresh run of one"


def test_an_advance_lacking_its_exit_criterion_delta_resets_the_counter(repo):
    """The second ratified falsification: a level move with no resolvable delta."""
    for i in (1, 2):
        atom = f"W1_{i}_thing"
        repo.atom(atom).spec_tied_test(atom).advance(atom)
    repo.atom("W1_bare_thing").advance("W1_bare_thing")  # no test, no fidelity row
    v = repo.flush().evaluate(test_runner=lambda files: True)
    assert v.count == 0
    assert "W1_bare_thing" in (v.reset_cause or "")
    assert v.satisfied is False


def test_a_failing_acceptance_test_is_a_lacking_delta(repo):
    """"Passing spec-tied acceptance test" means PASSING. A red test is not evidence."""
    repo = _three_clean(repo)
    v = repo.evaluate(test_runner=lambda files: False)
    assert v.count == 0
    assert v.satisfied is False


# ── EXIT CRITERION 3: purity / independence (TAUTOLOGY guard) ───────────────────


def test_provenance_prose_cannot_manufacture_an_advance(repo):
    """THE tautology guard. A ledger entry's `provenance` is the mover's own account of
    its evidence. If the counter read it, the counter would be checking the claim
    against the claim — so the most florid possible provenance on an atom with NO
    fidelity row and NO spec-tied test must still count for nothing."""
    repo.atom("W1_liar").advance(
        "W1_liar",
        provenance=(
            "L0->L3. Fidelity register row moved, R11-verified on the live surface, R15 both "
            "ways with 12 mutations, exit criterion landed, acceptance test passing, green."
        ),
    )
    v = repo.flush().evaluate(test_runner=lambda files: True)
    assert v.count == 0
    assert v.advances[0].evidence.status == "absent"


def test_the_same_primary_state_gives_the_same_answer(repo):
    """A pure function of primary state: two evaluations of an unchanged repo agree.
    Nothing may be carried between ticks."""
    repo = _three_clean(repo)
    a = repo.evaluate(test_runner=lambda files: True)
    b = repo.evaluate(test_runner=lambda files: True)
    assert (a.count, a.provable, a.satisfied) == (b.count, b.provable, b.satisfied)


def test_an_incidental_atom_mention_is_not_a_spec_tie(repo):
    """Found by running the counter against the REAL repository: indexing whole-file
    text gave `W1_6b_merit_order_reconstruction` two "acceptance tests" in which the
    atom id was only a fixture string. That over-counts — the direction that declares
    the harness done on evidence that does not exist — so the spec-tie is the module
    docstring, and a mention in a fixture must not resolve."""
    repo.atom("W1_mentioned").incidental_mention("W1_mentioned").advance("W1_mentioned")
    v = repo.flush().evaluate(test_runner=lambda files: True)
    assert v.advances[0].evidence.status == "absent"
    assert v.count == 0


def test_n_is_read_from_the_ruling_not_hardcoded(repo):
    """N is the DIRECTOR's dial. Move it in the ruling and the counter moves."""
    repo.ruling.write_text("Revised: **N = 5** consecutive.\n", encoding="utf-8")
    v = _three_clean(repo).evaluate(test_runner=lambda files: True)
    assert v.n_required == 5
    assert v.count == 3
    assert v.satisfied is False, "3 must not satisfy a bar of 5"


# ── EXIT CRITERION 4: fail-closed on missing / malformed / non-finite ───────────


def test_a_missing_ledger_refuses_rather_than_reading_as_zero_advances(repo):
    repo = _three_clean(repo)
    repo.ledger.unlink()
    v = repo.evaluate(test_runner=lambda files: True)
    assert v.error is not None
    assert v.satisfied is False and v.provable is False
    assert v.decision == "REFUSED"


def test_a_malformed_ledger_line_refuses(repo):
    repo = _three_clean(repo)
    repo.ledger.write_text(repo.ledger.read_text() + "{not json\n", encoding="utf-8")
    v = repo.evaluate(test_runner=lambda files: True)
    assert v.error is not None and v.satisfied is False


def test_a_non_finite_ledger_timestamp_refuses(repo):
    """Advances that cannot be ORDERED cannot establish a consecutive run."""
    repo.atom("W1_x").spec_tied_test("W1_x").advance("W1_x", ts_override="nonsense")
    v = repo.flush().evaluate(test_runner=lambda files: True)
    assert v.error is not None and "non-finite" in v.error
    assert v.satisfied is False


def test_a_missing_ratification_doc_refuses_rather_than_assuming_n(repo):
    repo = _three_clean(repo)
    repo.ruling.unlink()
    v = repo.evaluate(test_runner=lambda files: True)
    assert v.error is not None and v.n_required is None
    assert v.satisfied is False


def test_conflicting_values_of_n_refuse_rather_than_picking_one(repo):
    repo.ruling.write_text("N = 3 was ratified, but later N = 7.\n", encoding="utf-8")
    with pytest.raises(ExitCriterionError, match="CONFLICTING"):
        hx.ratified_n(repo.ruling)


def test_a_ruling_stating_no_n_refuses(repo):
    repo.ruling.write_text("The criterion is ratified.\n", encoding="utf-8")
    with pytest.raises(ExitCriterionError, match="no 'N"):
        hx.ratified_n(repo.ruling)


def test_a_malformed_fidelity_register_refuses(repo):
    repo = _three_clean(repo)
    repo.fidelity.write_text("{ broken", encoding="utf-8")
    v = repo.evaluate(test_runner=lambda files: True)
    assert v.error is not None and v.satisfied is False


def test_a_missing_tests_root_refuses(repo):
    """An unresolvable evidence kind is not an absent one."""
    repo = _three_clean(repo)
    for p in repo.tests.iterdir():
        p.unlink()
    repo.tests.rmdir()
    v = repo.evaluate(test_runner=lambda files: True)
    assert v.error is not None and v.satisfied is False


def test_a_map_with_no_product_atoms_refuses(repo):
    """A map that parses to nothing is a parse failure, not a project with no product —
    and reading it as 'no product advances' would be the quietest possible fail-open."""
    repo.atom("H1_thing", lane="H_harness", value_stream="close_to_learn")
    repo.advance("H1_thing")
    v = repo.flush().evaluate(test_runner=lambda files: True)
    assert v.error is not None and "NO product-lane atoms" in v.error


def test_a_fidelity_row_with_no_named_baseline_is_not_evidence(repo):
    """A lift with nothing to have moved relative to is a number, not movement."""
    repo.atom("W1_x").moved_fidelity_row("W1_x", baseline="").advance("W1_x")
    v = repo.flush().evaluate()
    assert v.advances[0].evidence.status == "absent"


def test_a_non_finite_fidelity_lift_is_not_evidence(repo):
    """R15 NaN-blindness: `nan > 0` is False but `nan != 0` is True, so a naive
    non-zero test would read NaN as movement."""
    repo.atom("W1_x").moved_fidelity_row("W1_x", lift=float("nan")).advance("W1_x")
    v = repo.flush().evaluate()
    assert v.advances[0].evidence.status == "absent"


# ── provability: HX2's load-bearing consequence, obeyed ─────────────────────────


def test_an_uncovered_stall_class_makes_a_full_count_unprovable(repo):
    """HX2: while a stall class has no detector, a zero stall count is NOT proof of a
    clean span. The count may still read 3 — and `satisfied` must still be False."""
    repo = _three_clean(repo)
    v = repo.evaluate(test_runner=lambda files: True, uncovered_ids=["harden_while_content_unminted"])
    assert v.count == 3
    assert v.provable is False
    assert v.satisfied is False
    assert any("NO detector" in r for r in v.unprovable_reasons)


def test_point_kind_classes_make_a_past_span_unprovable(repo):
    """Point-kind state is overwritten in place and never committed, so its silence
    over a past span proves nothing. Sampling each tick is the named HX1 residual."""
    repo = _three_clean(repo)
    v = repo.evaluate(test_runner=lambda files: True, point_kind_ids=["publish_gate_wedged_over_an_hour"])
    assert v.count == 3 and v.provable is False and v.satisfied is False
    assert any("point-kind" in r for r in v.unprovable_reasons)


def test_an_unavailable_detector_is_a_failed_check_not_a_clean_span(repo):
    from background.stall_class_register import StallEvent

    repo = _three_clean(repo)
    v = repo.evaluate(
        test_runner=lambda files: True,
        stall_detector=lambda since, now: [
            StallEvent("meaningful_progress_gap", None, "git unreadable", unavailable=True)
        ],
    )
    assert v.count == 3, "an unavailable check is not a stall EVENT, so it does not reset"
    assert v.provable is False and v.satisfied is False
    assert any("UNAVAILABLE" in r for r in v.unprovable_reasons)


def test_a_detector_that_raises_is_treated_as_unavailable(repo):
    def boom(since, now):
        raise RuntimeError("git exploded")

    repo = _three_clean(repo)
    v = repo.evaluate(test_runner=lambda files: True, stall_detector=boom)
    assert v.provable is False and v.satisfied is False


def test_unexecuted_acceptance_tests_block_provability_without_resetting(repo):
    """'The evidence exists but was not executed' is neither confirmation nor a lack.
    Collapsing it into either direction would be wrong: into confirmed is fail-open,
    into absent would call a real advance a falsification."""
    repo = _three_clean(repo)
    v = repo.evaluate()  # no runner
    assert v.count == 0, "unchecked advances do not increment"
    assert v.reset_cause is None, "unchecked advances do not reset either"
    assert v.provable is False and v.satisfied is False


def test_a_runner_that_raises_leaves_the_evidence_unchecked(repo):
    def boom(files):
        raise OSError("pytest not found")

    repo = _three_clean(repo)
    v = repo.evaluate(test_runner=boom)
    assert {a.evidence.status for a in v.advances} == {"unchecked"}
    assert v.satisfied is False


# ── scope: what counts as a product-content advance ─────────────────────────────


def test_harness_lane_atoms_are_not_content_advances(repo):
    for i in (1, 2, 3):
        atom = f"W1_{i}_thing"
        repo.atom(atom).spec_tied_test(atom).advance(atom)
    repo.atom("H9_map_writes", lane="H_harness", value_stream="wholesale_to_price")
    repo.spec_tied_test("H9_map_writes").advance("H9_map_writes")
    v = repo.flush().evaluate(test_runner=lambda files: True)
    assert "H9_map_writes" not in {a.atom for a in v.advances}
    assert v.count == 3, "a harness level move must neither add to nor reset the product run"


def test_close_to_learn_machinery_is_not_a_content_advance(repo):
    """Both markers exclude independently — an atom cannot escape by carrying only one."""
    repo.atom("B9_machinery", lane="B_commercial", value_stream="close_to_learn")
    repo.spec_tied_test("B9_machinery").advance("B9_machinery")
    v = repo.flush().evaluate(test_runner=lambda files: True)
    assert v.error is not None and "NO product-lane atoms" in v.error


def test_a_proposed_level_is_not_a_reached_level(repo):
    """The criterion says atoms must REACH their next level. A LEVEL_UP_PROPOSED entry
    is a proposal; counting it would let the counter be advanced by intent alone."""
    repo.atom("W1_x").spec_tied_test("W1_x").advance("W1_x", action="LEVEL_UP_PROPOSED")
    v = repo.flush().evaluate(test_runner=lambda files: True)
    assert v.advances == ()
    assert v.count == 0


def test_an_atom_no_longer_in_the_map_is_not_counted(repo):
    repo.atom("W1_x").spec_tied_test("W1_x").advance("W1_x")
    repo.advance("W1_deleted_atom")
    v = repo.flush().evaluate(test_runner=lambda files: True)
    assert {a.atom for a in v.advances} == {"W1_x"}


# ── R12: this is a gate on ONE decision, never a score ──────────────────────────


def test_the_verdict_names_a_decision_not_a_score(repo):
    """R12 binding: the counter gates 'may harness investment resume' and nothing else.
    Its public verdict vocabulary must stay decision-shaped so it cannot be quoted as a
    quality or fidelity number."""
    v = _three_clean(repo).evaluate(test_runner=lambda files: True)
    assert v.decision in {"HARNESS_INVESTMENT_MAY_RESUME", "KEEP_BUILDING_PRODUCT", "REFUSED"}


def test_the_summary_line_states_unprovable_rather_than_claiming_a_clean_span(repo):
    repo = _three_clean(repo)
    v = repo.evaluate(test_runner=lambda files: True, uncovered_ids=["harden_while_content_unminted"])
    line = hx.summary_line(v)
    assert "NOT PROVABLY clean" in line
    assert "MET" not in line


def test_the_summary_line_reports_a_refusal_loudly(repo):
    repo = _three_clean(repo)
    repo.ledger.unlink()
    line = hx.summary_line(repo.evaluate(test_runner=lambda files: True))
    assert "REFUSED" in line


# ── the real repository: the module must run against it without blowing up ──────


def test_it_runs_against_the_real_repository_and_does_not_claim_satisfaction(repo):
    """A live smoke test on real primary state. It deliberately asserts only what is
    structurally true regardless of how the project advances: HX2 left two stall classes
    uncovered, so the real span cannot yet be PROVEN clean, so `satisfied` is False.
    If this ever fails, either the holes were closed (good — and this test should be
    updated deliberately, not silently) or the provability guard has been weakened."""
    v = hx.evaluate()
    assert v.error is None, v.error
    assert v.n_required == 3
    assert v.provable is False
    assert v.satisfied is False
    assert v.advances, "the real ledger has product-content level moves"
