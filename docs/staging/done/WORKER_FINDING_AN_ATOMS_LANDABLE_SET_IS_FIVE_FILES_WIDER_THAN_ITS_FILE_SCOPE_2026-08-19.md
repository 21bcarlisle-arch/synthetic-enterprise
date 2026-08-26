**Severity:** RECORDED · **Lane:** H_harness

# An atom's landable set is five files wider than its `file_scope`, and nothing computes it

Found while landing `EP6_wall_protocol_typing`'s first BUILD pass (commit `fb19bc8e0`,
2026-08-19). Everything below is `observed-with-evidence` unless labelled `inferred` (R9).

## The observation

EP6's `file_scope` names two files:

```
company/interfaces/wall_protocol.py
tests/company/interfaces/test_wall_protocol.py
```

The commit that actually landed the atom needed **seven**. The other five were found one at
a time, by three separate gate refusals, each costing a full gate cycle (~75s of tests):

| file | why it is in the atomic write | found by |
|---|---|---|
| `docs/design/simplifications/EP6_wall_protocol_typing.yaml` | the pass's store note | known |
| `docs/design/simplifications/archive/EP6_wall_protocol_typing.001.yaml` | the append **rolled**; `load_all` merges live+archive, so `simplifications_count: 8` is 7 live + 1 archived | refusal 1 (`test_counts_match_file_contents`) |
| `docs/observability/gate_authorizations.jsonl` | the R16 self-certification row | refusal 2 (`level_promotion_gate`) |
| `docs/design/orphan_baseline.json` | the new module has no caller, deliberately (L1, built and dark) | refusal 3 (`orphan_ratchet`) |
| `docs/design/maturity_map.yaml` | level + count bookkeeping | known |

## Why this is a class and not an incident

Every one of those five is **derivable from the atom id before the first gate cycle is
spent**. The information exists; nothing assembles it. The refusals are all correct — none
of these controls is at fault, and each one caught a genuinely inconsistent tree — but a
worker learns the landable set by being refused, which means the cost is paid per atom, per
pass, forever, and a worker who gives up after the first refusal leaves the atom
half-landed. That is exactly the state EP6 was found in: its module, suite, store note,
roll file and ledger row had been sitting on disk since 16:19 while the map's level move sat
staged, so the RECORD said level 1 and the REPOSITORY had no such atom.

`file_scope` reads like the answer to "what does this commit touch" and is not. It is the
answer to "what may this atom edit" — a permission, not a manifest.

## The two traps that only appear on a shared tree

Both were live in this landing and both would have quietly corrupted a neighbouring lane:

1. **`maturity_map.yaml` carried a second lane's hunk** (EP1 pass 11, uncommitted). Swapped
   to HEAD's for the gate, not adopted.
2. **`orphan_baseline.json` cannot be regenerated with `--freeze` on a shared tree.**
   Running the tool the refusal message itself recommends SHRANK the list by seventeen
   modules (`clv_calculator`, `channel_roi`, `acquisition_cost`, …) — they only look
   reachable because EP1's uncommitted `tools/couple_clv.py` is on the disk. Freezing would
   have grandfathered another lane's unlanded work and retired seventeen real orphans in a
   commit about something else. **The refusal message's own advice is unsafe whenever the
   tree is dirty, and the tree is essentially always dirty here.** The safe form is: rebuild
   from `HEAD`, add your one line.

## Recommendation (recorded, not asked — NEVER_ASK_WITHOUT_RECOMMENDING)

Build `tools/landable_set.py --atom <id>`: given an atom id, emit the full pathspec —
`file_scope` + live store file + every archive file for that atom + `gate_authorizations.jsonl`
if the level moved + `orphan_baseline.json` if the deliverable adds an uncalled module + the
map. Cheap, purely derivable, and it converts three gate cycles into one. Pair it with a
`--from-head` flag on `orphan_ratchet --freeze` so the recommended repair stops being unsafe
on a dirty tree.

This is **queued, not fixed on sight** (SELF_INTERRUPT_DISCIPLINE): the machine is not
blocked — EP6 landed, and the workaround is known and written down here.

## Related, already queued

- `WORKER_FINDING_A_STORE_COUNT_INVARIANT_IS_GREEN_ON_THE_TREE_AND_RED_ON_THE_COMMIT_2026-08-19.md`
  — the same coupling seen from the invariant's side.
- `WORKER_FINDING_A_STEPS_OWN_PATH_LIST_IS_NOT_ITS_CHANGE_SET_2026-08-12.md` — the same
  shape one layer up.
