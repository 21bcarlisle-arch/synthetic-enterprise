"""background/axis_prescore.py — mechanise the DIRECTOR_AXES twin pre-score loop.

WHY THIS EXISTS (MAKE_IT_STICK, 2026-07-12): `docs/design/DIRECTOR_AXES.md`
§"The verdict loop" step 3 is a STANDING requirement — "before each expected
verdict, the twin pre-scores the same axes and logs its prediction to the same
ledger (`source: "twin_prediction"`) with a one-line rationale drawn ONLY from
its canon + origin facts. The director's verdict then scores the twin's
prediction. The shrinking prediction gap = the system internalising his taste."
Until this module, that requirement was PROSE-ONLY — the ledger
(`director_axis_verdicts.jsonl`) held only `director_verdict` rows and no writer
for the prediction side existed anywhere. Prose-only is the exact decay mode
MAKE_IT_STICK names ("a rule lives in CLAUDE.md AND as enforced code, or not at
all"). This is the mechanism.

WALLS (stated for the ledger, honoured by construction):
  - Law B (DIRECTOR_TWIN.md): the twin's prediction is LOGGED and READ; it
    NEVER updates the twin's canon and the gap NEVER trains the twin. The
    prediction is drawn only from the read-only `_default_invoke` (canon+origin
    facts, no tool access). Pure diagnostic.
  - HARD LAW §2 (DIRECTOR_AXES.md, DIRECTOR_STEER_SELF_MEASUREMENT_AND_AXES):
    the axis ledger is NEVER consumed by any allocation, draw, reward, or
    scheduling mechanism. This module adds a WRITER and a RETRO READ only — it
    is never imported by supervisor.py / find_work, and no number it computes
    feeds priority. A scorecard number severed from all wiring, by construction.
  - The VERDICTS stay the director's. This builds only the twin's PREDICTION
    side — no self-awarded axis score.

FAIL-CLOSED (R15): a malformed or absent prediction is DETECTED and raised
(`MalformedPrediction`), never silently written as a blank row or skipped.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

# Reuse the twin's read-only organs — no new authority, no new I/O path.
from background.director_twin import (
    CANON_PATH,
    _append_jsonl,
    _default_invoke,
    _read_jsonl,
)

PROJECT_DIR = Path(__file__).resolve().parent.parent
AXIS_LEDGER_PATH = PROJECT_DIR / "docs" / "observability" / "director_axis_verdicts.jsonl"

TWIN_PREDICTION_SOURCE = "twin_prediction"
DIRECTOR_VERDICT_SOURCE = "director_verdict"

# v1 axes — mirror of docs/design/DIRECTOR_AXES.md §"v1 axes". Kept minimal (a
# label per number); the axis definitions live in the doc, not duplicated here.
V1_AXES: dict[int, str] = {
    1: "website",
    2: "segmentation",
    3: "believability",
}

# Believability verdicts use categorical labels; axis-1 site uses "x/5". Both
# are normalised to [0,1] so a director-verdict and a twin-prediction can be
# differenced regardless of which scale each used. Mapping is EXPLICIT so the
# gap number carries its own definition (R14 spirit: no basis-less number).
_VERDICT_ORDINAL: dict[str, float] = {
    "MET": 1.0,
    "PARTIAL": 0.5,
    "ABSENT": 0.0,
    "FAIL": 0.0,
}


class MalformedPrediction(ValueError):
    """A twin pre-score could not be parsed into a verdict + rationale, or a
    write was attempted with a missing/blank required field. Fail-closed: raised
    rather than writing a blank/partial row (R15)."""


def _utc_date(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


def record_twin_prescore(
    *,
    axis: str,
    axis_number: int,
    rationale: str,
    predicted_verdict: str,
    component: str | None = None,
    predicted_score: str | None = None,
    ts: float | None = None,
    recorded_date: str | None = None,
    ledger_path: Path | None = None,
) -> dict:
    """Append ONE `twin_prediction` row to the axis ledger. Fail-closed: raises
    `MalformedPrediction` on any missing/blank required field — never writes a
    partial row. Returns the written entry."""
    if not (isinstance(axis, str) and axis.strip()):
        raise MalformedPrediction("axis is required and must be non-blank")
    if not isinstance(axis_number, int) or isinstance(axis_number, bool):
        raise MalformedPrediction("axis_number is required and must be an int")
    if not (isinstance(rationale, str) and rationale.strip()):
        raise MalformedPrediction("rationale is required and must be non-blank")
    if not (isinstance(predicted_verdict, str) and predicted_verdict.strip()):
        raise MalformedPrediction("predicted_verdict is required and must be non-blank")

    ts = time.time() if ts is None else ts
    entry = {
        "axis": axis.strip(),
        "axis_number": axis_number,
        "source": TWIN_PREDICTION_SOURCE,
        "predicted_verdict": predicted_verdict.strip(),
        "rationale": rationale.strip(),
        "ts": ts,
        "recorded_date": recorded_date or _utc_date(ts),
    }
    if component is not None and str(component).strip():
        entry["component"] = str(component).strip()
    if predicted_score is not None and str(predicted_score).strip():
        entry["predicted_score"] = str(predicted_score).strip()

    _append_jsonl(ledger_path or AXIS_LEDGER_PATH, entry)
    return entry


def build_prescore_prompt(
    *, axis: str, axis_number: int, component: str | None, canon_text: str, origin_facts: str = ""
) -> str:
    """The read-only twin prompt. The twin predicts the DIRECTOR's verdict on
    one axis from canon + origin facts ONLY — no world/company internals, no
    self-scoring. Structured so a missing field is detectable (fail-closed)."""
    comp = f" (component: {component})" if component else ""
    facts = origin_facts.strip() or "(no additional origin facts supplied)"
    return (
        "You are the director's twin. Predict — do NOT decide — the score the "
        f"DIRECTOR would give on the axis below{comp}, using ONLY his canon and "
        "the origin facts provided. You are logging a prediction the director's "
        "later verdict will score; you never award the score yourself.\n\n"
        f"AXIS {axis_number}: {axis}\n\n"
        "=== DIRECTOR CANON (his taste; the only lens you may use) ===\n"
        f"{canon_text}\n\n"
        "=== ORIGIN FACTS (observed state of the thing being judged) ===\n"
        f"{facts}\n\n"
        "Answer in EXACTLY this shape, both lines mandatory:\n"
        "PREDICTED_VERDICT: <one of MET|PARTIAL|ABSENT|FAIL, or a score like 3/5>\n"
        "RATIONALE: <one line, drawn only from canon + origin facts>\n"
    )


def parse_prescore_response(text: str) -> tuple[str, str]:
    """Extract (predicted_verdict, rationale) from the twin's reply. Fail-closed
    (R15): raises `MalformedPrediction` if either line is missing or blank —
    never returns a silent empty prediction."""
    verdict: str | None = None
    rationale: str | None = None
    for line in (text or "").splitlines():
        stripped = line.strip()
        upper = stripped.upper()
        if upper.startswith("PREDICTED_VERDICT:"):
            verdict = stripped.split(":", 1)[1].strip()
        elif upper.startswith("RATIONALE:"):
            rationale = stripped.split(":", 1)[1].strip()
    if not verdict:
        raise MalformedPrediction("no non-blank PREDICTED_VERDICT line in twin response")
    if not rationale:
        raise MalformedPrediction("no non-blank RATIONALE line in twin response")
    return verdict, rationale


def prescore_axis(
    *,
    axis: str,
    axis_number: int,
    component: str | None = None,
    origin_facts: str = "",
    invoke_fn=None,
    canon_path: Path | None = None,
    ledger_path: Path | None = None,
    ts: float | None = None,
) -> dict:
    """Invoke the read-only twin, parse its prediction, and record it. Reuses
    `director_twin._default_invoke` (no tool access, scratch cwd, secrets
    scrubbed) unless `invoke_fn` is injected (tests). Fail-closed end-to-end: a
    malformed twin reply raises before any write."""
    invoke = invoke_fn or _default_invoke
    canon_text = (canon_path or CANON_PATH).read_text(encoding="utf-8")
    prompt = build_prescore_prompt(
        axis=axis, axis_number=axis_number, component=component,
        canon_text=canon_text, origin_facts=origin_facts,
    )
    reply = invoke(prompt)
    predicted_verdict, rationale = parse_prescore_response(reply)
    is_score = "/" in predicted_verdict
    return record_twin_prescore(
        axis=axis,
        axis_number=axis_number,
        component=component,
        rationale=rationale,
        predicted_verdict=predicted_verdict,
        predicted_score=predicted_verdict if is_score else None,
        ts=ts,
        ledger_path=ledger_path,
    )


def _to_ordinal(row: dict) -> float | None:
    """Normalise a verdict/prediction row to [0,1], or None if unmappable. A
    'x/5' score (either side) takes precedence over a categorical label."""
    for key in ("score", "predicted_score", "predicted_verdict", "verdict"):
        raw = row.get(key)
        if not raw:
            continue
        text = str(raw).strip()
        if "/" in text:
            num, _, den = text.partition("/")
            try:
                n, d = float(num), float(den)
                if d:
                    return max(0.0, min(1.0, n / d))
            except ValueError:
                continue
        label = _VERDICT_ORDINAL.get(text.upper())
        if label is not None:
            return label
    return None


def _latest_by_key(rows: list[dict], source: str) -> dict[tuple[str, str], dict]:
    """Latest row (by ts) per (axis, component) for a given source."""
    out: dict[tuple[str, str], dict] = {}
    for r in rows:
        if r.get("source") != source:
            continue
        key = (str(r.get("axis", "")), str(r.get("component", "")))
        prev = out.get(key)
        if prev is None or r.get("ts", 0) >= prev.get("ts", 0):
            out[key] = r
    return out


def prediction_gap(ledger_path: Path | None = None) -> list[dict]:
    """READ-ONLY retro diagnostic. Pairs the latest twin_prediction and
    director_verdict per (axis, component) and returns the gap. Never consumed by
    any draw/reward (HARD LAW §2) — this is a read for the morning note only."""
    rows = _read_jsonl(ledger_path or AXIS_LEDGER_PATH)
    predictions = _latest_by_key(rows, TWIN_PREDICTION_SOURCE)
    verdicts = _latest_by_key(rows, DIRECTOR_VERDICT_SOURCE)
    out: list[dict] = []
    for key, pred in sorted(predictions.items()):
        verdict = verdicts.get(key)
        if verdict is None:
            continue  # prediction logged, director has not yet scored it
        p_ord = _to_ordinal(pred)
        v_ord = _to_ordinal(verdict)
        gap = abs(v_ord - p_ord) if (p_ord is not None and v_ord is not None) else None
        out.append({
            "axis": key[0],
            "component": key[1] or None,
            "twin_prediction": pred.get("predicted_verdict"),
            "director_verdict": verdict.get("verdict") or verdict.get("score"),
            "gap": None if gap is None else round(gap, 3),
        })
    return out


def retro_gap_line(ledger_path: Path | None = None) -> str:
    """One-line prediction-gap summary for the morning self-note. Fail-closed:
    a read error returns an honest 'not measurable' string, never a fabricated
    number. Emits an explicit line when NO prediction has yet been scored (the
    honest state the day this lands)."""
    try:
        gaps = prediction_gap(ledger_path)
    except Exception as e:  # noqa: BLE001 — fail-closed, honest RED line
        return f"prediction-gap NOT MEASURABLE (read error: {e})"
    if not gaps:
        rows = _read_jsonl(ledger_path or AXIS_LEDGER_PATH)
        n_pred = sum(1 for r in rows if r.get("source") == TWIN_PREDICTION_SOURCE)
        if n_pred == 0:
            return ("twin prediction-gap: NO twin_prediction rows yet — the pre-score "
                    "mechanism is live but has not run before a verdict (honest absent).")
        return ("twin prediction-gap: predictions logged but none yet scored by a "
                "director verdict on the same axis/component.")
    scored = [g for g in gaps if g["gap"] is not None]
    if scored:
        avg = round(sum(g["gap"] for g in scored) / len(scored), 3)
        return (f"twin prediction-gap (director − twin, 0=agree..1=opposite): "
                f"mean {avg} over {len(scored)} scored pair(s); "
                + "; ".join(f"{g['axis']}/{g['component']}: {g['gap']}" for g in scored))
    return f"twin prediction-gap: {len(gaps)} paired but none ordinal-mappable."
