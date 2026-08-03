<!-- BUILT 2026-08-03 (worker tick), atom SP3_size_and_clone_ratchet L0->L2. The park reason above
     (director_build_open) was abolished 2026-07-29 and swept 2026-08-03. The build is live:
     tools/size_ratchet.py + tools/size_ratchet_gate.py + tools/size_ratchet_override.py, wired into
     tools/git-hooks/pre-commit in WARN state, R15-proven both ways by 13 source mutations.
     THREE OF THIS DOCUMENT'S LOAD-BEARING CLAIMS WERE REFUTED BY BUILDING IT -- see the
     BUILD CORRECTIONS section appended at the foot. Read that before trusting anything above it. -->
# Size + Clone Ratchet — DISCOVER/Design (2026-07-28)

**Source:** `DIRECTOR_RULING_SHARED_PRIMITIVES_AND_CODE_STANDARDS_2026-07-28.md` §3 (Required shape,
decided) + §7 (Anti-Goodhart, binding) + §8 (Risk/mitigations) + Acceptance item 3.
**Mint:** `PLANNER_MINTED_size_and_clone_ratchet_2026-07-28.md`.
**This document:** the DESIGN of the mechanism, plus a **live line-count census run today** as
baseline evidence. It does not write a baseline artefact file, wire a gate, or touch any other file.
BUILD (the live ratchet, `tools/*_ratchet*.py`, pre-commit wiring, tests) proceeds only once a front
opens or `director_build_open` is granted.

---
## 0. Anti-Goodhart constraint (binding on every section below)

Per ruling §7, restated here because it constrains every design choice that follows: **clone count,
register count, and file size are tripwires and reported facts — never scores to minimise, never
inputs to any reward, fitness, or selection mechanism.** A ratchet that reds is a hard constraint
(pass/fail), never folded into a scalar, never a thing an agent is rewarded for lowering. Any design
below that could be gamed by structural perturbation (e.g. splitting one over-long file into two
under-count files with no reduction in real duplication, or writing an obfuscated variant of a cloned
function purely to dodge the AST fingerprint) is **itself the fidelity bug** the ratchet exists to
catch, not a workaround to endorse. The ratchet's own future implementation must not be tuned to make
its own numbers look better — a green ratchet is not a target, it is the absence of a fired tripwire.

---
## 1. BASELINE CAPTURE — design + live census (evidence, not artefact)

### 1.1 Scope: which tree, which globs, what's excluded

The ruling's own census method (§0): *"AST-level structural clone detection over all 788 source
modules (tests excluded)."* This design mirrors that scope exactly, so the ratchet's baseline is
directly comparable to the ruling's numbers.

**In scope (source tree):** `*.py` under the seven source roots that make up the built system:
`background/`, `company/`, `saas/`, `sim/`, `simulation/`, `interface/`, `tools/`.

