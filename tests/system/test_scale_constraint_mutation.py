"""R15 proof for every scale-constraint check — `AO4_scale_constraints_executable`.

Design: `docs/design/SCALE_CONSTRAINT_CHECKS.md` §4.

> *A constraint check that passes when the constraint is broken.*

That is the fail-open shape for this tier, and it is the whole risk: a check that
asserts "the code ran and produced a number" passes just as happily when the
constraint it names has been abandoned. **No control counts as evidence unless a
mutation test proves it fires on its own named defect** (R15).

The discipline, inherited verbatim from `test_join_cut_mutation.py`:

- The probe and its assertion live in `scale_constraints.py` and are imported
  *here and by the standing test* — the mutation runs the SAME assertion that
  ships. A mutation test carrying its own copy of the assertion proves something
  about the copy (`feedback_tautology_reappears_inside_r15_tests`).
- Each cut is made in the **production source** (monkeypatched at the module
  attribute the probe actually calls), not in the probe's fixture, except where
  the check's subject IS a file population — there the mutation is a mutated
  population handed to the same shipped assertion.
- Where a check is RED on the real tree today, the mutation runs in BOTH
  directions: a clean fixture must make it PASS. A control that can only fail is
  not a control (`feedback_control_that_can_only_fail_wedges`) — it is a wedge
  with a diagnostic message.
"""

import dataclasses
import textwrap

import pytest

from company.governance import decision_rights
from company.interfaces.bitemporal_event_log import BitemporalEventLog
from saas import bill_generator
from tests.system import scale_constraints as sc

pytestmark = pytest.mark.scale_report_only


# ── C-S1(a) — the bill must not read its inputs positionally ─────────────────

def test_cs1_order_check_fires_when_the_generator_reads_positionally(monkeypatch):
    """CUT: make the REAL bill generator carry one field derived from the FIRST
    record — the exact "assumes a delivery order" defect C-S1 forbids."""
    real = bill_generator.generate_bill

    def positional(customer_id, settlement_records, contract_type, *args, **kwargs):
        bill = dict(real(customer_id, settlement_records, contract_type, *args, **kwargs))
        bill["first_period_seen"] = settlement_records[0]["settlement_period"]
        return bill

    monkeypatch.setattr(bill_generator, "generate_bill", positional)
    with pytest.raises(AssertionError, match="C-S1 BROKEN"):
        sc.assert_arrival_order_tolerance(sc.probe_bill_arrival_order())


# ── C-S1(b) — late arrival must resolve by transaction time ──────────────────

def test_cs1_late_arrival_check_fires_when_the_log_resolves_by_append_order(monkeypatch):
    """CUT: make the REAL log return the most recently APPENDED record instead of
    the one that was knowable at the decision time. That is a look-ahead leak
    dressed as a storage detail."""
    def last_appended(self, decision_time, entity_id, fact_type, valid_time=None):
        matches = [
            r for r in self._records
            if r.entity_id == entity_id and r.fact_type == fact_type
        ]
        return None if not matches else self._decouple(matches[-1])

    monkeypatch.setattr(BitemporalEventLog, "as_known_at", last_appended)
    with pytest.raises(AssertionError, match="C-S1 BROKEN"):
        sc.assert_late_arrival_tolerance(sc.probe_late_arrival_visibility())


# ── C-S2(a) — duplicate delivery must be harmless ────────────────────────────

def test_cs2_idempotency_check_fires_when_the_generator_carries_state(monkeypatch):
    """CUT: give the REAL bill generator state that survives between calls, so a
    retry of the same input restates the customer's money."""
    real = bill_generator.generate_bill
    calls = {"n": 0}

    def stateful(*args, **kwargs):
        calls["n"] += 1
        bill = dict(real(*args, **kwargs))
        bill["total_amount_gbp"] = bill["total_amount_gbp"] * calls["n"]
        return bill

    monkeypatch.setattr(bill_generator, "generate_bill", stateful)
    with pytest.raises(AssertionError, match="C-S2 BROKEN"):
        sc.assert_duplicate_delivery_is_harmless(sc.probe_duplicate_delivery())


