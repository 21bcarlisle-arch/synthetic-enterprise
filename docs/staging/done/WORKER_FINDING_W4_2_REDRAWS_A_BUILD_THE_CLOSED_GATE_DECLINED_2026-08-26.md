**Severity:** LATENT · **Lane:** W4_the_wall

# WORKER FINDING — W4_2 draws a build that a closed gate declined, and its file_scope names the wrong file

LATENT, not BLOCKING: no published figure and no control's verdict is invalidated by it. The
capability the atom names is live in the two carriers, and the routing control that was missing
landed this tick. What remains is a map record that spends a tick each time it draws.

**Rank:** after the current top item. This costs a tick each time it draws, not a wall.
**Raised:** 2026-08-26, delivery seat, from the scheduled-tick self-refill draw of
W4_2_verifier_timing_extension (lane W4_the_wall, dial 3, level 1 to 3, loop_stage build).

## The finding — observed-with-evidence

The atom's deliverable is "Epistemic verifier extended to data-flow/timing violations, not
just literal imports", and its file_scope is tools/epistemic_verifier.py.

That exact build was decided against. docs/review_gates/done/EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md
is CLOSED with the director's own words recorded in it (2026-07-10, correlated with
docs/staging/done/from_rich_20260710_203008.md): "B/C confirmed — register + doc-fix, no build;
the PreToolUse hook (adoption sprint) is the near-term detector, the as-of snapshot object the
permanent fix. Close the gate." The gate's Resolution section states it plainly: the verifier
itself is NOT modified, and no new static or AST timing-detection logic is built into it.

So the map schedules, at dial 3, a build whose only honest outcome is refusing to do it. Someone
flipped this atom's loop_stage from idle to build in the working tree, which is what surfaced it.

## What is NOT wrong here — the capability is real, it just lives elsewhere

Both mechanisms the ruling routed the burden to exist and are live, verified this tick:

- Near-term: .claude/hooks/block_point_in_time_read.py, registered as a PreToolUse Edit|Write
  hook in .claude/settings.json, with deep behavioural coverage in
  tests/tools/test_claude_hooks.py (dangerous shapes flagged, as-of-bounded shapes cleared,
  absolute and worktree paths normalised after two separate fail-open repairs).
- Permanent: company/interfaces/point_in_time_view.py (PointInTimeView, as-of cut bound at
  construction) over company/interfaces/bitemporal_event_log.py, with its own tests.

The atom is therefore not unbuilt. Its deliverable was REHOMED by a director ruling and its map
record never followed.

## The gap this tick actually closed

Nothing asserted that the near-term half was still WIRED. An unregistered hook never runs: every
one of its behavioural tests stays green while it detects nothing, and the verifier's docstring
goes on naming a detector that fires on no edit anyone makes. That is R15 FAIL-SILENT applied to
a routing decision. tests/tools/test_epistemic_verifier_timing_routing.py now holds it, with
negative controls that feed the real settings file with the hook stripped and with the hook
re-registered under a read-only matcher.

## Recommendation — taken as far as this seat safely can, the rest is one edit

Reconcile the map record to the ruling rather than building against it:

1. W4_2_verifier_timing_extension: level_current 1 to 2, level_target 3 to 2, loop_stage back to
   idle, with a closed field in the house style already used elsewhere in the file this week.
2. Correct file_scope from tools/epistemic_verifier.py to the two real carriers:
   .claude/hooks/block_point_in_time_read.py and company/interfaces/point_in_time_view.py.
3. Record the level move self-certified into gate_authorizations.jsonl per R16, provenance being
   the two carriers plus the new routing control.

Level 2 and not 3 deliberately. L3 wants "lives in time, fails like reality, epistemically clean".
The near-term hook is a one-pattern heuristic over run_settlement and all_records, warning-only;
and point_in_time_view.py's own docstring is honest that it covers price and forward observables
while weather, generation and demand are "left for a later pass unless a similar caller-trusted
gap is found there too (not yet audited)". Claiming L3 here would repeat precisely the false
claim the 2026-07-10 self-audit caught on this same atom, when level 2 with expert_hour passed
turned out to rest on nothing. The honest remaining gap is the unaudited weather/generation/demand
read paths, and it belongs in the simplifications register, not hidden inside a level.

## Why this seat did not just make the edit

docs/design/maturity_map.yaml carries another seat's uncommitted in-flight edits, written under
half an hour before this finding — a set of atom closures in exactly the closed-field style
recommended above. Editing and landing the map by pathspec would have swept that seat's
unfinished work into this commit and misattributed it. The control and the report-count fix
landed on their own paths instead; this file carries the map half for disposition.

## Reversal

Revert the commit named in this tick's landing. The map is untouched by it, so there is nothing
to unwind there. If automated timing detection in the verifier is ever genuinely wanted, re-open
EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md and retire
tests/tools/test_epistemic_verifier_timing_routing.py's TestVerifierStaysImportDirectionOnly
alongside it — do not leave two registers disagreeing about who owns the burden.
