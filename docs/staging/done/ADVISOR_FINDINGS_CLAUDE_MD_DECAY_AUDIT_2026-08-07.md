# ADVISOR FINDINGS — the instruction file is over its own hard limit, and the decay audit has never run

**Severity:** LATENT · **Lane:** H_harness

**Staged 2026-08-07. Proportionality: the size breach is narrow and reversible — just do it. The gate blind spot is contract-touching — implement with the mitigations named below. The audit itself is a judgement pass, not a build.**

---

## 1. What was found

Two things, one narrow and one structural. Both were checked against origin this turn; every claim below traces to a specific artefact, and where I could not check something from here I say so.

### 1a. `CLAUDE.md` is over the hard limit it sets for itself

- Measured from origin `main` via the Contents API this turn: **35,504 characters** (131 lines).
- `background/claude_md_integrity.py` sets `MAX_CHARS = 35_000` as a fixed doctrine constant, deliberately independent of the file it measures.
- So the file is **504 characters over**, and `tests/tools/test_claude_md_integrity.py::test_real_claude_md_within_hard_limit` is a live-state assertion that would fail on it. That test carries no skip or xfail marker.

The commit history makes the shape of it plain:

- `08d31bcce` (2026-08-03 09:06Z) — *"docs(CLAUDE.md): correct stale in_progress/ scan-exemption claim; trim under 35k"*.
- `52693115b` (2026-08-03 13:21Z) — *"Budget cut: fork fan-out serial by default + a standing no-polling rule"*. This is the last commit to touch the file, and it put it back over.

Four hours between a deliberate trim and the regression. Nothing has touched the file since; it has been over for four days.

**What I could NOT check from here:** whether the full suite has actually been run against this state on the machine. I cannot run their suite from this seat. So I cannot tell you whether the test is currently sitting red or has simply not been exercised — that is a question for the box, not an inference to be asserted. Publishing was separately jammed across part of that window for an unrelated reason (`docs/retrospectives/2026-08-03-a-diagnostic-pinned-as-a-target-wedged-publishing-four-days.md`), which is one plausible reason the signal never surfaced, but I am labelling that **inferred**, not observed.

### 1b. The commit-time gate is structurally blind to edits of this file

`tools/pre_commit_test_gate.py` selects what to run two ways: a fixed safety-control set that fires when any staged path sits under `CODE_PREFIXES` (`background/`, `.claude/`, `tests/`, `tools/`, `saas/`, `company/`, `sim/`, `simulation/`, `interface/`), plus a per-file mapping from a changed `.py` source to its own test. There is also a named level-surface list of two data files that were specifically taught to the gate after they slipped through as "pure data".

`CLAUDE.md` is in none of those. It is not a `.py` file, it sits at the repo root under no code prefix, and it was never added to the level-surface list. **A commit that edits only `CLAUDE.md` runs no tests at all.**

This is the part worth naming as a class, not an instance. The document whose central doctrine is *"a rule lives in CLAUDE.md AND as enforced code, or not at all"* is the one document the commit gate cannot see you editing. The guard exists; it has a hole shaped like the thing it guards. Two files have already been taught to the gate for exactly this reason (the level surface, after two wedges on 2026-07-21) — so the pattern is known and this is its third instance.

### 1c. The decay audit itself has no record of ever being performed

`CLAUDE.md` commits the project to a decay audit at every epoch boundary: walk the prose-only rules and either mechanise or delete them. Searched `docs/observability/` for any artefact of such an audit: **zero hits**. No retrospective records one. The only piece of the doctrine that was ever built is the size-and-dangling-pointer control above (H7, 2026-07-16), which covers the file's *size*, not the *status of its rules*.

So: one narrow guard, quietly breached; the audit proper, never run once.

---

## 2. The problem to solve

Three separable problems. They are stated as problems, not as designs — the agent knows the tree better than I do and should choose the mechanisms.

