# Self-measurement, director axes, and the always-drawable lane — unified design + propose-back

**Serves:** `DIRECTOR_STEER_SELF_MEASUREMENT_AND_AXES_2026-07-22.md`. Goal in the director's words:
**stable, autonomous, continuous, parallel velocity.** The intent is the wall; the mechanism is mine
to design (his words: *"make sure it has some say… it sees more than you"*). This is the first-pass
response: the propose-back (§45 a/b/c), the unified shape reusing existing organs, the first
hand-computed daily-note seed, and the decomposition of the contract-touching builds.

---

## 0. What landed THIS pass (additive / reversible — the steer green-lit "just do them")

- `docs/design/DIRECTOR_AXES.md` — v1 axes file (§4), director-owned, wiring-severed.
- This document — propose-back + unified design + first daily-note seed (§1 worked instance below).

**Not touched this pass** (correctly deferred — contract-touching or map-owned):
- The always-drawable **draw wiring** (§3) — touches `supervisor.py`'s draw; R15-prove core preempts
  discovery before it lands. Decomposed as an atom below; not written from a worker tick.
- The daily-note **automation** (§1) and the **twin pre-score / advisor column** wiring — decomposed
  as atoms below. Registering them in `maturity_map.yaml` is a sole-map-writer act (THREE_LANES);
  proposed here for the orchestrator/twin to open, not self-added.

---

## 1. The daily self-note — reuse, don't accrete (OPERATIONAL_COHERENCE)

The steer's §1 asks for one computed note: verified autonomous hours, longest stall + honest cause,
one proposed fix, with the token/rate-limit resource inputs folded in as the "input half."