def test_cs2_idempotency_check_fires_when_redelivery_changes_the_read(monkeypatch):
    """CUT: the other half — make the store RESTATE on re-delivery rather than
    accept a duplicate as a no-op, so the second copy of an event changes what is
    read back.

    (The record itself is a frozen dataclass, so the cut has to REPLACE the entry
    rather than assign into it — the store's own immutability is why the weaker
    "just mutate the field" cut is not available. That is the constraint holding,
    not the test being awkward.)
    """
    real_record = BitemporalEventLog.record

    def restating_record(self, entity_id, fact_type, valid_time, transaction_time,
                         value, superseded_by_run=None):
        rec = real_record(self, entity_id, fact_type, valid_time, transaction_time,
                          value, superseded_by_run)
        if len(self._records) > 1:
            self._records[-1] = dataclasses.replace(
                self._records[-1], value={"kwh": -1.0}
            )
        return rec

    monkeypatch.setattr(BitemporalEventLog, "record", restating_record)
    with pytest.raises(AssertionError, match="C-S2 BROKEN"):
        sc.assert_duplicate_delivery_is_harmless(sc.probe_duplicate_delivery())


# ── C-S2(b)/A1 — RNG substream discipline ────────────────────────────────────

def _write_pkg(base, pkg_name, filename, body):
    pkg = base / pkg_name
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "__init__.py").write_text("")
    (pkg / filename).write_text(textwrap.dedent(body))
    return pkg


def test_cs2_global_rng_scan_fires_on_a_module_level_draw(tmp_path):
    """CUT: a module that draws from the PROCESS-GLOBAL stream — the 01:09Z
    incident's shape. The population is mutated (that is what this check's
    subject IS), the assertion is the shipped one."""
    _write_pkg(tmp_path, "simulation", "churn.py", """
        import random

        def draw_churn(customer_id):
            return random.random() < 0.02
    """)
    record = sc.probe_global_rng_users(packages=("simulation",), base=tmp_path)
    with pytest.raises(AssertionError, match="C-S2/A1 BROKEN"):
        sc.assert_no_global_rng_draws(record, allowed=set())


def test_cs2_global_rng_scan_does_not_fire_on_a_named_substream(tmp_path):
    """THE FALSE-POSITIVE DIRECTION, which matters as much: `random.Random(seed)`
    is the COMPLIANT construct, and so is `rng.random()` on an instance. A
    detector that flags them jams the pipeline against correct code
    (`feedback_control_false_positive_jams_pipeline`)."""
    _write_pkg(tmp_path, "simulation", "compliant.py", """
        import hashlib
        import random

        def _substream(base_seed, name):
            digest = hashlib.sha256(f"{base_seed}:{name}".encode()).digest()
            return random.Random(int.from_bytes(digest[:8], "big"))

        def draw(customer_id):
            rng = _substream(7, "churn")
            return rng.random(), rng.choice([1, 2, 3])
    """)
    record = sc.probe_global_rng_users(packages=("simulation",), base=tmp_path)
    assert record["modules_scanned"] > 0, "fixture did not get scanned at all"
    sc.assert_no_global_rng_draws(record, allowed=set())  # must NOT raise


def test_cs2_global_rng_scan_fails_when_it_scans_nothing(tmp_path):
    """FAIL-SILENT proof. An unavailable check is a FAILED check (R15): pointed at
    a package that does not exist, the guard must raise, not report 'compliant'."""
    record = sc.probe_global_rng_users(packages=("nowhere",), base=tmp_path)
    with pytest.raises(AssertionError, match="vacuous"):
        sc.assert_no_global_rng_draws(record, allowed=set())


