"""The five scale-constraint probes and their assertions — `AO4_scale_constraints_executable`.

Design: `docs/design/SCALE_CONSTRAINT_CHECKS.md`.
Constraints: `docs/staging/done/PRODUCTION_READINESS_SCALE_ADDENDUM.md` C-S1..C-S5.

Why probes and assertions live HERE rather than inside each test module
-----------------------------------------------------------------------
Same discipline as `chains.py`, for the same R15 reason. The fail-open shape
this tier defends against is *a constraint check that passes when the constraint
is broken*, and the only proof against it is to break the constraint in the
production source and show the assertion fires. That proof is worthless unless
the mutation test runs **the same assertion that ships**
(`feedback_tautology_reappears_inside_r15_tests`: only mutating the source finds
it; a mutation test carrying its own copy of the assertion proves something about
the copy).

So each constraint is a pair:

  probe_<name>(...) -> dict     drives REAL production functions / reads REAL state
  assert_<name>(record)         raises AssertionError if the constraint is broken

`test_scale_constraints.py` calls the pair on the tree as it is.
`test_scale_constraint_mutation.py` imports the *same* pair, breaks one thing,
and asserts the *same* assertion raises.

Every probe asserts its OWN PREMISE before returning: if the two things it
compares do not actually differ at the input, it raises rather than handing back
a comparison that would pass vacuously
(`feedback_population_control_needs_a_vacuity_guard` — 1557/1557 passed while the
field was absent).

Like `chains.py`, this module deliberately sees both sides of the epistemic wall
and must stay unreachable from shippable code — enforced by
`test_report_only_landing.py::test_no_production_module_imports_the_test_tree`,
which covers the whole of `tests/system/`.
"""

from __future__ import annotations

import ast
import datetime as dt
import json
import random
import subprocess
from pathlib import Path
from typing import Any

import yaml

from company.governance import decision_rights
from company.interfaces.bitemporal_event_log import BitemporalEventLog

# ── production sources under test — imported at module scope so a monkeypatch
# against the SOURCE module (the R15 break) is seen by the probes below ───────
from saas import bill_generator

ROOT = Path(__file__).resolve().parents[2]

#: The lanes whose atoms are COMPANY-SIDE — the layer that makes decisions behind
#: the epistemic wall. C-S5 binds "any company-side atom claiming maturity L3+",
#: so the population has to be named somewhere; naming it here (rather than
#: "every atom") keeps the check on the constraint's actual subject. W* lanes are
#: the world, H*/G* are the harness — neither is company-side logic.
COMPANY_SIDE_LANE_PREFIXES = ("A_", "B_", "C_", "D_", "E_", "F_")

TIME_SCALE_REGISTER = ROOT / "docs" / "design" / "TIME_SCALE_INVARIANCE_REGISTER.yaml"
MATURITY_MAP = ROOT / "docs" / "design" / "maturity_map.yaml"


# ══════════════════════════════════════════════════════════════════════════════
# C-S1 — EVENT-ARRIVAL TOLERANCE
#   "No company-side logic may assume batch completeness. Every decision,
#    valuation, or state update must behave correctly when the events it
#    consumes arrive one at a time, late, and out of order."
#
# Two probes, because the constraint has two halves that fail differently:
#   (a) ORDER — the same events, permuted, must produce the same answer
#   (b) LATENESS — an event that arrives after a later-stamped one must not
#       retroactively become visible to a decision taken before it
# ══════════════════════════════════════════════════════════════════════════════

