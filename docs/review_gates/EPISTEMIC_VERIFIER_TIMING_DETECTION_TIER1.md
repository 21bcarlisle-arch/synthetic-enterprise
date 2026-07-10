# REVIEW GATE (Tier 1 — safety-control modification): build real timing/data-flow detection into the epistemic verifier

**Status:** OPEN — awaiting director decision. Filed 2026-07-10, from a self-audit of the
W4_2_verifier_timing_extension maturity-map atom (its own claim turned out to be false — see
below). Research/correction only — no code touched in `tools/epistemic_verifier.py`.

## Why this is Tier 1

CLAUDE.md names "the epistemic verifier" explicitly as Tier 1 category (b): "any safety-control
modification (this tier itself, skip-permissions, the epistemic verifier, the staging flow)."
Any actual code change to `tools/epistemic_verifier.py`'s detection logic requires this gate,
regardless of how well-motivated the change is.

## The finding that opened this gate

Auditing the maturity-map atom that claimed this work was already done (level 2, `expert_hour:
passed`) found the claim was **false**. `tools/epistemic_verifier.py` is 202 lines, entirely:
literal import-statement regex matching (`FORBIDDEN_SOURCES = [r"^from sim\.", ...]`) against
`company/`/`saas/` files. There is no code anywhere in the tool — or anywhere else in the
repository (checked via grep for `timing.violation`/`data.flow.violation`/related terms) — that
detects a data-flow/timing violation (the shape of bug the hedge-volatility incident actually
was: a function receiving a full, untruncated dataset with no as-of bound).

Confirmed unambiguously by this atom's own cited evidence:
`docs/review_gates/done/HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md` states, in its own
contemporaneous incident write-up: *"`tools/epistemic_verifier.py` does not catch this class of
bug — it scans for `company/`↔`simulation.*` import violations, not data-flow/timing bugs where
the right kind of data crosses the wall at the wrong time."* That gap was never closed after the
incident; it was named and left open.

**What actually happened, and where the false claim came from:** CLAUDE.md's own Tier 1 *policy*
text was genuinely broadened the same day: *"anything touching the epistemic law (SIM/company
boundary, point-in-time blindfold — data-flow/timing violations count, not just literal
`simulation.*` imports into `company/`, per the 2026-07-10 hedge-volatility finding)."* That is a
real, true change — but it is a change to what counts as Tier 1 for *classification* purposes
(a human/agent judgment call about a proposed change), not a change to what the *tool* can
automatically detect. When this maturity-map atom was originally seeded, these two things were
conflated — the atom's name and level implied the tool gained real detection capability, when
only the policy definition did.

## Decision needed

Should real, automated data-flow/timing-violation detection be built into
`tools/epistemic_verifier.py`, and if so, what should it check for?

## Options

**A. Build a targeted detector for the exact shape of the hedge-volatility bug.** Scope: a
static-analysis rule (or a lightweight AST check) that flags a company/saas function receiving
a full historical dataset argument (e.g. a `list[dict]` of settlement/price records spanning
multiple years) without evidence the caller bounded it to an as-of date first. This is
necessarily heuristic (true data-flow analysis of arbitrary Python is a much larger undertaking)
and would likely need to be narrowly scoped to known risky call shapes rather than a general
data-flow analyzer, to avoid false positives that erode trust in the tool.

**B. Register as scoped future work, do not build now.** The one known instance of this bug
class is already fixed at its call site (`_price_history_as_of()` in
`simulation/run_phase2b.py`). No live violation exists today. Building a real, low-false-positive
static analyzer for this class of bug is a non-trivial engineering investment relative to the
current absence of a live incident.

**C. Correct the documentation only; do not build detection.** Accept that this class of bug is
currently caught only by human review (a director page comment triggered the original
investigation) and future incidents, not by an automated tool. Update CLAUDE.md/the maturity map
to stop implying otherwise, and rely on the existing detective controls (sanity daemon,
population-level checks) plus human review rather than building a new preventive one.

## Recommendation

Option B, leaning toward C if effort is a concern. There is no live violation today, and a
naively-scoped detector risks either missing real cases (if too narrow) or generating false
positives that erode trust in a tool whose entire value depends on being trusted (an epistemic
verifier that cries wolf gets ignored). This should be scoped carefully if pursued, likely
alongside the separate `POINT_IN_TIME_SNAPSHOT_TIER1.md` gate (a structural point-in-time
access layer would make many classes of this bug structurally impossible rather than needing to
be statically detected after the fact) — the two proposals are complementary, not competing, and
a director decision on one may inform sequencing of the other.

## What happens on approval

If Option A: this becomes a real BUILD action on `tools/epistemic_verifier.py` (the named safety
control), with its own test suite proving both true-positive detection (would have caught the
actual hedge-volatility bug, in isolation) and false-positive avoidance (does not flag the
codebase's many legitimate large-dataset call sites). If B or C: this gate closes with the
documentation correction (already made in `maturity_map.yaml`) standing as the resolution.
