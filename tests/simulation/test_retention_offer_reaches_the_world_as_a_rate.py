"""The run's retention offer reaches the world as the OFFERED RATE, on the household's own roll.

DEFECTS, one control each (director, 2026-10-09; finding
`WORKER_FINDING_THE_RUNS_RETENTION_OFFER_REACHES_THE_WORLD_AS_A_FLAT_TWENTY_PERCENT_WHATEVER_ITS_SIZE`):
  1. the discount's size never reaches the world (a 3% and an 8% offer keep alike);
  2. a zero discount moves something (the offer itself, not its price, is credited);
  3. the answer is decided on a coin of its own rather than the household's renewal roll;
  4. the flat, unsourced RETENTION_EFFECTIVENESS is read anywhere again.
"""
from __future__ import annotations

import ast
import datetime as dt
from pathlib import Path

import pytest

from simulation import coin_drawn_decision_set as cds
from simulation.customer_events import roll_lifecycle_event
from simulation.retention_offer import ask_world_at_offer, offered_rate

TIERS = (0.0, 0.03, 0.05, 0.08)
REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def asked():
    """Per household at its first renewal: the world at the full rate, and the run's answer at each
    tier, framing neutral (multiplier 1) and matched (1.35, the top of the sourced range)."""
    households = cds.draw_households(42, start_year=2016, end_year=2018, acquisitions_per_year=25.0)
    out = []
    with cds.registered(households):
        for c in households:
            joined = dt.date.fromisoformat(c.acquisition_date)
            decision = joined + dt.timedelta(days=365)
            rate = cds.default_offer_ex_vat(joined)
            kw = dict(records_so_far=cds.lean_day_records(c.customer_id, c.eac_kwh, joined,
                                                          decision, rate),
                      customers=[c.to_customer_dict()], old_rate_gbp_per_mwh=rate,
                      new_rate_gbp_per_mwh=cds.default_offer_ex_vat(decision),
                      market_year=decision.year)
            full = roll_lifecycle_event(c.customer_id, decision.isoformat(), cds.FUEL, **kw)
            if full is None:
                continue
            row = {"full": full, "id": c.customer_id}
            for m in (1.0, 1.35):
                row[m] = {d: ask_world_at_offer(roll_lifecycle_event, c.customer_id,
                                                decision.isoformat(), cds.FUEL, kw, full,
                                                discount_pct=d, framing_multiplier=m)
                          for d in TIERS}
            # The world asked directly at each offered rate, nothing of the run's in between.
            row["direct"] = {d: roll_lifecycle_event(c.customer_id, decision.isoformat(), cds.FUEL, **{
                **kw, "new_rate_gbp_per_mwh": offered_rate(kw["new_rate_gbp_per_mwh"], d)})
                for d in TIERS}
            out.append(row)
    assert len(out) > 30, len(out)
    return out


def _kept(rows, m, d):
    return sum(r[m][d]["event_type"] == "renewed" for r in rows)


def test_a_bigger_discount_keeps_at_least_as_many_on_the_same_roll(asked):
    """DEFECT 1. Monotone per household and in total, and the 8% tier keeps STRICTLY more than no
    offer: a world blind to the discount (the flat 0.20, or `offered_rate` returning the full rate)
    keeps every tier alike and reds the strict leg."""
    for m in (1.0, 1.35):
        for r in asked:
            p = [r[m][d]["effective_retention_probability"] for d in TIERS]
            stays = [r[m][d]["event_type"] == "renewed" for d in TIERS]
            assert p == sorted(p), (r["id"], p)
            assert stays == sorted(stays), (r["id"], stays)
        kept = [_kept(asked, m, d) for d in TIERS]
        assert kept == sorted(kept), kept
        assert kept[-1] > kept[0], f"the 8% offer kept nobody the full rate lost: {kept}"
    assert _kept(asked, 1.35, 0.08) >= _kept(asked, 1.0, 0.08)


def test_a_zero_discount_changes_nothing(asked):
    """DEFECT 2. An offer of 0% is the full rate: same stay, same P(stay), at any framing (the
    framing scales the price's effect, and there is none)."""
    for r in asked:
        for m in (1.0, 1.35):
            zero = r[m][0.0]
            assert zero["event_type"] == r["full"]["event_type"], r["id"]
            assert zero["effective_retention_probability"] == pytest.approx(
                r["full"]["effective_retention_probability"], abs=1e-4), r["id"]


def test_the_answer_is_the_households_own_roll(asked):
    """DEFECT 3. At neutral framing the run's answer IS the world re-asked at the offered rate, for
    every household and tier: an independent coin in `answer_retention_offer` disagrees with it on
    some household. Both outcomes must occur among the offered, or agreement says nothing."""
    outcomes = set()
    for r in asked:
        for d in TIERS:
            direct = r["direct"][d]
            assert r[1.0][d]["event_type"] == direct["event_type"], (r["id"], d)
            outcomes.add(direct["event_type"])
            # The pre-offer truth is the full-rate one (Phase QA), never the discounted one.
            assert r[1.0][d]["realized_churn_probability"] == r["full"]["realized_churn_probability"]
    assert outcomes == {"renewed", "churned"}, outcomes


def test_no_reader_of_the_flat_retention_effectiveness_remains():
    """DEFECT 4. No Python name, attribute or import `RETENTION_EFFECTIVENESS` anywhere in the tree.
    Read as code (ast), so the prose recording its retirement does not count. The company's own
    belief `_RETENTION_EFFECTIVENESS` is a different name on the other side of the wall."""
    readers, read = [], 0
    for path in REPO.rglob("*.py"):
        # Parts RELATIVE to the repo: a linked worktree lives under `.claude/worktrees/`, and
        # filtering the absolute path skipped every file there (first draft; mutation-caught).
        if {".git", ".claude", "node_modules", ".venv"} & set(path.relative_to(REPO).parts):
            continue
        read += 1
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            name = (node.id if isinstance(node, ast.Name) else node.attr
                    if isinstance(node, ast.Attribute) else None)
            names = [a.name for a in node.names] if isinstance(node, ast.ImportFrom) else [name]
            if "RETENTION_EFFECTIVENESS" in names:
                readers.append(f"{path.relative_to(REPO)}:{node.lineno}")
    assert read > 1000, f"only {read} Python files read: the census cannot see the tree"
    assert not readers, readers
