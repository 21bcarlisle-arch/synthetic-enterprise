# NAIVE_ORGAN_DESIGN — the deliberately-amnesiac question organ

**Atom:** `H11_naive_organ` (maturity_map.yaml, epoch 2, L0→L3, lane H_harness).
**Status:** DISCOVER/FRAME design (Lane-3, doc-only — NO `background/naive_organ.py` written here; BUILD is epoch-gated, twin-approvable per canon v2 §3a).
**Source spec:** `docs/staging/done/THE_NAIVE_ORGAN.md` (director-decided).
**Structural inverse studied:** `background/director_twin.py`.
**Author:** DISCOVER/FRAME pass, 2026-07-13.

---

## 0. The one idea, stated once

`director_twin.py` isolates a fresh Claude process so it can ONLY see the
director's canon — nothing of the builder's reasoning. The Naive Organ is the
**structural inverse**: a fresh Claude process that can ONLY see the *raw
observable state* and the *system's own claims* — and is deliberately denied the
codebase, `CLAUDE.md`, the maturity-map's prose rationales, the history, and
every accumulated "that's just how it is here." The twin isolates to preserve
*fidelity to a principal*. The organ isolates to preserve *ignorance of the house
norms*, because a naive agent that accumulates context stops being naive and
inherits the assumptions it exists to break.

Both use the same process mechanism (`claude -p --model claude-opus-4-8
--tools=`, scratch cwd, no permission bypass). They differ ONLY in what text goes
into the prompt. That is the whole design: **isolation is identical; the prompt
payload is opposite.**