def probe_bill_arrival_order(*, customer_id: str = "SCALE-CS1-1") -> dict:
    """Bill one customer's settlement records in canonical, reversed and
    shuffled arrival order, through the REAL bill generator.

    A real settlement feed does not arrive sorted. If `generate_bill` reads
    anything positionally — first record wins for a period boundary, last record
    sets a rate — the three bills diverge and the company's money depends on
    delivery order.
    """
    periods = 48
    records = [
        {
            "customer_id": customer_id,
            "settlement_date": "2023-02-28",
            "settlement_period": p,
            # DELIBERATELY NOT UNIFORM: identical records are invariant under
            # permutation for trivial reasons, so a uniform fixture would pass
            # even against a positional bug.
            "consumption_kwh": 5.0 + p * 0.25,
            "revenue_gbp": (5.0 + p * 0.25) / 1000.0 * 140.0,
            "wholesale_cost_gbp": (5.0 + p * 0.25) / 1000.0 * 60.0,
        }
        for p in range(1, periods + 1)
    ]

    # PREMISE: the records must be genuinely distinguishable, or permuting them
    # is a no-op and the comparison below is vacuous.
    volumes = {r["consumption_kwh"] for r in records}
    if len(volumes) != len(records):
        raise AssertionError(
            "probe premise violated: settlement records are not distinguishable, "
            "so arrival order cannot possibly change the answer"
        )

    reversed_records = list(reversed(records))
    shuffled = list(records)
    random.Random(20260809).shuffle(shuffled)
    # PREMISE: the shuffle must genuinely have moved something.
    if [r["settlement_period"] for r in shuffled] == [r["settlement_period"] for r in records]:
        raise AssertionError("probe premise violated: the shuffled order is the canonical order")

    return {
        "canonical": bill_generator.generate_bill(customer_id, records, "fixed"),
        "reversed": bill_generator.generate_bill(customer_id, reversed_records, "fixed"),
        "shuffled": bill_generator.generate_bill(customer_id, shuffled, "fixed"),
    }


def assert_arrival_order_tolerance(record: dict) -> None:
    """C-S1(a). The bill must not depend on the order its inputs arrived in."""
    canonical = record["canonical"]
    for label in ("reversed", "shuffled"):
        other = record[label]
        differing = {
            k: (canonical.get(k), other.get(k))
            for k in set(canonical) | set(other)
            if canonical.get(k) != other.get(k)
        }
        assert not differing, (
            f"C-S1 BROKEN — the bill changed when its settlement records arrived in "
            f"{label} order. Company-side logic is assuming a delivery order it will "
            f"not get at scale. Fields that moved: {differing}"
        )


def probe_late_arrival_visibility() -> dict:
    """Append three facts to the REAL bitemporal log in the WRONG order — the
    latest-stamped one first, then the two that were 'in flight' — and read the
    log back as of each decision time.

    This is the arrival shape the sim can never produce: sim-time hands a whole
    period's events to the code at once, so nothing here is ever late.
    """
    log = BitemporalEventLog()
    t = [dt.datetime(2023, 2, d, 12, 0, tzinfo=dt.timezone.utc) for d in (1, 2, 3)]
    values = [100.0, 200.0, 300.0]
    # PREMISE: the values must differ, or "the right one is visible" is vacuous.
    if len(set(values)) != len(values):
        raise AssertionError("probe premise violated: the three facts are indistinguishable")

    # OUT OF ORDER ON PURPOSE: index 2 (the newest) is appended first.
    for i in (2, 0, 1):
        log.record(
            entity_id="SCALE-CS1-2",
            fact_type="consumption_estimate",
            valid_time=dt.date(2023, 2, 28),
            transaction_time=t[i],
            value=values[i],
        )

    seen = {}
    for i, decision_time in enumerate(t):
        rec = log.as_known_at(decision_time, "SCALE-CS1-2", "consumption_estimate")
        seen[i] = None if rec is None else rec.value
    return {"seen": seen, "values": values}


def assert_late_arrival_tolerance(record: dict) -> None:
    """C-S1(b). A late-arriving event must not be visible to a decision taken
    before its transaction_time, and an out-of-order APPEND must not make the
    newest fact win at every earlier decision time.

    That second half is the real fail: a store that returns "the last thing
    appended" reads as a look-ahead leak — the company sees a fact it could not
    have had.
    """
    seen, values = record["seen"], record["values"]
    for i, expected in enumerate(values):
        assert seen[i] == expected, (
            "C-S1 BROKEN — reading as-of the moment fact "
            f"{i} became knowable returned {seen[i]!r}, not {expected!r}. "
            "Events that arrived out of order are being resolved by APPEND order "
            "instead of by transaction time, so the company can see facts that had "
            "not arrived yet."
        )


# ══════════════════════════════════════════════════════════════════════════════
# C-S2 — IDEMPOTENCY, DETERMINISTIC REPLAY, AND RNG SUBSTREAM DISCIPLINE (A1)
#   "Processing the same event twice must be harmless; replaying an event
#    history must reproduce identical state."
#   A1: "each stochastic subsystem draws from its own NAMED, SEEDED substream,
#    so adding a draw in one subsystem cannot perturb any other."
# ══════════════════════════════════════════════════════════════════════════════

