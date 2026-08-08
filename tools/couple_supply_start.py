"""COUPLED-TRIAD runner: the RE-CONTRACTING WORLD <-> ``C_supply_start_semantic_separation``.

This is HARNESS code. It sits OUTSIDE the epistemic wall by design and is the ONLY
layer permitted to hold the world's hidden ANSWER KEY (each account's *true*
relationship start) and the company's observable-only BELIEF (the tenure its own
CRM code computes) side by side, to measure the belief-vs-truth GAP
(`COUPLED_TRIAD_DESIGN.md` 1.3; same role as the other ``tools/couple_*`` runners).
It lives in ``tools/`` -- NOT under ``saas/`` or ``company/`` -- so it is not scanned
by the epistemic verifier and may legitimately import ``simulation.*``.

WHY THIS PAIR EXISTS. ``C_supply_start_semantic_separation`` reached L2 on 2026-08-03
with an explicitly-named residual (c): *"L3 additionally owes the coupled-triad gap
measurement: the company has not yet been tested against a world that re-contracts a
customer and then checks whether its believed tenure tracks the truth."* That is the
COUPLED_TRIAD binding rule's company half -- **no company capability is complete
until it has faced a world that can defeat it**. This runner is that world.

THE COUPLED LOOP (3 loops):

  1. WORLD adds depth  -- ``draw_recontracting_world()`` re-contracts customers: a
                          predecessor churns at a 365-day term boundary and the
                          home-mover is won back as a NEW account (the SIM's real
                          mechanism -- ``run_phase2b`` ``home_move_won`` ->
                          ``won_successor_activations`` -> ``notify_acquisition``,
                          ``channel="home-move-win"``). The successor's CRM record
                          deliberately carries the PREDECESSOR's genesis date as its
                          term anchor, because that is what keeps the renewal grid
                          aligned. The date the relationship ACTUALLY began -- the
                          term boundary the win landed on -- is the ANSWER KEY, held
                          here and NEVER handed to the company.
  2. COMPANY copes     -- the company sees only what a real supplier's CRM sees: the
                          account record (``acquisition_date`` = the anchor,
                          ``successor_of``) and, where its registration processing
                          captured it, the acquisition event's ``event_date``. Both
                          beliefs are computed by the company's OWN shipped code
                          (``company.crm.lifecycle_tracker.CustomerLifecycle.
                          tenure_days`` -- consumer-table row 2), never re-implemented
                          here; only the date fed into it differs.
  3. HARNESS measures  -- ``prediction_gap`` over believed vs true tenure in years,
                          normalised to the no-skill baseline (predict the mean tenure
                          every time).

THE TWO BELIEFS, AND WHICH ONE IS THE HEADLINE.

  * ``naive`` -- tenure from ``acquisition_date``. **This is what the company actually
    believes and publishes TODAY**: the 7 live-wrong consumers enumerated in
    ``docs/design/SUPPLY_START_SEMANTIC_SEPARATION_DISCOVER.md`` (churn-estimate
    tenure, per-customer ``tenure_years``, the acquisition-cohort bucket and three
    rendered "Customer since" surfaces) all still read that field. So the HEADLINE
    ``gap`` written to the ledger is the naive one -- the Proof door's coupled-gap
    panel should show the company's real standing, not a capability it has built but
    not yet routed.
  * ``separated`` -- tenure from ``company.crm.supply_start.derive_supply_start``,
    i.e. the mechanism THIS atom built. Carried in ``components`` as the counterfactual:
    what the gap becomes once ``C_supply_start_consumer_routing`` routes the consumers.

ON THE SEPARATED BELIEF SCORING ~0 UNDER FULL OBSERVABILITY -- THIS IS NOT A LEAK.
For an inference pair (W2_7 <-> C9, W1_11 <-> C14) a gap of 0 means the observables
leaked hidden state, which is a defect. This pair is not an inference pair. The
registration date is not hidden world state the company has to guess: it is a fact the
supplier itself processed when it took the account on. A CRM that records the date it
registered a customer is *correct*, not clairvoyant. The honest question for this
mechanism is therefore not "how accurately does it infer?" but "what does it do when
the registration observable is DEGRADED?" -- which is what the regime sweep below asks,
and where the world does defeat it.

HOW THE WORLD DEFEATS THE SEPARATED MECHANISM (the reason this runner is not theatre).
``derive_supply_start`` resolves in a stated order, and two of its three rungs are
exposed by a realistic observable-quality regime (C-S1: events arrive singly, late, or
not at all -- the company may not assume batch completeness):

  * **activation absent, link present** -> rung 3 returns ``None``. The company must say
    UNKNOWN. That is an honest abstention, not an error -- but it is a real COVERAGE
    cost, and every consumer then needs a stated behaviour for "we do not know".
  * **activation absent, link ALSO absent** -> rung 2 fires ("no ``successor_of``, so
    this record's ``acquisition_date`` genuinely is its own start") and hands back the
    ANCHOR. The company is then **confidently wrong** -- the exact phantom tenure this
    atom exists to remove, reintroduced through the linkage observable rather than
    through the date one. A lost predecessor link is an ordinary CRM data-quality
    failure (an erroneous transfer reversed, a customer who left and re-registered
    independently), so this is a live failure mode and not a contrived one.

``regime_sweep()`` measures both, and ``confident_wrong`` counts the second class
separately from ``unknown`` -- because a wrong answer and no answer are not the same
defect and must not be averaged into one number.

SCORING AN ABSTENTION (stated, because the alternative is forbidden). An UNKNOWN cannot
be scored as zero tenure or as the anchor -- ``C_supply_start_consumer_routing``'s mint
forbids exactly that, since it silently restores the phantom. Here an abstention is
scored at the NO-SKILL value (the climatological mean tenure): the company earns no
credit and no penalty beyond blind for declining to answer. Nothing is published from
this substitution; it exists only so a population that mixes answers with abstentions
has one comparable score. ``unknown_share`` is reported alongside so the abstention rate
is never hidden inside the gap.

R15 INDEPENDENCE / NOT A TAUTOLOGY. The truth is the world's re-contracting event date,
drawn here from the term grid and never given to the company. The naive belief is
computed from a DIFFERENT field (the predecessor's genesis anchor on the CRM record),
so the naive gap is a real measurement of a real error. The separated belief is computed
from the registration observable, which is deliberately degradable -- and under
degradation it produces both abstentions and confident-wrong answers, so it can and does
score badly. Mutation coverage: ``tests/tools/test_couple_supply_start.py``.

NO GOAL-SEEKING (R12/R13). Nothing here or in the company is tuned toward a target gap.
The term grid, the successor set and the anchor pinning are the world's existing frozen
mechanics; the gap is whatever they produce.

DETERMINISM (C-S2). Every draw comes from a NAMED seeded substream keyed on the account
id, so the same population is produced on every machine and a draw here can never shift
another subsystem's stream. No wall-clock anywhere in the measurement: ``as_of`` is
passed in, and ``measured_at``/``run_git_commit`` for the ledger are gathered by
``main()``, never by the measurement functions.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional, Sequence

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from saas.customers import CUSTOMERS, SUCCESSOR_CUSTOMERS

from company.compliance.domain_invariants import (
    check_supply_start_not_before_first_observable,
)
from company.crm.lifecycle_tracker import CustomerLifecycle, LifecycleStage
from company.crm.supply_start import derive_supply_start

from background.gap_metric import prediction_gap, write_gap_entry

WORLD_ATOM_ID = "WORLD_recontracting_relationship_start"
TWIN_ATOM_ID = "C_supply_start_semantic_separation"

#: The end of the real 2016-25 history the simulation runs against. Passed in
#: everywhere; never read from a clock (C-S2 / the forbidden-clock rule).
DEFAULT_AS_OF = "2025-12-31"

#: One fixed-term period. The successor's anchor is pinned to the predecessor's
#: genesis date precisely so both sit on this grid (`simulation/renewals.py`).
TERM_DAYS = 365

DAYS_PER_YEAR = 365.25

#: A first bill follows the first meter read by roughly a billing cycle. Only its
#: ORDERING matters here (both observables sit at or after the true supply start,
#: so the earliest of them is the bound the R10 class guard checks against).
FIRST_BILL_LAG_DAYS = 30


# ---------------------------------------------------------------------------
# Deterministic draws (C-S2: named substreams, stable across machines)
# ---------------------------------------------------------------------------

def _stable_uniform(substream: str, key: str) -> float:
    """A reproducible U[0,1) for `key` within a NAMED substream.

    Same (substream, key) -> same value on every machine and every run, and a
    draw in one substream can never shift another's sequence (C-S2). Used
    instead of a global RNG so the world population is a pure function of its
    inputs.
    """
    digest = hashlib.sha256(f"{substream}|{key}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / float(1 << 64)


# ---------------------------------------------------------------------------
# 1. WORLD -- re-contract customers and hold the answer key
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WorldAccount:
    """One account as the WORLD knows it. `true_relationship_start` is the answer
    key and never crosses to the company."""

    account_id: str
    predecessor_id: Optional[str]
    term_anchor: str              # what the CRM record carries as acquisition_date
    true_relationship_start: str  # ANSWER KEY -- harness only
    activation_event: Optional[str]  # the registration event the world emitted

    @property
    def is_recontracted(self) -> bool:
        return self.predecessor_id is not None

    @property
    def first_meter_read(self) -> str:
        """An account is metered from the day its supply actually starts. This is a
        SECOND, INDEPENDENT observable of the same fact as the registration event --
        and unlike the `successor_of` link it is not paperwork that can quietly go
        missing, because a supplier that is not reading the meter is not supplying."""
        return self.true_relationship_start

    @property
    def first_issued_bill(self) -> str:
        return (dt.date.fromisoformat(self.true_relationship_start)
                + dt.timedelta(days=FIRST_BILL_LAG_DAYS)).isoformat()


def _term_boundary(anchor: str, k: int) -> str:
    return (dt.date.fromisoformat(anchor) + dt.timedelta(days=TERM_DAYS * k)).isoformat()


def draw_recontracting_world(as_of: str = DEFAULT_AS_OF) -> list[WorldAccount]:
    """The world: base accounts, plus the same accounts re-contracted after a churn.

    Base accounts (`saas.customers.CUSTOMERS`) genuinely began on the date their
    record carries, so anchor == truth for them; they are in the population
    precisely so the measurement is not scored on successors alone.

    Successors (`saas.customers.SUCCESSOR_CUSTOMERS`) are the re-contracting: the
    predecessor churned at one of its 365-day term boundaries and the home-mover
    was won back as a new account activating that day. WHICH boundary is the
    world's draw -- deterministic per account, uniform over the boundaries that
    fall on or before `as_of`. The record keeps the predecessor's genesis date as
    its anchor (correct and load-bearing for the renewal grid), so anchor != truth
    for exactly these accounts.
    """
    as_of_date = dt.date.fromisoformat(as_of)
    world: list[WorldAccount] = []

    for customer in CUSTOMERS:
        anchor = customer["acquisition_date"]
        world.append(WorldAccount(
            account_id=customer["customer_id"],
            predecessor_id=None,
            term_anchor=anchor,
            true_relationship_start=anchor,
            activation_event=anchor,
        ))

    for customer in SUCCESSOR_CUSTOMERS:
        anchor = customer["acquisition_date"]
        account_id = customer["customer_id"]
        max_k = max(1, (as_of_date - dt.date.fromisoformat(anchor)).days // TERM_DAYS)
        u = _stable_uniform("recontracting_world.term_index", account_id)
        k = min(max_k, 1 + int(u * max_k))
        activation = _term_boundary(anchor, k)
        world.append(WorldAccount(
            account_id=account_id,
            predecessor_id=customer.get("successor_of"),
            term_anchor=anchor,
            true_relationship_start=activation,
            activation_event=activation,
        ))

    return world


# ---------------------------------------------------------------------------
# 2. COMPANY -- observables only, then the company's own shipped tenure code
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ObservableRegime:
    """How much of the registration paperwork actually reached the CRM.

    A DIAGNOSTIC sweep dimension, not a claim about real-world capture rates: it
    answers "what defeats the mechanism", never "how often does this happen".
    Selection is deterministic per account (C-S2), so a regime is reproducible.
    """

    name: str
    activation_capture: float = 1.0  # share of re-contracted accounts whose event arrived
    link_capture: float = 1.0        # share whose `successor_of` link was recorded


FULL_OBSERVABILITY = ObservableRegime("full_observability", 1.0, 1.0)


def _captured(substream: str, account_id: str, rate: float) -> bool:
    if rate >= 1.0:
        return True
    if rate <= 0.0:
        return False
    return _stable_uniform(substream, account_id) < rate


def observables_for(world: Sequence[WorldAccount], regime: ObservableRegime):
    """Project the world onto what the company can see. Returns (records, activations).

    `records` are CRM account records -- the anchor and, where it was captured, the
    predecessor link. `activations` is the acquisition-event feed keyed by account.
    The answer key is not in either.
    """
    records: list[dict] = []
    activations: dict[str, str] = {}

    for account in world:
        link_seen = (
            account.predecessor_id is not None
            and _captured("registration.link_capture", account.account_id,
                          regime.link_capture)
        )
        activation_seen = account.activation_event is not None and not (
            account.is_recontracted and not _captured(
                "registration.activation_capture", account.account_id,
                regime.activation_capture,
            )
        )
        records.append({
            "customer_id": account.account_id,
            "acquisition_date": account.term_anchor,
            "successor_of": account.predecessor_id if link_seen else None,
            # The R10 class guard's independent observables. These survive the
            # loss of the registration paperwork, which is the whole reason the
            # guard is a separate line of defence and not a restatement of the
            # derivation (R15 independence).
            "acquisition_event_date": account.activation_event if activation_seen else None,
            "first_meter_read_date": account.first_meter_read,
            "first_issued_bill_date": account.first_issued_bill,
        })
        if activation_seen:
            activations[account.account_id] = account.activation_event

    return records, activations


def guard_flags(record: Mapping, believed_supply_start: Optional[str]) -> bool:
    """Would this atom's R10 class guard FIRE on what the company wrote?

    `SUPPLY_START_NOT_BEFORE_FIRST_OBSERVABLE` re-derives the bound from the
    account's own observables and never imports the derivation it audits, so it is
    a genuine second opinion: a supply_start earlier than the first meter read is
    impossible regardless of how it was derived. Returns True when the guard
    REJECTS the record (i.e. it caught a phantom).
    """
    audited = dict(record)
    audited["supply_start"] = believed_supply_start
    return not check_supply_start_not_before_first_observable(audited)


def _tenure_years(start: Optional[str], as_of: str) -> Optional[float]:
    """Tenure via the company's OWN shipped lifecycle code, not a re-implementation.

    `CustomerLifecycle.tenure_days` is consumer-table row 2 -- the same call the
    live tenure/cohort consumers make. Only the date handed to it differs between
    the two beliefs, which is exactly the thing under measurement.
    """
    if start is None:
        return None
    lifecycle = CustomerLifecycle(
        customer_id="_measure",
        acquisition_date=dt.date.fromisoformat(start),
        stage=LifecycleStage.ACTIVE,
    )
    return lifecycle.tenure_days(dt.date.fromisoformat(as_of)) / DAYS_PER_YEAR


def believed_tenure_naive(record: Mapping, as_of: str) -> Optional[float]:
    """What the company believes TODAY: tenure counted from `acquisition_date`."""
    return _tenure_years(record.get("acquisition_date"), as_of)


def believed_tenure_separated(record: Mapping, activations: Mapping[str, str],
                              as_of: str) -> Optional[float]:
    """What the company would believe with THIS ATOM's mechanism in the loop.

    `None` means the company declines to answer (UNKNOWN) -- which is a legitimate
    output, never to be filled in from the anchor.
    """
    return _tenure_years(derive_supply_start(record, activations), as_of)


# ---------------------------------------------------------------------------
# 3. HARNESS -- score belief against the answer key
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BeliefScore:
    gap: Optional[float]
    raw_gap: float
    g0: float
    baseline: str
    n: int
    n_unknown: int
    n_confident_wrong: int
    mean_phantom_years: float
    max_phantom_years: float

    @property
    def unknown_share(self) -> float:
        return self.n_unknown / self.n if self.n else 0.0

    def as_components(self, prefix: str) -> dict:
        return {
            f"{prefix}_gap": self.gap,
            f"{prefix}_mae_years": round(self.raw_gap, 6),
            f"{prefix}_unknown_share": round(self.unknown_share, 6),
            f"{prefix}_confident_wrong": self.n_confident_wrong,
            f"{prefix}_mean_phantom_years": round(self.mean_phantom_years, 6),
            f"{prefix}_max_phantom_years": round(self.max_phantom_years, 6),
        }


def score_belief(truth_years: Sequence[float],
                 belief_years: Sequence[Optional[float]],
                 *, phantom_tolerance_years: float = 0.5) -> BeliefScore:
    """Score one belief against the answer key.

    An abstention (`None`) is scored at the no-skill value -- see the module
    docstring: it may not be scored as zero or as the anchor, and it must not be
    silently dropped either (dropping would let the company look good by declining
    to answer). `unknown_share` is reported separately so the substitution is
    never mistaken for an answer.

    A CONFIDENT-WRONG account is one where the company gave an answer that
    overstates the relationship by more than `phantom_tolerance_years` -- the
    phantom-tenure defect. It is counted separately from an abstention because a
    wrong answer and no answer are different failures and averaging them hides one.
    """
    if len(truth_years) != len(belief_years):
        raise ValueError(
            f"truth/belief length mismatch: {len(truth_years)} vs {len(belief_years)}")
    if not truth_years:
        raise ValueError("score_belief: empty population")

    prior = sum(truth_years) / len(truth_years)
    scored = [prior if b is None else b for b in belief_years]

    phantoms = [
        b - t for t, b in zip(truth_years, belief_years)
        if b is not None and b - t > phantom_tolerance_years
    ]
    result = prediction_gap(truth_years, scored, prior_value=prior)
    n_unknown = sum(1 for b in belief_years if b is None)
    return BeliefScore(
        gap=result.gap,
        raw_gap=result.raw_gap,
        g0=result.g0,
        baseline=result.baseline,
        n=len(truth_years),
        n_unknown=n_unknown,
        n_confident_wrong=len(phantoms),
        mean_phantom_years=(sum(phantoms) / len(phantoms)) if phantoms else 0.0,
        max_phantom_years=max(phantoms) if phantoms else 0.0,
    )


def measure_regime(world: Sequence[WorldAccount], regime: ObservableRegime,
                   as_of: str = DEFAULT_AS_OF) -> dict:
    """Run both beliefs against the answer key under one observable regime."""
    records, activations = observables_for(world, regime)
    truth = {a.account_id: a.true_relationship_start for a in world}

    truth_years = [_tenure_years(truth[r["customer_id"]], as_of) for r in records]
    naive = [believed_tenure_naive(r, as_of) for r in records]
    separated = [believed_tenure_separated(r, activations, as_of) for r in records]

    # DEFENCE IN DEPTH. The derivation can be defeated by missing paperwork; the
    # R10 class guard is asked, independently, whether what the company wrote is
    # even possible given the account's own meter reads and bills.
    naive_caught = sum(
        1 for record in records
        if record["acquisition_date"] < truth[record["customer_id"]]
        and guard_flags(record, record["acquisition_date"])
    )
    naive_phantoms = sum(
        1 for record in records
        if record["acquisition_date"] < truth[record["customer_id"]]
    )
    separated_written = [derive_supply_start(r, activations) for r in records]
    separated_phantoms = sum(
        1 for record, written in zip(records, separated_written)
        if written is not None and written < truth[record["customer_id"]]
    )
    separated_caught = sum(
        1 for record, written in zip(records, separated_written)
        if written is not None and written < truth[record["customer_id"]]
        and guard_flags(record, written)
    )

    return {
        "regime": regime.name,
        "activation_capture": regime.activation_capture,
        "link_capture": regime.link_capture,
        "naive": score_belief(truth_years, naive),
        "separated": score_belief(truth_years, separated),
        "naive_phantoms": naive_phantoms,
        "naive_caught_by_guard": naive_caught,
        "separated_phantoms": separated_phantoms,
        "separated_caught_by_guard": separated_caught,
    }


#: The sweep is a DIAGNOSTIC over observable quality (R12: a diagnostic, never a
#: target). It is deliberately not a probability distribution over real capture
#: rates -- it isolates WHICH missing observable defeats the mechanism.
SWEEP_REGIMES = (
    FULL_OBSERVABILITY,
    ObservableRegime("activation_lost_link_kept", activation_capture=0.0, link_capture=1.0),
    ObservableRegime("activation_lost_link_lost", activation_capture=0.0, link_capture=0.0),
)


def regime_sweep(world: Sequence[WorldAccount], as_of: str = DEFAULT_AS_OF) -> list[dict]:
    return [measure_regime(world, regime, as_of) for regime in SWEEP_REGIMES]


def _sweep_row(row: dict) -> dict:
    """One regime's line in the ledger `components`. Both beliefs are reported per
    regime, and phantoms are reported separately from guard catches, so a reader can
    see whether a bad answer was PUBLISHED or merely produced and then rejected."""
    naive, separated = row["naive"], row["separated"]
    return {
        "regime": row["regime"],
        "activation_capture": row["activation_capture"],
        "link_capture": row["link_capture"],
        "separated_gap": separated.gap,
        "separated_unknown_share": round(separated.unknown_share, 6),
        "separated_confident_wrong": separated.n_confident_wrong,
        "separated_mean_phantom_years": round(separated.mean_phantom_years, 6),
        "separated_phantoms": row["separated_phantoms"],
        "separated_caught_by_guard": row["separated_caught_by_guard"],
        "naive_gap": naive.gap,
        "naive_confident_wrong": naive.n_confident_wrong,
        "naive_phantoms": row["naive_phantoms"],
        "naive_caught_by_guard": row["naive_caught_by_guard"],
    }


#: What the published gap MEANS. Kept beside the measurement it describes, because a
#: ledger number a later reader cannot interpret is a number they will misread.
HEADLINE_NOTE = (
    "PHANTOM TENURE on a re-contracted customer. Truth = the term boundary the "
    "home-move win actually landed on (world answer key); the company's LIVE "
    "belief reads the predecessor's genesis anchor out of `acquisition_date`, so "
    "every re-contracted account reads as though the relationship never restarted. "
    "The headline gap is that LIVE belief -- the mechanism that fixes it "
    "(C_supply_start_semantic_separation) is BUILT but not yet ROUTED to the 7 "
    "live consumers (C_supply_start_consumer_routing), so the published tenure, "
    "cohort and 'Customer since' figures still carry the phantom. `separated_*` is "
    "the counterfactual once routed; the regime sweep shows where the world still "
    "defeats the built mechanism -- losing the activation event costs COVERAGE "
    "(honest UNKNOWN), but losing the `successor_of` link as well makes it "
    "CONFIDENTLY WRONG again, because the no-successor rung hands back the anchor. "
    "DEFENCE IN DEPTH: `*_caught_by_guard` is how many of those phantoms this "
    "atom's R10 class guard (SUPPLY_START_NOT_BEFORE_FIRST_OBSERVABLE) rejects "
    "anyway, from the account's own meter reads and bills -- observables that "
    "cannot go missing the way the registration paperwork can."
)


def measure(as_of: str = DEFAULT_AS_OF):
    """The coupled measurement. Returns (GapResult, extras).

    The HEADLINE gap is the NAIVE belief under full observability -- what the
    company actually believes and publishes today. The separated mechanism's
    counterfactual and the degraded-regime sweep ride in `components`.
    """
    world = draw_recontracting_world(as_of)
    sweep = regime_sweep(world, as_of)
    headline = sweep[0]

    naive = headline["naive"]
    separated = headline["separated"]

    result = prediction_gap(
        [_tenure_years(a.true_relationship_start, as_of) for a in world],
        [_tenure_years(a.term_anchor, as_of) for a in world],
    )
    result.components.update(naive.as_components("naive"))
    result.components.update(separated.as_components("separated"))
    result.components.update({
        "as_of": as_of,
        "n_accounts": len(world),
        "n_recontracted": sum(1 for a in world if a.is_recontracted),
        "regime_sweep": [_sweep_row(row) for row in sweep],
    })
    result.note = HEADLINE_NOTE

    extras = {
        "world": world,
        "sweep": sweep,
        "headline": headline,
    }
    return result, extras


def _git_head() -> Optional[str]:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Coupled-triad gap: re-contracting world "
                                             "vs the company's believed tenure")
    ap.add_argument("--as-of", default=DEFAULT_AS_OF)
    ap.add_argument("--write-ledger", action="store_true",
                    help="persist the measured gap into coupled_gap_ledger.json")
    args = ap.parse_args()

    result, extras = measure(args.as_of)

    print(f"WORLD  {WORLD_ATOM_ID}")
    print(f"TWIN   {TWIN_ATOM_ID}")
    print(f"as_of  {args.as_of}   accounts={result.components['n_accounts']} "
          f"re-contracted={result.components['n_recontracted']}")
    print()
    print(f"HEADLINE gap (live/naive belief) = {result.gap}")
    print(f"  MAE {result.raw_gap:.4f} yr vs no-skill {result.g0:.4f} yr")
    print()
    print(f"{'regime':<28} {'sep_gap':>9} {'unknown':>9} {'conf_wrong':>11} "
          f"{'phantom_yr':>11} {'guard':>9}")
    for row in result.components["regime_sweep"]:
        gap = row["separated_gap"]
        caught = f"{row['separated_caught_by_guard']}/{row['separated_phantoms']}"
        print(f"{row['regime']:<28} {('n/a' if gap is None else f'{gap:9.4f}'):>9} "
              f"{row['separated_unknown_share']:>9.2f} "
              f"{row['separated_confident_wrong']:>11d} "
              f"{row['separated_mean_phantom_years']:>11.3f} "
              f"{caught:>9}")
    live = result.components["regime_sweep"][0]
    print(f"\nLIVE belief phantoms caught by the R10 class guard: "
          f"{live['naive_caught_by_guard']}/{live['naive_phantoms']}")

    if args.write_ledger:
        write_gap_entry(
            WORLD_ATOM_ID, TWIN_ATOM_ID, result,
            measured_at=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            run_git_commit=_git_head(),
        )
        print("\nledger updated: docs/observability/coupled_gap_ledger.json")


if __name__ == "__main__":
    main()