def test_cs2_substream_independence_check_fires_on_a_shared_stream(monkeypatch):
    """CUT: collapse the REAL substream derivation onto ONE shared generator —
    exactly what adding a draw to a shared stream does to replay."""
    import random as _random

    from simulation import population_draw

    shared = _random.Random(1234)
    monkeypatch.setattr(population_draw, "_substream", lambda base_seed, salt="": shared)
    with pytest.raises(AssertionError, match="C-S2/A1 BROKEN"):
        sc.assert_substream_independence(sc.probe_substream_independence())


# ── C-S3 — asynchronous wall contracts ───────────────────────────────────────

def test_cs3_check_fires_when_the_pending_interval_is_not_representable(monkeypatch):
    """CUT: make the REAL pending surface always empty — a request that is never
    observably in flight is a synchronous contract wearing an async schema."""
    monkeypatch.setattr(
        decision_rights, "pending_decision_requests_as_of",
        lambda *a, **k: [],
    )
    with pytest.raises(AssertionError, match="C-S3 BROKEN"):
        sc.assert_request_and_response_are_separate_events(sc.probe_request_response_split())


def test_cs3_check_fires_when_latency_is_estimated_rather_than_measured(monkeypatch):
    """CUT: report the SLA instead of the real gap. This is the subtler defect —
    the schema still has two events, but the number that would tell you the wall
    is slow is fabricated."""
    real = decision_rights.resolve_decision_request

    def estimating(*args, **kwargs):
        event = real(*args, **kwargs)
        object.__setattr__(event, "actual_elapsed_seconds", event.expected_elapsed_seconds)
        return event

    monkeypatch.setattr(decision_rights, "resolve_decision_request", estimating)
    with pytest.raises(AssertionError, match="C-S3 BROKEN"):
        sc.assert_request_and_response_are_separate_events(sc.probe_request_response_split())


def test_cs3_same_step_check_passes_when_a_same_instant_answer_is_refused(monkeypatch):
    """BOTH DIRECTIONS for the residual check. It is red on the real mechanism
    today; this proves it is not a control that can ONLY be red — give it a
    mechanism that refuses a zero-latency answer and it goes green."""
    real = decision_rights.resolve_decision_request

    def refusing(*args, **kwargs):
        event = real(*args, **kwargs)
        if not event.actual_elapsed_seconds:
            raise ValueError("a decision request cannot be answered in the instant it was made")
        return event

    monkeypatch.setattr(decision_rights, "resolve_decision_request", refusing)
    sc.assert_same_step_resolution_is_rejected(sc.probe_same_step_resolution())  # must NOT raise


# ── C-S4 — persistence behind an interface ───────────────────────────────────

def _point_mirror_register_at(monkeypatch, tmp_path, pairs, dest_dir, published=None):
    """Point the register at a throwaway tree AND stub the published-blob reader.

    `published` maps repo-relative path -> content as it would appear in the
    commit. Stubbing the reader (rather than building a scratch git repo) keeps
    the mutation on the thing under test — the COMPARISON — while the shipped
    assertion runs unchanged. The real reader has its own coverage in
    `test_scale_constraints.py`, which runs it against this repo's actual HEAD.
    """
    from tools import mirror_github_pages

    monkeypatch.setattr(mirror_github_pages, "_STATE_JSON_FILES", pairs)
    monkeypatch.setattr(mirror_github_pages, "DOCS_STATE", dest_dir)
    monkeypatch.setattr(sc, "ROOT", tmp_path)
    if published is not None:
        monkeypatch.setattr(sc, "_read_published", lambda rel: published.get(rel))


def _cs4_tree(tmp_path):
    src_dir, dest_dir = tmp_path / "site" / "state", tmp_path / "docs" / "state"
    src_dir.mkdir(parents=True)
    dest_dir.mkdir(parents=True)
    return src_dir, dest_dir


