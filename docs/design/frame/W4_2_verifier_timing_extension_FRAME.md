# FRAME — W4_2_verifier_timing_extension

**Atom:** `W4_2_verifier_timing_extension` — "Epistemic verifier extended to data-flow/timing
violations, not just literal imports"
**Lane:** W4_the_wall · **dial:** 3 · **level_current:** 1 · **level_target:** 3 ·
**file_scope:** `tools/epistemic_verifier.py`
**Stage:** DISCOVER/FRAME (Lane-3, doc-only). **No verifier code touched. No level move.**

> This is a framing artifact only. It does NOT authorize, design-to-build, or perform any change
> to `tools/epistemic_verifier.py`. The real-detection build is a Tier-1 safety-control
> modification and is director-gated (see §2). Reading `tools/epistemic_verifier.py` for this
> FRAME was read-only.

---

## 1. Current state (grounded in the actual code)

`tools/epistemic_verifier.py` (305 lines, read 2026-07-16) does exactly one thing: it detects
**literal SIM imports** in `company/` and `saas/` `.py` files. Mechanism:

- `FORBIDDEN_SOURCES` — line-anchored regexes (`^from sim\.`, `^import simulation\.`, …).
- `_module_is_forbidden()` + `_scan_source()` — an **AST** pass (primary) over `ast.Import` /
  `ast.ImportFrom` nodes, catching the whitespace/alias/bare-import forms the line regex fails
  open on (`from  simulation.x import y`, `import simulation`, one-line compound imports). The
  line-regex `_scan_lines()` is the SyntaxError fallback only.
- `APPROVED_SEAM` (`company/interfaces/sim_interface`) and `APPROVED_ORCHESTRATION` are exempted;
  `_check_unavailable()` correctly turns an unreadable-but-requested file into a non-empty
  finding (R15 FAIL-SILENT guard — an unavailable check is a failed check).

That is the whole detection surface: **"does this file's import graph reach into `sim`/`simulation`?"**
It is a good, mutation-hardened *import-boundary* checker.

**What it structurally cannot catch:** any epistemic-wall breach that does **not** cross an import
boundary. Two shapes:

1. **Data-flow leaks** — a value *derived from* future / as-of-blind data flows into a company
   decision, through legitimate, already-approved channels (function arguments, the seam,
   observables). No forbidden import exists anywhere; the import graph is clean.
2. **Timing (point-in-time-blindfold) violations** — the *right kind* of data crosses the wall at
   the *wrong time*: a value that would be legitimate as-of date D is used to decide something
   dated earlier than D.

