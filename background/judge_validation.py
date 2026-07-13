"""JUDGE VALIDATION -- measuring the verdict-producing organs
(JUDGING_THE_JUDGES.md Part 1, director P1, 2026-07-13).

THE PROBLEM (the honest residual that started this): the LLM-judge verdict
QUALITY is structurally un-mutation-testable. You cannot inject a defect that
proves a JUDGMENT was bad -- a mutation test proves a MECHANICAL control fires
on its named defect (CONTROLS_THAT_CANNOT_FAIL / R15), but a judge's output is
an opinion, not a computed value, so there is no mutation whose "the control
must now FAIL" you can assert.

THE STANDING RULE this module makes real (lands in CLAUDE.md separately):
  "Where a control cannot be mutation-tested, it must be OUTCOME-tested.
   No verdict-producing organ escapes measurement entirely -- if we cannot
   test HOW it decides, we test WHETHER it was right."

FOUR APPROACHES (the staged doc's own four; each is a metric definition + the
computation over whatever real data exists, honest about what only accrues live):

  1. OUTCOME CORRELATION (strongest, nearly free) -- a judge whose PASSES later
     FAIL is a bad judge. The trust ledger already records
     `defects_found_post_close`; `trust_ledger.record_post_close_defect` attaches
     a later-found defect back to the PASS that let it through.
     `outcome_error_rates()` computes, per judge (evaluator) and per task class,
     (passes that later proved defective) / (total passes) = the judge's
     empirical error rate. Validates judgment by CONSEQUENCE.

  2. CONSISTENCY -- same input, repeated: does the judge return the same verdict?
     `consistency_flip_rate()` scores a list of verdicts from repeated identical
     invocations. A judge that flips on identical evidence is noise and its
     verdict cannot support a promotion. Real-Opus flip-rate accrues live (each
     real repeated invocation appends a sample); the metric + a stubbed judge are
     testable here without network.

  3. INDEPENDENCE -- differently-primed judges (persona/seed/context) on the same
     artefact: do they agree? `independence_disagreement_rate()` scores a mapping
     {judge -> verdict}. Systematic disagreement is a finding about the JUDGE, not
     the artefact. Accrues live as real independent judges are run on shared
     artefacts.

  4. GOLD SET -- the director's own Expert Hours are human-adjudicated cases (the
     C6 SME-as-household bill, the naked-hedging volatility-leak chart, the
     population smell-test catch, the C1 meter-read mismatch). `load_gold_set()`
     reads tests/fixtures/judge_gold_set/; `score_judge_against_gold()` runs a
     judge over them and returns its MISS rate -- a judge that misses what the
     director caught is a weak judge, now with a number. A real LLM judge's score
     accrues live (it must be invoked per case); mechanical controls and baseline
     judges (rubber-stamp / oracle) score deterministically NOW.

ANTI-CAPTURE / LAW A: every number here is a DIAGNOSTIC, never a target. Nothing
in this module feeds back to tune a judge, a rubric, or a threshold. A judge is
never "improved" toward a gold-set score -- a rising score with no independent
corroboration is exactly the grader-capture tell `trust_ledger` already flags.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Optional

from background import trust_ledger as tl

PROJECT_DIR = Path(__file__).resolve().parent.parent
GOLD_SET_DIR = PROJECT_DIR / "tests" / "fixtures" / "judge_gold_set"

# A judge, for validation purposes, maps a case-dict to a verdict string.
# "defect" = the judge flagged a problem (NEEDS_WORK / fired / held);
# "pass"   = the judge let it through. Any other string is treated as "pass"
# for gold-set scoring (a non-committal verdict did NOT catch the defect).
JudgeFn = Callable[[dict], str]

VERDICT_DEFECT = "defect"
VERDICT_PASS = "pass"


# ── APPROACH 1: OUTCOME CORRELATION ──────────────────────────────────────────
def outcome_error_rates(entries: Optional[list[dict]] = None) -> dict:
    """Per (evaluator, task_class): the judge's empirical error rate =
    (PASS verdicts whose work LATER proved defective) / (total PASS verdicts).

    Reads the trust ledger (the ONE place post-close defects are attached to the
    verdict that let them through, via `record_post_close_defect`). This is the
    strongest validation because it needs no extra apparatus -- the data is a
    by-product of running the business, and a judge cannot argue with a defect
    reality found after it signed off.

    Returns {"per_judge_class": {...}, "per_judge": {...}, "overall": {...}}.
    `error_rate` is None where there are zero PASS verdicts (never claim an error
    rate from an empty record -- R12 anti-goal-seek applied to the metric itself).
    """
    if entries is None:
        entries = tl._load_ledger()

    def _blank():
        return {"passes": 0, "passes_with_later_defect": 0,
                "total_post_close_defects": 0, "error_rate": None}

    per_jc: dict = defaultdict(_blank)
    per_j: dict = defaultdict(_blank)
    overall = _blank()

    for e in entries:
        if e.get("verdict") != tl.Verdict.PASS.value:
            continue
        judge = e.get("evaluator_name", "?")
        klass = e.get("task_class", "?")
        d = int(e.get("defects_found_post_close", 0) or 0)
        for bucket in (per_jc[(judge, klass)], per_j[judge], overall):
            bucket["passes"] += 1
            bucket["total_post_close_defects"] += d
            if d > 0:
                bucket["passes_with_later_defect"] += 1

    def _finalise(bucket):
        if bucket["passes"] > 0:
            bucket["error_rate"] = round(
                bucket["passes_with_later_defect"] / bucket["passes"], 4)
        return bucket

    return {
        "per_judge_class": {f"{j}|{k}": _finalise(v) for (j, k), v in per_jc.items()},
        "per_judge": {j: _finalise(v) for j, v in per_j.items()},
        "overall": _finalise(overall),
    }


# ── APPROACH 2: CONSISTENCY ───────────────────────────────────────────────────
def consistency_flip_rate(verdicts: list[str]) -> dict:
    """Same input repeated -> same verdict? `verdicts` is the list of verdicts a
    single judge returned across N identical invocations. flip_rate = fraction of
    samples that DISAGREE with the modal verdict; 0.0 = perfectly consistent,
    -> (N-1)/N as it approaches maximal disagreement. Fewer than 2 samples ->
    flip_rate None (a single sample cannot be inconsistent -- honest, not zero)."""
    n = len(verdicts)
    if n < 2:
        return {"samples": n, "flip_rate": None, "modal_verdict": (verdicts[0] if verdicts else None),
                "distinct_verdicts": len(set(verdicts))}
    counts = Counter(verdicts)
    modal, modal_n = counts.most_common(1)[0]
    return {
        "samples": n,
        "flip_rate": round((n - modal_n) / n, 4),
        "modal_verdict": modal,
        "distinct_verdicts": len(counts),
    }


def repeat_invoke(judge_fn: JudgeFn, case: dict, n: int) -> list[str]:
    """Invoke a judge N times on the SAME input and collect its verdicts -- the
    live-accrual driver for `consistency_flip_rate`. With a real Opus judge this
    spends N invocations; tests pass a deterministic/stubbed judge_fn. The point
    of the metric is precisely to expose a judge whose `judge_fn` is NOT a pure
    function of its input."""
    return [judge_fn(case) for _ in range(n)]


# ── APPROACH 3: INDEPENDENCE ──────────────────────────────────────────────────
def independence_disagreement_rate(verdicts_by_judge: dict) -> dict:
    """Differently-primed judges on the SAME artefact -> do they agree?
    `verdicts_by_judge` = {judge_name: verdict}. disagreement_rate = fraction of
    judges NOT holding the majority verdict; 0.0 = unanimous. A high rate is a
    finding about the JUDGES (their priming/persona/seed drives the verdict more
    than the artefact does), not about the artefact. Fewer than 2 judges ->
    None (independence is undefined for a single judge)."""
    verdicts = list(verdicts_by_judge.values())
    n = len(verdicts)
    if n < 2:
        return {"judges": n, "disagreement_rate": None, "majority_verdict": None,
                "unanimous": None}
    counts = Counter(verdicts)
    majority, majority_n = counts.most_common(1)[0]
    return {
        "judges": n,
        "disagreement_rate": round((n - majority_n) / n, 4),
        "majority_verdict": majority,
        "unanimous": len(counts) == 1,
        "verdicts_by_judge": dict(verdicts_by_judge),
    }


# ── APPROACH 4: GOLD SET ──────────────────────────────────────────────────────
def load_gold_set(gold_dir: Optional[Path] = None) -> list[dict]:
    """Load the director-Expert-Hour gold cases. Each is a real case the director
    (or an equivalent human adjudication) CAUGHT -- so every case's known verdict
    is 'defect'. A judge that returns 'pass' on one MISSED what the director saw."""
    gold_dir = gold_dir or GOLD_SET_DIR
    cases = []
    for p in sorted(gold_dir.glob("*.json")):
        cases.append(json.loads(p.read_text(encoding="utf-8")))
    return cases


def score_judge_against_gold(judge_fn: JudgeFn,
                             gold_cases: Optional[list[dict]] = None) -> dict:
    """Run `judge_fn` over every gold case and score it. Since every gold case's
    director verdict is 'defect', the judge's job is to return 'defect' too.
      recall  = caught / total       (of the director's catches, how many the judge also caught)
      misses  = the cases the judge PASSED that the director flagged (the weak spots, named)
    A perfect judge scores recall 1.0; a rubber stamp scores 0.0. The number is a
    DIAGNOSTIC -- never tune a judge toward it (Law A / anti-capture)."""
    gold_cases = gold_cases if gold_cases is not None else load_gold_set()
    caught, misses = 0, []
    for case in gold_cases:
        verdict = judge_fn(case)
        if verdict == VERDICT_DEFECT:
            caught += 1
        else:
            misses.append({"case_id": case.get("case_id"),
                           "returned": verdict,
                           "defect_class": case.get("defect_class")})
    total = len(gold_cases)
    return {
        "total_cases": total,
        "caught": caught,
        "missed": len(misses),
        "recall": round(caught / total, 4) if total else None,
        "misses": misses,
    }


# ── baseline judges (deterministic; give a REAL number now, and prove the
#    scorer discriminates -- a scorer that a rubber stamp passes is theatre) ──
def rubber_stamp_judge(_case: dict) -> str:
    """The null judge: passes everything. Scores recall 0.0 against the gold set
    by construction -- if it ever scored higher, the gold set / scorer is broken."""
    return VERDICT_PASS


def oracle_judge(case: dict) -> str:
    """The ceiling: reads the case's own recorded director verdict. Scores recall
    1.0 by construction -- a sanity check that the scorer credits a real catch,
    the upper mirror of the rubber stamp's lower one."""
    return case.get("director_verdict", VERDICT_PASS)


# ── the summary the site + digest consume ────────────────────────────────────
def summary(entries: Optional[list[dict]] = None,
            gold_cases: Optional[list[dict]] = None) -> dict:
    """One dict wiring all four approaches, for `tools/generate_judge_validation_data.py`
    and the digest. Consistency/independence carry the metric DEFINITION plus a
    note that real-Opus samples accrue live (there is no network under the publish
    path to invoke real judges N times), matching how the naive organ's real-Opus
    hit-rate and the twin's fidelity metric accrue over live runs."""
    gold_cases = gold_cases if gold_cases is not None else load_gold_set()
    return {
        "standing_rule": (
            "Where a control cannot be mutation-tested, it must be OUTCOME-tested. "
            "No verdict-producing organ escapes measurement."
        ),
        "outcome_correlation": outcome_error_rates(entries),
        "gold_set": {
            "cases": [{"case_id": c.get("case_id"),
                       "director_verdict": c.get("director_verdict"),
                       "defect_class": c.get("defect_class"),
                       "source": c.get("source")} for c in gold_cases],
            "rubber_stamp_baseline": score_judge_against_gold(rubber_stamp_judge, gold_cases),
            "oracle_ceiling": score_judge_against_gold(oracle_judge, gold_cases),
            "note": ("Real LLM-judge (phase-close-evaluator, cold-eyes) recall against "
                     "these cases accrues live -- each case must be put to the judge as a "
                     "fresh-context artefact; the baseline (rubber-stamp=0.0) and ceiling "
                     "(oracle=1.0) bound the score and prove the scorer discriminates now."),
        },
        "consistency": {
            "metric": "flip_rate = fraction of repeated-identical-input verdicts disagreeing with the modal verdict",
            "accrues_live": True,
            "note": ("Each real repeated invocation of an Opus judge on identical evidence "
                     "appends a sample; flip_rate>0 means the judge is noise and its verdict "
                     "cannot support a promotion. No real invocation happens under the publish "
                     "path (cost/no-network), so this accrues over live judge runs."),
        },
        "independence": {
            "metric": "disagreement_rate = fraction of differently-primed judges on one artefact not holding the majority verdict",
            "accrues_live": True,
            "note": ("Systematic disagreement between independent judges on the same artefact "
                     "is a finding about the JUDGE. Accrues as real independent judges are run "
                     "on shared artefacts."),
        },
    }