def test_cs4_check_passes_on_a_faithfully_mirrored_pair(monkeypatch, tmp_path):
    """BOTH DIRECTIONS, and this one first: without it, "the check fires on drift"
    would be equally satisfied by an assertion that can never pass."""
    src_dir, dest_dir = _cs4_tree(tmp_path)
    _point_mirror_register_at(
        monkeypatch, tmp_path, [(src_dir / "ledger.json", "ledger.json")], dest_dir,
        published={
            "site/state/ledger.json": '{"balance_gbp": 12.5, "n": 3}',
            # Same CONTENT, different formatting — a mirror is not required to be
            # byte-identical, only to say the same thing.
            "docs/state/ledger.json": '{"n": 3,\n "balance_gbp": 12.5}',
        },
    )
    sc.assert_durable_state_is_not_forked(sc.probe_durable_state_duplication())


def test_cs4_check_fires_when_a_derived_copy_disagrees_with_its_source(monkeypatch, tmp_path):
    """CUT: the copy says a different number. This is the money-in-duplicate
    defect the structural audit named (FINDING 2) — 'which copy is the truth?'"""
    src_dir, dest_dir = _cs4_tree(tmp_path)
    _point_mirror_register_at(
        monkeypatch, tmp_path, [(src_dir / "ledger.json", "ledger.json")], dest_dir,
        published={
            "site/state/ledger.json": '{"balance_gbp": 12.5}',
            "docs/state/ledger.json": '{"balance_gbp": 99.0}',
        },
    )
    with pytest.raises(AssertionError, match="C-S4 BROKEN"):
        sc.assert_durable_state_is_not_forked(sc.probe_durable_state_duplication())


def test_cs4_check_fires_on_an_undeclared_duplicate(monkeypatch, tmp_path):
    """CUT: a second copy of durable state that the register does not mention, so
    nothing says which one is derived."""
    src_dir, dest_dir = _cs4_tree(tmp_path)
    # Undeclared: same filename in two roots, absent from the register. This half
    # is a FILESYSTEM question (does a rogue copy exist at all?), not a published
    # -content one, so it reads the tree.
    (src_dir / "rogue.json").write_text("{}")
    (dest_dir / "rogue.json").write_text("{}")
    _point_mirror_register_at(
        monkeypatch, tmp_path, [(src_dir / "ledger.json", "ledger.json")], dest_dir,
        published={
            "site/state/ledger.json": '{"balance_gbp": 12.5}',
            "docs/state/ledger.json": '{"balance_gbp": 12.5}',
        },
    )
    with pytest.raises(AssertionError, match="C-S4 BROKEN"):
        sc.assert_durable_state_is_not_forked(sc.probe_durable_state_duplication())


def test_cs4_check_fails_when_nothing_could_be_read_as_published(monkeypatch, tmp_path):
    """FAIL-SILENT proof, and the one this check most plausibly ships with: the
    register declares pairs but none of them resolve (a renamed path, a file that
    was never committed). "No drift found" over an unreadable population must
    FAIL, not pass — an unavailable check is a FAILED check (R15)."""
    src_dir, dest_dir = _cs4_tree(tmp_path)
    _point_mirror_register_at(
        monkeypatch, tmp_path, [(src_dir / "ledger.json", "ledger.json")], dest_dir,
        published={},  # nothing resolves
    )
    with pytest.raises(AssertionError, match="vacuous"):
        sc.assert_durable_state_is_not_forked(sc.probe_durable_state_duplication())


def test_cs4_check_fails_when_the_register_is_empty(monkeypatch, tmp_path):
    """FAIL-OPEN proof: an empty register must not read as 'nothing has drifted'."""
    dest_dir = tmp_path / "docs" / "state"
    dest_dir.mkdir(parents=True)
    _point_mirror_register_at(monkeypatch, tmp_path, [], dest_dir, published={})
    with pytest.raises(AssertionError, match="vacuous"):
        sc.assert_durable_state_is_not_forked(sc.probe_durable_state_duplication())


# ── C-S5 — time-scale invariance declaration ─────────────────────────────────

_MAP_FIXTURE = """
- id: C99_a_company_atom
  lane: C_customer_ops
  level_current: 3
- id: W99_a_world_atom
  lane: W1_market_weather
  level_current: 3
- id: C98_not_yet_l3
  lane: C_customer_ops
  level_current: 2
"""


