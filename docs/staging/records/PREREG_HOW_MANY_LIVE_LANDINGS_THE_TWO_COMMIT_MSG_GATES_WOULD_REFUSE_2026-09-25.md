**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# PREREG — how many live landings would `write_time_gate` and `next_step_gate` refuse if `surgical_land` ran the `commit-msg` chain?

**Filed 2026-09-25 by the delivery seat (lane 0), BEFORE the census was run.** Claim id:
`wire-the-commit-msg-gates-into-the-surgical-land-door-after-censusing-what-they-would-refuse`.
The result is at the bottom, beside these predictions and not in place of them.

## The question, and why the census comes before the wiring

`tools/surgical_land.py` runs `sh tools/git-hooks/pre-commit` in a clean extract and then commits
with `commit-tree` + `update-ref`. Git therefore never invokes `commit-msg`, so neither of the two
message gates in that chain — `tools/write_time_gate.py` (the REUSE record) and
`tools/next_step_gate.py` (the `NEXT:` trailer) — has ever fired on the door almost every landing
uses. Measured 2026-09-25: 14 of the last 16 trunk commits came through that door.

Wiring them in is a one-line change with an unbounded blast radius: `next_step_gate` refuses ANY
commit whose message names an open atom and carries no `NEXT:` trailer, and every lane's landings
would start meeting that refusal mid-flight. So the number comes first.

## Predictions (recorded before running anything)

Population: the last 200 first-parent commits of `origin/main`, and the `surgical_land` subset of
them (those carrying `[surgical-land receipt]`).

1. **`write_time_gate` refusals over 200 commits: 8.** Reasoning: most trunk traffic is docs,
   registers and edits to existing modules, which the gate never touches; it only bites on an ADDED
   non-test `.py` under a code root. I expect ~20–30 of 200 commits to add such a module, and
   expect most seat commits to carry a REUSE block anyway because `CLAUDE.md` asks for one — so the
   refusals should be the daemon-authored and worker-authored additions, a minority.
2. **`next_step_gate` refusals over 200 commits: 40.** Reasoning: its own docstring records that
   only 17 of a recent window carried a trailer at all, while atom ids (and now bare atom NUMBERS)
   appear constantly in commit subjects. The number form is what makes this the larger of the two.
3. **`next_step_gate` will be the binding constraint, by more than 3×.** If both were small the
   item would not have been filed rather than fixed on sight.
4. **At least one refusal will be a FALSE positive I have to judge** — an atom number matched inside
   a path or an unrelated token. `atoms_named_in` matches by substring and by number prefix, and
   its own docstring accepts over-matching.

## What "done" means for this claim

The census number published beside these predictions; the two gates actually reached by the
`surgical_land` door, in a way that a control can fail; and the blast radius stated rather than
discovered by other lanes.

---

## RESULT — measured 2026-09-25, kept beside the predictions

Population: the last **200 first-parent commits** of this tree's `HEAD` (`ba9bc6733`). Of those,
**156 carry a `surgical_land` receipt**, 8 carry a hook-gate mark, **0 carry both**, 36 carry
neither (daemon commits predating the mark). 41 are merges.

The gates were driven through their own pure predicates — `write_time_gate.evaluate(added, message,
rows)` and `next_step_gate.verdict(message, open)` — with the added-path list built the way the gate
builds it (`staged_additions`, including the `MERGE_HEAD` subtraction) and the open-atom set read
from **the map blob at each commit**, not from today's map.

| | predicted | measured |
|---|---|---|
| commits adding a capability module at all | 20–30 | **5** |
| `write_time_gate` refuses | 8 | **1** |
| `next_step_gate` refuses | 40 | **1** |
| EITHER refuses | — | **2 of 200 (1.0%)** |
| merge commits refused | — | **0 of 41** |

The two refusals, named:

* `7cb432d36` — `tools/size_term_paired_floor.py`, G2: `CLASS:` reads `PATTERN-REUSE`, which is not
  one of the three ruled part classes. The record is present and one field of it is malformed.
* `fc390b918` — advances `C5_key_moment_conversion` and carries no `NEXT:` trailer.

### Grading the predictions

1. **8 → 1. WRONG, by 8×**, and wrong at the step before the gate: I predicted 20–30 commits would
   add a capability module and 5 did. The trunk's traffic is registers, findings and edits to
   existing modules.
2. **40 → 1. WRONG, by 40×.** This was the prediction the whole item was filed on — that
   `next_step_gate` would refuse every lane's landing mid-flight. See the finding below: the cause
   is not that the population complies, it is that the gate is almost never *asked*.
3. **"`next_step_gate` binds by more than 3×". WRONG.** They are equal, at one each.
4. **"at least one false positive I will have to judge". RIGHT — and it was in my instrument, not
   in the gate.** The first census run diffed each commit against its first parent alone and
   reported **4** `write_time_gate` refusals, **3 of them merges**, each naming a module the other
   parent had authored and recorded. `write_time_gate.staged_additions` already subtracts those
   (landed the same day) and the census was not asking the gate's question. A pre-registered count
   predicts the instrument, not the world.

### What was wired, and what the number bought

`tools/surgical_land.py` now runs `sh tools/git-hooks/commit-msg` in the extract —
`run_message_gate` — **before** the ~9-minute `pre-commit` chain, so a missing REUSE record costs
seconds rather than a cycle and a lost compare-and-swap race. A merge landing declares its other
parent through `.git/MERGE_HEAD` (and withdraws it before the expensive chain, which `git merge`
never runs at all). The chain's own message edits are discarded, so receipt-XOR-mark stays exact and
`--verify` remains the single checkable claim; the receipt now names **both** chains, because a
receipt naming one of two is how the next census reaches the same wrong answer this item was filed
over. Eleven source mutations were run against the eleven new controls in
`tests/tools/test_surgical_land.py`; each fired on the control written for it.

### The finding this measurement produced

`next_step_gate` is **reachable on 1 of 200 commits**: 110 atoms were open, 100 of them have a
distinct number form, and exactly one commit message in 200 names any of them (confirmed by an
independent grep, not only by the gate's own matcher). Filed as
`docs/staging/SEAT_FINDING_THE_NEXT_STEP_GATE_IS_REACHABLE_ON_ONE_COMMIT_IN_200_AND_NO_ATOM_HAS_MOVED_IN_241_2026-09-25.md`.
*(Corrected beside the original: `68717e7e1` landed this sentence naming a filename that is in no
tree — the finding was renamed after this paragraph was written and nothing checks a record's
pointers. A finding nobody can open is a finding nobody drew.)*
Wiring the chain in makes the gate *able* to ask; it does not make the population ask it.
