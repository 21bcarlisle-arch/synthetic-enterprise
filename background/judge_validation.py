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

# Below this many PASS verdicts we do NOT claim a judge has a MEASURED error
# rate -- a 0.0 computed over one verdict is not "this judge is perfect", it is
# "this judge is unmeasured", and reporting it as 0.0 with no flag is the R15
# FAIL-OPEN pattern (a control that passes on an empty/thin record). Mirrors
# trust_ledger.autonomy_level's own >=3 floor, for the same reason.
MIN_PASSES_FOR_MEASURED_RATE = 3


# ── THE CLOSE-PATH CALLER (H14_close_path_caller, 2026-07-14) ─────────────────
# The honest residual H14 exists to fix: `outcome_error_rates` and
# `measurement_coverage` were CORRECT but starved -- nothing in the real close
# path ever fed the trust ledger, so a judge's post-close error rate could never
# accrue and every organ read `escapes_measurement=True` forever. The organs that
# actually PRODUCE verdicts on this project are the phase-close-evaluator AGENT
# and the cold-eyes-walk SKILL -- markdown surfaces. A markdown surface can only
# INSTRUCT a call, it cannot GUARANTEE one; so the enforce-able part of the fix is
# this single, tested Python entry point (+ its `record-close` CLI) that both the
# phase-close skill and the evaluator agent are told to run as their last step.
# The evaluator agent has Bash, so "run this one command" is a concrete mechanism,
# not a hope -- but be honest: an agent can still skip a prose instruction, so the
# guarantee is exactly as strong as the agent following its own SKILL/agent brief,
# no stronger. What this DOES remove is the "there is no caller at all" gap: after
# this, the moment any evaluator's verdict is recorded through here, the outcome
# loop closes and coverage begins to move off 0.0.
def record_close_verdict(
    task_class,
    verdict,
    evaluator_name: str,
    subject: str,
    *,
    evaluated_at: Optional[str] = None,
    notes: str = "",
) -> dict:
    """Record ONE close-path verdict AND close the outcome-correlation loop.

    Call this at phase close with the JUDGING ORGAN (`evaluator_name`, e.g.
    "phase-close-evaluator" / "cold-eyes-walk") and the ATOM under judgement
    (`subject`, e.g. the atom id or the reviewed commit SHA). Two effects:

      1. The verdict is appended to the trust ledger (`trust_ledger.record_verdict`,
         which still enforces the INDEPENDENT_EVALUATORS whitelist -- a
         self-reported grader name raises).

      2. THE WIRING H14 WAS MISSING: if this verdict is NEEDS_WORK and a PRIOR
         PASS exists for the SAME subject, that earlier PASS let a defect through
         -- so the post-close defect is attributed back to it via
         `trust_ledger.record_post_close_defect`. A NEEDS_WORK on a
         previously-PASSed atom is precisely "a defect found after it was closed",
         and charging it to the PASS that missed it is what moves that judge's
         measured error rate off 0.0. If no prior PASS exists (a first-ever
         NEEDS_WORK on never-passed work), nothing is charged -- that judge caught
         the problem, it is not its error.

    Returns {"verdict_entry": <dict>, "post_close_defect": <dict or None>,
             "charged_regression": <bool>}. `charged_regression` is True iff a
    prior PASS was found and debited -- the observable signal that the outcome
    loop actually closed on this call.
    """
    # Accept enums or their string values (the CLI passes strings).
    tc = task_class if isinstance(task_class, tl.TaskClass) else tl.TaskClass(str(task_class))
    vd = verdict if isinstance(verdict, tl.Verdict) else tl.Verdict(str(verdict))

    entry = tl.record_verdict(
        task_class=tc,
        verdict=vd,
        evaluator_name=evaluator_name,
        subject=subject,
        evaluated_at=evaluated_at,
        notes=notes,
    )
    verdict_entry = {**{k: getattr(entry, k) for k in (
        "evaluator_name", "subject", "evaluated_at", "rework_required", "notes")},
        "task_class": entry.task_class.value, "verdict": entry.verdict.value}

    post_close_defect = None
    charged = False
    if vd == tl.Verdict.NEEDS_WORK:
        # A re-review that fails a previously-PASSed subject IS a post-close
        # defect against the judge that passed it. record_post_close_defect
        # raises KeyError when there is no prior PASS -- which is the legitimate
        # "first-ever NEEDS_WORK, nothing to charge" case, not an error.
        try:
            post_close_defect = tl.record_post_close_defect(
                subject, 1, discovered_at=evaluated_at,
                notes=f"NEEDS_WORK from {evaluator_name} on previously-passed {subject}")
            charged = True
        except KeyError:
            post_close_defect = None
            charged = False

    return {
        "verdict_entry": verdict_entry,
        "post_close_defect": post_close_defect,
        "charged_regression": charged,
    }


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
    Each bucket carries:
      - `error_rate`: (passes_with_later_defect / passes), or None on zero passes.
      - `escapes_measurement`: True when `passes` < MIN_PASSES_FOR_MEASURED_RATE
        -- the sample is too thin to have MEASURED this judge at all. This is the
        load-bearing honesty of H14: a verdict-organ showing error_rate 0.0 over
        one PASS is NOT a measured-perfect judge, it is an UNMEASURED one, and
        R15 forbids a control that reads as passing when it is really unmeasured
        (FAIL-OPEN). `error_rate` is still computed (a provisional signal) but a
        consumer must gate any promotion claim on `escapes_measurement is False`.
    """
    if entries is None:
        entries = tl._load_ledger()

    def _blank():
        return {"passes": 0, "passes_with_later_defect": 0,
                "total_post_close_defects": 0, "error_rate": None,
                "escapes_measurement": True}

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
        bucket["escapes_measurement"] = bucket["passes"] < MIN_PASSES_FOR_MEASURED_RATE
        return bucket

    return {
        "per_judge_class": {f"{j}|{k}": _finalise(v) for (j, k), v in per_jc.items()},
        "per_judge": {j: _finalise(v) for j, v in per_j.items()},
        "overall": _finalise(overall),
    }


def measurement_coverage(entries: Optional[list[dict]] = None) -> dict:
    """The forbidden-state rollup H14 exists to surface: which verdict-organs
    have a MEASURED error rate, and which currently ESCAPE measurement.

    "A verdict-organ with no measured error rate escapes measurement (forbidden)"
    -- so we do not merely compute the rate, we compute and PUBLISH how many
    organs are still unmeasured. Coverage = measured_judges / total_judges over
    the judges that have recorded at least one PASS. A coverage below 1.0 is not
    an error to hide; it is the honest statement of how much of the verdict
    surface is still un-outcome-tested, and the number that must fall over live
    runs as `record_post_close_defect` accrues.
    """
    rates = outcome_error_rates(entries)
    per_j = rates["per_judge"]
    measured = sorted(j for j, b in per_j.items() if not b["escapes_measurement"])
    unmeasured = sorted(j for j, b in per_j.items() if b["escapes_measurement"])
    total = len(per_j)
    return {
        "min_passes_for_measured_rate": MIN_PASSES_FOR_MEASURED_RATE,
        "judges_with_a_pass_record": total,
        "measured_judges": measured,
        "unmeasured_judges": unmeasured,
        "coverage": round(len(measured) / total, 4) if total else None,
        "all_measured": (total > 0 and not unmeasured),
        "note": ("Coverage is the fraction of verdict-organs with a MEASURED "
                 "outcome-error rate (>= min_passes PASS verdicts). Unmeasured "
                 "organs escape measurement (R15-forbidden as promotion evidence) "
                 "until the post-close linkage accrues over live runs; a 0.0 "
                 "computed error over a thin record is NOT a clean bill of health."),
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
        "measurement_coverage": measurement_coverage(entries),
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


# ── CLI: the concrete command the close path runs ────────────────────────────
# The phase-close skill and the phase-close-evaluator agent are INSTRUCTED to run
# this at close (the agent has Bash). It is the single, tested command that feeds
# the trust ledger, so the instruction is "run one line", not "write code".
def _main(argv: Optional[list[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="python3 -m background.judge_validation",
        description="Record a phase-close verdict so the judge outcome-correlation loop closes.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    rc = sub.add_parser("record-close",
                        help="Record one judging-organ verdict on an atom (feeds the trust ledger).")
    rc.add_argument("--task-class", required=True,
                    help=f"one of: {', '.join(c.value for c in tl.TaskClass)}")
    rc.add_argument("--verdict", required=True,
                    help=f"one of: {', '.join(v.value for v in tl.Verdict)}")
    rc.add_argument("--evaluator", required=True,
                    help=f"the judging organ; one of: {', '.join(sorted(tl.INDEPENDENT_EVALUATORS))}")
    rc.add_argument("--subject", required=True,
                    help="the atom id or reviewed commit SHA under judgement")
    rc.add_argument("--evaluated-at", default=None, help="ISO date (default: today, real)")
    rc.add_argument("--notes", default="", help="free-text note")

    sub.add_parser("coverage", help="Print current measurement coverage over the trust ledger.")

    args = parser.parse_args(argv)

    if args.cmd == "record-close":
        result = record_close_verdict(
            args.task_class, args.verdict, args.evaluator, args.subject,
            evaluated_at=args.evaluated_at, notes=args.notes)
        print(json.dumps(result, indent=2, default=str))
        if result["charged_regression"]:
            print(f"\n[outcome loop closed] a prior PASS on {args.subject!r} was debited a "
                  "post-close defect -- that judge's measured error rate has moved.")
        return 0

    if args.cmd == "coverage":
        print(json.dumps(measurement_coverage(), indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(_main())