**Reused organs (no new parallel measurement layer — the steer's own §13 anti-gaming principle):**
- **The gates ARE the anti-gaming layer.** "Verified" = passed the existing level gate
  (`is_valid_level_up` / `gate_authorizations.jsonl`), epistemic verifier, and test suite. No parallel
  verifier.
- Origin commit history + `gate_authorizations.jsonl` → the numerator (verified work landing).
- `deadmans-switch-log.md` commit-clock + `decision_log.jsonl` → stalls and their causes.
- `director_input_log` / staging arrival times → "without director input in the prior hour."
- **`rate_limits` sensor** (confirmed available, Claude Code v2.1.215, subscription auth; unwired —
  `DIRECTOR_AMENDMENT_TOKEN_RESOURCE_DIMENSION` step-zero result) → the input half. Fold the two
  parked steers (TOKEN_RESOURCE_DIMENSION, HEARTBEAT_TOKEN_BURN) in HERE as the resource inputs, per
  the steer's explicit instruction not to leave three competing measurement designs.

**One honest definition of "verified autonomous hours" that resists the obvious mislead (see §3b):**
count only commits that (a) move a gate-backed `level_current`, OR (b) land new capability/tests, OR
(c) change a headline figure *with its clock* — and **explicitly EXCLUDE mechanical-republish commits**
(diff touches only `docs/reports/**`, `docs/status/LATEST.md`, `site/data/**` and leaves net/EV
unchanged). Without this exclusion the auto-process treadmill (a commit every ~15 min republishing an
unchanged £1,521,070) reads as 24h of autonomy when zero capability moved. This exclusion is the
single most important honesty decision in the whole note.

## 1a. FIRST DAILY-NOTE SEED (v0, hand-computed from real disk/git — 2026-07-22 ~07:00 BST)

_Manually computed as the worked instance the steer asked to see in the first pass; the automation
below replaces it. Numbers are from origin + ledgers this morning, labelled observed vs inferred (R9)._

- **Verified autonomous hours (prior ~12h overnight window):** ≈ **0** _(observed)_. Origin shows
  ~50 commits in the window, ALL `Auto-process run complete` mechanical republishes with net unchanged
  at £1,521,070 — none move a level or land capability. The last capability/level commits were
  2026-07-21 daytime (W1_5→L3 `f4f417297`, C13→L3, the `diagnose_map_blocked_set` classifier
  06:09/06:43/13:57). So overnight: full pipeline liveness, **zero verified product progress.**
- **Longest stall and its cause:** **~12.3h** _(observed — commit-clock 738 min at 05:59 UTC)_,
  classified **authority-gated + stranded-awaiting-grant** _(inferred from ledger + map state)_: every
  top build atom sits behind a director-console wall — W1_4 L2→L3 coupled-triad (director-reserved,
  no W1 company twin registered), W1_8 (`schema_sim_structure` gate + R13 zonal curriculum), SITE1
  (director re-Expert-Hour). Plus the `cwd-fix` worktree orphaned/stranded (deadman: 1 orphaned fork
  never merged home). This is precisely the failure class the steer names: *"work stalls when finished
  work awaits a grant."*
- **One proposed fix (class-level, R10):** build the **always-drawable discovery lane (§3)**. Had it
  existed overnight, the authority-gated draw would have fallen through to F1–F5 forward-discovery
  instead of resting 12h — turning ~12h of stranded rest into optional forward research that yields
  instantly when a grant arrives. This is the steer's own §3; the overnight evidence is its business case.

## 1b. Automation (decomposed atom — see §4 SM1)

A `background/daily_self_note.py` computing the above from the reused organs, publishing to the site +
NTFY digest, fail-closed if a source is missing (an unavailable input is a red, not a silent zero —
R15). Definitions are ledger-governed: changing what a number MEANS is a director-ratified edit, not a
quiet code change.

---

## 2. HARD LAW — carried verbatim

No scorecard number feeds draw priority, reward, selection, scheduling, or any optimisation
mechanically. The note is read by reasoning entities only. Honest reds are CREDITED in the retro
(the C13 wind-chill negative-CWV finding is the culture; concealment is the perverse incentive). This
is enforced structurally: the note writer has no path into the draw; the draw never reads the note.

---

## 3. The always-drawable lane (contract-touching — sequence + R15-prove)

Wire the forward-discovery register (F1 conversations, F2 plain-language, F3 volunteer mechanics, F4
international, F5 competitor field — `COMPETITOR_FIELD_FRAME.md` etc.) as the **OPTIONAL standing
fallback lane**, reusing the CORE/OPTIONAL entitlement classes already designed in
`RESOURCE_AWARE_SCHEDULING_PROPOSAL` (+ its token amendment). Draw order:

1. CORE below-target build (unchanged, always preempts).
2. CORE DISCOVER/FRAME on idle/gated atoms (unchanged).
3. **NEW — OPTIONAL forward-discovery (F1–F5)** — drawn ONLY when 1+2 are empty/gated AND token
   headroom is above threshold (sensor from §1). Yields instantly to any CORE arrival (spot-instance).
4. Rest — legitimate ONLY when 1+2 gated AND the F1–F5 backlog is genuinely empty (rare by construction).

**R15 obligations before this lands (the steer's own condition):**
- A mutation proving a below-target CORE atom ALWAYS preempts an in-flight OPTIONAL draw (core-preempts).
- A mutation proving a stale/missing token sensor withholds ONLY OPTIONAL and never stops CORE
  (headroom is a DIAL not a WALL — TOKEN_RESOURCE_DIMENSION §5, fail-closed one direction only).
- A mutation proving the OPTIONAL lane cannot draw product/harness *build* work (it is discovery/
  research only — the draw-mix balance still binds; no harness-polish loophole).

---

## 4. Decomposed atoms (proposed for the sole map-writer / twin to open — NOT self-added)

- **SM1 — daily self-note automation** (§1b). Additive, own commit, narrow/reversible. DISCOVER/FRAME
  workable now; BUILD when opened. Deps: none hard (rate_limits sensor optional, fail-closed without it).
- **SM2 — rate_limits token-headroom sensor** (folds TOKEN_RESOURCE_DIMENSION §3 + HEARTBEAT_TOKEN_BURN
  measurement req). Additive disk-snapshot writer reading the statusline payload, fail-closed on
  staleness. Note: HEARTBEAT_TOKEN_BURN's *rest-cost* concern is already RESOLVED by the scheduled-
  invocation cutover (rest = no process = ~0 tokens); SM2 is now only about OPTIONAL-lane headroom
  gating, not rest cost. Mark that steer's rest-cost half resolved when SM2 lands.
- **SM3 — always-drawable OPTIONAL discovery lane** (§3). Contract-touching; the three R15 mutations
  are its exit test. Sequence AFTER SM2 (needs the headroom read) but the draw-fallthrough can land
  first with headroom-gating stubbed to "always allowed."
- **SM4 — twin axis pre-score + verdict ledger** (§4/DIRECTOR_AXES.md verdict loop). Extends the
  twin's §3a role; logs a prediction before each director verdict; Law B preserved (no canon update).
- **SM5 — advisor's column** (§5): computed from origin facts only — advisor false-status calls
  (claim contradicted by origin), staged docs that needed a clarification loop, stalls on an empty
  pre-staged queue. Machine computes evidence; director scores. Additive.

---

## 5. Propose-back — my say (steer §45)

**(a) Wrong shapes / reuse / thrash risks I can see from inside:**
- **Reuse, don't build a parallel verifier.** The gates already decide "verified"; the note must read
  their verdicts, never re-adjudicate. A second verifier would drift from the first and become theatre.
- **The auto-process treadmill will corrupt "verified hours" unless republish commits are excluded**
  (§1). This morning's data is the proof: 50 commits, 0 capability. Without the exclusion the number
  lies in the flattering direction — the worst kind.
- **HEARTBEAT_TOKEN_BURN is already substantially resolved** by the scheduled-invocation migration I'm
  running under; folding its full text in as open work would re-litigate a solved problem. Fold only
  its *measurement* half (per-hour resource cost) into SM2; mark the rest-cost half resolved.
- **Coherence:** four docs already touch scheduling (RESOURCE_AWARE_SCHEDULING_PROPOSAL,
  FAN_WIDENING_SAFETY_CASE, PARALLEL_LANES_PROPOSAL, H20). SM3 must extend the first, not spawn a
  fifth — the director's standing complaint about "stages creating forks in its guidance."

**(b) Metrics that will mislead / invite gaming despite §2's severed wiring:**
- **"Verified autonomous hours" as a maximand** — even severed from the draw, an agent authoring its
  own retro is tempted to split work into more commits, or to prefer easy ungated work over hard
  director-gated work (which zeroes the clock). *Mitigation:* the number is machine-computed (agent
  narrates, doesn't compute); and honest-red credit (§2) must visibly reward surfacing a stall, so
  choosing the hard gated path is never punished by the scorecard.
- **Twin pre-score → director verdict** risks the twin learning to predict what the director wants to
  hear (Law B violation). *Mitigation:* the prediction is logged read-only and NEVER updates canon;
  the gap is a diagnostic, not a training signal. Canon changes only by director overturn.
- **Advisor's column** is computed by the machine the advisor steers — conflict of interest.
  *Mitigation:* origin-facts-only (false-status = claim provably contradicted by origin); the machine
  computes evidence, never editorialises; the director scores.

**(c) What I'd measure that hasn't been named:**
- **Authority-gated-hours ÷ drained-hours ratio (weekly).** Splits "stalled because everything
  drawable is behind a director wall" (fix: a grant, or SM3) from "stalled because nothing is left"
  (fix: more atoms). This is the number that directly answers the director's own *"why am I the
  bottleneck?"* — it is the MAKE_IT_STICK anti-decay metric (turns waiting on a human, target zero)
  made visible. This morning it would read ≈100% authority-gated — a clear, actionable signal.
- **Republish-to-capability commit ratio.** How much of origin churn is mechanical republish vs real
  capability. A high ratio is productivity theatre; surfacing it stops the treadmill reading as progress.
- **Wall re-draw churn.** How often the supervisor re-draws a freshly-walled atom (a known DIAL
  defect). Counts wasted ticks — cheap to compute from the draw log, and it targets exactly the
  "re-churn a walled atom" waste already seen.
