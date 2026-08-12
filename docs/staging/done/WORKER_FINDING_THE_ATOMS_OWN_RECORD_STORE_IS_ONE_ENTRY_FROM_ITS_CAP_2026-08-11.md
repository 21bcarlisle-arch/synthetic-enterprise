# WORKER FINDING — the atom's own record store is one entry from its cap

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-11, during the sixth Expert Hour on `H_GAP_fabric_belief_truth_gap`
**Class:** a ratchet about to wedge a lane · **Disposition:** QUEUED, not fixed on sight
**Gate:** `tests/design/test_simplifications_store.py::test_every_file_within_size_bound`

## The measurement

```
docs/design/simplifications/H_GAP_fabric_belief_truth_gap.yaml
    98,386 B at HEAD   (cap 102,400 = 100 KiB, tools/simplifications_store.py:63)
   101,324 B after this Hour's entry, trimmed to a summary
     1,076 B headroom remaining
```

The last nine entries on this atom average **5.4 KB**. The store therefore admits
**zero** further Hours at their established size. The next Hour on this atom cannot
record itself without going red on a gate — and this atom has taken an Hour most days.

This is not caused by the sixth Hour's entry. It was already at **96% of cap** before
it, and the entry was cut to a 2.6 KB summary with its full text staged separately.

## A second, smaller thing found on the way

Re-serialising the store with `yaml.dump(..., width=100)` inflates this file by
**2,058 bytes** against HEAD's formatting (100,444 vs 98,386 for identical content);
`width=1000` reproduces it to within 130 B. A writer that reflows the file spends 2 KB
of an atom's budget on nothing, and the size gate cannot tell that apart from content.
Any tool appending to the store should dump at `width=1000`.

## Why it is queued rather than fixed here

The cap is one file per atom, keyed by filename (`_path_for` = `<atom_id>.yaml`), with
an orphan check and a count check reading the same directory. So a drain cannot be
"another file in the same directory" — it needs a designed home, a reader that knows
about it, and both consistency checks taught the new shape. That is the OPS1 rule
(`docs/design/OPERATIONAL_LAYER_DESIGN.md`): design the whole, do not accrete a
mechanism to patch a symptom at the end of a bounded tick.

It is also the same shape as the drain the **fifth** Hour performed one layer up, when
this atom's entry blew the per-atom budget in `maturity_map.yaml` and its narratives
were rehomed into this store (`records_rehomed: [evidence, expert_hour_findings]`).
That drain moved the problem down a level rather than bounding it. The next one should
bound it — a narrative archive with a retention rule, so a long-lived atom's record
stops being a monotonically growing file that eventually wedges its own lane.

## Suggested shape (not built)

- A per-atom archive (e.g. `docs/design/simplifications/archive/<atom_id>.yaml`)
  excluded from the per-file cap but included in the orphan/count checks.
- `for_atom` concatenates archive + live; `records_for_atom` unchanged for readers.
- A retention rule that is a MECHANISM, not a convention: entries older than N or
  beyond the last K are moved on write, so no tick has to remember to drain.
- The count check must count archive + live, or the drain silently loses entries —
  the failure mode this project has already recorded as *"a drain nobody asserts is a
  one-time cleanup"*.

## Evidence

Both numbers above are `os.path.getsize` on the real files, and the gate's own
threshold is read from `tools/simplifications_store.py::MAX_FILE_BYTES`.
