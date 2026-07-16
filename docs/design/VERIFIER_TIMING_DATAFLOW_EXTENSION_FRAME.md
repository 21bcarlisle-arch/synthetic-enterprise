# DESIGN — Data-flow / Timing Detection Extension for `tools/epistemic_verifier.py`

**Atom:** `W4_2_verifier_timing_extension` · **lane:** W4_the_wall · **dial:** 3 ·
**level_current:** 1 · **level_target:** 3 · **file_scope:** `tools/epistemic_verifier.py`
**Stage:** DISCOVER/FRAME (Lane-3, doc-only). No verifier code touched. No level move — HOLD at 1.

> **This document does NOT authorize a build.** It is a concrete, contingent detection design —
> ready to hand off IF and only if the director reopens the closed Tier-1 gate
> `docs/review_gates/done/EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md` (2026-07-10 resolution:
> *"Option B/C confirmed — register + doc-fix, no build"*). Extending `tools/epistemic_verifier.py`'s
> detection surface is a Tier-1 safety-control modification (CLAUDE.md names "the epistemic
> verifier" explicitly); it is never authorized by a FRAME-stage design doc, a build delegation, or
> this atom's own `level_target: 3`. This doc **companions**, does not replace or contradict,
> `docs/design/frame/W4_2_verifier_timing_extension_FRAME.md` (the existing FRAME, which already
> reached the correct conclusion: level stays 1, gate closed B/C, no build authorized). That FRAME
> did the policy/provenance work; this doc does the mechanism-level work its §3 sketched only at a
> paragraph's depth, so the design is not reinvented from zero on the day the gate might reopen.

---

## 1. Recap: what the current verifier catches, and its exact blind spots

Read directly from `tools/epistemic_verifier.py` (383 lines):

- **Detection surface is import-direction only.** `FORBIDDEN_SOURCES` (lines 56-63) is a
  line-anchored regex list (`^from sim\.`, `^import simulation\.`, …). The primary scan is AST-based
  (`_scan_source`, lines 214-246): it walks `ast.Import` / `ast.ImportFrom` nodes and, since the
  KL-2b extension, `ast.Call` nodes matching `importlib.import_module(...)` / `__import__(...)`
  with a **literal string-constant** first argument (`_dynamic_import_target`, lines 161-180).
  `_module_is_forbidden` (lines 113-130) matches root package `sim`/`simulation`, exempting
  `APPROVED_SEAM` (`company/interfaces/sim_interface`, line 46) and `APPROVED_ORCHESTRATION`
  (lines 50-53). The line-regex `_scan_lines` (lines 249-268) is the SyntaxError fallback only.
  `_check_unavailable` (lines 192-211) correctly turns an unreadable-but-requested file into a
  non-empty finding — an existing R15 FAIL-SILENT guard worth reusing, not reinventing.
- **The question it answers:** "does this file's import graph reach a forbidden module name?"
  That is the whole surface. The module's own docstring (lines 17-31) states outright that
  data-flow/timing detection is explicitly OUT of scope, citing the closed
  `EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md` gate by name.
- **What it structurally cannot catch — proven by the real incident it did not catch:**
  `docs/review_gates/done/HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md`. `simulation/run_phase2b.py`
  loaded the full 2016-2025 `elec_records` list once (~line 682-693) and passed it **unsliced**
  into `decide_hedge_fraction()` at every renewal (~line 1526-1528); `estimate_price_volatility()`
  (`company/trading/hedge_decision.py` ~line 59-60) took `prices[-90:]` — the last 90 days of
  *whichever list it was handed*, not the 90 days before the decision's own date. A 2018 renewal
  was silently hedged using 2021-22 crisis volatility. **No forbidden import ever appeared.** The
  import graph was, and remains, clean — the verifier was and would still be GREEN on this exact
  bug. This is the canonical proof that "import-boundary clean" and "epistemically honest" are two
  different properties, and the verifier only tests the first.

Two structurally distinct un-caught classes follow directly from this:

1. **Data-flow leaks** — a sim-internal-derived value reaches a company decision without a literal
   forbidden import: via a return value, a shared container, a variable threaded through an
   intermediary function, or (per the incident) via a legitimately-approved channel (a plain
   function argument) that simply carries more than it should.
2. **Timing (point-in-time-blindfold) violations** — the *right kind* of data crosses the wall at
   the *wrong time*: a value legitimately available as-of date D is used to decide something dated
   before D. This is a temporal property, not an import-graph property; no import-scanner design can
   see it directly.

## 2. Data-flow detection design

### 2.1 Vocabulary, reusing an existing sibling pattern

`tools/internal_seam_verifier.py` already solves a structurally similar problem for the
company's *internal* domain seams: it classifies a file's domain (`classify_path`), resolves each
import's target domain, and flags a cross-domain import that isn't the approved seam or a
documented baseline entry (lines 88-121). That is **import-direction taint with a one-hop
source→sink check**, not general data-flow — and it is the right level of ambition to copy, not
exceed. The data-flow detector below is deliberately the same shape, generalised from "which
domain does this module belong to" (import-time) to "does this VALUE originate from an unbounded
source" (assignment/call-time), using `ast.NodeVisitor` over a single function body plus one level
of call-argument forwarding — not a general inter-procedural taint engine.

### 2.2 Sources (taint origins)

A **denylist of known-unbounded accessor calls**, grounded in what this codebase actually has,
not a hypothetical general rule:

- `BitemporalEventLog.all_records()` (`company/interfaces/bitemporal_event_log.py` lines 163-170) —
  named loudly in its own docstring as "company decision code must never call this."
- Direct SIM data-pull functions used as a data-access convenience per
  `LiveSimInterface._load_price_records` (`company/interfaces/sim_interface.py` lines 252-266):
  `sim.system_prices_history.get_system_prices_range`, `sim.gas_prices_history.load_nbp_history`,
  `sim.cache_store.get_cached_prices` — legitimate to call (the underlying data is public market
  data), but their return value is an **unbounded full-window list**, exactly the shape that hid
  the incident.
- Any company/saas-local variable literally named `elec_records`, `gas_records`, `all_records`, or
  matching `*_records` where the assigning call is one of the above (a narrow, named-pattern match,
  same tradeoff `block_point_in_time_read.py` already accepts for its own denylist).

### 2.3 Sinks

Call sites inside `company/` or `saas/` whose callee name matches a **decision-function naming
convention** already used throughout this codebase: `decide_*`, `estimate_*` (e.g.
`decide_hedge_fraction`, `estimate_price_volatility` — the two actual call sites in the real
incident), plus any call explicitly listed in a small, hand-maintained `KNOWN_DECISION_SINKS`
table (starting with exactly those two, extended on each future incident — same "grow the denylist
from real incidents" discipline the existing verifier already uses for `FORBIDDEN_SOURCES`).

### 2.4 Propagation (the taint step itself)

Within one function body: an `ast.NodeVisitor` builds a small def-use map — `ast.Assign` /
`ast.AnnAssign` targets inherit the taint of their value expression; a tainted name passed as a
positional/keyword argument to a sink call is a finding; a tainted name **returned** propagates
taint to the caller's assigned variable, followed exactly one call-frame (matching the real
incident's shape: `elec_records` assigned once, passed as an argument two call-frames later). Depth
is capped at **one hop** deliberately (Simplicity Guard): this catches the real incident's actual
shape without building a general call graph.

**A tainted value is "cleared" (bounding evidence)** if, between source and sink, it passes through
a call whose name matches `history_as_known_at`, `as_known_at`, `get_price_history_as_of`,
`get_history_as_known`, `_price_history_as_of`, or contains `bisect`/`as_of` in the callee name —
i.e. it visibly went through `PointInTimeView` / `BitemporalEventLog`'s own bounded methods
(`company/interfaces/point_in_time_view.py` lines 143-203) or the legacy bisect-slice fix. This
mirrors `block_point_in_time_read.py`'s existing `_BOUNDING_EVIDENCE` regex (`as_of|bisect`),
generalised from "same diff" to "same taint chain."

### 2.5 Honest limits of the static approach

- **Aliasing**: `x = elec_records; y = x` two-deep aliasing beyond a shallow scan is not tracked;
  neither is taint through a `dict`/`list` container assembled from a tainted source (`{"prices":
  elec_records}` then unpacked later).
- **Dynamic dispatch**: a sink reached via `getattr(obj, name)(...)` or a callback stored in a
  variable defeats a name-match sink rule, exactly as `_dynamic_import_target` already documents for
  non-literal dynamic-import targets (lines 161-180) — same class of heuristic ceiling, honestly
  inherited here.
- **Cross-module, multi-hop chains** (beyond one call frame) are out of scope by design (§2.4);
  extending depth trades false-negatives for false-positives and engineering cost roughly
  linearly, with no clear stopping point — this is why the frame's §3 correctly rates a *general*
  taint engine (Option A) as high-cost/high-false-positive.
- **Complement, not substitute**: the structural fix already chosen and partially built —
  `PointInTimeView` (`company/interfaces/point_in_time_view.py`) — makes the unbounded list
  unrepresentable at the object level rather than merely detected after the fact. A static
  data-flow detector is a *defence-in-depth detective control* for code that has not yet migrated
  onto `PointInTimeView`, not a replacement for finishing that migration.

## 3. Timing detection design

### 3.1 Lean on typed time, not inferred time

The bitemporal log already carries exactly the two typed axes a timing check needs —
`valid_time` (what the fact is about) and `transaction_time` (when it became knowable) —
per `BitemporalRecord` (`company/interfaces/bitemporal_event_log.py` lines 38-53). `as_known_at()`
(lines 107-133) already enforces `transaction_time <= decision_time` structurally: **any code that
goes through this object cannot commit a timing violation by construction.** The corresponding
"nothing knowable yet" answer is `None` (an honest absence, not a fabricated zero) — the sibling
pattern `recorded_sim_interface.py`'s `ReplayStatus.NOT_KNOWABLE_YET` names the same idea
explicitly for the replay/trace path (`NOT_KNOWABLE_YET` fail-closed on `datetime.min`, lines
60-65, 205, 225, 308, 319).

**Consequence for the detector's design:** a static timing check should not attempt to reconstruct
"is `observed_at` after `as_of`" from raw code (undecidable in general — dates are runtime data).
It should instead check a **structural property**: *does this call site read historical/temporal
data through an object that enforces the axis relationship (`PointInTimeView`/`BitemporalEventLog`),
or does it bypass that object via a raw list/slice operation on a variable sourced from an
unbounded accessor (§2.2)?* This reframes "timing detection" as "data-flow detection with a
temporal-bypass-specific sink/pattern set" — the same AST machinery as §2, a different pattern
table, not a second analysis engine (Simplicity Guard).

### 3.2 Concrete pattern table

Flag, in `company/`/`saas/` code:

1. A call to `BitemporalEventLog.all_records()` — outside `tools/`/`tests/` (the class's own
   docstring already names this the forbidden call, lines 163-170; today nothing enforces it).
2. A `Subscript` slice (`x[-N:]`, `x[:N]`) applied to a name whose taint traces (per §2.4) to an
   unbounded source (`elec_records`/`get_system_prices_range(...)`/etc.) **without** an intervening
   bounding call — this is the literal `prices[-VOL_LOOKBACK_DAYS:]` shape from the real incident
   (`company/trading/hedge_decision.py` ~line 59-60), generalised.
3. A `PointInTimeView(...)` construction whose `decision_time` argument is not a variable/parameter
   visibly named `decision_time`/`as_of`/`term_start`/`renewal_date` (a much weaker, purely
   name-based sanity check — flags e.g. `PointInTimeView(dt.datetime.now())` inside a historical
   replay, a real-but-different timing bug shape) but does **not** attempt to verify the value is
   actually correct at runtime (undecidable statically, per §3.1).

### 3.3 What this does NOT attempt

It does not simulate execution to compute concrete `observed_at`/`as_of` values and compare them —
that is what `as_known_at()`'s runtime filter already does, correctly, for any code that uses it.
The static detector's entire job is to catch code that **doesn't use it** — structurally the same
job §2's data-flow detector does, aimed at the specific bypass shapes named above.

## 4. R15 — mutation tests (binding acceptance condition, not optional)

Per R15 (doctrine: TAUTOLOGY / FAIL-OPEN / FAIL-SILENT), each detector below must ship with its own
`tests/tools/test_epistemic_verifier_dataflow.py` (mirroring the existing style of
`tests/tools/test_internal_seam_verifier.py`, which already plants a fresh cross-domain import and
asserts the sibling verifier flags it).

**Data-flow detector:**
- `test_dataflow_fires_on_planted_leak` — a fixture file with `records = get_system_prices_range(...)`
  flowing unbounded into `decide_hedge_fraction(records)` (the real incident's shape, reconstructed
  as a minimal fixture) → detector MUST flag it. This is the CONFIRMED-fires proof R15 requires.
- `test_dataflow_clean_on_bounded_call` — the same shape but routed through
  `view.get_price_history_as_of()` first → detector MUST NOT flag it (false-positive avoidance;
  an epistemic verifier that cries wolf gets ignored, per the existing FRAME's §3 caution).
- `test_dataflow_clean_on_current_codebase` — run against the real, current `company/`/`saas/` tree
  and assert **zero** new findings beyond the one real historical instance (already fixed at its call
  site) — proves the detector doesn't drown real signal in false positives on day one.
- `test_dataflow_unavailable_on_unparseable_file` — a deliberately-malformed `.py` fixture must
  produce a `check_unavailable`-style finding (reusing the existing pattern, lines 192-211), never a
  silent clean PASS — the FAIL-OPEN killer pattern.
- `test_dataflow_fails_closed_if_detector_module_broken` — simulate the detector module itself
  raising on import/call (e.g. monkeypatch it to throw) and assert the phase-close gate treats that
  as a FAILED check (non-zero exit), never a silently-skipped PASS — the FAIL-SILENT killer pattern.
  Note the existing `main()`'s `except Exception: pass` (line 375) wraps only the *observability
  status update*, not the scan itself — any new detector must preserve that distinction, never widen
  the swallow to cover `scan()`'s own result.

**Timing detector:**
- `test_timing_fires_on_replanted_hedge_volatility_bug` — reconstruct the exact historical shape
  (unsliced `elec_records`, `prices[-90:]`) as a fixture and assert RED. This is the single most
  important test in this whole design: it is the literal defect this atom exists because of.
- `test_timing_clean_on_current_fixed_code` — scan the current, already-fixed call sites in
  `simulation/run_phase2b.py` / `company/trading/hedge_decision.py` and confirm no finding (the bug
  is fixed there; the detector must not regress that into a false positive).
- `test_timing_clean_on_point_in_time_view_usage` — a fixture using `PointInTimeView` end-to-end
  must scan clean (proves the detector doesn't penalise the actual correct pattern).
- `test_timing_unavailable_on_unparseable_file` / `test_timing_fails_closed_if_detector_broken` —
  same two FAIL-OPEN/FAIL-SILENT pairs as the data-flow detector, plus: `main()`'s existing
  `--diff` "no company files changed → scan everything" fallback (lines 341-349) must be preserved
  and extended to the new detector, not bypassed — an empty diff must never read as "nothing to
  check."

A detector that cannot pass ALL of the above is not evidence of anything (R15's own words: "a
control that cannot fail is worse than none").

## 5. R10 — registered simplification (what this extension will NOT catch)

Per R10, closing this class must not be claimed as total coverage. Named, honest gaps that remain
open even after both detectors above ship:

1. **Multi-hop / cross-module data-flow** beyond one call frame (§2.4) — a value stored on an
   object attribute and read much later, threaded through a dict/JSON round-trip, or passed through
   3+ function calls. Only a general inter-procedural taint engine catches this, which §2.5 argues
   against building (cost/false-positive tradeoff).
2. **Dynamic dispatch / reflective sinks** (`getattr`, stored callables, `exec`) — same ceiling the
   existing dynamic-import heuristic already documents and accepts (lines 161-180).
3. **Runtime-only, data-dependent timing correctness** — code that is correct for some concrete
   dates and wrong for others depending on values only known at runtime. No static check can decide
   this in general (§3.1); only the structural `PointInTimeView` object (Option C, the director-named
   permanent fix) closes it by construction, by making the unbounded read unrepresentable rather
   than detecting it after the fact.
4. **Non-Python surfaces** — JSON configs, generated artefacts, notebooks — outside the AST
   scanner's file scope entirely.

These stay the territory of: `PointInTimeView` migration completion (the real fix), the
`.claude/hooks/block_point_in_time_read.py` PreToolUse hook (near-term detective complement), and
human/Expert-Hour review — exactly where the closed gate already placed them. Nothing in this
design claims to retire those mechanisms.

## 6. L1 → L2 → L3 BUILD decomposition (contingent on Tier-1 gate reopening)

Stays within `file_scope: ["tools/epistemic_verifier.py"]` plus its test file, matching the atom's
declared scope. **Neither step may begin without an explicit, in-console (or gate-file-clearing)
director decision reopening `EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md` and reversing its closed
B/C resolution** — this decomposition is written so that decision, if and when made, has a ready
plan, not so it can be started unilaterally.

- **L1 (current, held here):** import-boundary detection only (existing, unchanged); this FRAME +
  the existing `docs/design/frame/W4_2_verifier_timing_extension_FRAME.md` as evidence of a
  deepened, honest understanding of the gap. No code change.
- **L2 target (data-flow detector shipped + mutation-tested):** implement §2's detector as a new
  function (`_scan_dataflow_source` or similar, additive to the existing `_scan_source`/`_scan_lines`
  pair, same file) gated behind an explicit flag until proven low-noise on the real tree; all five
  data-flow mutation tests from §4 green; `_format_report` extended to report data-flow findings
  distinctly from import findings (never conflated — a reviewer must be able to tell which class of
  violation fired).
- **L3 target (timing detector added + both wired into the phase-close gate):** implement §3's
  pattern table; all timing mutation tests from §4 green, including the load-bearing
  `test_timing_fires_on_replanted_hedge_volatility_bug`; both detectors promoted from
  flag-gated to default-on in `scan()`; the `phase-close` skill and CLAUDE.md's own description of
  the epistemic verifier updated to accurately state the new surface (closing exactly the kind of
  claim/reality gap this atom was already corrected for once — see §1's provenance note in the
  existing FRAME). R10 registered-simplification list (§5) carried into the tool's own docstring, so
  a future reader sees the honestly-bounded coverage, not an implied total one.

No level move happens as a result of this document. `level_current` stays `1`.