**P1 — The file is over its own declared ceiling.** Get it back under. This is a content problem, and the interesting half is *which* content leaves: the standing rule is that a rule must exist as enforced code or not at all, so the candidates for removal are the paragraphs that are pure exhortation with no mechanism behind them. Trimming by deleting whitespace or shortening sentences satisfies the number and defeats the point.

**P2 — A change to the instruction file must be able to fail a gate.** Today it cannot. What the right trigger surface is, and whether the answer generalises beyond this one file to every governing document that has a live control over it, is the agent's call. The class question worth asking: *which other files carry a live control that the commit gate cannot see being edited?* If the answer is more than this one, fix the class.

**P3 — The decay audit has never been performed. Perform it once.** Walk the rules in `CLAUDE.md` and, for each, establish whether a mechanism actually enforces it or whether it is prose only. Every prose-only rule then gets one of two dispositions: mechanised, or deleted. There is no third option — the project's own doctrine is explicit that a prose-only rule is worse than no rule, because it creates the illusion of control. Expect deletions; that is the point, and it also serves P1.

---

## 3. Non-negotiables

- **A trim must not become a quiet loosening.** Raising `MAX_CHARS` to accommodate the current file would satisfy the test and destroy the control. The constant is doctrine; it moves only by the director's word, not to make a red test green.
- **Whatever gate change lands must be proven able to fail** — a mutation showing it fires on an oversize instruction file committed alone. A gate extension that passes on everything is the fail-open pattern this project already names.
- **The audit's output is a record, not a claim.** If it is performed and leaves no artefact anyone can read later, it has not been performed — that is exactly why I could not tell whether it had ever happened.
- **Deletion is a legitimate outcome and should not be avoided out of caution.** A rule that has never been enforced has never actually been in effect; removing its text changes nothing about the running system and makes the file honest.

---

## 4. Risk

**What it touches:** the root instruction file every session loads; the commit-time test gate that every commit passes through; potentially the set of rules the agent operates under.

**Blast radius:**

- *P1 (trim)* — low. Content-only. The risk is judgement, not breakage: deleting a rule that turns out to be load-bearing.
- *P2 (gate)* — moderate, and this is the one to be careful with. Widening what the pre-commit gate runs slows every commit, and the gate's own docstring is explicit that it was scoped narrow deliberately to keep the loop's cadence fast. A change that makes every docs commit run the safety-control set would be a real cost paid continuously.
- *P3 (audit)* — low mechanically, high in judgement. It changes what the agent believes it is bound by.

**Probable failure modes, and the mitigations inline:**

1. *The trim satisfies the number and loses nothing real* — mitigate by requiring each deletion to name whether the rule had a mechanism, so the trim doubles as the first pass of P3 rather than a separate cosmetic exercise.
2. *The gate widening taxes the commit loop* — mitigate by scoping the new trigger to the specific files that carry a live control over them, rather than widening the prefix set to catch all documentation.
3. *A load-bearing rule gets deleted as "prose only" because its mechanism lives somewhere the search did not look* — mitigate by requiring the disposition to name the mechanism's location when one is found, so a "no mechanism" verdict is a stated search that came back empty rather than an absence of effort.
4. *The audit is performed and its findings absorbed but never recorded* — the project's own distinction between consumed and absorbed applies to the advisor's asks too. The artefact is the deliverable.

---

## 5. Decided vs open

**Decided (director, this turn):** all three are to be done, in one pass, on the restart.

**Open, and genuinely the agent's:** the trigger surface for P2; how far the class fix extends; the format of the audit record; which specific rules survive P3.

**Not open:** the value of `MAX_CHARS`.

---

## 6. Why this came up

The director was reading a widely-circulated personal `CLAUDE.md` — forty lines, six workflow principles, largely exhortation. The comparison it invited was not about its content, most of which this project has in far stronger form. It was about size: forty lines fits in working attention, thirty-five thousand characters has to be searched. That is what prompted the check, and the check found the guard for exactly that problem already built, already breached, and unable to see the edit that breached it.
