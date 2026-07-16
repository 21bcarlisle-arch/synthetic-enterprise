# G4 — Unified Failure Register (FRAME)

**Atom:** `G4_unified_failure_register` (lane G_data_learning, dial 3, level 0→target 3)
**Stage:** FRAME only (doc-only fork; no code, no maturity_map.yaml edit, no git). L0→L1 per this doc.
**File scope declared for future BUILD:** `docs/retrospectives/`, `tools/`, `tests/`.

Sources actually read while writing this doc (cited inline below, not invented):
`CLAUDE.md` (R3/R9/R10/R15 text), `docs/retrospectives/2026-07-04-verification-week.md`,
`2026-07-08-wake-doorbell-third-strike.md`, `2026-07-09-doorbell-failure-5-busy-regex.md`,
`2026-07-13-tmux-injection-two-strikes.md`, `2026-07-13-stale-running-code-second-occurrence.md`,
`2026-07-14-evaporated-director-decision.md`, `2026-07-14-tmux-injection-third-strike-and-fail-silent-deadman.md`,
`docs/observability/action_needed_register.json` (existing register precedent, dict-of-items with
`resolved`/`first_asked_at`/`last_pinged_at` fields), `docs/observability/naive_organ_log.jsonl` and
`docs/observability/test_execution_log.jsonl` (existing append-only JSONL precedents),
`tools/generate_method_data.py` and `site/data/method.json` (the Method door's existing R1–R6 +
retro-library rendering, which this atom extends rather than replaces).

---

## 1. Problem statement

CLAUDE.md's R3 reads: *"Two-strike redesign: a second false completion claim on the same
component means eliminate/redesign the mechanism, not patch it again."* As written and as
actually operated, "same component" is the unit of counting, and the counting is a human (or
this agent) noticing in the moment, not a mechanical tally. Both halves of that are named
gaps in the retros themselves:

- **Per-component counting missed a per-CLASS repeat that was hiding across components.**
  The tmux-injection saga (`2026-07-13-tmux-injection-two-strikes.md`) correctly fired R3 on
  its third strike — but only because all three strikes happened to hit the *same* pane-busy-
  detection code path in a five-day window someone was actively watching. The wake-doorbell
  saga one week earlier (`2026-07-08-wake-doorbell-third-strike.md`) is the SAME failure
  class — a shared safety primitive (`send_keys_when_idle`/idle-gating) partially migrated,
  with at least one caller left on a raw, unguarded write — recurring in a *different*
  component (`session_watchdog.py`'s autoloop nudge vs. its own `check_session_usage()` vs.
  `_relay_inbound_command()`). That retro explicitly lists the still-open sibling call sites
  as "registered in PRIORITIES.md backlog... to avoid it being silently dropped again" —
  which is exactly the human-vigilance dependency R3 is supposed to remove. The class fired
  again anyway, a THIRD time, six days later, as a 6-hour blackout
  (`2026-07-14-tmux-injection-third-strike-and-fail-silent-deadman.md`, root cause A: yet
  another raw, unguarded `subprocess.run(["tmux","send-keys",...])` call site,
  `check_session_usage()`, never migrated). Three components, one failure class
  ("shared-primitive bypass — a caller left on the unguarded path"), and R3 only ever fired
  by luck of a human tracing the pane-injection thread specifically, not because the class
  was being counted.
- **"Committed != running" (R2) recurred as a *named*, self-aware repeat and still took a
  human noticing the symptom twice.** `2026-07-13-stale-running-code-second-occurrence.md`
  states this directly: *"This is the identical class already found once before, named
  directly in `background/health_check.py`'s own pre-existing docstrings... That manual fix
  held for exactly one incident before recurring."* The retro's own "class-level lesson"
  section says the fix (a real automated check) was needed precisely *because* the manual
  instance-fix "relied on someone noticing the symptom and correctly diagnosing the cause
  each time." No register existed to have made the second occurrence a mechanical alarm
  instead of a second manual catch.
