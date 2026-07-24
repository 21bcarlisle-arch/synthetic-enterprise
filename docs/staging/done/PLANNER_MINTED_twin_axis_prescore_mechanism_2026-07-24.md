<!-- SUPERVISOR_DRAW: blocked -->
<!-- draw-visibility marker (2026-07-24): COMPLETE — scope 1-3 all discharged this tick; archiving to done/. No self-drawable step remains (a live pre-score fires only on a real director-verdict cadence event, which is external). -->

> **[DONE — 2026-07-24 worker tick] Scope 1 (FRAME) + 2 (reversible BUILD writer + R15 both-ways test) + 3 (retro gap-line read) all shipped.**
> **Gap that was verified & is now closed:** `director_axis_verdicts.jsonl` held 5 `director_verdict` rows and 0 `twin_prediction`; NO writer existed anywhere (MAKE_IT_STICK prose-only decay). The mechanism is now LIVE.
> **BUILD shipped this tick:**
> - `background/axis_prescore.py` — the pre-score writer: `record_twin_prescore(...)` appends `{axis, axis_number, source:"twin_prediction", predicted_verdict, rationale, ts, recorded_date}` to the ledger; `prescore_axis(...)` invokes the twin via `director_twin._default_invoke` (read-only, canon+origin only, no new authority); `prediction_gap()` / `retro_gap_line()` are the read-only retro diagnostic.
> - `tests/background/test_axis_prescore.py` — **R15 both-ways (12 tests, all green):** FIRES (a valid prediction is written and `prediction_gap` pairs it against a later verdict; the writer is load-bearing) / FAILS-CLOSED (a missing/blank verdict, missing rationale, empty reply, or blank required field all raise `MalformedPrediction`, and NOTHING is written — mutation-confirmed defence-in-depth: parse AND record both fail closed). Plus a §2-severance test asserting `supervisor.py` never imports the module.
> - `background/daily_self_note.py` — the read-only gap line wired into the morning note (renders the honest-absent line today: "NO twin_prediction rows yet — the mechanism is live but has not run before a verdict").
> - **Gates:** `tools/epistemic_verifier` PASS (525 files); `test_daily_self_note` + `test_director_twin` still green (34 passed/1 skipped).
> **Walls honoured (for the ledger):** Law B — the prediction is logged & read, NEVER trains the twin / updates canon. HARD LAW §2 — the module is a WRITER + a RETRO READ only; supervisor.py does not import it (tested). Verdicts stay the director's; only the twin's PREDICTION side is built.
> **No open sub-item.** The next event is external (a live pre-score before a real director-verdict cadence event) — not a build step. Archived to `done/`.

# [PLANNER-MINTED] Mechanise the DIRECTOR_AXES twin pre-score loop (currently prose-only) (2026-07-24)

**Type:** RUNG-7 planner mint (WORK_IS_THE_DEFAULT 2026-07-23, rung 7; rungs 1–6 empty this tick). **Propose-then-proceed.**

## What ratified goal this serves
- **Axis / source:** `docs/design/DIRECTOR_AXES.md` §"The verdict loop (how a judgment enters)" step 3, established by `DIRECTOR_STEER_SELF_MEASUREMENT_AND_AXES_2026-07-22.md` §4 (director-ratified).
- The doc states, as a standing requirement: *"Before each expected verdict, the twin pre-scores the same axes and logs its prediction to the same ledger (`source: "twin_prediction"`) with a one-line rationale drawn ONLY from its canon + origin facts. The director's verdict then scores the twin's prediction. The shrinking prediction gap = the system internalising his taste."*

## The gap (verified on disk this tick)
- `docs/observability/director_axis_verdicts.jsonl` exists and holds **5 rows, all `source: "director_verdict"`** — **zero `source: "twin_prediction"` rows**.
- `grep -rniE 'director_axis_verdicts' --include=*.py` → **no writer anywhere**; `background/director_twin.py` has **no axis / pre_score / prediction path**. The 5 verdict rows were hand-recorded per rulings.
- **Conclusion:** the twin pre-score is **prose-only, never mechanised** — the exact MAKE_IT_STICK (2026-07-12) decay mode: *"a rule lives in CLAUDE.md AND as enforced code, or not at all; prose-only is worse than no rule."* Without a mechanism the belief-vs-truth-on-the-director loop never runs and the prediction gap is never measurable.

## Real-world fidelity / goal gained
The coupled-triad's own belief-vs-truth law applied to the director himself: a logged twin prediction **before** each director verdict makes "the system internalising his taste" a **measured, shrinking number**, not an aspiration. It is the self-measurement axis the director explicitly asked for.

## Scope (propose-then-proceed)
1. **FRAME** (drawable now, doc-only): name the trigger for "an expected verdict" (director cadence / milestone), the exact write path (a small `background/axis_prescore.py` appending `{axis, axis_number, source:"twin_prediction", rationale, ts, recorded_date}` to the ledger), and the twin-invocation shape (read-only, canon+origin facts only — reuses `director_twin.py`'s existing read-only `_default_invoke`, no new authority).
2. **BUILD** (reversible): the pre-score writer + one R15 **both-ways** test (fires: a prediction is written before a verdict; fails-closed: a malformed/absent prediction is detected, not silently skipped). Wire the invocation to the same cadence signal the retro uses.
3. Emit the gap (director verdict − twin prediction) as a read-only diagnostic line in the morning retro.

## Walls this mint does NOT cross (stated for the ledger)
- **Law B (DIRECTOR_TWIN.md) is binding and honoured:** the prediction is logged and read; it **NEVER updates the twin's canon** and the gap **NEVER trains the twin**. Pure diagnostic.
- **HARD LAW §2 of the self-measurement steer:** the ledger is **never consumed by any allocation, draw, reward, or scheduling mechanism** — this build adds a *writer* and a *retro read*, never a wiring into the draw. A scorecard number severed from all wiring, by construction.
- The **verdicts themselves stay the director's** — this builds only the twin's *prediction* side; no self-awarded axis score.

## Propose-then-proceed window
Standard planner window. FRAME + the reversible writer/test proceed under reversible authority (git reverts). No one-way door, no L3 self-promotion, no curriculum value. If contended, PRODUCT-FIRST items win the draw (this is a self-measurement mechanism, not a product surface) — but it forbids rest while idle.
