**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Gates judge from the base, property tests for billing, and diff-triggered checks (2026-11-20)

**Type:** STEER, through the advisor channel. The director's words, from chat on Fri 20 Nov:

- 09:06 GMT, sharing Addy Osmani, "How the Claude Code team thinks about verification" (X article, 17 Nov 2026), as text, with no comment.
- 09:08 GMT, on the advisor's recommendation below: "Yes stage it"

## What the advisor found (check it)

**The source:** Addy Osmani (Claude Code team at Anthropic), 17 Nov 2026. It describes how the team verifies code that is "~90%" written and reviewed by Claude. Key practices:
- run the change end to end;
- a failing check after three rounds brings in a human;
- cheap checks first;
- each commit stamped with how it was verified, including "none";
- new gates start in off, observe, then enforce;
- reviewers are reviewed (reverts, rejections, a size-matched clean control);
- misses become rules, which are pruned on a routine;
- flaky tests are root-caused or deleted with a written reason, never retried until they pass.

Three of its lines meet our gaps:
- **"If a change can modify the check that judges it, the check is broken."** Their Code Review reads REVIEW.md "from the base or default branch, never from the pull request's changes."
- **Property tests** (Hypothesis for Python): "keep agents honest by using edge cases that aren't created with the same bias as the agent that created the original code." Their examples include invariants, idempotency, round-trip and equivalence.
- **A 39-item reliability checklist,** "each with a trigger that can be read from a diff, a check, and the incidents or PRs behind it… Claude reads the diff and checks only the items whose trigger matches – usually 3 to 10 – so nobody has to memorize past outages."

**Against us:**
- **Self-judging gates (likely; confirm).** `core.hooksPath` is `tools/git-hooks`, in the working tree. A commit that edits a gate, or a module a gate imports, appears to be judged by the edited version. `tools/director_document_gate.py` protects director documents, not the gates.
- **No property tests.** `git grep` finds no `hypothesis` import anywhere under `tests/` (0 files), across a suite of about 39,465 tests. Our repeat defects are in billing and payments (half-month first DD, bill shock), which is property-test territory.
- **Always-loaded rules.** CLAUDE.md is about 9,900 tokens on every call. Only the wall reminders in `.claude/rules/` are path-scoped. The 17 Nov lineage work is about to give each rule its incident, which is what a diff-triggered item needs.
- **Re-gating cost, confirmed in our own words.** `background/delivery_seat.py` records a landing that "lost all 3 attempts in 2637 s: each re-cut re-ran the full gate (~880 s)".

## The outcome wanted, in order

### 1. Gates judge from the base, never from the change (first; correctness)

1. **Confirm or refute the gap.** Can a commit that weakens a gate, or a module it imports, pass under the weakened version? Demonstrate it in a throwaway worktree with a deliberately weakened gate. Do not land the weakening.
2. **If confirmed:** the gate chain runs the gates as they exist on `origin/main`, the base, against the change. Do it with a read-only checkout or a materialised base tree, not by reading the change's copy. A commit that changes a gate is judged by the old gate. The new gate takes effect only once landed.
3. **Bootstrapping.** A gate change that the old gate would refuse is not a bypass case. Split it so the old gate passes it, or raise it with a recommendation. HOOK-BYPASS IS A WALL; no exception is created here.
4. **Start the change in observe mode,** as their gates do: log what judging-from-base would have refused, then enforce.
5. Prove the new arrangement can fail (mutation): a weakened gate in a change must be caught.

### 2. Property tests for billing and payments

1. Add Hypothesis as a test dependency (one line, REUSE noted). Write property tests for the invariants the payment lifecycle (16 Nov) declares. Candidates:
   - a balance and its components reconcile;
   - a first DD is never set from a part-month;
   - running a billing or DD review twice equals running it once (idempotency);
   - a bill's VAT and standing charge follow the one declared rule (the VAT lesson: one rule, many implementations);
   - serialisation round-trips.
2. **Start with the defects we already had.** Each past billing or DD defect should be one a property test would have caught. Say which would have been, and which not.
3. **Keep generation cheap.** The cheap-gates-first rule holds. If the suite gets slower, measure by how much and move heavy properties to a scheduled run.

### 3. Diff-triggered checks, as an option in the CLAUDE.md trial

In the delete-and-add-back trial (from 21 Nov), a line whose absence shows has a third outcome besides keep and drop: **move it to a diff-triggered checklist item.** Each item has:
- a trigger readable from the diff (paths, symbols, file kinds);
- a check;
- its lineage (incident, finding, ruling).