**Explicitly excluded:**
- `tests/` — mirrors the ruling's own scope; test line-count growth is governed by test-suite health
  (`tools/pre_commit_test_gate.py`), not this ratchet. Including tests would also double-count every
  migration (a shared primitive's guard test is *supposed* to grow).
- `__pycache__/`, `node_modules/`, `.claude/worktrees/**` — generated/vendored/ephemeral, never
  hand-authored, would poison both line counts and clone fingerprints with duplicated worktree copies.
- `docs/`, `site/`, `data/`, `logs/` — non-Python; out of scope for a *code* ratchet (the site-lane
  gate and `moap_coherence_gate.py` already govern `site/`+`docs/` coherence; a size ratchet inventing
  a second axis there would be an accretion, not a fit — CLAUDE.md "DON'T ACCRETE").
- `functions/` is in scope by name but currently empty (0 files) — included for forward-compat so a
  first file dropped there is baselined from its first commit, not silently exempt.

### 1.2 Baseline snapshot: where it lives (design, not written here)

A JSON artefact at `docs/observability/size_ratchet_baseline.json` (same directory convention as
`fidelity_evidence_ledger.json`, `sanity_adjudication_ledger.json`, `coupled_gap_ledger.json` — the
project's standing home for machine-read/machine-written state), shaped:

```json
{
  "captured_at": "2026-07-28T00:00:00Z",
  "captured_by_commit": "<sha of the commit that froze this baseline>",
  "scope_roots": ["background", "company", "saas", "sim", "simulation", "interface", "tools"],
  "files": {
    "background/supervisor.py": 3957,
    "saas/reporting/annual_report.py": 9276,
    "...": "..."
  },
  "totals": {"file_count": 789, "line_count": 169852}
}
```

Written **once**, by the BUILD half, at the moment the ratchet goes live — not by this DISCOVER pass
(per the task instruction: report the numbers here, don't write the artefact). Every subsequent
ratchet run diffs the current tree against this frozen snapshot: `current_lines[f] > baseline[f]`
is the per-file violation predicate from ruling §3 bullet 1 ("no existing source file may exceed its
current line count"). A file **removed** from the tree is dropped from the live comparison (nothing
to violate) but stays in the historical snapshot for audit. A file with **no baseline entry** (new
file) is governed by the new-file cap (§3.2 below), not the exceed-baseline rule.

### 1.3 Live census run today (evidence)

Counted `*.py` files under the seven in-scope roots, excluding `__pycache__/` and `node_modules/`,
as of this DISCOVER pass (2026-07-28):

| Root | Files | Lines |
|---|---:|---:|
| `background/` | 85 | 29,331 |
| `company/` | 459 | 71,365 |
| `saas/` | 34 | 15,820 |
| `sim/` | 32 | 5,136 |
| `simulation/` | 75 | 21,554 |
| `interface/` | 4 | 875 |
| `functions/` | 0 | 0 |
| `tools/` | 100 | 25,771 |
| **Total** | **789** | **169,852** |

For reference only (excluded from ratchet scope, matches the ruling's own exclusion): `tests/` = 1,068
files, 195,297 lines.

**Corroboration:** the ruling's §0 census reports **788** source modules; this run counts **789** —
a 1-file difference, most plausibly a file added/removed between the advisor's tarball pull and today
(e.g. `saas/privacy_policy_page`-adjacent work landed since). Close enough (0.1%) to confirm the scope
definition above reproduces the ruling's method; the BUILD half should re-run this exact census at
go-live and freeze whatever it reads then as `docs/observability/size_ratchet_baseline.json`, not
today's numbers (today's are illustrative/design evidence, not the frozen baseline — the tree will
have moved by the time BUILD_OPEN lands).

**Files already over the two candidate caps (relevant to §3.2 below — these are *existing* files,
grandfathered under the "no larger than today" rule, never retroactively broken by a new-file cap):**
- 27 files exceed 600 lines (top: `saas/reporting/annual_report.py` 9,276; `background/supervisor.py`
  3,957; `simulation/run_phase2b.py` 2,722; `tools/generate_dashboard_data.py` 1,791;
  `background/process_run_complete.py` 1,774; `tools/generate_shadow_html.py` 1,689).
- 66 files exceed 400 lines.

This matters for the cap design in §3.2: a **hard 600-line gate applied retroactively to existing
files would immediately red 27 files** the ratchet is not supposed to touch (ruling §3: "no existing
source file may exceed its *current* line count" — its own count, not a universal cap). The 600/60
numbers are explicitly scoped to **new** files/functions only.

---
## 2. CLONE CEILING — design

### 2.1 No existing clone-census tool found in-repo

Searched `background/`, `tests/`, `tools/` for clone/duplication-census tooling
(`clone_census|duplication_census|clone_detect|code_clone|clone_register|jscpd`) — **no match**. The
223-instance census in the ruling was run by the advisor **externally**, against a pulled tarball, not
via any tool that lives in this repo. The BUILD half therefore needs to **build** the census tool, not
reuse one — there is nothing to reuse.

### 2.2 Minimal AST-based approach (mirrors the ruling's own method, in-repo, re-runnable)

Ruling §0's method, restated as an algorithm the BUILD half can implement directly with the Python
standard library `ast` module (no new dependency):

1. Walk the same scope as §1.1 (seven source roots, `.py` files).
2. Parse each file with `ast.parse`; walk to every `FunctionDef`/`AsyncFunctionDef` node (top-level and
   nested/method).
3. For each function body, produce a **structural fingerprint**: a sequence of AST node *type* names
   only — `ast.walk(node)` over the body, emitting `type(n).__name__` for each, discarding identifiers,
   constants, and docstrings (this is what makes it *structural* rather than textual — two functions
   with different variable names but the same control flow collide, matching the ruling's method).
4. Keep only fingerprints with **≥45 nodes** (ruling's own threshold — short functions collide by
   chance and would flood the census with noise; `sum(x, y): return x + y`-class functions are not the
   target).
5. Hash each fingerprint sequence (e.g. `hashlib.sha256` over the joined type-name sequence).
6. Group by hash; a group is a **clone-set** when it spans **≥2 distinct files** (same-file repetition
   is a different code smell, not what the ruling counted — ruling: "structurally identical function
   instances **across different files**").
7. The **clone count** the ratchet gates on is `sum(len(group) for group in clone_sets)` — i.e. total
   instances in multi-file clone-sets, the same quantity the ruling's 223 names (not the count of
   clone-*sets*, which the ruling separately reports as 70).

This reproduces the ruling's method closely enough to be **directly comparable** to the 223 baseline
without the BUILD half needing to guess at unstated parameters. Implementation lives at
`tools/clone_census.py` (BUILD half), callable both standalone (`python3 tools/clone_census.py` — for
the standing structural review, ruling §5.3) and imported by the ratchet gate for the pass/fail count.

### 2.3 Integration into the build gate

The clone count from §2.2 is compared against the **frozen ceiling (223)** recorded in the same
baseline artefact as §1.2 (`docs/observability/size_ratchet_baseline.json`, key `"clone_ceiling": 223`)
— not re-derived from a live re-run of the ruling's number, since the ruling fixed it explicitly
("today's 223" is the frozen constant, ruling §3 + Acceptance 3: "clone ceiling recorded at 223").
**The dependency named in the mint** (`clone_census_gap_register`, ruling §5.1) is a **soft dep**: this
ratchet does not wait for that register to land — it records 223 directly from the ruling text now,
and reconciles (adopts the register's live-recomputed figure as the *new* frozen ceiling, one-time,
logged) if and when that register's own census tool lands and disagrees. **Never a target of zero**
(ruling §3, restated in §7 Anti-Goodhart above) — the gate is `clone_count > 223 → FAIL`, there is no
lower-bound check and never should be one.

---
## 3. RATCHET RULES — mechanism design (rules are decided by the ruling; this is the enforcement design)

### 3.1 No existing file may exceed its current line count

Per-file comparison against the frozen baseline (§1.2): for every `*.py` file in scope present in both
the baseline and the working tree, `current_lines > baseline_lines[file] → violation`. A file's
baseline entry updates **only** when the ratchet is deliberately re-frozen (name-logged event, not
automatic — an automatic re-freeze-on-every-commit would let the ratchet silently absorb growth,
defeating the whole point).

### 3.2 New files / new functions capped

**New file** = present in the working tree, absent from the baseline snapshot. Cap: candidate **600
lines**, explicitly framed by the ruling as "to beat," not gospel. Given §1.3's evidence that 27
*existing* files already exceed 600 (and would be grandfathered, never gated), 600 is a reasonable
ceiling to hold *new* work to — it does not retroactively touch anything already over that line, and
holding new files to a number below several of the worst existing offenders directly serves the
ruling's own diagnosis (§0: "an agent … that never asks 'does this already exist?' … produces 91
hand-rolled registers" — a fresh 900-line register file would be exactly that pattern recurring).
**Candidate to beat, concretely:** 400 lines is a tighter bar worth proposing at BUILD time — §1.3
shows 66 files already exceed 400, i.e. 400 is *already* a common natural size in this codebase, not
an artificial squeeze; a new file at 400+ is worth a second look under §5's override rather than a
silent pass at 600. Left as a BUILD-time decision, not fixed here.

**New function** = a `FunctionDef`/`AsyncFunctionDef` node (by qualified name: module path + function
name, so a rename is treated as new — intentional, forces the ratchet to notice renames rather than
silently carrying an old baseline entry forward under a new name) absent from the baseline's function
inventory. Cap: candidate **60 lines** (`ast` end_lineno − lineno). Same "beat it" framing as above.

### 3.3 Any file touched by other work comes out no larger than it went in

This is the **narrowest and most important** rule — it is what makes the ratchet *drain* debt rather
than merely freeze it. Enforcement: for a file that appears in the commit's diff (touched — added,
modified, not merely present), the rule is stricter than §3.1's "no larger than baseline": it is "no
larger than the file's line count **immediately before this commit**" — i.e. compare against the
pre-commit `HEAD` version of the file via `git show HEAD:<path> | wc -l`, not the frozen baseline. A
file sitting untouched at 900 lines is fine indefinitely (§3.1 grandfathers it); the moment a commit
*touches* it, that commit may not grow it. This is how "debt drains by side-effect, never by
remediation sprint" (mint title) actually happens: the 91 registers shrink only when someone touches
one for an unrelated reason and the gate holds the touch to net-neutral-or-smaller, never by a
scheduled sprint.

### 3.4 Clone ceiling — 223, never a target of zero

Covered in §2.3. Restated for completeness of the rules list.

---
## 4. WARN-THEN-GATE rollout (ruling §8 mitigation)

**Why:** ruling §8, "Third concern": *"A size ratchet that reds on any growth will block legitimate
work mid-phase … the ratchet warns for one full cycle before it gates, and carries a named, logged
override rather than a silent one."*

**Design — two-state gate, state stored in the baseline artefact itself:**

```json
{
  "...": "... (as §1.2)",
  "rollout_state": "warn",
  "warn_started_at_commit": "<sha>",
  "warn_started_at": "2026-07-28T00:00:00Z"
}
```

- **`rollout_state: "warn"`** (initial state at BUILD go-live): a violation (§3.1–3.4) is detected,
  **printed loudly** to the pre-commit output (non-zero visibility, e.g. a boxed `[SIZE-RATCHET WARN]`
  block naming the file, its baseline count, its new count, and the delta) and **appended to a
  standing warn-log** (`docs/observability/size_ratchet_warnings.jsonl`, append-only, same convention
  as `decision_log.jsonl`) — but `tools/size_ratchet_gate.py` **exits 0** (does not block the commit).
- **`rollout_state: "gate"`**: identical violation detection, but the tool **exits 1** (blocks the
  commit, joins the `||  exit 1` chain in `tools/git-hooks/pre-commit` alongside
  `level_promotion_gate.py`, `moap_coherence_gate.py`, etc.).

**Transition trigger — "one full cycle," made concrete rather than left as a vague duration:** this
project's own standing retro/structural-review cadence is **already named** in the ruling itself (§5.3:
"the existing retro cadence (~50 phases / 2 weeks)"). Reuse it rather than invent a second clock: the
warn→gate flip is a **deliberate, logged, single edit** to `rollout_state` in the baseline artefact,
made no earlier than one retro cadence (~50 phases or 2 weeks, whichever the standing cadence resolves
to at the time) after `warn_started_at`, and only after inspecting the warn-log for the cycle to confirm
no chronic unresolved warn (a file still red at cycle-end without an override — §5 — is a sign the cap
is wrong, not that the gate is ready; fix the cap, don't flip early to force compliance). This mirrors
the ratchet's own Anti-Goodhart clause: the *transition itself* must not be rushed to hit a forecast
(LAW A — the plan is a diagnostic, dates are forecasts, "no atom may be promoted … to hit a forecast").

**No auto-flip.** The transition is a named, git-visible, one-line diff to the baseline artefact
(`rollout_state: "warn" → "gate"`) reviewed like any other config change — never a timer that flips
itself silently, which would reproduce exactly the "committed != running / silent state change" class
R2/R7 already forbid.

---
## 5. Named, LOGGED override path (not silent)

**Design: reuse `background/decision_log.py`, don't invent a parallel mechanism.** The repo already
has exactly the primitive this needs — `log_decision()` / `decide()`, append-only JSONL at
`docs/observability/decision_log.jsonl`, "writes itself, not discipline-written" (its own docstring).
Building a second override-log would itself be exactly the kind of duplication ruling §3/§5 exists to
stop.

**Mechanism (BUILD-time design):**
1. A violation in `gate` state does not have a bypass flag on the gate tool itself (no
   `--skip-ratchet`, which would be silent-by-construction the moment someone reaches for it under
   time pressure — CLAUDE.md's own routine-creation precedent: "if a required output cannot be
   achieved with a genuinely minimal … set, leave it disabled rather than widen scope to fit").
2. Instead, an override is a **pre-existing, named, logged decision** the commit can point to: before
   committing, the author (human or agent) runs a small helper (`tools/size_ratchet_override.py
   --file <path> --why "<reason>" --reverse "<how to undo>"`) that calls
   `background.decision_log.log_decision()` with `what="size ratchet override: <file>"`, the supplied
   `why`, and `how_to_reverse` — and **records the specific new line count being authorized** as part
   of the log entry (so the override is scoped to *this* growth, not a standing exemption).
3. The gate (`tools/size_ratchet_gate.py`), on finding a violation, checks
   `docs/observability/decision_log.jsonl` for a **matching, unexpired** override entry (same file
   path, new count ≥ the count the gate is currently seeing) logged in this commit's session — if
   found, the gate passes **and prints the override's `why`/logged timestamp inline** (so a passing
   gate with an override is visibly different in the commit's own CI-equivalent output from a plain
   pass, satisfying "not silent"). If no matching entry, it fails per §4's `rollout_state`.
4. The override is **per-instance, not per-file-forever** — growing the same file again later requires
   a fresh logged override, so the log accumulates a full, auditable history of every deliberate
   exception, matching the standing structural review (ruling §5.3) which can then report "N overrides
   this cycle, on files X/Y/Z, for reasons A/B/C" as part of its drift report.

---
## 6. R15 both-ways plan (mandatory before the gate is relied on)

Design of the mutation tests the BUILD half must write and pass (mirrors the pattern already proven in
`tests/tools/test_moap_coherence_gate.py`, `tests/tools/test_ruling_archive_question_gate.py`):

1. **File-growth fires (warn state):** take a file at its baseline count, append lines past it, run the
   gate in `rollout_state: "warn"` → asserts exit 0 **and** a new line appended to
   `size_ratchet_warnings.jsonl` naming the file and delta. Revert the file → gate exits 0, no new warn
   line (warn-log only grows on real violations, not on every run — a warn-log that grows every run
   regardless of violation would itself be a fail-open control, indistinguishable signal from noise).
2. **File-growth fires (gate state):** same mutation, `rollout_state: "gate"` → asserts **exit 1**.
   Revert → exit 0. This is the core "grow past count / add 224th clone ⇒ warns-then-gates; revert ⇒
   passes" proof named in the mint's exit criteria.
3. **Clone-ceiling fires:** synthetically add a 224th structurally-identical function instance
   (duplicate an existing ≥45-node function body into a second file) → clone census reads 224 → gate
   fires (warn or gate per rollout state, same as #1/#2). Remove the duplicate → census reads back to
   223 (or below) → passes.
4. **New-file cap fires:** add a new 700-line file (no baseline entry) → fires against the 600
   candidate cap. Shrink under 600 → passes.
5. **Touched-file-net-larger fires:** modify an existing file (already under its own baseline) such
   that the commit's diff makes it larger than its pre-commit `HEAD` version, while still staying under
   the frozen baseline → **must still fire** (this is the §3.3 rule, stricter than §3.1 — proves the
   two rules are independently enforced, not just the baseline check reused twice). Revert to
   pre-commit size or smaller → passes.
6. **Override passes and is logged, never silent:** run the override helper (§5) for a genuine
   violation, then run the gate → asserts exit 0 **and** asserts the gate's own output/log contains the
   override's `why` and timestamp (not just a bare pass) **and** asserts `decision_log.jsonl` gained the
   entry. Run the gate again for a *different*, un-overridden growth on the same file → asserts it still
   fires (proves the override is scoped to the logged instance, not a standing exemption — closes the
   obvious fail-open: "one override silently exempts the file forever").
7. **Rollout-state transition is a no-op on detection logic:** the same violation fixture run under
   both `rollout_state` values produces identical *detection* (same warning payload/log entry) and only
   differs in exit code — proves warn/gate is a presentation/blocking toggle, not two different
   (and therefore divergently-buggy) detection code paths.

Each of 1–6 above is a **fires-then-clears** pair, matching R15's own definition (mutation proves the
control fires on its own named defect, not merely that it passes on clean input) — a control that only
ever passes is worthless per R15 doctrine, restated in the mint and this doc's §0.

---
## 7. Wiring point (for the BUILD half's reference — not built here)

`tools/git-hooks/pre-commit` already chains gates as `python3 tools/<gate>.py || exit 1`
(`level_promotion_gate.py`, `moap_coherence_gate.py`, `site_lane_gate.py`,
`ruling_archive_question_gate.py`, `pre_commit_test_gate.py`). `tools/size_ratchet_gate.py` joins the
same chain, positioned **after** the test gate (no point size-gating a commit whose tests are already
red) and **before** the level-promotion gate is immaterial (they're independent checks; order doesn't
matter beyond "test gate first" as an efficiency/clarity convention, not a correctness one).

---
## 8. Open questions left for the BUILD half (not this design's call, or genuinely undecided)

- Exact new-file/new-function numbers to *beat* 600/60 (§3.2 floats 400 as a candidate tighter bar,
  backed by the census showing 400 is already a common natural size — BUILD-time decision).
- Whether the clone census (§2.2) should also fingerprint methods on classes distinctly from
  module-level functions, or collapse them — the ruling's method description doesn't disambiguate;
  the BUILD half should re-derive 223 with its chosen convention and confirm it still lands at (or
  very near) 223 before trusting the frozen ceiling.
- Precise wording/format of the standing warn-log's boxed pre-commit output — cosmetic, BUILD's call.

Nothing above is a wall. No safety/auth/curriculum control is touched by any part of this design
(mint's own "Walls untouched" section, restated): this is build-discipline tooling only.

---
# BUILD CORRECTIONS (2026-08-03 worker tick, atom `SP3_size_and_clone_ratchet` L0→L2)

Three load-bearing claims above were **refuted by measurement during the build**. They are corrected
here rather than edited away, because the pattern is the point: this is the sixth consecutive atom
whose closed DISCOVER doc contained a build-blocking error, and the errors keep being of *different
kinds*. A closed DISCOVER doc is a hypothesis, not a specification.

## Correction 1 — §2.1 "No existing clone-census tool found in-repo" is now FALSE

§2.1 concluded: *"The BUILD half therefore needs to **build** the census tool, not reuse one — there
is nothing to reuse."* True on 2026-07-28. **False by the time BUILD drew**, and by only six days:
`background/shared_primitive_census.py` (atom SP5, landed earlier on 2026-08-03) ships a
parameterised AST clone detector — `_clone_census` / `_function_shape` / `_iter_source_files`, with
`DEFAULT_NODE_THRESHOLD = 45` — whose own module docstring records the reconciliation it owed SP3:
*"to be reconciled against SP3's own detector once that atom lands, never silently assumed equal."*

Building the designed `tools/clone_census.py` would have put **a second AST clone detector in the
repo, committed by the atom whose entire purpose is to stop duplication** — the 91-registers pattern
reproduced by its own remedy. So the build **imports SP5's detector** instead, and
`test_sp3_does_not_ship_a_rival_clone_detector` fails if the fingerprinting ever comes home.

**Worth carrying:** a DISCOVER doc's "nothing exists to reuse" finding has a shelf life measured in
days on a codebase moving this fast, and it is exactly the claim whose staleness does the most
damage — it is the claim that authorises writing new code.

## Correction 2 — §2.3's "freeze the ceiling at 223 from the ruling text" is a FAIL-OPEN, and 223 is not reproducible

§2.3 said to record 223 directly from the ruling and reconcile later. §1.2 said the opposite for file
sizes (*"freeze whatever it reads then… today's are illustrative, not the frozen baseline"*). The
document contradicts itself, and **§2.3 is the wrong half**.

§8 named the condition for trusting 223: *"re-derive 223 with its chosen convention and confirm it
still lands at (or very near) 223 before trusting the frozen ceiling."* **Measured at build time, it
does not, under either available convention:**

| convention | scope | clone-sets | instances |
|---|---|---:|---:|
| ruling §0 (external, 2026-07-28) | "788 source modules" | 70 | **223** |
| SP5's detector, SP5's 5 roots | 707 files | 87 | **269** |
| SP5's detector, SP3's 8 roots | 813 files | 92 | **283** |
| body-only fingerprint, 8 roots | 813 files | 68 | **209** |

The spread is not drift alone — the tree also moved hard (789 → 818 files, **+24k lines in six
days**), and the conventions genuinely differ (SP5 fingerprints the whole function node including
its signature; a body-only fingerprint reads 74 lower). **Freezing 223 against a tree measuring 283
would have handed the ratchet 60 instances of silent headroom on day one** — someone could have added
60 cross-file clones and the gate would have stayed green. That is a fail-open by construction, and
it is the opposite of what a ratchet is.

**Built instead:** the ceiling is frozen from the detector that actually runs, over the declared
scope, at the moment of freezing (**283**), with the ruling's 223 carried in the artefact as
`historical_reference_ceiling` plus a note — so the delta stays visible and is never laundered into
"we were always at 283". This resolves §8's second open question by answering it in the negative.

## Correction 3 — the ceiling the ruling set was never actually enforced anywhere

Found while checking whether SP5 already gated on its own constant. `CLONE_CEILING = 223` appears at
exactly **two** sites in the whole repo: its definition, and one write into
`docs/observability/shared_primitive_census.json`. **It is never compared to anything.** The artefact
on disk today reads `"clone_ceiling": 223` next to `"clone_count": 267` — a 44-instance breach,
sitting in primary state, firing nothing.

So the ruling's ceiling existed as a **reported fact with no tripwire attached**. That is precisely
the orphan-transition class this project has now recorded five times (`generate_evidence_data.generate()`,
`write_fabric_gap_entries`, `fabric_settlement_gap.py`, `TenancyChangeCoupler`, and the W1_11 wiring
mutation) — here in its subtlest disguise yet: not a function nobody calls, but a **constant nobody
compares**. It reads as enforcement to anyone grepping for the number.

SP3 *is* the missing tripwire, which is the strongest available argument that this atom was worth
building rather than archiving.

## Open questions §8 — resolved

- **Tighter new-file cap (400 vs 600):** kept at **600**. 89 existing files already exceed 400 and 43
  exceed 600; a 400 cap on new files while 89 existing files sit above it invites the split-to-dodge
  perturbation §0 forbids. 600 with a logged override is the honest bar. Revisit at the warn→gate flip
  with a cycle of real warn-log evidence, not now on argument alone.
- **Methods vs module-level functions:** collapsed (both counted), because that is what SP5's detector
  does and a single detector is worth more than a marginally better convention. Recorded, not hidden.
- **Warn-log format:** JSONL, one object per finding, same convention as `decision_log.jsonl`.

## What this build does NOT claim (the honest L2/L3 boundary)

`rollout_state` is **warn**: the ratchet detects, prints and logs, and does **not** block. It has
therefore never actually prevented a real regression in the wild, which is what L3 needs. The
warn→gate flip is a deliberate one-line diff after one retro cadence of warn-log evidence, and is
this atom's named L3 residual. **A gate that has only ever run in warn state is an untested brake.**

## Findings registered, not fixed on sight (SELF_INTERRUPT_DISCIPLINE — the machine is not blocked)

1. **SP5's census scope omits `tools/` and `interface/`** (110 files, ~31k lines it never sees), while
   the ruling's own census scope was "all 788 source modules". SP3 uses the wider, ruling-faithful
   scope. Two live numbers now describe "the clone count" over different scopes; they must be
   reconciled to one, and SP5's is the side that deviates. Not fixed here — it is another atom's file
   and changing its scope moves its register's output.
2. **SP5's `CLONE_CEILING = 223` is now doubly wrong** — unenforced (correction 3) *and* 46 below its
   own detector's live reading of its own scope. Reconciling it against SP3's frozen ceiling is the
   natural next touch on that module.