def probe_duplicate_delivery() -> dict:
    """Deliver the SAME event twice to the REAL log and re-run the REAL bill
    generator on the same input twice.

    At-least-once delivery is what a queue gives you. Duplicate delivery is not a
    hypothetical at scale; it is the normal case.
    """
    log = BitemporalEventLog()
    tt = dt.datetime(2023, 2, 2, 12, 0, tzinfo=dt.timezone.utc)
    args = dict(
        entity_id="SCALE-CS2-1",
        fact_type="meter_read",
        valid_time=dt.date(2023, 2, 28),
        transaction_time=tt,
        value={"kwh": 412.0},
    )
    log.record(**args)
    once = log.as_known_at(tt, "SCALE-CS2-1", "meter_read")
    log.record(**args)  # the SAME event, delivered again
    twice = log.as_known_at(tt, "SCALE-CS2-1", "meter_read")

    records = [
        {
            "customer_id": "SCALE-CS2-1",
            "settlement_date": "2023-02-28",
            "settlement_period": p,
            "consumption_kwh": 8.0,
            "revenue_gbp": 8.0 / 1000.0 * 140.0,
            "wholesale_cost_gbp": 8.0 / 1000.0 * 60.0,
        }
        for p in range(1, 49)
    ]
    return {
        "read_once": None if once is None else once.value,
        "read_twice": None if twice is None else twice.value,
        "bill_first": bill_generator.generate_bill("SCALE-CS2-1", records, "fixed"),
        "bill_second": bill_generator.generate_bill("SCALE-CS2-1", records, "fixed"),
    }


def assert_duplicate_delivery_is_harmless(record: dict) -> None:
    """C-S2(a). Re-delivering an event, and re-running a valuation, must not
    change the answer."""
    assert record["read_once"] is not None, (
        "probe is vacuous: the first delivery was not readable at all"
    )
    assert record["read_twice"] == record["read_once"], (
        "C-S2 BROKEN — the same event delivered twice changed what the log reads "
        f"back: {record['read_once']!r} -> {record['read_twice']!r}"
    )
    assert record["bill_second"] == record["bill_first"], (
        "C-S2 BROKEN — billing the same inputs twice produced different bills, so "
        "the generator is carrying state between calls and a retry would restate "
        "the customer's money"
    )


#: Modules under `simulation/` that draw from the PROCESS-GLOBAL `random` module
#: rather than their own named substream, as of this tier's landing. Bounded
#: EXACTLY, not as a floor: a new offender fails, and so does a FIXED one (which
#: forces the stale pin out rather than letting it silently protect nothing —
#: `feedback_forgiveness_baseline_needs_a_once_only_guard`).
KNOWN_GLOBAL_RNG_MODULES: set[str] = set()  # populated by the landing sweep below


#: The packages that carry stochastic logic. All four are scanned, so a draw
#: added on the company side of the wall is caught by the same guard as one added
#: in the world.
STOCHASTIC_PACKAGES = ("simulation", "sim", "company", "saas")


def probe_global_rng_users(
    packages: tuple[str, ...] = STOCHASTIC_PACKAGES, base: Path | None = None
) -> dict:
    """AST-scan packages for calls to the MODULE-LEVEL `random` functions.

    This is A1's defect at the CLASS, not the instance. The 01:09Z incident was a
    new draw on a SHARED stream shifting every subsequent draw and destroying
    replay. `random.random()` is that shared stream by construction: every module
    in the process draws from one generator, so adding a draw anywhere moves
    everything downstream everywhere.

    Detected structurally (an `ast.Attribute` whose value is the `random` NAME),
    not by substring — a substring detector reads `self.random()` and
    `rng.random()` as offences and an aliased import as clean, which is the
    control-fidelity defect already fixed once in `test_publish_gate_scope.py`.
    """
    root = base or ROOT
    offenders: dict[str, list[str]] = {}
    scanned = 0
    paths = [p for pkg in packages for p in sorted((root / pkg).rglob("*.py"))]
    for path in paths:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        scanned += 1
        # Only count `random` if it is the stdlib module bound by an import in
        # THIS file — a local variable called `random` is not the global stream.
        imports_random = any(
            (isinstance(n, ast.Import) and any(a.name == "random" and a.asname is None
                                               for a in n.names))
            for n in ast.walk(tree)
        )
        if not imports_random:
            continue
        hits = sorted({
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "random"
            # `random.Random(...)` CREATES an isolated generator — that is the
            # compliant construct, not the offence.
            and node.func.attr not in {"Random", "SystemRandom"}
        })
        if hits:
            offenders[str(path.relative_to(root))] = hits
    return {"offenders": offenders, "modules_scanned": scanned}