def _point_cs5_at(monkeypatch, tmp_path, register_yaml, map_yaml=_MAP_FIXTURE):
    reg = tmp_path / "register.yaml"
    mp = tmp_path / "map.yaml"
    reg.write_text(register_yaml)
    mp.write_text(map_yaml)
    monkeypatch.setattr(sc, "TIME_SCALE_REGISTER", reg)
    monkeypatch.setattr(sc, "MATURITY_MAP", mp)


def test_cs5_check_fires_on_an_undeclared_company_side_l3_atom(monkeypatch, tmp_path):
    """CUT: an atom reaches L3+ on the company side and says nothing."""
    _point_cs5_at(monkeypatch, tmp_path, "declarations: []\nexceptions: []\n")
    with pytest.raises(AssertionError, match="C-S5 BROKEN"):
        sc.assert_time_scale_declarations_cover_the_population(
            sc.probe_time_scale_declarations()
        )


def test_cs5_check_passes_once_the_atom_declares(monkeypatch, tmp_path):
    """The other direction — a declaration genuinely satisfies it."""
    _point_cs5_at(
        monkeypatch, tmp_path,
        "declarations:\n  - atom_id: C99_a_company_atom\n    invariant: true\nexceptions: []\n",
    )
    sc.assert_time_scale_declarations_cover_the_population(sc.probe_time_scale_declarations())


def test_cs5_amnesty_cannot_grow(monkeypatch, tmp_path):
    """CUT: park a NEW undeclared atom in the landing amnesty. The frozen pin is
    what stops the escape hatch — an amnesty without an 'exactly this' bound
    measures nothing (`feedback_forgiveness_baseline_needs_a_once_only_guard`)."""
    _point_cs5_at(
        monkeypatch, tmp_path,
        "declarations: []\nexceptions: []\nundeclared_at_landing:\n  - C99_a_company_atom\n",
    )
    with pytest.raises(AssertionError, match="AMNESTY MOVED"):
        sc.assert_time_scale_declarations_cover_the_population(
            sc.probe_time_scale_declarations(), frozen_baseline=set()
        )


def test_cs5_amnesty_entry_that_gets_declared_must_be_removed(monkeypatch, tmp_path):
    """CUT: an atom is BOTH declared and still in the amnesty. Left alone, the pin
    would outlive the thing it pins and silently protect nothing."""
    _point_cs5_at(
        monkeypatch, tmp_path,
        "declarations:\n  - atom_id: C99_a_company_atom\n    invariant: true\n"
        "exceptions: []\nundeclared_at_landing:\n  - C99_a_company_atom\n",
    )
    with pytest.raises(AssertionError, match="STALE AMNESTY"):
        sc.assert_time_scale_declarations_cover_the_population(
            sc.probe_time_scale_declarations(),
            frozen_baseline={"C99_a_company_atom"},
        )


def test_cs5_check_fails_when_the_map_is_unreadable(monkeypatch, tmp_path):
    """FAIL-OPEN proof: a map that parses to nothing must not read as 'everyone is
    covered'. This is the exact shape that let a population control pass 1557/1557
    while the field was absent."""
    _point_cs5_at(monkeypatch, tmp_path, "declarations: []\nexceptions: []\n", map_yaml="[]\n")
    with pytest.raises(AssertionError, match="vacuous"):
        sc.assert_time_scale_declarations_cover_the_population(
            sc.probe_time_scale_declarations()
        )


def test_cs5_check_ignores_world_and_harness_lanes(monkeypatch, tmp_path):
    """SCOPE. C-S5 binds COMPANY-SIDE atoms; a W-lane atom at L3 must not be
    demanded. Without this the check would be measuring a population the
    constraint never named."""
    _point_cs5_at(
        monkeypatch, tmp_path,
        "declarations:\n  - atom_id: C99_a_company_atom\n    invariant: true\nexceptions: []\n",
    )
    record = sc.probe_time_scale_declarations()
    assert record["owed"] == {"C99_a_company_atom"}, (
        f"the owed population is wrong: {sorted(record['owed'])}"
    )