**Canonical example the current tool cannot catch — the hedge-volatility lookback foresight bug**
(`docs/review_gates/done/HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md`): `run_phase2b.py` loaded the
full-window `elec_records` list once and passed it **unsliced** into `decide_hedge_fraction()` at
*every* renewal point; `estimate_price_volatility()` then took `prices[-90:]` — the last 90 days
of *the whole dataset* (immediately before the run's `effective_end` of 2025-06-07), not the 90
days before each decision's actual date. A 2018 renewal was effectively hedged using post-2021-22
crisis volatility. The incident write-up states this in its own words: *"`tools/epistemic_verifier.py`
does not catch this class of bug — it scans for `company/`↔`simulation.*` import violations, not
data-flow/timing bugs where the right kind of data crosses the wall at the wrong time."* No
forbidden import was ever present — the verifier was, and would still be, GREEN on this bug.

**Provenance correction (important for honesty):** this atom once claimed level 2 /
`expert_hour: passed` implying the tool already had timing detection. That claim was **false** and
was corrected down to level 1. What genuinely changed on 2026-07-10 was CLAUDE.md's Tier-1
*classification policy* (data-flow/timing now *count* as epistemic-law changes for judgment
purposes) — not the tool's automated detection. The two were conflated. This FRAME must not repeat
that conflation: **policy broadened; the tool did not gain detection.**

## 2. Why this is Tier-1 / a one-way door

CLAUDE.md names "the epistemic verifier" explicitly as a Tier-1 safety control. Extending its
detection surface changes what the machine's *safety posture asserts* — i.e. what a GREEN verifier
means. A verifier that silently gains (or wrongly claims) new detection changes every downstream
promotion/Expert-Hour/green-suite decision that rests on it. That is a safety-control modification:
one-way-door category 5 (security posture / safety-control changes), director-reserved, escalate
via NTFY, never build unilaterally.

**Gate status (must be stated accurately):** the review gate
`docs/review_gates/done/EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md` is **CLOSED** (director
decision 2026-07-10): **Option B/C confirmed — NO build into `tools/epistemic_verifier.py`;
register + doc-fix only.** The director's words: *"register + doc-fix, no build; the PreToolUse
hook (adoption sprint) is the near-term detector, the as-of snapshot object the permanent fix."*
So the detection burden was deliberately routed to **two separate mechanisms** rather than a
modified verifier: (1) near-term — the `.claude/hooks/block_point_in_time_read.py` PreToolUse hook
(a NEW hook, not a change to the verifier); (2) permanent — the point-in-time / as-of snapshot
interface object (`POINT_IN_TIME_SNAPSHOT_TIER1.md`). **Any move to now build real detection INTO
the verifier would require a fresh Tier-1 director decision reversing that B/C resolution** — it is
not authorized by the closed gate, and this FRAME does not authorize it.

## 3. What data-flow / timing detection would REQUIRE (design exploration only)

Three broad approaches, honestly appraised:

- **A — Taint / data-flow analysis.** Track values sourced from future-/as-of-blind data (the full
  historical record lists, forward curves, anything the seam yields without an as-of bound)
  through to their use in a company decision, and flag a decision that consumed an unbounded
  future value. *Feasibility:* true inter-procedural data-flow analysis of arbitrary Python is a
  large, brittle undertaking — dynamic typing, aliasing, container mutation, list slicing (`[-90:]`
  is exactly the operation that hid the bug) all defeat naive static tracking. *False-positive
  risk:* HIGH. The codebase has many *legitimate* large-dataset call sites; a naive taint rule
  flags them all. An epistemic verifier's entire value is being trusted — one that cries wolf gets
  ignored, which is worse than no tool (R15: a control that cannot fire cleanly on real defects is
  a liability).

- **B — Static approximation / targeted heuristic.** A narrowly-scoped AST rule for the *known
  risky shape*: a company/saas function receiving a full multi-year record list without evidence
  the caller bounded it to an as-of date. *Feasibility:* buildable, but necessarily heuristic —
  too narrow misses real cases, too broad false-positives. It detects *a shape*, not *the semantic
  violation*.

- **C — Structural prevention via an as-of / point-in-time snapshot contract (the cited permanent
  fix).** Rather than *detect* the bug after the fact, make it *unrepresentable*: the seam yields
  an as-of-bounded snapshot object; asking it for data implies an as-of date; there is no unbounded
  full-window list to accidentally `[-90:]`. This is the director-named permanent fix
  (`POINT_IN_TIME_SNAPSHOT_TIER1.md`) and is architecturally the strongest — it converts a
  detection problem into an impossibility. The PreToolUse hook (`block_point_in_time_read.py`) is
  the near-term detective complement. **Neither of these is a change to the verifier** — which is
  precisely why the gate closed B/C: the practical detection/prevention burden was moved OFF the
  named Tier-1 control and onto new, separately-owned mechanisms.

**Honest conclusion:** real data-flow/timing detection built *into the verifier* is high-cost,
high-false-positive, and — per the closed gate — not the chosen path. The chosen path (as-of
snapshot + PreToolUse hook) does the work structurally elsewhere. This atom's L1→L3 target, taken
literally as "the verifier gains detection," is in tension with the closed gate; unblocking it
requires the director to re-open the question (see §6).

## 4. R15 requirement (binding acceptance condition on any gated build)

R15: no control counts as evidence unless a **mutation test proves it fires on its own named
defect**. If real data-flow/timing detection is ever built (into the verifier or elsewhere as a
*claimed* wall control), it MUST be mutation-tested by **re-introducing the volatility-lookback
foresight bug** — restore the unsliced `elec_records` / `prices[-90:]` path — and confirming the
control turns RED. It must simultaneously demonstrate **false-positive avoidance**: GREEN on the
codebase's many legitimate large-dataset call sites. A detector that cannot be shown to fire on the
one real historical instance of its own bug class is worse than none (the exact failure this atom
already committed once: claiming a detection capability that did not exist). This is a hard
acceptance condition on any future build, not a nice-to-have.

## 5. COUPLED TRIAD framing

W4 (the wall) is the **HARNESS** leg of the triad: it measures whether the **company** saw
something it should not have — the belief-vs-truth gap where the belief is "the company only knew
what was knowable as-of the decision date" and the truth may be "a future-derived value leaked in."
The SIM leg supplies data with real temporal structure; the company leg discovers/decides through
the seam (and is *allowed to be wrong* — misreading the blindfold is a realistic supplier failure);
the wall/harness leg measures the gap. **The gap this atom would close:** today the harness measures
only the *import-boundary* gap (does company code reach into `sim`?) and reports GREEN on the entire
class of *temporal* gaps (future-derived value used at an earlier decision). The hedge-volatility
bug is the proof the gap is real and material — it was caught by a human page comment, not the
harness. Closing it means the harness can measure "did a decision consume data it could not have
had as-of its own date," which is the actual point-in-time-blindfold invariant. Per the coupled-triad
rule, no world/SIM temporal-structure capability should reach L3 until this measurement exists —
but building the measurement is Tier-1-gated, so the current honest state is: gap named, gap
measured only by the near-term hook + human review, not by the verifier.

## 6. Recommendation

**Keep `level_current` at 1. Do NOT move the level.** Real progress here is entirely
policy-and-understanding: the detection surface has not changed and the gate that would let it
change is closed B/C. Moving the level would repeat the exact false-completion this atom was
already corrected for.

The real, bankable progress this FRAME records: (a) the current tool's surface is accurately
characterized (import-boundary only, AST-hardened); (b) the canonical uncatchable defect is
documented with its incident trail; (c) the R15 mutation-test acceptance condition is fixed for any
future build; (d) the gate's B/C resolution is correctly stated so the atom's literal L3 target is
no longer read as authorization.

**What the director would need to decide to unblock L1→L3:** an explicit, in-console (or
gate-file-clearing) **re-opening of `EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md`** reversing its
B/C resolution — i.e. a decision to build *real automated data-flow/timing detection into a named
wall control*, choosing among approaches A/B/C of §3 (most likely C, the as-of snapshot structural
fix, which does the work without modifying the verifier and may retire this atom's "extend the
verifier" framing entirely). Absent that reversal, the correct disposition is: level stays 1, the
work stays doc-only, and the practical wall-timing burden stays with the PreToolUse hook + as-of
snapshot object + human review, exactly as the closed gate directs.
