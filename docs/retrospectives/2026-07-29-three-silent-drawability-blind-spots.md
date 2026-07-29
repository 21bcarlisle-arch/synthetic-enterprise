# Why did 31 pieces of work stay invisible through every gate, test, rule and review? (2026-07-29)

**Prompted by:** `docs/staging/DIRECTOR_QUESTION_WHY_INVISIBLE_WORK_2026-07-29.md` (advisor bridge,
carrying the director's question). Not a bug report — the director had already accepted the bug
fixes; this is the standing-back question of why an elaborate apparatus of rules, gates, mutation
tests, hardening loops and reviews could not *see* the absence of drawable work for days.

**Claim discipline (R9):** every factual claim below is labelled `observed-with-evidence` (a cited
commit, file:line, or memory record checked against current code) or `inferred` (my reasoning from
the evidence, clearly marked as such). Where I could not re-verify a claim against live code because
a concurrent fork was mid-edit on the same file, I say so rather than assert it as current fact.

## What happened — three incidents, same shape, three different files

**1. EIGHTH CLASS — the deadman's watchdog silenced itself (2026-07-27, commit `b55981046`,
`observed-with-evidence`: `docs/design/` ruling doc + `[[project_eighth_class_pending_batch_deadlock_2026_07_27]]`).**
The machine rested 42h (Sat 11:09Z → Mon 05:07Z) publishing "REST-LEGITIMATE (whole authorized set
empty)" while 6 `PLANNER_MINTED_*.md` mints sat open in `in_progress/`. Two independent root causes,
both confirmed against the actual fix commit:
- **H2:** the deadman's `[STALL]` page was suppressed by the "proven-rest fold"
  (`deadmans_switch.run_cycle` calling `supervisor._is_drained_and_gated`) — the watchdog's own
  legitimacy check *delegated to the exact mechanism whose falsely-empty verdict it existed to
  catch*. A tautology: the check and the thing checked shared one source.
- **H1:** `value_chain_observation_window_cap` had genuine drawable BUILD work, but its
  `SUPERVISOR_DRAW: blocked` marker went stale after the blocking ruling was resolved three days
  earlier — nothing re-evaluated it once the underlying condition changed.
- Fix: `_check_open_mint_escalation` (now `background/deadmans_switch.py:322`, verified present in
  current code) runs *before and independent of* the proven-rest fold, reading
  `_open_blocked_mints()` — which reads `docs/staging/in_progress/*.md` directly off disk, not
  through the supervisor's own drawability logic (`deadmans_switch.py:276-284`'s own docstring
  states this independence is deliberate: *"so it stays independent of the supervisor's own rest
  logic, the thing that mis-declared rest legitimate"*).

**2. The planner's rest-proof had the identical blind spot two days later (2026-07-29, 02:07Z tick,
`observed-with-evidence`: `[[feedback_planner_rest_proof_fired_window_blindspot]]`).** A 00:06Z
rest-proof claimed all 27 blocked mints were walled on director-reserved authority. Five were not —
their release conditions (elapsed `propose_then_proceed` windows, a landed dependency) had already
fired, but the static `blocked` marker never got re-checked against that. Same shape as EIGHTH
CLASS's H1, on a *different* code path, *after* H1 had already been fixed once.

**3. The self-refill HARDEN doorbell mask (2026-07-29, ongoing per
`[[feedback_selfrefill_harden_masks_staging_backlog]]`, still unfixed in code — this one is
prose-only).** `process_run_complete.py` archives only the *newest* `run_complete_*.md` marker,
leaving older ones sitting in the scanned staging root; each un-archived marker re-grants a
supervisor turn roughly every 2 minutes, manufacturing a false "agenda+staging empty, go re-harden"
doorbell while a real archiving backlog (23-24 markers observed in one instance) sits unprocessed.

## Root cause, not the instance (R4)

I re-read the actual code, not just the incident write-ups, to check whether "the fix" for (1)
actually reached (2). It didn't, and the reason is precise, not vague:

`background/supervisor.py:2851` (`_in_progress_minted_slugs`, backing the planner's
`_planner_rest_proof_fresh` at line 2947) and `background/deadmans_switch.py:276`
(`_open_blocked_mints`, backing the deadman's escalation) are **two independent reimplementations**
of "which mints in `in_progress/` are blocked." Both correctly track *set membership* — which files
currently carry a `blocked` vs `self-drawable` marker — and both were written to be honest about that
membership. **Neither checks whether an individual blocked marker is still TRUE.** The 07-27 fix
(H2) made the deadman's rest-legitimacy check independent of the supervisor's rest-decision logic;
it did not (and structurally could not, being in a different module answering a different question)
make the *planner's* rest-proof check whether a blocked mint's own release condition had fired. The
07-29 fired-window incident is not a recurrence of an unfixed bug — it is the **same class landing
on the one call site the first fix never touched**, because the first fix was scoped to *make one
consumer of "is rest legitimate" independent of another*, not to build *one shared, independently-true
source of "has this specific block actually cleared"* that every consumer (deadman, planner
rest-proof, self-refill HARDEN doorbell) must consult.

**The advisor's hypothesis, checked point by point against this evidence:**
1. *"Everything tested that things WORK; nothing tested that things APPEAR."* **Confirmed.** Every
   R15 test I can find for these three mechanisms proves a control fires on its own named defect —
   none of them assert "given N days of unresolved backlog, SOMETHING must appear in the drawable
   set." The invariant itself was never encoded, only each mechanism's local behaviour.
2. *"All three faults were silent by construction... 'nothing available' was the correct output from
   corrupted input."* **Confirmed**, and worth sharpening: it wasn't corrupted input, it was **stale
   input that was correct when written**. A `blocked` marker was true the day it was set; nothing
   ever re-asked it whether it was still true. "Silent" here specifically means *no distinction
   between "checked and still blocked" and "marked blocked once and never revisited."*
3. *"The tests were written by the same reasoning that wrote the fault."* **Confirmed for (1)/(2):**
   the 07-27 fix added independence between two consumers' *drawability logic*, which is exactly the
   axis the original bug was on — a reasonable, but insufficiently general, response. It did not ask
   "what if the same shape exists on a third, not-yet-audited consumer" — which is precisely where
   (3) still lives today, unfixed.
4. *"Nobody wrote the one invariant that mattered: if unfinished work exists, something must be
   drawable."* **Confirmed, and this is the actual root cause, not a restatement of it.** What
   exists today is three *ad hoc, locally-scoped* approximations of that invariant (the deadman's
   independent blocked-mint read, the planner's set-membership diff, a still-unwritten check for
   run_complete backlog) rather than one shared function every rest-claiming path calls.
5. *"Eight rules were added about choosing work, none about whether the list was true."*
   **Confirmed** by the shape of the fix history itself: `MULTI_ATOM_DRAW`, `THREE_LANES`,
   `PRIORITISATION_RULES`, the rung system (RUNG 1-7) all govern *selection among* candidates; none
   of them assert *the candidate set's own completeness*.

**The class, named:** call it **stale-truth invisibility** — a status flag that was correct when
written, is never re-asked whether it is still correct, and whose silence (returning the same
"nothing to do" answer) is indistinguishable from genuine exhaustion. It is the mechanical opposite
of a `blocked_on` field with no reason (the class the director already closed via
`unstated_reason_block_impossible`, R10) — that class hid work by never *stating why* something was
blocked; this class hides work by stating why once and never *re-checking* it.

## A fourth instance, found by the sweep this session (not previously known)

The director asked for a sweep: "where else does the system trust a single count, a single derived
view, or a single 'nothing to report' that nothing independently contradicts?" I ran the ntfy/PIN
sweep for ruling item 4 this session and, while auditing the maturity map's structural integrity,
found: `docs/design/maturity_map.yaml` is parsed by every consumer via plain `yaml.safe_load`, which
silently keeps the *last* value of a duplicate key. `C11_segment_debt_policy` carried four copies of
the `(expert_hour, real_world_twin, depends_on)` block-tail (three other atoms' content, appended to
the wrong entry by earlier registration commits) — the file **parsed successfully**, every consumer
got a dict, and the wrong value (an empty `depends_on`, three atoms silently missing their
`real_world_twin`) was accepted as truth with no error anywhere. Exact same shape: a derived view
(the parsed atom dict) that nothing independently contradicted. Fixed and landed this session —
`tests/controls/test_map_reconciliation.py::test_no_atom_in_the_real_map_has_duplicate_keys`,
committed `ae0f67079`, mutation-proven both ways (a planted duplicate fires; a clean map stays
silent). The live map currently has zero duplicates (the test is green against real disk, verified
this session) — this was a **latent** defect, not an active one, but it is the same class recurring
in a fourth, previously-unaudited location (the map's own parse layer) within the same 48 hours.

## The fix — what's verified landed vs what's correctly left for the concurrent sweep

- **(1) and item-4-of-today's-ruling: landed and verified this session.** The min-length/PIN gate on
  inbound director messages (`background/ntfy_responder.py::_write_to_staging`) is deleted; 218
  tests green including two new R15-both-ways tests (`test_write_to_staging_keeps_short_message_...`)
  proving a terse steer with nothing formally open now stages, and a broken `open_items()` lookup no
  longer silently eats a real message. Committed `ae0f67079`, pushed to origin.
- **(4) the duplicate-key guard: landed and verified this session**, same commit.
- **(2) and (3): correctly NOT touched in this thread.** A separate fork is, concurrently with this
  retro, executing the rest of today's `DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY_2026-07-29`
  (abolishing `director_build_open`/`director_level_up` as blocking mechanisms entirely). That sweep
  reads and rewrites the exact same `blocked_on`/`BLOCK_RELEASE` markers this retro's root-cause
  analysis is about. Editing `background/staging_disposition.py`, `background/deadmans_switch.py`'s
  marker vocabulary, or the `in_progress/*.md` mint docs from this thread at the same time would risk
  exactly the "two writers, one file, silently wrong result" shape this retro is diagnosing — so I
  deliberately left that code untouched and let the dispatched fork own it. Once permission-gating is
  abolished per today's ruling, most of the *specific* stale-marker cases (Channel A/B in
  `docs/design/SELF_AUTHORITY_RELEASE_SWEEP_2026-07-29.md`, 16 of the ~21 blocked mints as of that
  doc) disappear structurally — there is no longer a director-permission gate left to go stale on.

## The residual invariant — named precisely, registered as real next work, not proposed-and-parked

Removing permission-gating shrinks the class but does not close it: a `propose_then_proceed` time
window and a genuine unbuilt BUILD dependency are still real block types that can silently clear
without anything re-checking them. The invariant that would catch all three incidents (and the
fourth) at the root, not per-instance:

> **One shared, independently-read function — not duplicated per consumer — that computes "does any
> currently-blocked item's own release condition already hold?", called by every path that is about
> to claim rest is legitimate** (the deadman's escalation, the planner's rest-proof, the self-refill
> HARDEN doorbell, and any future one). Today there are two independent reimplementations of "what's
> the blocked SET" (`supervisor.py::_in_progress_minted_slugs`, `deadmans_switch.py::_open_blocked_mints`)
> and zero implementations of "is a given block still TRUE" — that check was done by hand, once, on
> 2026-07-29 02:07Z, and evaporated (MAKE_IT_STICK's own diagnosis: memory decays, mechanism doesn't).

I am not building this inline in this thread, for the concurrency reason stated above (the exact
files it would touch are mid-edit by the ruling-execution fork) and because the *shape* of what
counts as "a block's release condition" is being redefined by that same fork this hour — writing a
staleness-checker against the pre-ruling vocabulary would be dead code within the hour. This is
registered as the named follow-on for the next tick once the ruling-execution fork lands: build
`background/block_condition_resolver.py` (or fold into `deadmans_switch._open_blocked_mints`) as the
**single** source both the deadman and the planner's rest-proof call, plus a third caller for the
run_complete-backlog case in item (3). R15 requirement for that follow-on: a planted
already-fired-but-still-marked-blocked mint must flip the rest-proof to non-fresh (fires), and a
genuinely-still-blocked mint must not (silent on a clean input).

## What was NOT lost / genuine scope of harm

No data was corrupted, no external commitment was missed, and no company-facing figure was wrong —
this is a build-throughput cost (days of the harness reporting itself exhausted while real,
already-approved work sat undrawn), not a safety or financial incident. The duplicate-key finding (4)
was latent (zero atoms currently affected) — a near-miss caught by the sweep, not an active data-loss
incident.
