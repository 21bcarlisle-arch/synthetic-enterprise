# The consolidation rhythm — an epoch cannot close without a record of the pruning

**Atom:** `AO6_consolidation_rhythm` (H_harness, epoch 3).
**Serves:** `DIRECTOR_PROGRAMME_ARCHITECTED_OUT_2026-08-05.md` §RHYTHM.
**Mechanism:** `tools/consolidation_rhythm.py` · **Ledger:** `docs/observability/consolidation_ledger.jsonl`
· **Proof:** `tests/tools/test_consolidation_rhythm.py` · **Wired:** `tools/git-hooks/pre-commit`

## The ask, in the director's words

> Canon already prunes the harness and advisor memory at epoch boundaries. Extend the same duty to
> code: every epoch close includes a consolidation pass — duplicates found, orphans wired or
> retired, the target-design document updated. **Organic growth between boundaries; deliberate
> pruning at them.**

## Why this is code and not a line in a checklist

The atom's own `origin_note` specified the failure mode before anything was built:

> This is the step that decides whether the whole programme decays. MAKE_IT_STICK is directly on
> point: *every rule that DECAYED was an exhortation; every rule that HELD was a MECHANISM.* An
> epoch-close consolidation pass that lives only as prose in a checklist WILL evaporate exactly as
> the earlier exhortations did.

So the deliverable is a check that **fails an epoch close lacking its consolidation record**. The
line added to `.claude/skills/phase-close/SKILL.md` points at the gate; it is not the gate.

## What "epoch close" is, measurably

Epoch E is CLOSED when it holds at least one atom in `docs/design/maturity_map.yaml` and every one
has `level_current >= level_target`. That is *read from the map*, never declared by hand — "the
epoch closed" is an observation, not an announcement.

`--gate` compares the **staged** map against **HEAD's**. A commit moving an epoch from open to
closed without a **committed** pass record is refused. A map edit that closes nothing pays nothing;
an already-closed epoch is never re-charged (a gate that fires constantly is one people route
around).

## The ratchet, and why it is bounded

The tree carries a large pre-existing orphan pile — **266 of 843 modules** at baseline, the same
number AO7's T4 target reports from a different tool. Demanding all of it at the next boundary would
make the first close impossible, so the ledger opens with exactly **one `baseline` record**: it
stamps that pile as declared, visible debt and forgives it *for coverage purposes only*. Every
orphan appearing **after** the baseline must carry a disposition before an epoch can close.

That is the atom's own sentence, mechanised. `--report` prints the unaccounted set at any time, so
growth is visible continuously rather than only at a boundary.

**A second baseline is the obvious escape and is refused (G8).** Without that guard, the cheapest
move available to a future turn facing a coverage failure is to re-baseline and forgive itself,
leaving the mechanism green forever while measuring nothing.

## The three dispositions

| | meaning | how the **tree** contradicts a false claim |
|---|---|---|
| `retired` | the module is gone | the path still exists → G5 fails |
| `wired` | it has a caller now | the live index still finds no caller → G5 fails |
| `kept` | deliberately left, with a named reason | *nothing* — see below |

Only `kept` is unfalsifiable, and that is deliberate. The same director amendment governing AO2
draws the wall: *"know, then choose — forced reuse that couples two purposes is the mirror error of
duplication and is equally a defect."* A gate accepting only `wired`/`retired` would compel the
decision rather than the look, and would push a turn into deleting a module it should have kept. So
`kept` is the recorded, reasoned, attributable choice; because the ledger is append-only, a module
kept at successive closes accumulates a visible history, which `--report` prints as `kept_repeats`.

## R12 — the load-bearing inversion, pinned both ways

This measures whether the pass **happened**. It never scores **how much was pruned**. A pass that
deliberately keeps every orphan, with reasons, is rc 0; a tree with a larger orphan census than
yesterday is rc 0. There is no count that turns this red and there must never be one — the moment
there were, the cheapest route to green would be deleting modules, the metric editing the
territory. Pinned in both directions in the suite.

## R15 — the three killer patterns

- **TAUTOLOGY.** The coverage rule does not compare the ledger against itself. It compares the
  ledger against the **live orphan set** derived by AO1's `capability_index.py` from the actual
  tree. A hand-forged record with an empty census buys nothing: only the single baseline forgives,
  and every other module still shows up in the live scan. Disposition *claims* are checked the same
  way. The ledger states intent; the tree states fact; they come from different places on purpose.
- **FAIL-OPEN.** A map yielding zero atoms, or an index yielding zero rows, **raises** — "0
  unaccounted orphans" and "0 modules scanned" are the same number and opposite facts. When no
  epoch is closed the coverage rule reports **NOT APPLICABLE by name**, never as if verified.
- **FAIL-SILENT.** An unreadable ledger line, an unparseable map, an unavailable index and an
  unknown disposition word are all refusals. There is no skip disposition. Under `--gate`, a record
  present only in the worktree and never staged is refused: the record must be committed to count.

### The mutation pass found a guard that could not fail

A tenth mutation was written against `if members and all(...)` in `closed_epochs` — the defence
against `all([])` reading an empty epoch as closed. **Nothing went red.** The guard was unreachable
from the only path that builds `by_epoch` (which appends, so every key has a member). It was
deleted with its mutation rather than kept as an unfalsifiable guard; the reachable vacuity — a map
yielding no atoms at all — is guarded in `atoms_from_map` and does fire.

## Usage

```
python3 tools/consolidation_rhythm.py --check      # every closed epoch has its pass (rc 2 if not)
python3 tools/consolidation_rhythm.py --report     # the standing census, never gating
python3 tools/consolidation_rhythm.py --record --epoch 2 --dispositions passes.json
```

`--dispositions` takes a JSON list of `{"path", "disposition", "reason"}` objects. The census itself
is **machine-taken at record time** by running the index — it is never typed.

## Known limit, stated rather than left silent

The gate fires at epoch boundaries, and no epoch is closed today (epoch 1 is one parked atom away).
So the *gate* is dormant while the *report* is live from this commit. That is the duty's real shape
— pruning belongs at boundaries — but it does mean the standing number is what carries the
mechanism between them. Wiring `--report`'s unaccounted count into the daily digest is the natural
next increment and is deliberately not half-built here.