def assert_no_global_rng_draws(record: dict, allowed: set[str] | None = None) -> None:
    """C-S2(b) / A1. Every stochastic subsystem draws from its OWN generator."""
    allowed = KNOWN_GLOBAL_RNG_MODULES if allowed is None else allowed
    assert record["modules_scanned"] > 0, (
        "probe is vacuous: no modules were scanned at all, so 'no offenders' means "
        "nothing (fail-open — an unavailable check is a FAILED check, R15)"
    )
    found = set(record["offenders"])
    assert found == allowed, (
        "C-S2/A1 BROKEN — the set of modules drawing from the PROCESS-GLOBAL random "
        "stream has changed. A draw added to a shared stream shifts every subsequent "
        "draw in the process and destroys deterministic replay (the 01:09Z incident).\n"
        f"  new:   {sorted(found - allowed)}\n"
        f"  fixed: {sorted(allowed - found)} (remove it from KNOWN_GLOBAL_RNG_MODULES)"
    )


def probe_substream_independence() -> dict:
    """Advance one named substream hard, then draw from another, and compare
    against the same second draw made without touching the first.

    This is A1's property stated as an experiment rather than as a convention:
    *adding a draw in one subsystem leaves every other subsystem's stream
    bit-identical.* Run against the REAL derivation helpers in
    `simulation/population_draw.py`, not a local re-implementation.
    """
    from simulation import population_draw

    base_seed = 90210

    def _draws(name: str, n: int = 8) -> list[float]:
        return [population_draw._substream(base_seed, name).random() for _ in range(n)]

    # Baseline: subsystem B's sequence with nothing else having happened.
    baseline_b = [population_draw._substream(base_seed, "beta").random()]
    # Now burn a lot of draws on subsystem A — the "new feature added draws" case.
    burner = population_draw._substream(base_seed, "alpha")
    burned = [burner.random() for _ in range(500)]
    after_b = [population_draw._substream(base_seed, "beta").random()]

    # PREMISE: the two substreams must genuinely be different streams, else
    # "independent" is satisfied by them being the same constant.
    if _draws("alpha", 4) == _draws("beta", 4):
        raise AssertionError(
            "probe premise violated: two differently-named substreams produced the "
            "same sequence, so independence cannot be distinguished from identity"
        )
    if not burned:
        raise AssertionError("probe premise violated: no draws were burned")

    return {"baseline_b": baseline_b, "after_b": after_b}


def assert_substream_independence(record: dict) -> None:
    """C-S2(b) / A1, the positive direction."""
    assert record["after_b"] == record["baseline_b"], (
        "C-S2/A1 BROKEN — draws added to one subsystem moved another subsystem's "
        f"stream: {record['baseline_b']} -> {record['after_b']}. Replay is no longer "
        "reproducible across a feature addition."
    )


# ══════════════════════════════════════════════════════════════════════════════
# C-S3 — ASYNCHRONOUS WALL CONTRACTS
#   "Request and response are separate events in time, never a synchronous call
#    assuming same-step resolution."
# ══════════════════════════════════════════════════════════════════════════════