- **A decision-delivery failure and an alarm-liveness failure are the same class under
  different skins, and nothing said so at the time.** `2026-07-14-evaporated-director-decision.md`
  names this explicitly: *"A director decision that evaporates unnoticed is its own defect
  class — decision delivery needs the same landed-verification as alarms and injections... the
  shared lesson is landed-verification, not the specific channel."* That retro had to
  re-derive the connection to the deadman's-switch fail-silent finding and the tmux
  injection-log work by re-reading them — there was no index that already tagged all three
  as `landed-verification-gap` and could have surfaced the pattern the FIRST time, not the
  third.

**The mechanism gap, stated plainly:** R3's "Nth strike" is currently a property computed
implicitly, per human attention span, over whichever single component someone happens to be
tracing. It needs to be a property computed **mechanically, globally, per failure CLASS**,
so that strike 2 of a class — regardless of which component it lands on next — is a named,
surfaced, alarm-worthy event the moment the second entry is appended, not a pattern a retro
notices in hindsight.

This is squarely R10 territory too (*"An absurdity-class defect may NOT be closed with an
instance fix. Closure requires extending the invariant library... so the entire class fails
automatically"*) applied to the retro/incident-tracking practice itself, not to a simulation
invariant.

---

## 2. Failure-class taxonomy

Classes are derived from the actual retros above, not invented in the abstract. Each class is
a short, stable tag (`kebab-case`), a one-line definition, and the retros that instantiate it.
The taxonomy is **open** — a new occurrence may introduce a new tag, but an occurrence must be
checked against *existing* tags first (fuzzy match on description + component keywords) before
minting a new one, or every occurrence looks novel and the counter never accumulates.

| tag | definition | instances observed |
|---|---|---|
| `shared-primitive-bypass` | A safety/gating mechanism was hardened or introduced, but at least one caller was left on (or reverted to) the old unguarded path, and that caller later fails the same way the primitive was built to prevent. | wake-doorbell strike 3 (`session_watchdog` autoloop, unmigrated); tmux-injection third strike (`check_session_usage`, unmigrated); the same retro's own "still open" `_relay_inbound_command` finding |
| `committed-not-running` (maps directly to R2) | A code fix lands in git/is tested, but a long-running process that embodies the old behaviour is never restarted, so the fix is inert in practice. | verification week (session watchdog claimed fixed twice while stale); `2026-07-13-stale-running-code-second-occurrence.md` (supervisor + session-watchdog + ntfy-responder all found stale simultaneously) |
| `external-state-misdetection` | Logic infers a foreign system's state (an idle/busy TUI pane, a scroll position) from a fragile pattern/heuristic rather than an invariant, and the foreign format/state shifts out from under the pattern. | doorbell failures #1 (pattern-list), #4 (supervisor rebuild), #5 (busy-spinner regex vs. Claude Code's own persistent checklist UI); tmux-injection strikes 1–2 (spinner regex twice wrong) |
| `landed-verification-gap` (a.k.a. fire-and-forget) | A signal (alarm, decision, injected instruction) is confirmed SENT but never confirmed RECEIVED/APPLIED by its intended destination, so a genuine failure to land is indistinguishable from success. | evaporated director decision (07-14); implicitly, every wake-doorbell failure before `send_keys_when_idle`'s read-back verify existed |
| `fail-silent-self-referential-monitor` (R15's FAIL-SILENT pattern, concretely instantiated) | A watchdog's own liveness/staleness signal can be refreshed by the watchdog (or a sibling daemon) itself, so the thing meant to detect "nothing is happening" can never fire while daemons are merely breathing but not working. | deadman's-switch 6-hour blackout, root cause B (`2026-07-14-tmux-injection-third-strike-and-fail-silent-deadman.md`) |
| `false-completion-claim` (maps directly to R1) | An artifact is asserted done from the producer's own view without the external consumer's fetch confirming it; producer and consumer diverge. | verification week's founding cluster (PROJECT_STATE.txt stale-to-advisor, session watchdog twice) |
| `control-tautology-or-fail-open` (R15's TAUTOLOGY/FAIL-OPEN patterns) | A control's checked value is derived from the same source it's meant to verify, or the control passes silently on missing/zero/malformed input. | named as doctrine in R15/`CONTROLS_THAT_CANNOT_FAIL.md` (not yet instanced in a dedicated retro read for this doc — flagged as a class to seed the register with from that doc's own findings at BUILD time, not fabricated here) |

Tagging is **many-to-one per occurrence is allowed but discouraged** — pick the primary class;
a genuinely dual-class incident (e.g. the third tmux strike is both `shared-primitive-bypass`
and, via its deadman finding, `fail-silent-self-referential-monitor`) gets **two register
entries**, one per class, linked by the same `retro_link` and `component`, because each class's
strike-count must accrue independently (that IS the point of per-class counting: the deadman
half of that incident is strike 1 of its own class, not strike 3 of the bypass class).

---

## 3. Register schema (append-only)

**Store form:** `docs/retrospectives/failure_register.jsonl` — one JSON object per line,
append-only, matching the two existing JSONL precedents in this repo
(`docs/observability/naive_organ_log.jsonl`, `docs/observability/test_execution_log.jsonl`).
Chosen over a JSON dict (the `action_needed_register.json` pattern) because that register's
shape is *mutate-in-place-by-key* (an item resolves, its `resolved` flag flips) — the wrong
shape here, since a failure register's whole value is that no entry is ever edited after the
fact; append-only is the property that makes "Nth entry of a class" a stable, replayable count
(also consistent with C-S2's idempotent/deterministic-replay discipline in CLAUDE.md, applied
here to the register itself rather than sim state).

Per-line fields:

```jsonc
{
  "id": "FR-2026-07-14-001",              // FR-<date>-<seq>, monotonic per day, assigned at append time
  "date": "2026-07-14",                   // date of the retro/incident, not append time
  "component": "background/session_watchdog.py::check_session_usage",
  "class_tags": ["shared-primitive-bypass"],   // >=1 tag from the taxonomy in §2; may propose a new tag
  "retro_link": "docs/retrospectives/2026-07-14-tmux-injection-third-strike-and-fail-silent-deadman.md",
  "one_line": "check_session_usage() fired /usage via raw unlocked tmux send-keys, bypassing the gated relay every other caller was migrated to.",
  "rule_forged_or_reaffirmed": null,       // e.g. "R3" if this occurrence is the one that forged/reaffirmed a numbered rule; null otherwise
  "prior_strikes_same_component": 2,       // informational only — the OLD per-component count, kept for continuity with existing retro prose
  "written_by": "tools/failure_register.py append (or manual, at retro-close time)"
}
```

Design notes:
- `class_tags` is the field the global counter reads. A single occurrence may legitimately
  carry more than one tag (see §2's dual-class note), in which case it counts toward BOTH
  classes' strike totals — this is intentional, not double-counting, because each class is an
  independently-tracked defect lineage.
- No field is ever mutated after append. A correction (wrong tag, wrong retro link) is filed as
  a NEW entry with a `supersedes` field pointing at the wrong one, never an edit-in-place — the
  same discipline the register itself exists to enforce elsewhere (an append-only history you'd
  quietly rewrite is not append-only).
- Entries are written at **retro-close time** (the existing `incident-retro` skill's own
  closing step gains one more action: append a line here), not invented retroactively for old
  incidents in bulk by this FRAME doc — backfilling the ~10 existing retros read above into the
  register is explicitly a BUILD-time task (§7), not something this design doc performs, since
  it is real product-adjacent-data authorship, which FRAME may not do.

---

## 4. Global per-class strike counter

`tools/failure_register.py::count_strikes(class_tag: str) -> int` — a pure function over the
JSONL file: read every line, count entries whose `class_tags` contains `class_tag`, return the
count. No per-component grouping, no windowing, no decay — a class's strike count is simply
"how many times has this ever happened, anywhere in the codebase, ever," which is exactly what
R3 needs and exactly what per-component counting was failing to give it.

**Mechanical alarm rule:** on every append, recompute `count_strikes()` for each tag on the new
line. If the resulting count is **>= 2** for any tag, emit an `[R3-ALARM]` finding (same shape
as the existing `action_needed_register` / `[ACTION NEEDED]` idiom already used elsewhere in
this codebase) naming: the class tag, the count, every prior `retro_link`+`component` sharing
that tag, and the literal R3 sentence from CLAUDE.md. This alarm is the mechanism that makes
"second strike fires the redesign mandate" true by construction rather than by someone
re-reading old retros and noticing a pattern (which is what actually happened for all three
examples in §1 — after the fact, not at the moment the second entry existed).

The alarm is **advisory, not blocking** — per Rule 0 / PROCEED_BY_DEFAULT, it never halts BUILD;
it registers a finding (SELF_INTERRUPT_DISCIPLINE: queue it, don't stop the world) that the next
digest / phase-close surfaces. Concretely: `[R3-ALARM] class=shared-primitive-bypass count=3 —
CLAUDE.md R3 mandates eliminate/redesign, not a fourth patch. Prior: FR-2026-07-08-00X
(session_watchdog autoloop), FR-2026-07-14-00Y (check_session_usage), FR-2026-07-14-00Z
(_relay_inbound_command, if filed). See <retro_links>."

---

## 5. Surfacing on the Method door

`site/data/method.json` already renders (per `tools/generate_method_data.py`, read above) a
static `rules` list (R1–R6 with the incident that forged each) and a filesystem-computed
`retro_library` list (title/date/size/path per file in `docs/retrospectives/`). This atom adds
one more computed section, `failure_register_summary`, alongside those two — same generation
pass, same "computed fresh from the filesystem at generation time" discipline the module's own
docstring already states for the staging-loop/retro-library sections:

```jsonc
"failure_register_summary": {
  "total_entries": 11,
  "classes": [
    {"tag": "shared-primitive-bypass", "strike_count": 3, "alarm": true,
     "latest_retro": "docs/retrospectives/2026-07-14-tmux-injection-third-strike-and-fail-silent-deadman.md"},
    {"tag": "committed-not-running", "strike_count": 2, "alarm": true, ...},
    {"tag": "external-state-misdetection", "strike_count": 4, "alarm": true, ...},
    ...
  ],
  "generated_at": "2026-07-16T00:00:00Z"
}
```

This is **non-blocking presentation only** — the Method door is a read-only public artifact
(per R11, "done" for a user-visible change means fetching the live page); the register/alarm
mechanism in §4 is independent of whether the Method door happens to be regenerated that
minute. `generate_method_data.py` already has a clean seam for this (it reads `RETRO_DIR`
directly; `count_strikes()` reads the same directory tree by convention, no new coupling to
sim/company internals — this is pure harness self-observation, not a SIM/company wall crossing).

---

## 6. R15 mutation-testing the strike-alarm control

Per R15, this control counts as evidence only once a mutation test proves it actually fires on
its own named defect, and does not fail open/silent on degenerate input. Three required tests,
named against R15's three killer patterns:

1. **FIRES on a planted second strike (the "must catch its own defect" test — the load-bearing
   one).** Write two synthetic entries sharing a novel test-only tag (e.g.
   `test-only-class-x`) to a temp copy of the register; assert `count_strikes("test-only-class-x")
   == 2` and assert the alarm-emission function returns/raises the `[R3-ALARM]` finding on the
   second append, not the first. This is the direct analogue of the "planted defect" mutation
   tests already used elsewhere in this repo for other controls (e.g.
   `test_no_raw_tmux_send_keys_outside_relay_module` from the 07-14 retro, which was proven RED
   on 3 real sites before the fix — same discipline: prove the detector currently in the repo
   would have caught the actual historical incident, using the real tag + a synthetic
   second line, not a hand-wavy assertion that the logic "looks correct").
2. **Does NOT fail-open on an EMPTY or missing register file.** `count_strikes()` against a
   nonexistent/zero-byte `failure_register.jsonl` must return `0` cleanly (not crash, not
   silently report "no alarm" in a way indistinguishable from "checked and found none" — the
   distinction matters because R15's FAIL-OPEN pattern is specifically "passes on missing/zero
   input"; the test asserts the function surfaces "register unreadable" as a DISTINCT state from
   "register read, zero matches," e.g. via a raised exception or an explicit `status:
   "unavailable"` field, never silently returning the same `0` a legitimately-clean register
   would return).
3. **Does NOT fail-silent on a MALFORMED line.** One corrupt JSON line (truncated write, mid-append
   crash — a real risk for an append-only log under the same concurrent-writer conditions
   CLAUDE.md already documents for this shared tree, "Concurrent writers on this one working
   tree") must not silently abort the whole scan and report a falsely-low count; the parser
   skips/flags the bad line and the finding surfaces `parse_errors: [...]` rather than quietly
   returning a count as if the file were clean end-to-end.

These three tests are the mutation-test evidence required before this control counts toward any
promotion/Expert-Hour/green-suite claim, per R15's own text.

---

## 7. Proposed BUILD decomposition

Kept deliberately small — SIMPLICITY GUARD: this is a JSONL file, a ~100-line pure-Python
counting/alarm module, and one generator-file addition. No database, no service, no new daemon.

- **L1 (this doc, done here).** Design frame: taxonomy, schema, counter semantics, alarm
  contract, Method-door surfacing shape, R15 test plan. `file_scope`: `docs/design/` only
  (this document + the atom_status inbox entry) — no code, no maturity_map.yaml edit, matching
  this fork's own restriction.

- **L2 (BUILD, next open atom turn).** `file_scope`: `docs/retrospectives/`, `tools/`, `tests/`.
  - `docs/retrospectives/failure_register.jsonl` — created empty, then backfilled with one
    entry per class-tagged occurrence identified in §2 from the ~10 retros actually read (the
    backfill is real authored content, hence BUILD not FRAME).
  - `tools/failure_register.py` — `append_entry()`, `count_strikes(tag)`, `check_alarms()`
    (returns the list of tags at strike >= 2 with their finding text), `read_register()` (the
    fail-open/fail-silent-safe reader from §6).
  - `tests/tools/test_failure_register.py` — the three R15 mutation tests from §6, plus basic
    schema/append tests.
  - Wire `check_alarms()` into the existing digest-generation path (wherever
    `action_needed_register`-style findings already surface per-digest — the doc doesn't name
    a specific call site here since that requires reading the live digest generator, which is
    BUILD-time discovery, not FRAME-time invention) as a non-blocking queued finding
    (SELF_INTERRUPT_DISCIPLINE: register, don't halt).

- **L3 (BUILD, follow-on).** `file_scope`: `tools/generate_method_data.py`, `site/data/method.json`.
  - Add `failure_register_summary` per §5, regenerate `method.json`, fetch the live Method door
    per R11 and quote the rendered class/strike-count values as evidence.
  - Add the alarm to whichever per-digest alarm surface this repo already uses (grep for the
    existing `[ACTION NEEDED]`/alarm emission pattern at BUILD time), so an `[R3-ALARM]` is a
    real alarmed-every-digest item, not just a JSON field nobody reads — matching CLAUDE.md's
    own anti-decay principle ("Alarmed every digest" already named for the MAKE_IT_STICK
    anti-decay metrics; this generalises the same practice to per-class strike counts).

No atom in this decomposition touches `sim/**`, `company/**`, or `saas/**` — this is pure
harness self-observation tooling, consistent with the epistemic wall (nothing here reads
simulation internals; it reads the project's own retro/incident history).