The checklist is read at commit or review time, and only the matching items run. Report how many always-loaded tokens move to triggered items and whether protection held in the golden set. Use the path-scoped rules mechanism where it fits before building anything new.

### Also

- **Three rounds, then stop.** Confirm the machine stops after three failed attempts to fix a failing check and files it, rather than looping. If not, propose it.
- **Flaky tests** are root-caused or deleted with a written reason. Confirm there is no retry-until-green anywhere.

## Reading-log entry to append

| Date | Source | Shared by | What we took | Verdict |
|---|---|---|---|---|
| 2026-11-20 | Addy Osmani, "How the Claude Code team thinks about verification" (X article, 17 Nov 2026) | Director | We already do E2E doors, cheap gates first, verification stamps, misses into rules, and reviewer review. Gaps: gates judged from the change, not the base; no property tests; rules always loaded rather than diff-triggered. | ADOPT (three items, in order) |

## Risk

Touches: the commit gate chain (item 1); test dependencies and new tests (item 2); the CLAUDE.md trial's design (item 3).
Blast radius: item 1 is every commit, which is why it starts in observe mode.
Probable failure modes:
- **Judging from the base deadlocks a legitimate gate fix.** Mitigated by splitting the change, and by the observe phase revealing it first.
- **Property tests that only restate the code.** Each property comes from the lifecycle or the rules, not from reading the implementation.
- **Triggers too narrow,** so an item never fires. Each triggered item must fire on at least one past diff that touched what it guards.

Proportionality: item 1 touches the gate chain. Implement with the named mitigations, observe first. Items 2–3 implement directly.

— Director steer, 20 Nov 2026, his words above; the reading and drafting are the advisor's.

## Done

Item 1 is on in observe mode; items 2 and 3 and the "Also" items are live continuations.

- **1.1, the gap: confirmed.** A gate weakened inside a change passes that change, because the
  hook runs every gate from the committing tree (and under `surgical_land`, the hook script too).
  This was demonstrated in bb33b0a629:
  `docs/staging/records/SEAT_RECORD_A_GATE_IS_JUDGED_BY_ITS_OWN_EDITED_COPY_2026-11-20.md`.
- **K8 page first:** `docs/market_research/gates_judged_from_the_base_2026-11-20.md`. It records
  the design choices and GAP-1 to GAP-6. The main GAP is that gate *data* (baselines, `.mode`
  files) is still read from the change, and observe mode counts how often a change touches it.
- **1.2/1.4, observe mode:** `tools/base_judged_gates.py`, wired as the second line of
  `tools/git-hooks/pre-commit`. The observer itself is read from HEAD, never from the change. For
  each gate whose import closure (read from the base) the change stages, or whose hook line the
  change alters, it reruns the gate twice in identical shadow trees. One side uses the base's code,
  the other the change's code; both read the change's data. It logs to
  `.git/base_judged_gates.jsonl` (`--report`) and refuses nothing.
  - **The base is the parent commit, not the literal `origin/main` ref,** because
    `surgical_land`'s extract has no refs. The landing compare-and-swaps onto that parent.
  - **The two pytest gates are rerun only when their own file or a direct import is touched.**
    Their closures are about 440 files. Otherwise the record says `deferred`.
- **At real inputs:** a clone at bb33b0a629, with an empty `.dta` staged and
  `ukds_microdata_refusal` weakened, gave base rc 1, change rc 0, `would_refuse: true`. Observer
  overhead was 4.4 s. An unrelated change reruns nothing, with an overhead of 3.7 s.
- **1.3, bootstrap:** the observer takes effect from the commit after the one that lands it (HEAD
  has no copy until then). Enforce will split any gate change the old gate refuses; it never
  bypasses.
- **1.5, mutation:** `tests/tools/test_a_weakened_gate_inside_a_change_is_caught.py` covers a
  weakened gate, a weakened imported module, a dropped hook line, the whole partition and
  fail-soft. Five source mutations each red their named test: the base side read from the change,
  the closure stopping at the gate's own file, a dropped line never seen, every gate rerun, and an
  observer crash propagating.
- **Continuations, each naming this steer:**
  - `gates-judged-from-the-base-enforce` (read a week of the log, then enforce with the hook
    script itself from the base);
  - `property-tests-for-billing-and-payments` (item 2);
  - `diff-triggered-checks-in-the-claude-md-trial` (item 3);
  - `three-rounds-then-stop-and-no-retry-until-green` (the "Also" items).
- The reading-log row is appended.

Decision: harness yes