def probe_request_response_split() -> dict:
    """Submit a real governed decision request, observe it PENDING while
    unanswered, resolve it later, and read the measured latency back.

    Uses an injected log rather than the module singleton, so this probe cannot
    pollute the shared `_DECISION_LOG` other tests read.
    """
    log = BitemporalEventLog()
    t0 = dt.datetime(2023, 3, 1, 9, 0, tzinfo=dt.timezone.utc)
    mid = t0 + dt.timedelta(hours=4)
    t1 = t0 + dt.timedelta(hours=9)
    cls = decision_rights.DecisionClass.PRICING_MOVE
    valid_time = dt.date(2023, 3, 1)

    decision_rights.submit_decision_request(
        cls, "SCALE-CS3-1", {"move_pct": 3.0}, {"why": "probe"}, valid_time,
        submitted_at=t0, log=log,
    )
    pending_at_t0 = decision_rights.pending_decision_requests_as_of(t0, cls, log=log)
    pending_mid = decision_rights.pending_decision_requests_as_of(mid, cls, log=log)

    resolved = decision_rights.resolve_decision_request(
        cls, "SCALE-CS3-1", valid_time, {"approved": True}, "probe", resolved_at=t1, log=log,
    )
    pending_after = decision_rights.pending_decision_requests_as_of(t1, cls, log=log)

    return {
        "pending_at_submit": [e.entity_id for e in pending_at_t0],
        "pending_while_open": [e.entity_id for e in pending_mid],
        "pending_after_resolve": [e.entity_id for e in pending_after],
        "measured_elapsed_seconds": resolved.actual_elapsed_seconds,
        "real_gap_seconds": (t1 - t0).total_seconds(),
        "resolved_status": resolved.status,
    }


def assert_request_and_response_are_separate_events(record: dict) -> None:
    """C-S3. The pending interval must be REPRESENTABLE and its latency MEASURED
    — a synchronous contract has neither."""
    assert "SCALE-CS3-1" in record["pending_at_submit"], (
        "C-S3 BROKEN — a submitted request was not observable as pending at the "
        "moment it was submitted, so the request/answer split is not represented"
    )
    assert "SCALE-CS3-1" in record["pending_while_open"], (
        "C-S3 BROKEN — a request stopped reading as pending while it was still "
        "unanswered; a decision taken mid-flight would see a fabricated answer"
    )
    assert "SCALE-CS3-1" not in record["pending_after_resolve"], (
        "C-S3 BROKEN — an answered request is still pending, so the pending queue "
        "never drains"
    )
    assert record["resolved_status"] == "decided", (
        f"C-S3 BROKEN — resolution left status={record['resolved_status']!r}"
    )
    assert record["measured_elapsed_seconds"] == record["real_gap_seconds"], (
        "C-S3 BROKEN — the answer's latency is not the REAL gap between request and "
        f"answer ({record['measured_elapsed_seconds']} vs "
        f"{record['real_gap_seconds']}); latency is being estimated, not measured, "
        "which is exactly what a same-step contract hides"
    )


def probe_same_step_resolution() -> dict:
    """Try to answer a request in the SAME INSTANT it was made.

    This is A4's named exemplar — the DD-mandate submit-and-resolve-in-the-same-step
    bug found by W5_1's Expert Hour — asked of the general mechanism. Under C-S3
    a zero-latency answer is not a fast answer, it is a *synchronous* one, and the
    contract is supposed to make it unrepresentable.
    """
    log = BitemporalEventLog()
    t0 = dt.datetime(2023, 3, 1, 9, 0, tzinfo=dt.timezone.utc)
    cls = decision_rights.DecisionClass.PRICING_MOVE
    valid_time = dt.date(2023, 3, 1)
    decision_rights.submit_decision_request(
        cls, "SCALE-CS3-2", {"move_pct": 3.0}, {"why": "probe"}, valid_time,
        submitted_at=t0, log=log,
    )
    try:
        resolved = decision_rights.resolve_decision_request(
            cls, "SCALE-CS3-2", valid_time, {"approved": True}, "probe",
            resolved_at=t0, log=log,
        )
    except Exception as exc:  # noqa: BLE001 — any rejection is a pass here
        return {"rejected": True, "detail": f"{type(exc).__name__}: {exc}", "elapsed": None}
    return {"rejected": False, "detail": None, "elapsed": resolved.actual_elapsed_seconds}


def assert_same_step_resolution_is_rejected(record: dict) -> None:
    """C-S3, the fail-open direction. KNOWN RED AT LANDING — see
    `docs/design/SCALE_CONSTRAINT_CHECKS.md` §C-S3."""
    assert record["rejected"], (
        "C-S3 RESIDUAL — a decision request was answered in the SAME INSTANT it was "
        f"submitted (measured latency {record['elapsed']}s). The mechanism represents "
        "the pending interval but does not REQUIRE one, so the same-step contract "
        "A4 names as the exemplar of this class is still writable."
    )