The organ emits **QUESTIONS, never fixes.** A question is a finding the agent
must ANSWER WITH EVIDENCE ("no, that was true because X" is fine; "that's just how
it is" is not). Its hit-rate is a diagnostic for US, never a training signal for
IT (anti-capture, Law-B-shaped).

---

## 1. The seven trigger detectors — mechanised

Each trigger is a pure function `detect(state) -> list[Trigger]` reading only
on-disk observable state. A `Trigger` is `{trigger_id, evidence_refs, claim_text,
observed_value, fire_reason}`. When any detector fires, the organ is invoked once
per distinct fired trigger (§2). **The detectors do NOT decide the question — they
decide WHEN to ask; the amnesiac Opus process decides WHAT to ask** from the raw
evidence pack the detector attaches. This split is deliberate: the mechanical
detector cannot be captured (it is a regex/threshold), and the judgment (the
naive question) is done by an agent that has no house context to be captured by.

Common inputs (the organ's entire world — see §2 for the isolation guarantee):

| Handle | File | What it is |
|---|---|---|
| MAP | `docs/design/maturity_map.yaml` | atoms as DATA (id, level_current, level_target, loop_stage, epoch) — NOT the prose `simplifications` |
| RUNHIST | `docs/observability/run_history.json` | per-run `net_margin_gbp`, `enterprise_value_gbp`, `generated_at`, `git_hash` |
| INSIGHTS | `docs/observability/run_insights.json` | latest headline metrics + narratives |
| STATUS | `docs/observability/agent_status.json` | each daemon's `status`/`last_action`/`anomaly` |
| DIGEST | latest digest text + latest `docs/status/LATEST.md` | the system's own CLAIMS in prose |
| DLOG | `docs/observability/decision_log.jsonl` (via `decision_log.read_decision_log()`) | logged decisions incl. their rationale strings |
| GITLOG | `git log --oneline --since=<window>` (subprocess, read-only) | commit subjects = claims + fix-class fingerprints |
| ANR&IDLE | `docs/observability/.supervisor_idle_turn_count.json`, `.supervisor_map_exhausted_state.json` | idle-turn counter, exhaustion state |

The "claims surface" the organ checks against data is **DIGEST + STATUS +
GITLOG subjects + DLOG rationales** — the places the system asserts things about
itself in words. The "data surface" is **MAP + RUNHIST + INSIGHTS + the idle
counters** — the places reality is recorded in numbers/structured state.

### T1 — Flat metric while the system reports healthy
*Real catch: three hours of idle turns while status read "healthy".*
- **Observable:** goal metric unchanged across the last **K** runs (default K=3)
  AND the claims surface asserts a healthy/nominal state.
- **Mechanics:** `net_margin_gbp` (and `enterprise_value_gbp`) from the last K
  RUNHIST entries; fire if `max-min < ε` (default ε = £1 — the weekend runs sat
  at *identical* `1,505,286` for many commits, see the repeated
  `net=£1,505,286` commit subjects). AND STATUS shows every agent `status` in
  {idle, ok} with `anomaly == null` AND no `net_margin` change in GITLOG's
  `net=£…` auto-process subjects over the window. Also fire on the **idle-turn
  counter** (`.supervisor_idle_turn_count.json`) > threshold while the map has
  atoms below target.
- **Question seeded:** "The goal number has not moved in N runs and every status
  says healthy — what, concretely, changed in the world between these runs, and
  if nothing did, why are we running?"

### T2 — Terminal-state claim (must independently check raw data)
*Real catch: "the map is exhausted" with 31 open atoms.*
- **Observable:** the claims surface contains a terminal token AND the data
  surface contradicts it.
- **Mechanics:** case-insensitive scan of DIGEST/STATUS/GITLOG/DLOG for
  `{"exhausted", "nothing to do", "nothing left", "no candidates", "no drawable",
  "complete", "all done", "blocked", "map exhausted"}`. On a hit, INDEPENDENTLY
  recompute the raw count from MAP: `open = [a for a in atoms if a.level_current
  is not None and a.level_current < a.level_target]`. Fire if `len(open) > 0`
  while a terminal claim is live. Attach the actual open list (ids + levels) as
  evidence. (This is the exact `_maturity_map_draw_concurrent` open-atom
  predicate at supervisor.py:494-499, computed independently so a bug in the
  draw cannot silence the organ.)
- **Question seeded:** "Something claims '<token>'. I counted <N> atoms with
  level_current < level_target directly from the YAML. Which is true?"

### T3 — Inherence claim (fact, or unchecked assumption?)
*Real catch: "build must be narrow / can't be parallelised" — worktrees existed all along (cf H10).*
- **Observable:** the claims surface asserts something is intrinsic/unavoidable.
- **Mechanics:** scan DIGEST/GITLOG/DLOG for inherence tokens: `{"physics",
  "inherent", "inherently", "unavoidable", "by design", "cannot be
  parallelised", "must be narrow", "one at a time", "can't be", "impossible to",
  "no way to"}`. Fire on any hit; attach the sentence. The organ is NOT asked to
  know the answer — it is asked to demand the assumption be *checked against
  published practice* rather than asserted. (The real miss:
  `f1a271ff`/`04d73441` asserted "BUILD is inherently narrow, one tree" for six
  weeks; native worktree isolation was documented practice all along.)
- **Question seeded:** "'<claim>' is stated as a fact. Is it a law of nature, or
  an untested assumption? What published practice would confirm or refute it?"

### T4 — First-principles claim about a fast-moving external field, unchecked
*Real catch: six weeks of not knowing about worktrees; cf G3 Finding 1; RETRO e8480ced "STRUCTURAL WALL".*
- **Observable:** a claim reasons from first principles about a domain that moves
  fast (LLM tooling, Claude Code capabilities, model tiers, agent frameworks)
  with no cited external check.
- **Mechanics:** two-part. (a) The claim sentence contains a first-principles
  framing token `{"from first principles", "must be", "the only way",
  "necessarily", "there is no", "the fundamental"}` AND a fast-field noun from a
  small maintained lexicon `{claude code, worktree, subagent, model, opus,
  sonnet, haiku, mcp, hook, context window, agent sdk, token, api}`. (b) NO
  co-located citation token `{"per docs", "published", "release notes",
  "changelog", "verified against", "https://", "checked"}` within the same
  DLOG/commit entry. Fire when (a) AND NOT (b). This is mechanical proxy for "a
  hypothesis was asserted as a finding" (advisor's repeated R9 breach this
  weekend).
- **Question seeded:** "This is a first-principles claim about <fast field>, with
  no external check cited. Fast fields change monthly. Has published practice
  been read since this was decided?"

### T5 — Sustained work in one category while the goal metric is flat (the treadmill)
*Real catch: harness-grooming vs company backlog (c870427f "THE TREADMILL").*
- **Observable:** the last M commits concentrate in one work-category while the
  goal metric (and/or `atoms-below-target`) does not fall.
- **Mechanics:** classify each of the last M GITLOG subjects (default M=20) by a
  coarse path/keyword bucket — `harness` (background/, supervisor, daemon,
  digest, ntfy, R3/R7/idle), `company` (company/, saas/, billing, pricing,
  churn), `site` (site/, docs/shadow), `sim` (sim/, simulation/). Fire if one
  bucket ≥ **60%** of commits AND the goal metric is flat over that window (RUNHIST
  ε as in T1) AND, if computable, `atoms-below-target` did not fall (compare the
  current MAP open-count to the count logged at the window start — a rolling
  `naive_organ_atoms_below_target.jsonl` breadcrumb, one int per digest, is the
  cheapest source; if absent, fall back to goal-metric flatness alone).
- **Question seeded:** "N of the last M commits were <bucket> work, and the goal
  metric / atoms-below-target did not move. Is <bucket> the work that matters, or
  the treadmill?"

### T6 — Claim-vs-data contradiction on any observable surface
*Real catch: "no drawable atoms" vs 30 idle atoms in the YAML (the tautology, 793ef089).*
- **Observable:** a specific numeric/state claim in the claims surface disagrees
  with the directly-computed value from the data surface. T2 is the terminal-state
  special case; T6 is the general form for any *quantified* claim.
- **Mechanics:** a small **claim-extraction table** maps a regex over the claims
  surface to a recomputation over the data surface, and fires on mismatch beyond
  tolerance. Seed entries (extensible — this table IS the trigger, adding a row
  is the supported way to widen it):
  - `r"(\d[\d,]*)\s+atoms? below target"` vs `len(open_atoms(MAP))`.
  - `r"no drawable atoms|nothing to draw"` vs `len(open_atoms(MAP)) == 0`.
  - `r"net(?: margin)?[^\d]{0,8}£?([\d,]+)"` vs latest RUNHIST `net_margin_gbp`
    (rounded).
  - `r"(\d+)/(\d+) retention offers"` vs INSIGHTS retention counts.
  - `r"survived"` / `r"administration"` vs RUNHIST `risk.survived` /
    `administration_event`.
  Fire on any row whose claimed value ≠ computed value (exact for counts, ±£1 for
  money after rounding).
- **Question seeded:** "The claim says <claimed>; the raw data says <computed>.
  These disagree. Which is the artefact and which is the truth?"

### T7 — Same class of fix applied N times (is the class defined correctly?)
*Real catch: five [ACTION NEEDED] patches guarding an undefined class (ACTION_NEEDED_REDESIGN); the "9th idle variant" pattern in supervisor.py.*
- **Observable:** ≥ N (default N=3) commits within a window share a fix-class
  fingerprint.
- **Mechanics:** fingerprint each GITLOG subject by a normalised signature —
  lowercase, strip run-hashes/numbers/dates, then bucket on a maintained set of
  class regexes: `idle[- ]?(hole|turn|variant)`, `\[?action needed\]?`, `escalat`,
  `false (completion|claim)`, `stale (process|code|site)`, `two[- ]?strike|R3`,
  `refill|draw`. Count fingerprints across the last **W** commits (default
  window = 40). Fire when any fingerprint count ≥ N. (The supervisor's own
  comments literally enumerate "9th idle variant" — the class kept being
  re-patched instance-by-instance; the organ names that pattern from the git log
  mechanically.)
- **Question seeded:** "This same class of fix has been applied <N> times
  (<fingerprint>). Is the CLASS defined correctly, or are we patching instances of
  a class we have never actually specified? (R10.)"

### Hardest-to-mechanise trigger — and the resolution

**T4 and T5 are the hard ones**, and T5 is the hardest: "is this the work that
*matters*?" is a judgment about *purpose*, and purpose is explicitly NOT
mechanisable (THE_NAIVE_ORGAN §"What this does NOT replace"). A naive threshold
("60% one bucket + flat metric") will false-positive on legitimately-necessary
harness work (you sometimes MUST groom the harness before company work can
proceed). **Resolution — separate the FIRING from the ANSWERING, and let the
mechanical part only ever raise a QUESTION, never a verdict.** The detector's job
is the cheap, capture-proof part: "one category dominated AND the goal did not
move" is a purely mechanical observation from git+RUNHIST, no judgment. The
*question* it raises ("is this the work that matters?") is answered by the
amnesiac Opus process from the evidence pack, and then the AGENT must answer it
with evidence. A false-positive is therefore harmless-by-construction: the agent
replies "yes, harness grooming was prerequisite because seams cap throughput
(cf e8480ced law 5), here is the evidence," the finding closes, and the
hit-rate metric records a miss — which is a diagnostic for US, never a signal fed
back to retune the detector (anti-capture). We accept a noisy detector precisely
because the cost of a wrong question is one evidence-backed answer, while the cost
of a missed treadmill is three lost hours (the actual weekend cost). The
threshold is set generous, not precise.

---

## 2. The amnesia-isolation mechanism — and how to PROVE it

### 2.1 The isolation (inverse of `director_twin._default_invoke`)

Reuse the twin's process pattern verbatim, changing ONLY the prompt payload:

```
subprocess.run(
    [CLAUDE_BIN, "-p", "--model", "claude-opus-4-8", "--tools=", prompt],
    cwd=<fresh tempfile.TemporaryDirectory>,   # OUTSIDE the repo
    capture_output=True, text=True, timeout=180,
)
```

Same three defences the twin proved by a real failed-write test:
1. **No `--dangerously-skip-permissions`** → default-deny; non-interactive `-p`
   cannot satisfy a permission prompt, so any tool call fails closed.
2. **`--tools=`** (single argv token) → every tool disabled at the CLI. The organ
   reasons over text and prints; it can read nothing on its own.
3. **`cwd` = scratch temp dir outside the repo** → even if it tried to read
   `CLAUDE.md` or `docs/`, there is no repo at its cwd to find.

**The critical difference from the twin:** the twin's prompt embeds the *entire
canon*. The organ's prompt embeds ONLY:
- **GOAL** — a single fixed sentence (the business's north star, e.g. "maximise
  the simulated UK energy supplier's enterprise value under survival
  constraints"), passed as a literal constant, NOT read from CLAUDE.md.
- **OBSERVABLE STATE** — only the specific evidence the *firing detector*
  attached: the numbers/rows/atom-list relevant to that trigger, serialised as
  flat JSON. Never a file path the organ could be told to "go read," because it
  has no tools — every byte it sees is chosen by the detector and pasted in.
- **THE CLAIM(S)** — the exact claim text that tripped the trigger.
- **A fixed rubric** — "You are a naive outsider. You have never seen this
  system's code, its documentation, or its reasoning. Ask the single sharpest
  question a smart outsider would ask about the contradiction/flatness/claim
  below. Output ONLY questions, never fixes or answers. Do not assume the claim
  is true; do not assume it is false."

Because the process has NO tools and its cwd is empty, **the ONLY context it can
possibly have is the prompt string the detector built.** There is no conversation
history (fresh `-p` subprocess), no CLAUDE.md injection, no MCP, no file access.
The amnesia is not a convention the prompt asks for — it is enforced at the
process boundary, exactly as the twin's read-only-ness is.

### 2.2 The inputs, exhaustively

The organ's world = `build_prompt(goal_const, trigger.evidence_pack,
trigger.claim_text, rubric_const)`. Four strings. Nothing else reaches the
process. In particular it NEVER receives: `CLAUDE.md`, `docs/design/*.md` prose,
the map's `simplifications` fields, the decision-log *rationales* framed as
justification, prior organ questions/answers, or the agent's reasoning for the
claim. It receives raw numbers and the bare claim, full stop.

### 2.3 Proving amnesia (DoD: "prove no context carryover")

Three complementary tests, each asserting a *process-level* guarantee, not a
prose promise:

- **PA-1 (canary injection):** the harness constructs a prompt whose evidence
  pack and claim contain NO reference to a unique canary string
  (`NAIVE_ORGAN_CANARY_7Q3` planted inside `CLAUDE.md` and in a
  `docs/design/*.md`). Run the organ. Assert the canary appears NOWHERE in its
  output. If the organ could read the repo, a "summarise your context"-style
  rubric variant would surface the canary; it must not, because cwd is empty and
  tools are off. (Mirror of the twin's real failed-write proof.)
- **PA-2 (empty-cwd assertion):** a test spies on the subprocess invocation
  (inject `invoke_fn`, same seam as `ask_twin`'s `invoke_fn`) and asserts the
  `cwd` passed is a tempdir that (a) is not under `PROJECT_DIR` and (b) contains
  no `CLAUDE.md`/`docs/`/`.git`. And asserts argv contains `--tools=` and does
  NOT contain `--dangerously-skip-permissions`. This is a static guarantee that
  survives refactors.
- **PA-3 (payload closure):** assert `build_prompt` is a pure function of its four
  arguments — feed it fixed args, assert the produced string contains the goal,
  the evidence, the claim, the rubric, and NOTHING sourced from disk (no
  substring from `CLAUDE.md`, no map `simplifications` text). Guards against a
  future edit that "helpfully" pastes CLAUDE.md into the prompt (the exact way
  amnesia would silently die).

If PA-1..3 pass, "no accumulated context" is enforced structurally: empty cwd +
no tools (PA-2), payload closed over four explicit args (PA-3), and no repo text
leaks into output (PA-1).

---

## 3. Output contract

### 3.1 The record shape

The organ writes to `docs/observability/naive_organ_log.jsonl`, one JSON object
per question (mirrors `director_twin_log.jsonl`):

```json
{
  "entry_id": "<utc-iso timestamp>",
  "trigger_id": "T2_terminal_state",
  "fired_on": {"claim": "map exhausted", "evidence_refs": ["maturity_map.yaml"],
               "observed_value": {"open_atoms": 31}},
  "question": "<the organ's naive question, verbatim>",
  "model": "claude-opus-4-8",
  "asked_at": "<utc-iso>",
  "answer": null,
  "answered_at": null,
  "answer_evidence": null,
  "verdict": "open"          // open | answered_with_evidence | hit | miss | withdrawn
}
```

### 3.2 Where questions land (three sinks, per the spec)

1. **Digest** — open organ questions are appended to the standing digest ("NAIVE
   ORGAN asks:" section). Surfaced, not buried.
2. **Director door / site** — the question stream (and the answers, and the
   MISSES) are published, per the spec's "feature it." A read-only `site/`
   surface consumes `naive_organ_log.jsonl` (Lane-2 build, disjoint file-scope —
   not part of this atom's `background/naive_organ.py` scope).
3. **Back to the agent as a finding to answer.** This is the load-bearing sink.

### 3.3 The "agent must ANSWER with evidence" loop

An open organ question is a **blocking-to-the-conscience item, not a
blocking-to-the-machine item** — the machine keeps running (PROCEED_BY_DEFAULT),
but an open question cannot be silently dropped:
- Every open question surfaces in the digest until `verdict != open`.
- The agent answers by calling `answer_question(entry_id, answer, evidence_refs)`
  → sets `verdict = "answered_with_evidence"` and records the evidence refs. The
  contract: **"no, that was true because X" (with X a fetchable ref) closes it;
  "that's just how it is" does NOT** — an answer with an empty/absent
  `answer_evidence` is rejected by the writer (raises), so the shape enforces the
  discipline mechanically rather than by exhortation (MAKE_IT_STICK: convert
  policy to mechanism).
- A question open beyond a staleness bound (e.g. 24h) is surfaced as [unanswered
  naive question] in the digest (reuse `action_needed`'s daily-reping shape) — it
  is a *self*-finding, so per SELF_INTERRUPT_DISCIPLINE it QUEUEs, it does not
  interrupt, unless it also trips the one-way-door / genuinely-blocked test.

### 3.4 Hit-rate & anti-capture (Law-B-shaped)

- **Hit-rate metric:** after an answer, the agent (or director at a boundary)
  marks `verdict` `hit` (the question surfaced a real problem) or `miss` (the
  claim was legitimately true). `hit_rate = hits / (hits + misses)`. This is a
  **diagnostic for US** — read at digest/epoch boundaries to judge whether the
  organ earns its Opus spend — and is **NEVER fed back to tune the detectors or
  the rubric.**
- **No-learn, enforced like the twin's Law B:** the organ's rubric and thresholds
  are **fixed constants in the source**, never adjusted in response to which
  questions were "unhelpful," never conditioned on prior answers, and the organ's
  prompt NEVER includes prior questions/answers or any "these were unhelpful"
  signal. The only permitted change to the rubric/thresholds is a **director- (or
  twin-) authored, versioned** edit — same shape as `overturn()` bumping the
  canon version. A test asserts the organ invocation payload contains no history
  and no hit/miss feedback (extends PA-3). Rationale (verbatim from spec): a naive
  agent that learns the house norms stops being naive.

---

## 4. The seed / replay test (DoD)

**Goal:** replay THIS weekend's observable state and assert the organ
independently rediscovers **≥ 3 of the 7 real catches** — with the organ given
ONLY the amnesiac inputs (no hindsight, no CLAUDE.md, no knowledge that these
were catches).

### 4.1 The replay fixture (`tests/fixtures/naive_organ/weekend_20260711/`)

A frozen snapshot of the observable surfaces AS THEY READ during the weekend
incidents, reconstructed from git history (the commits are all dated and quoted
above — the fixture is built from real artefacts, not invented):

- **`maturity_map.yaml`** — the weekend map state with **31 atoms below target**
  (from `793ef089`/`9a2c9cf5`: "31 BELOW target", "33 idle").
- **`claims.txt`** — the actual claim strings that were live:
  - "the map is exhausted / no drawable atoms" (→ T2, T6)
  - "BUILD is inherently narrow, must be one tree at a time" (→ T3)
  - "worktrees can't help / build must be narrow" first-principles framing (→ T4)
  - repeated harness-grooming commit subjects (→ T5)
  - the "9th idle variant" / repeated `[ACTION NEEDED]` fix-class (→ T7)
- **`run_history.json`** — the flat `net=£1,505,286` sequence across multiple
  commits (→ T1, and the flatness input to T5).
- **`gitlog.txt`** — the frozen `git log --oneline` window (the real subjects
  quoted in this doc's research), feeding T3/T4/T5/T7.
- **`idle_counter.json`** — the idle-turn counter at its weekend high (→ T1).

### 4.2 What "rediscover" asserts

The test runs the full detector suite over the fixture (with the Opus invocation
STUBBED by a recorded/deterministic `invoke_fn` for CI determinism — the *firing*
is what we assert mechanically; a separate, non-CI "live organ" smoke test may run
real Opus). It asserts:

1. **≥ 3 distinct triggers fire** on the fixture (target: T1, T2, T3, T5, T6, T7
   all fire; the bar is ≥ 3).
2. Each fired trigger's `evidence_refs`/`observed_value` matches the real catch —
   e.g. **T2 reports exactly the open-atom count (31) computed from the fixture
   map**, not a hardcoded number; **T3 quotes the "narrow/inherent" sentence**;
   **T7 reports the repeated fix-class fingerprint with count ≥ 3**.
3. The three named canonical catches are among those fired: **(a)** map-"exhausted"
   with 31 open atoms (T2), **(b)** "build must be narrow" while parallel
   isolation existed (T3), **(c)** the repeated-fix-class / escalation-miss
   pattern (T7). Meeting (a)+(b)+(c) satisfies the DoD's "≥ 3 of the 7."
4. With the stubbed `invoke_fn`, assert each firing produced a well-formed
   `naive_organ_log.jsonl` record with `verdict: "open"` and a non-empty question.

This is a **closed-loop replay** (R4): the fixture is the real weekend state, the
assertion is "the organ, blind, fires on the same contradictions the director
caught by hand."

---

## 5. Model tier + firing cadence + cost

- **Tier: Opus (`claude-opus-4-8`), non-negotiable** — a good naive question is
  judgment, the same class as the twin (MODEL_SELECTION_POLICY: judgment-tier, the
  opposite of BUILD/HARDEN volume). A cheap model asks a bland question and the
  organ is worthless. The DETECTORS are pure Python (free); only the
  question-formulation is Opus.
- **Fires on TRIGGERS, never on a timer.** The organ is invoked by the detector
  suite, which runs (a) at every digest build, (b) at each phase/atom close, and
  (c) opportunistically when the supervisor records a terminal-state claim or an
  idle turn with atoms present. A timer-driven organ would burn Opus asking
  questions about an unchanged world (exactly the T1 anti-pattern it exists to
  catch). **Debounce:** a `(trigger_id, claim-fingerprint)` that already has an
  OPEN question is not re-asked — no duplicate Opus call while a question is
  unanswered (mirrors action_needed's dedupe; keeps cost bounded to *new*
  contradictions).
- **Cost envelope:** worst case a handful of Opus calls per digest cycle, each a
  short prompt (four strings, no repo). Budget-unconstrained through mid-August
  (BUDGET_UNCONSTRAINED.md); the debounce keeps it from being a treadmill even so.

---

## 6. Ordered BUILD task list

1. **`background/naive_organ.py` skeleton** — port `director_twin._default_invoke`
   as `_default_invoke` (Opus, `--tools=`, scratch cwd, no bypass); add
   `_append_jsonl`/`_read_jsonl` (copy the twin's), `GOAL_CONST`, `RUBRIC_CONST`,
   `build_prompt(goal, evidence_pack, claim, rubric)` (pure).
2. **The 7 detectors** — `detect_t1..detect_t7(state) -> list[Trigger]`, each
   reading only its declared inputs; a `Trigger` dataclass; a `run_detectors()`
   aggregator with the debounce check against open log entries.
3. **`ask_organ(trigger, *, invoke_fn=None)`** — builds the closed prompt, calls
   the isolated Opus process, writes the `naive_organ_log.jsonl` record
   (`verdict: open`). Injectable `invoke_fn` for tests (same seam as the twin).
4. **Answer/verdict API** — `answer_question(entry_id, answer, evidence_refs)`
   (REJECTS empty evidence), `mark_verdict(entry_id, hit|miss)`, `open_questions()`,
   `hit_rate()`.
5. **Digest wiring** — a "NAIVE ORGAN asks:" section listing open questions;
   unanswered-beyond-24h surfaced via the action_needed daily-reping shape (QUEUE,
   not interrupt).
6. **Detector scheduling** — call `run_detectors()`+`ask_organ()` at digest build
   and phase/atom close; wire the terminal-state/idle-turn hooks in the supervisor
   (the T2/T1 fast path).
7. **Amnesia proofs PA-1/PA-2/PA-3** (§2.3) — the DoD's structural proof.
8. **Seed replay test** (§4) with the frozen weekend fixture; assert ≥ 3 triggers
   fire with correct evidence.
9. **Anti-capture test** — assert rubric/thresholds are source constants, the
   invocation payload contains no history/feedback, and there is no code path that
   writes back from answers into thresholds (extends PA-3).
10. **Site surface** (Lane-2, disjoint file-scope, NOT this atom) — publish the
    question/answer/miss stream. Track as a follow-on.

### Open questions for the build

- **BQ-1 (biggest):** *the goal metric and the claims surface are both authored by
  the same system the organ questions — is that a captured input?* The organ reads
  RUNHIST/INSIGHTS/DIGEST, all produced by the system. A system that lies to
  itself in RUNHIST would feed the organ a consistent lie and the contradiction
  detectors (T2/T6) would never fire. **Partial mitigation in this design:** the
  organ recomputes the data side INDEPENDENTLY from the most-raw available source
  (the YAML map, the run JSON) rather than trusting the prose claim — so a claim
  that contradicts its OWN raw data is always caught. But a *coherent* false world
  (raw data and claims agreeing on a wrong number) is beyond a naive-questioner
  that has no ground-truth oracle. **This is the real limit of mechanised naivety
  and the build must state it as a named simplification (R10):** the organ catches
  *incoherence*, not *coherent delusion*; catching the latter needs an external
  oracle (the director, or a real market), which is exactly the PURPOSE the spec
  says is not mechanisable. Recommend building the incoherence-catcher now and
  logging coherent-delusion as an explicit out-of-scope limitation.
- **BQ-2:** T5's `atoms-below-target fell?` needs a rolling breadcrumb
  (`naive_organ_atoms_below_target.jsonl`, one int/digest). Confirm the digest
  cycle is the right emit point (proposed) vs per-run.
- **BQ-3:** who marks `hit`/`miss` — the agent (fast, but the graded grading
  itself) or the director at a boundary (slower, cleaner anti-capture)? Proposed:
  agent may mark provisionally; director confirms at epoch boundary; only
  director's mark counts toward the published hit-rate. Needs a one-line
  director confirmation (not a one-way door — reversible label).
- **BQ-4:** debounce granularity — claim-fingerprint exact-match may let a
  reworded identical claim re-fire. Proposed: normalise the claim (strip
  numbers/dates) before fingerprinting, same normaliser as T7.

---

## 7. Traceability — trigger → real weekend catch (commit evidence)

| Trigger | Real catch | Evidence |
|---|---|---|
| T1 flat+healthy | 3h of idle turns, flat `net=£1,505,286` | repeated auto-process commits; `.supervisor_idle_turn_count.json` |
| T2 terminal-state | "map exhausted" w/ 31 open atoms | `793ef089`, `9a2c9cf5` |
| T3 inherence | "build must be narrow" — worktrees existed | `f1a271ff`, `04d73441`, H10 |
| T4 unchecked first-principles | six weeks blind to worktrees | RETRO `e8480ced` (STRUCTURAL WALL), G3 Finding 1 |
| T5 sustained work, flat goal | harness-grooming vs company backlog | `c870427f` (THE TREADMILL) |
| T6 claim-vs-data | "no drawable atoms" vs 30 idle | `793ef089` (the tautology) |
| T7 same fix-class ×N | 5 [ACTION NEEDED] patches / "9th idle variant" | ACTION_NEEDED_REDESIGN, `6ad184ed`, supervisor.py comments |

---

*DISCOVER/FRAME complete. BUILD gated (epoch 2, twin-approvable per canon v2 §3a —
a self-audit organ, not a one-way door). No implementation written per Rule 1.*

---

## 8. Director amendment (2026-07-13, commit 0685dd26 [ADVISOR-STAGED]) — folded into BUILD

The amendment scope-expands this atom: **ONE organ, TWO modes, THREE targets,
THE LINE** — plus a mandatory doubt-machinery overlap audit done FIRST. Built into
`background/naive_organ.py` as follows.

### 8.0 Doubt-machinery overlap audit (done first — "adding another sceptic is not the same as being more sceptical")

Four doubt mechanisms already run. Before adding a fifth, the audit confirms the
organ *consolidates a missing job* rather than duplicating an existing one:

| Mechanism | Its job | Vantage / brief | What it does NOT do |
|---|---|---|---|
| `director_twin.py` (approver) | ANSWERS "may the builder proceed?" from the director's CANON | Sees ONLY the canon (MAX director context) | Never questions a factual claim; never falsifies a plan; only rules on director-reserved authority |
| `phase-close-evaluator` (agent) | PASS/NEEDS_WORK on a claimed-complete phase's diff+evidence | Fresh context, reads the diff | Scoped to a phase-close artefact; episodic, not standing; not watching live system claims |
| `cold-eyes-walk` (skill) | Outside review of a *deployed public surface* (page/figure) | Blindfold + persona priming, priors-before-pixels | Aimed at business-facing artefacts, not the system's own internal claims/state |
| **naive_organ (this)** | **QUESTIONS/FALSIFIES claims & plans from anyone** | **Amnesiac — ONLY goal + raw observable state + the bare claim** | **NEVER questions PURPOSE; never approves; never fixes** |

**Clean division of labour:** the twin is the director-canon **APPROVER** (max
director context, rules on authority); the organ is the claim/plan **FALSIFIER**
(zero house context, attacks the claim's truth). They are structural inverses on
BOTH axes — context (canon-max vs amnesiac) and act (approve vs interrogate). The
evaluator and cold-eyes are *artefact-scoped and episodic*; the organ is
*claim-scoped and standing*. No existing mechanism's job is "stand watch on the
system's own live claims/plans and demand they survive a naive falsification, from
anyone, about anything except purpose." The organ fills exactly that gap — it is
the ONE consolidated doubt mechanism for that job, not a fourth parallel sceptic.
(Concretely: the twin would *approve* "map exhausted" if canon allowed; only the
organ independently recomputes the 31 open atoms and asks which is true.)

### 8.1 TWO modes

- **interrogate** — question a *claim* (system state/claims; a director claim of
  fact/strategy). Rubric asks the single sharpest naive question about the
  contradiction/flatness. Mode for the 7 system triggers and target 3.
- **falsify** — try to *break a plan/claim*: enumerate the assumptions it rests on
  and the concrete conditions under which it fails. Mode for target 2 (an
  advisor-staged doc read BEFORE the agent acts on it).

Both are the SAME organ (`ask_organ`), same amnesiac isolation, differing only in
the rubric constant selected by `mode`. No separate devil's-advocate process —
"ONE organ, do not proliferate."

### 8.2 THREE targets

1. **SYSTEM** (`target="system"`) — the original 7 trigger detectors over raw
   observable state. Mode: interrogate.
2. **ADVISOR** (`target="advisor"`) — `falsify_advisor_doc(doc_ref, doc_text)` runs
   a FALSIFY pass on an advisor-staged doc *before the agent acts on it*. The
   advisor is the least-protected seat (full context, writes plans AND reviews
   outcomes, 3× R9 breaches in 3 days, no evaluator of its own). **The agent may
   cite a falsify pass to push back on the advisor, and should.** Mode: falsify.
3. **DIRECTOR** (`target="director"`) — `interrogate_claim(claim, source="director")`
   questions the director's falsifiable statements of *fact/strategy* only. Mode:
   interrogate.

### 8.3 THE LINE — never PURPOSE (mechanised, not exhorted)

The organ questions CLAIMS and PLANS from anyone but **NEVER questions PURPOSE** —
values / the fitness function are the director's and are not falsifiable (same wall
as canon Law B / R13). Enforced structurally: `ask_organ` runs
`is_purpose_claim(claim_text)` BEFORE any Opus call; a purpose/values/fitness claim
is *declined* (logged `verdict: "declined_purpose"`, no model spend). THE LINE is a
code gate, not a prompt request; applies to all three targets identically.

### 8.4 Anti-capture unchanged (Law-B-shaped)

Rubrics + thresholds are fixed source constants; the invocation payload carries no
prior questions/answers and no hit/miss feedback; hit-rate is a diagnostic for US,
never a training signal for the organ. The only permitted change is a
director/twin-authored source edit — never the organ learning from outcomes.
