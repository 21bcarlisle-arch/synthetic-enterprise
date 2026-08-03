"""F1c -- the HARNESS conversation gap organ (atom F1c_harness_conversation_gap),
the close_to_learn sibling that closes the F1 "simulating conversations" coupled
triad (proposal docs/design/proposals/F1_conversations_coupled_triad_BUILD_PROPOSAL.md
§3c; FRAME docs/design/frame/F1_conversations_coupled_triad_FRAME.md §3c).

THIS ATOM'S PREMISE, CORRECTED (R10 honesty -- checked against the live map, not
assumed): F1a (`simulation/conversation_response.py`) and F1b
(`company/comms/conversation_generator.py` +
`company/comms/susceptibility_estimator.py`) are BOTH ALREADY BUILT to L2
(maturity_map.yaml lines 2440-2479, level_current=2, loop_stage=harden,
LEVEL_UP_SELF_CERTIFIED 2026-07-30). This module exercises the REAL, shipped
F1a/F1b code -- not a synthetic/injected truth fixture -- for all three
measurements below. What is genuinely NOT yet true: F1a/F1b are not invoked by
any `run_phase*.py` driver (grep-confirmed at FRAME time: no
`conversation_response`/`ConversationGenerator`/`SusceptibilityEstimator` symbol
outside `company/comms/`, `simulation/`, and their own tests), so there is no
LIVE population conversation history in `docs/reports/run_output_latest.json`
to read the way `background/dd_h_solvency_gap.py` reads a DD3 block. This organ
is therefore SELF-CONTAINED: it builds its own synthetic customer population and
its own conversation history by calling the real F1a/F1b modules directly, and
is explicit that live-population wiring remains open (see `measure()`
docstring). When that wiring lands, only `_synthetic_population` /
`_train_estimator`'s population source need change -- the three measurement
functions (`belief_vs_truth_gap`, `outcome_uplift_vs_control`,
`intent_leak_rate`) are population-source-agnostic already.

THE THREE THINGS THIS ORGAN REPORTS (atom spec, verbatim from the map):
  1. belief-vs-truth susceptibility GAP per customer (company posterior mean vs
     SIM true scalar) -- `belief_vs_truth_gap` / `summarise_gap`.
  2. whether the conversation improved the outcome vs a no-message/neutral
     control, CA-weighted 55/35/10 (CS-heavy, NOT equal-weighted) --
     `outcome_uplift_vs_control` / `ca_weighted_outcome_score`.
  3. the MANDATORY R15 intent-leak control -- a company whose action
     correlates with the true hidden trait BEYOND what its observed replies
     justify -- `intent_leak_rate` / `detect_intent_leak`.

THE WALL (binding, load-bearing). This is HARNESS code, so like
`background/dd_h_solvency_gap.py` / `tools/couple_cohort.py` it is one of the
few places PERMITTED to hold the SIM's true hidden scalar (read via
`simulation.nudge_physics`) and the company's belief (read via
`company.comms.susceptibility_estimator`) side by side -- that is the referee's
job, not a violation (`background/` is outside the `company/`+`saas/` scope
`tools.epistemic_verifier` scans, exactly like its DD-H precedent). What is
STRUCTURALLY forbidden and asserted by `tests/harness/test_conversation_gap.py`:
  * this module writes to exactly ONE path, its own ledger
    (`GAP_LEDGER_PATH`) -- never into any `company/`, `saas/`, or `simulation/`
    file, and never mutates any externally-supplied estimator/generator (every
    measurement function either takes a fresh throwaway estimator it owns, or
    is a pure read);
  * this module is never imported by `background/supervisor.py` / the draw --
    the gap is a DIAGNOSTIC (R12), it must never feed priority, reward,
    selection, or scheduling.

REPRODUCING THE HONEST-EXPLORATION RESIDUAL (R10, named not papered over): the
shipped F1b `ConversationGenerator`, wired to a genuinely empty estimator, sends
`neutral_framed`/`neutral_toned` FOREVER -- it has no self-directed exploration
policy (confirmed by reading `_tone_and_framing`: an empty belief always
resolves to the neutral default via `_argmax_value`'s empty-means branch). A
real supplier CRM would run some exploration/A-B schedule to *discover* which
lever lands; F1b does not ship one. Without SOME exploration, this triad can
never depart from "always neutral" in a closed loop and the belief-vs-truth gap
would be a trivial, uninformative 100% for every customer. `_train_estimator`
below supplies that exploration schedule FOR MEASUREMENT PURPOSES ONLY, on a
throwaway estimator this module owns -- it does not alter F1b's shipped
behaviour and is not a production fix. The absence of a real exploration policy
in F1b is a genuine residual, logged here for a future atom, not fixed in this
file_scope.

C-S2 DETERMINISM: every function here is a pure function of its inputs (the
synthetic population id scheme is deterministic; `simulation.conversation_response
.respond` and the belief update are both already pure/idempotent by F1a/F1b's own
design). `measure()` called twice with the same arguments returns identical
output -- no wall-clock, no unseeded randomness anywhere in this module.

ANTI-GOAL-SEEK (R12): every number this organ produces is a DIAGNOSTIC. Success
is the intent-leak control CATCHING a peeking variant, never the gap or the
uplift being any particular size -- nothing here is tuned toward a target value.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Mapping, Optional, Sequence

from interface.contracts.conversation_seam import (
    Channel,
    ConversationMessage,
    Product,
    ResponseAction,
    Situation,
)
from simulation import conversation_response as _sim_conversation_response
from simulation import nudge_physics as _sim_nudge_physics
from company.comms.conversation_generator import ConversationGenerator, CustomerSegment
from company.comms.susceptibility_estimator import (
    FRAMING_VALUES,
    SusceptibilityEstimator,
    TONE_VALUES,
)

PROJECT_DIR = Path(__file__).resolve().parent.parent
GAP_LEDGER_PATH = PROJECT_DIR / "docs" / "observability" / "conversation_gap_ledger.json"

# The lever-value <-> true-category matching vocabulary, duplicated HERE BY
# CONVENTION (never by import of either side's private symbol):
# `simulation/nudge_physics.py::_MATCHING_FRAMING`/`_MATCHING_TONE` hold the SIM
# truth-side mapping; `company/comms/susceptibility_estimator.py::
# _FRAMING_VALUE_TO_CATEGORY`/`_TONE_VALUE_TO_CATEGORY` hold the company-side
# inverse. The harness independently re-derives the SAME shared lever
# vocabulary both sides already speak (exactly the company module's own
# comment: "the company happens to speak the same lever language the world
# responds to, exactly as a real supplier's ... offer is the same artefact the
# customer reacts to") -- a third copy is the referee's own, read-only.
_FRAMING_CATEGORY_TO_LEVER: dict[str, str] = {
    _sim_nudge_physics.FramingSusceptibility.LOSS_AVERSE.value: "loss_framed",
    _sim_nudge_physics.FramingSusceptibility.GAIN_RESPONSIVE.value: "gain_framed",
    _sim_nudge_physics.FramingSusceptibility.NEUTRAL.value: "neutral_framed",
}
_TONE_CATEGORY_TO_LEVER: dict[str, str] = {
    _sim_nudge_physics.ToneSusceptibility.EMPATHETIC_RESPONSIVE.value: "empathetic_toned",
    _sim_nudge_physics.ToneSusceptibility.FIRM_RESPONSIVE.value: "firm_toned",
    _sim_nudge_physics.ToneSusceptibility.NEUTRAL.value: "neutral_toned",
}

_DEFAULT_CUSTOMER_COUNT = 120
_DEFAULT_TRAINING_ROUNDS = 15
# Default situation subset for `measure()` (simplicity guard -- not the full
# eight-situation set every tick): one framing-sensitive (RENEWAL), one
# tone-sensitive (MISSED_PAYMENT), and the CA-complaints-heaviest situation
# (INBOUND_COMPLAINT, tone-sensitive). Callers wanting full Q1 coverage pass
# `situations=list(Situation)` explicitly.
_DEFAULT_SITUATIONS: tuple[Situation, ...] = (
    Situation.RENEWAL,
    Situation.MISSED_PAYMENT,
    Situation.INBOUND_COMPLAINT,
)
# The honest baseline leak rate is EXACTLY 0.0 (proven by construction, see
# `detect_intent_leak`); any positive threshold already gives slack, so this is
# not tuned to make the alarm quiet (R12).
_INTENT_LEAK_THRESHOLD = 0.05

# Which lever a situation's OUTCOME actually responds to -- duplicated BY
# CONVENTION from `simulation/conversation_response.py::_SITUATION_PROFILE`'s
# own `framing_sensitive`/`tone_sensitive` flags (a private table; this harness
# does not import it, it re-derives the same public fact stated in the module's
# own docstring and the proposal/FRAME §3 tables: "no situation is both -- the
# company chooses one lever per message, and only the matched lever lifts the
# base rate"). Used ONLY to decide which lever `_train_estimator` VARIES for a
# situation during exploration -- holding the lever that situation's outcome
# does not respond to fixed at neutral, so training evidence is not diluted by
# a lever the outcome never reacted to. Every `Situation` member is exactly one
# of these two sets (exhaustive, tested).
_FRAMING_SENSITIVE_SITUATIONS: frozenset[Situation] = frozenset(
    {
        Situation.WELCOME,
        Situation.RENEWAL,
        Situation.TARIFF_CHANGE,
        Situation.WIN_BACK,
        Situation.ANNUAL_STATEMENT,
    }
)
_TONE_SENSITIVE_SITUATIONS: frozenset[Situation] = frozenset(
    {Situation.MISSED_PAYMENT, Situation.BILL_SHOCK, Situation.INBOUND_COMPLAINT}
)


class ConversationGapUnmeasurable(ValueError):
    """Raised when this organ's own inputs are unusable (empty population, an
    upstream F1a/F1b call failing) -- an R15 FAIL-CLOSED refusal to fabricate a
    gap/uplift/leak-rate rather than reporting an honest not-measurable row."""


# ---------------------------------------------------------------------------
# Synthetic population + training (self-contained, see module docstring).
# ---------------------------------------------------------------------------


def _synthetic_population(n: int = _DEFAULT_CUSTOMER_COUNT) -> list[str]:
    """A deterministic customer-id population this organ owns for measurement.
    NOT a live population -- see module docstring on live-wiring status."""
    if n <= 0:
        raise ConversationGapUnmeasurable(f"customer_count must be positive, got {n}")
    return [f"f1c_harness_cust_{i:04d}" for i in range(n)]


def true_framing_category(customer_id: str) -> str:
    """The SIM ground truth (read directly -- the harness is the referee)."""
    return _sim_nudge_physics.susceptibility_for(customer_id).value


def true_tone_category(customer_id: str) -> str:
    return _sim_nudge_physics.tone_susceptibility_for(customer_id).value


def _train_estimator(
    estimator: SusceptibilityEstimator,
    customer_ids: Sequence[str],
    situation: Situation,
    product: Product,
    rounds: int = _DEFAULT_TRAINING_ROUNDS,
) -> None:
    """Seed `estimator` with a genuine observed-reply history, driven ENTIRELY
    through the real F1a `respond()` + F1b `observe_response()` -- a
    round-robin exploration across every value of the lever THIS situation's
    outcome actually responds to (see module docstring: F1b ships no
    exploration policy of its own, so this harness supplies one for
    measurement purposes on a throwaway estimator), holding the other,
    outcome-irrelevant lever fixed at neutral so its evidence is not diluted
    by a lever the outcome never reacted to."""
    vary_framing = situation in _FRAMING_SENSITIVE_SITUATIONS
    for round_idx in range(rounds):
        framing_value = FRAMING_VALUES[round_idx % len(FRAMING_VALUES)] if vary_framing else "neutral_framed"
        tone_value = TONE_VALUES[round_idx % len(TONE_VALUES)] if not vary_framing else "neutral_toned"
        for customer_id in customer_ids:
            message = ConversationMessage(
                message_id=f"{customer_id}:{situation.value}:train:{round_idx}",
                situation=situation,
                channel=Channel.EMAIL,
                product=product,
                tone=tone_value,
                framing=framing_value,
                emitted_step=round_idx,
            )
            response = _sim_conversation_response.respond(customer_id, message)
            estimator.observe_response(customer_id, message, response)


# ---------------------------------------------------------------------------
# (1) Belief-vs-truth susceptibility gap.
# ---------------------------------------------------------------------------


def belief_vs_truth_gap(
    customer_ids: Sequence[str], estimator: SusceptibilityEstimator
) -> list[dict]:
    """Per-customer belief-vs-truth row: the company's posterior CATEGORY
    (`estimator.inferred_*_susceptibility`) against the SIM's true CATEGORY
    (`true_*_category`), plus a continuous gap -- how far the belief's
    confidence in the TRUE matching lever sits below full confidence (1.0). A
    customer never trained defaults the continuous gap to the honest Beta(1,1)
    prior mean (0.5), never a fabricated 0."""
    rows: list[dict] = []
    for customer_id in customer_ids:
        truth_framing = true_framing_category(customer_id)
        truth_tone = true_tone_category(customer_id)
        belief_framing = estimator.inferred_framing_susceptibility(customer_id)
        belief_tone = estimator.inferred_tone_susceptibility(customer_id)
        framing_means = estimator.belief(customer_id).framing_means()
        tone_means = estimator.belief(customer_id).tone_means()
        true_framing_lever = _FRAMING_CATEGORY_TO_LEVER[truth_framing]
        true_tone_lever = _TONE_CATEGORY_TO_LEVER[truth_tone]
        framing_gap = 1.0 - framing_means.get(true_framing_lever, 0.5)
        tone_gap = 1.0 - tone_means.get(true_tone_lever, 0.5)
        rows.append(
            {
                "customer_id": customer_id,
                "true_framing_category": truth_framing,
                "belief_framing_category": belief_framing,
                "framing_category_match": belief_framing == truth_framing,
                "framing_gap": round(framing_gap, 6),
                "true_tone_category": truth_tone,
                "belief_tone_category": belief_tone,
                "tone_category_match": belief_tone == truth_tone,
                "tone_gap": round(tone_gap, 6),
            }
        )
    return rows


def summarise_gap(rows: Sequence[Mapping]) -> dict:
    n = len(rows)
    if n == 0:
        raise ConversationGapUnmeasurable("no customers to score the belief-vs-truth gap over")
    return {
        "n_customers": n,
        "framing_category_match_rate": round(sum(r["framing_category_match"] for r in rows) / n, 6),
        "tone_category_match_rate": round(sum(r["tone_category_match"] for r in rows) / n, 6),
        "mean_framing_gap": round(sum(r["framing_gap"] for r in rows) / n, 6),
        "mean_tone_gap": round(sum(r["tone_gap"] for r in rows) / n, 6),
    }


# ---------------------------------------------------------------------------
# (2) Did the conversation improve the outcome -- Citizens-Advice-weighted
# (55% customer service / 35% complaints / 10% commitments), NOT equal-
# weighted. Source: docs/market_research/f1_simulating_conversations.md,
# "Citizens Advice star-rating" table (Open item 1).
# ---------------------------------------------------------------------------

CA_CUSTOMER_SERVICE_WEIGHT = 0.55
CA_COMPLAINTS_WEIGHT = 0.35
CA_COMMITMENTS_WEIGHT = 0.10

_POSITIVE_ACTIONS = frozenset({ResponseAction.REPLY, ResponseAction.CLICK, ResponseAction.PAY})

# Customer commitments (Guaranteed Standards / voluntary guarantees, 10%
# weight) is explicitly "policy, not conversation" per the CA methodology
# table -- this triad has no policy-compliance model, so it is carried as a
# named CONSTANT baseline, never faked as conversation-movable. This is why
# the uplift below is driven entirely by the 90% (55+35) that conversation CAN
# move -- the 10% is honestly inert by design, not silently dropped.
_COMMITMENTS_BASELINE = 1.0


def _service_score(action: ResponseAction) -> float:
    """CS axis proxy (contact ease / timely, engaged service, 55% weight): a
    positive engaged action scores full marks; silence is neutral (no service
    was tested either way); any negative/failure action scores zero."""
    if action in _POSITIVE_ACTIONS:
        return 1.0
    if action is ResponseAction.NO_REPLY:
        return 0.5
    return 0.0  # MISS / SWITCH / COMPLAIN


def _complaints_score(action: ResponseAction) -> float:
    """Complaints-handling axis proxy (35% weight): a raised COMPLAIN is the
    direct negative signal; every other action is a clean no-complaint
    outcome."""
    return 0.0 if action is ResponseAction.COMPLAIN else 1.0


def ca_weighted_outcome_score(action: ResponseAction) -> float:
    """The Citizens-Advice-weighted (55/35/10) outcome score for one observed
    action, in [0, 1]."""
    return (
        CA_CUSTOMER_SERVICE_WEIGHT * _service_score(action)
        + CA_COMPLAINTS_WEIGHT * _complaints_score(action)
        + CA_COMMITMENTS_WEIGHT * _COMMITMENTS_BASELINE
    )


def outcome_uplift_vs_control(
    customer_ids: Sequence[str],
    estimator: SusceptibilityEstimator,
    situation: Situation,
    product: Product,
    step: int,
) -> dict:
    """CA-weighted outcome score of the company's real (belief-informed)
    message vs a neutral-message control, over the same customers/situation.

    VARIANCE REDUCTION (common random numbers, not a mocked comparison): the
    control message reuses the TREATED message's `message_id`, so F1a's named
    RNG substreams (keyed on customer_id + message_id) draw IDENTICAL random
    numbers for both arms -- the ONLY thing that can move the outcome is the
    differing tone/framing lever. This isolates the causal effect using the
    real, unmodified `simulation.conversation_response.respond`."""
    if not customer_ids:
        raise ConversationGapUnmeasurable("no customers to score the outcome uplift over")
    generator = ConversationGenerator(estimator)
    treated_scores: list[float] = []
    control_scores: list[float] = []
    for customer_id in customer_ids:
        treated_message = generator.generate(customer_id, CustomerSegment(), situation, product, step)
        treated_response = _sim_conversation_response.respond(customer_id, treated_message)
        treated_scores.append(ca_weighted_outcome_score(treated_response.action))

        control_message = ConversationMessage(
            message_id=treated_message.message_id,
            situation=situation,
            channel=treated_message.channel,
            product=product,
            tone="neutral_toned",
            framing="neutral_framed",
            emitted_step=step,
        )
        control_response = _sim_conversation_response.respond(customer_id, control_message)
        control_scores.append(ca_weighted_outcome_score(control_response.action))

    n = len(customer_ids)
    treated_mean = sum(treated_scores) / n
    control_mean = sum(control_scores) / n
    return {
        "n_customers": n,
        "situation": situation.value,
        "treated_ca_weighted_score": round(treated_mean, 6),
        "control_ca_weighted_score": round(control_mean, 6),
        "uplift": round(treated_mean - control_mean, 6),
    }


# ---------------------------------------------------------------------------
# (3) MANDATORY R15 intent-leak control.
# ---------------------------------------------------------------------------

GenerateFn = Callable[[str, CustomerSegment, Situation, Product, int], ConversationMessage]


def honest_zero_evidence_generate(
    customer_id: str, segment: CustomerSegment, situation: Situation, product: Product, step: int
) -> ConversationMessage:
    """Reference HONEST `generate_fn`: a FRESH `ConversationGenerator` wired to
    a FRESH, EMPTY `SusceptibilityEstimator` -- exactly what a real supplier
    would send on its very first contact with a customer it has never
    observed. New estimator/generator per call -- no shared/leaked state."""
    generator = ConversationGenerator(SusceptibilityEstimator())
    return generator.generate(customer_id, segment, situation, product, step)


def intent_leak_rate(
    generate_fn: GenerateFn,
    customer_ids: Sequence[str],
    situation: Situation,
    product: Product,
    step: int = 0,
) -> dict:
    """THE MANDATORY R15 CONTROL. Calls `generate_fn` for each customer with
    ZERO PRIOR OBSERVATIONS and checks whether the EMITTED lever already
    matches the customer's TRUE hidden category (read directly from
    `simulation.nudge_physics` -- the harness is the referee).

    With zero observed replies there is NO legitimate evidence an honest
    company could have used to pick a matched, non-neutral lever (proposal
    §3c / FRAME §3c: "a company whose action correlates with the true hidden
    trait beyond what its observed replies justify is an intent-leak"). Any
    non-neutral match at this point can only be explained by reading the truth
    directly. Customers whose TRUE category is 'neutral' are excluded from
    each axis's denominator -- a neutral send to a neutral-truth customer is
    not evidence of leaking, since neutral is also the honest zero-evidence
    default.

    FAIL-OPEN GUARD (R15 -- found empirically while hardening this atom): an
    axis with ZERO scored customers must never report a fabricated `0.0`
    ("clean") leak rate -- that is indistinguishable from a genuinely-tested
    clean result and would let a starved population (e.g. an all-neutral-truth
    subset, or an accidentally-empty one) silently read as "no leak detected"
    when NOTHING was actually checked. An unscored axis reports `None`
    instead; `detect_intent_leak` treats `None` as "this axis contributes no
    verdict", never as evidence of cleanliness. If BOTH axes are starved (no
    evidence anywhere), that is a total control failure -- fail CLOSED with
    `ConversationGapUnmeasurable`, matching this module's fail-closed
    philosophy elsewhere (`summarise_gap`, `outcome_uplift_vs_control`)."""
    if not customer_ids:
        raise ConversationGapUnmeasurable("no customers to score the intent-leak control over")
    framing_leaks = tone_leaks = framing_scored = tone_scored = 0
    for customer_id in customer_ids:
        message = generate_fn(customer_id, CustomerSegment(), situation, product, step)
        truth_framing = true_framing_category(customer_id)
        truth_tone = true_tone_category(customer_id)
        if truth_framing != _sim_nudge_physics.FramingSusceptibility.NEUTRAL.value:
            framing_scored += 1
            if message.framing == _FRAMING_CATEGORY_TO_LEVER[truth_framing]:
                framing_leaks += 1
        if truth_tone != _sim_nudge_physics.ToneSusceptibility.NEUTRAL.value:
            tone_scored += 1
            if message.tone == _TONE_CATEGORY_TO_LEVER[truth_tone]:
                tone_leaks += 1
    if framing_scored == 0 and tone_scored == 0:
        raise ConversationGapUnmeasurable(
            "zero non-neutral-truth customers scored on EITHER axis -- the "
            "intent-leak control has no evidence to certify a clean result "
            "from (R15 fail-open guard); widen the population/situation "
            "rather than trust a silent 0.0"
        )
    return {
        "n_customers": len(customer_ids),
        "framing_scored": framing_scored,
        "tone_scored": tone_scored,
        "framing_leak_rate": round(framing_leaks / framing_scored, 6) if framing_scored else None,
        "tone_leak_rate": round(tone_leaks / tone_scored, 6) if tone_scored else None,
    }


def detect_intent_leak(rate_row: Mapping[str, Optional[float]], threshold: float = _INTENT_LEAK_THRESHOLD) -> bool:
    """Fires True iff EITHER lever's leak rate exceeds `threshold`. The honest
    baseline is EXACTLY 0.0 (proven by construction -- see
    `honest_zero_evidence_generate` / `ConversationGenerator._tone_and_framing`'s
    empty-belief default), so any positive threshold already gives slack; this
    is not tuned to make the alarm quiet (R12). An axis reported as `None`
    (zero scored customers, see `intent_leak_rate`'s fail-open guard)
    contributes no verdict -- it is never treated as evidence of cleanliness
    nor coerced to a number that could raise a TypeError."""
    framing_rate = rate_row.get("framing_leak_rate")
    tone_rate = rate_row.get("tone_leak_rate")
    return (
        (framing_rate is not None and framing_rate > threshold)
        or (tone_rate is not None and tone_rate > threshold)
    )


# ---------------------------------------------------------------------------
# Top-level measurement + ledger (mirrors background/dd_h_solvency_gap.py).
# ---------------------------------------------------------------------------


def measure(
    customer_count: int = _DEFAULT_CUSTOMER_COUNT,
    situations: Optional[Sequence[Situation]] = None,
    product: Product = Product.DUAL_FUEL,
    training_rounds: int = _DEFAULT_TRAINING_ROUNDS,
) -> dict:
    """Run the full self-contained F1c measurement against the REAL, shipped
    F1a/F1b modules (see module docstring on the self-contained/not-yet-live-
    wired status). FAIL-CLOSED: any failure raises `ConversationGapUnmeasurable`
    -- callers must not fabricate a row on exception."""
    try:
        customer_ids = _synthetic_population(customer_count)
        chosen_situations = list(situations) if situations else list(_DEFAULT_SITUATIONS)
        if not chosen_situations:
            raise ConversationGapUnmeasurable("no situations to measure")
        estimator = SusceptibilityEstimator()
        for situation in chosen_situations:
            _train_estimator(estimator, customer_ids, situation, product, training_rounds)

        gap_rows = belief_vs_truth_gap(customer_ids, estimator)
        gap_summary = summarise_gap(gap_rows)

        uplift_by_situation = {
            situation.value: outcome_uplift_vs_control(
                customer_ids, estimator, situation, product, training_rounds
            )
            for situation in chosen_situations
        }

        leak_row = intent_leak_rate(
            honest_zero_evidence_generate, customer_ids, chosen_situations[0], product
        )
        leak_fired = detect_intent_leak(leak_row)
    except ConversationGapUnmeasurable:
        raise
    except Exception as e:  # noqa: BLE001 -- fail-closed, never a silent/fabricated pass
        raise ConversationGapUnmeasurable(f"F1c measurement failed: {e}") from e

    return {
        "measurable": True,
        "n_customers": len(customer_ids),
        "situations_measured": [s.value for s in chosen_situations],
        "belief_vs_truth_gap": gap_summary,
        "outcome_uplift_by_situation": uplift_by_situation,
        "intent_leak": {**leak_row, "fired": leak_fired},
    }


def _load_ledger(ledger_path: Path) -> list[dict]:
    try:
        data = json.loads(ledger_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


def record_gap(
    *,
    measured_at: str,
    run_git_commit: Optional[str] = None,
    ledger_path: Optional[Path] = None,
    **measure_kwargs,
) -> dict:
    """Measure + APPEND a dated row to the history ledger (the ONLY file this
    module ever writes). Determinism (C-S2): the caller supplies `measured_at`
    / `run_git_commit`; this function never calls a clock. A not-measurable row
    is recorded too (FAIL-SILENT guard) -- an honest absence stays legible in
    history rather than a silent skip."""
    lp = ledger_path or GAP_LEDGER_PATH
    try:
        row = measure(**measure_kwargs)
    except ConversationGapUnmeasurable as e:
        row = {"measurable": False, "reason": str(e)}
    row["measured_at"] = measured_at
    row["run_git_commit"] = run_git_commit
    rows = _load_ledger(lp)
    rows.append(row)
    lp.parent.mkdir(parents=True, exist_ok=True)
    lp.write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    return row


def retro_gap_line(**measure_kwargs) -> str:
    """One-line summary for the morning self-note (NOT wired in from this
    file_scope -- see FRAME doc residuals). PURE (no side effect) and
    fail-closed: any measurement error returns an honest RED string, never a
    fabricated number."""
    try:
        row = measure(**measure_kwargs)
    except ConversationGapUnmeasurable as e:
        return f"conversation belief-vs-truth gap NOT MEASURABLE ({e})"
    gs = row["belief_vs_truth_gap"]
    leak = row["intent_leak"]
    leak_txt = "⚠ INTENT-LEAK FIRED" if leak["fired"] else "clean (no intent-leak detected)"
    return (
        f"conversation belief-vs-truth gap (framing match {gs['framing_category_match_rate']:.0%}, "
        f"tone match {gs['tone_category_match_rate']:.0%}) over {row['n_customers']} synthetic "
        f"customers across {len(row['situations_measured'])} situations; "
        f"intent-leak control: {leak_txt}"
    )


def main() -> None:
    print(retro_gap_line())


if __name__ == "__main__":
    main()