# ══════════════════════════════════════════════════════════════════════════════
# C-S4 — PERSISTENCE BEHIND AN INTERFACE
#   "All durable state access goes through the append-only event-log abstraction;
#    no decision logic may depend on the current storage form."
#
# The testable half of that at this scale is the one the director already cites
# by name (ADVISOR_FINDINGS_STRUCTURAL_AUDIT FINDING 2): durable money state
# exists in DUPLICATE. A copy is legitimate only if it is DERIVED and IDENTICAL —
# the moment source and copy disagree, "which one is the truth?" has no answer
# and the storage form has started determining the money.
# ══════════════════════════════════════════════════════════════════════════════

def _read_published(relpath: str) -> str | None:
    """The file's content AS PUBLISHED — the committed blob, not the working tree.

    This matters and is not a convenience. `docs/state/` is served by GitHub Pages
    straight from this repo on every push; the working tree is a construction
    site. A publish pass writes `site/state/` from the generators and copies it to
    `docs/state/` a few hundred lines of pipeline later, so for a window in every
    single pass the two disagree on disk **and nobody is wrong** — the copy step
    simply has not run yet. Measuring the working tree turns that ordinary window
    into an alarm, which is how a control earns a reputation for crying wolf and
    gets ignored (R5: an alarm nobody reads is worse than none).

    The committed pair is what the consumer actually fetches, and a publish pass
    commits both sides together — so a disagreement THERE is drift at rest, with
    no benign explanation. R11's own discipline: verify the artefact the consumer
    gets.
    """
    r = subprocess.run(
        ["git", "show", f"HEAD:{relpath}"],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    return None if r.returncode != 0 else r.stdout


def probe_durable_state_duplication() -> dict:
    """Read the REAL mirror register and compare every declared pair AS PUBLISHED.

    The register (`tools/mirror_github_pages.py::_STATE_JSON_FILES`) is imported,
    not restated — a restated copy would keep passing after the real register
    changed.
    """
    from tools.mirror_github_pages import _STATE_JSON_FILES, DOCS_STATE

    declared, drifted, missing, compared = [], [], [], []
    for src, name in _STATE_JSON_FILES:
        dest = DOCS_STATE / name
        rel = (str(src.relative_to(ROOT)), str(dest.relative_to(ROOT)))
        declared.append(rel)
        src_blob, dest_blob = _read_published(rel[0]), _read_published(rel[1])
        if src_blob is None or dest_blob is None:
            # Not published at all — nothing to compare, and nothing a consumer
            # can be misled by. Recorded, not asserted on; the non-vacuity guard
            # below is what stops "everything is missing" reading as compliance.
            missing.append(rel)
            continue
        compared.append(rel)
        if _canonical(src_blob) != _canonical(dest_blob):
            drifted.append(rel)

    # UNDECLARED duplication: the same durable-state filename living in two
    # different roots without the register saying it is a mirror.
    declared_names = {name for _, name in _STATE_JSON_FILES}
    roots = [ROOT / "site" / "state", ROOT / "site" / "data", ROOT / "docs" / "state"]
    by_name: dict[str, list[str]] = {}
    for root in roots:
        if not root.exists():
            continue
        for path in root.glob("*.json"):
            by_name.setdefault(path.name, []).append(str(path.relative_to(ROOT)))
    undeclared = {
        name: sorted(paths)
        for name, paths in by_name.items()
        if len(paths) > 1 and name not in declared_names
    }
    return {
        "declared": declared,
        "compared": compared,
        "drifted": drifted,
        "missing": missing,
        "undeclared_duplicates": undeclared,
    }


def _canonical(blob: str) -> str:
    """Compare CONTENT, not bytes — key order and whitespace are the writer's
    business, but a differing value is drift."""
    try:
        return json.dumps(json.loads(blob), sort_keys=True)
    except ValueError:
        return f"<unparseable:{hash(blob)}>"


def assert_durable_state_is_not_forked(record: dict) -> None:
    """C-S4. See `docs/design/SCALE_CONSTRAINT_CHECKS.md` §C-S4."""
    assert record["declared"], (
        "probe is vacuous: the mirror register declares no pairs at all, so 'no drift' "
        "means nothing"
    )
    assert record["compared"], (
        "probe is vacuous: the register declares pairs but NONE of them could be read "
        f"as published ({record['missing']}), so 'no drift' means nothing — an "
        "unavailable check is a FAILED check (R15)"
    )
    assert not record["drifted"], (
        "C-S4 BROKEN — a DERIVED copy of durable state disagrees with its source AS "
        "PUBLISHED. Two copies of the money that differ have no answer to 'which one "
        f"is the truth?': {record['drifted']}"
    )
    assert not record["undeclared_duplicates"], (
        "C-S4 BROKEN — durable state is duplicated OUTSIDE the mirror register, so "
        "nothing declares which copy is derived: "
        f"{record['undeclared_duplicates']}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# C-S5 — TIME-SCALE INVARIANCE DECLARATION
#   "Any company-side atom claiming maturity L3+ must state whether its logic is
#    time-scale invariant, and register any exception as a named simplification
#    per R10."
#
# This is the one constraint that is a DECLARATION, not a behaviour, so the check
# is a register check: the population that owes a declaration is derived from the
# map, and the register must cover it.
# ══════════════════════════════════════════════════════════════════════════════

def probe_time_scale_declarations() -> dict:
    """Derive who owes a declaration from the REAL map, and read the REAL register."""
    atoms = yaml.safe_load(MATURITY_MAP.read_text(encoding="utf-8"))
    if isinstance(atoms, dict):  # tolerate a wrapped document
        atoms = atoms.get("atoms", [])
    owed = {
        a["id"]
        for a in atoms
        if isinstance(a, dict)
        and (a.get("level_current") or 0) >= 3
        and str(a.get("lane", "")).startswith(COMPANY_SIDE_LANE_PREFIXES)
    }
    register = yaml.safe_load(TIME_SCALE_REGISTER.read_text(encoding="utf-8")) or {}
    declared = {d["atom_id"] for d in (register.get("declarations") or [])}
    exceptions = {e["atom_id"] for e in (register.get("exceptions") or [])}
    baseline = set(register.get("undeclared_at_landing") or [])
    return {
        "owed": owed,
        "declared": declared,
        "exceptions": exceptions,
        "baseline": baseline,
        "atoms_read": len(atoms),
    }


def assert_time_scale_declarations_cover_the_population(
    record: dict, frozen_baseline: set[str] | None = None
) -> None:
    """C-S5. Every company-side L3+ atom is declared, excepted, or in the frozen
    landing amnesty — and the amnesty may not grow."""
    assert record["atoms_read"] > 0, (
        "probe is vacuous: the maturity map parsed to zero atoms, so 'everyone is "
        "covered' means nothing (fail-open on a missing/malformed source, R15)"
    )
    assert record["owed"], (
        "probe is vacuous: no company-side atom is at L3+, so this check would pass "
        "over an empty population forever"
    )
    covered = record["declared"] | record["exceptions"] | record["baseline"]
    undeclared = record["owed"] - covered
    assert not undeclared, (
        "C-S5 BROKEN — company-side atoms at L3+ with no time-scale invariance "
        f"declaration and no registered exception: {sorted(undeclared)}. Declare them "
        f"in {TIME_SCALE_REGISTER} (this is a one-line statement, not a build)."
    )
    if frozen_baseline is not None:
        assert record["baseline"] == frozen_baseline, (
            "C-S5 AMNESTY MOVED — `undeclared_at_landing` is the frozen set of atoms "
            "that were already L3+ when this check landed. It may only SHRINK, and "
            "shrinking requires editing the frozen set here too.\n"
            f"  added:   {sorted(record['baseline'] - frozen_baseline)}\n"
            f"  removed: {sorted(frozen_baseline - record['baseline'])}"
        )
    stale = record["baseline"] & (record["declared"] | record["exceptions"])
    assert not stale, (
        f"C-S5 STALE AMNESTY — these atoms are BOTH in the landing amnesty and "
        f"properly declared: {sorted(stale)}. Remove them from "
        "`undeclared_at_landing` so the amnesty keeps measuring something."
    )
