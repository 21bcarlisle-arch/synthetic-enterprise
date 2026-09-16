**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — publish-gate unwedge) · **Class:** `publish_gate_and_wedge`

# The publish gate's one red at HEAD was a carrier that conflates absent and unreadable on purpose

**2026-09-09, scheduled tick.** Found by reading `.publish_gate_state.json` after reconciling the
tree, not by being told. One blocking test, one carrier, and the exemption it needed was the
opposite direction to every exemption already in the file.

---

## 1. What was wedging publish

`docs/observability/.publish_gate_state.json` named exactly one blocking test:
`tests/background/test_episode_prior_partition.py::test_every_real_census_hit_is_covered`, with
`episode_clean_publishes: 0` and 8 episode failures, the last two recorded `unattributed`.

The rung is an anti-narrowing control: its subject is the self-clearing alarm census's own `real`
rows, never a maintained list, so a carrier that becomes `real` must be probed or named with its
reason. `publish_standing_reds.json` became a `real` row on 2026-09-09 and wedged the gate from
the moment it did.

## 2. The shared tree and clean HEAD disagreed about which carrier, and that mattered

| tree | uncovered carriers |
|---|---|
| shared working tree | `.standing_red.json`, `publish_standing_reds.json` |
| clean extract of HEAD | `publish_standing_reds.json` only |

`.standing_red.json` is another lane's **uncommitted** disposition row. Fixing the pair from the
shared tree's reading would have been covering a carrier that is in nobody's commit, on the
strength of a red only this working tree can see. Measured in a clean extract before touching
anything, exactly because a green or a red in the shared tree measures several lanes and not this
change.

**It is deliberately left uncovered.** When that lane lands its row, this rung tells them so and
its disposition already carries the answer — its `loader` field says `standing_red.load` is
fail-open by design, proved at
`test_a_corrupt_ledger_reads_as_nothing_standing_rather_than_a_reconstructed_accusation`. Covering
it here would be this lane writing an exemption for a claim it did not make.

## 3. The exemption is the opposite direction to every one above it, so it is its own bucket

Every existing exemption in that rung says *a sibling proves this carrier TELLS THE TWO APART*.
`publish_standing_reds.json` needs the opposite: `publish_standing_red.load_ledger` is fail-open by
design and says so in its own docstring — a missing store, an `OSError`/`ValueError` read and a
structurally wrong document all return `empty_ledger()`. Absent and unreadable deliberately read
the SAME.

That is the dangerous direction — an empty ledger reports *less* standing work, not more — and the
module argues for it rather than assuming it: the alternative escalates a subject the ledger cannot
name, and an escalation carrying no node id is the wallpaper that module replaced. The cost is
bounded to one publish cycle, because the next refusal repopulates through `record_refusal` and
`save_ledger` rewrites the whole document rather than merging.

Filed under `covered_by_a_sibling` it would have had this rung reporting that a conflation was
distinguished — a worse failure than the gap it closes. So it is a separate `deliberately_conflated`
bucket whose name states the direction.

## 4. The citation check got one leg stronger than the one it sits beside

The existing check asserts the cited sibling FILE is on disk. That cannot see a file which outlives
the control it was cited for. The new bucket asserts the named test FUNCTIONS are in the file.

**Poisoned separately, each in its own clean extract of HEAD, because a red from the wrong cause
reads exactly like the control working:**

| poison | result |
|---|---|
| rename `test_a_broken_ledger_cannot_take_the_publish_cycle_down` in the sibling | RED, naming the missing function |
| add a new `real` carrier to the dispositions, sibling untouched | RED, naming `.a_brand_new_carrier.json` |

The first run of poison 2 was discarded: the extract had no `.git`, the sibling restore failed
silently, and the rename was still in place — so that red could have come from either cause and
established neither. Re-run from a fresh extract with the sibling untouched. Recorded because the
discarded run looked exactly like a pass of the experiment.

The second poison is the one that matters: it proves the exemption did **not** make the rung
fail-open. A new carrier still reds.

## What is next

1. **The gate should clear on the next publish cycle.** `episode_clean_publishes` was 0 with 8
   failures; if it does not clear, the cause is not this test and the two `unattributed` failures
   are where to look — they name no cause, so which one it was is not established by that record.
2. **`.standing_red.json` will red this rung when its lane lands.** Its disposition already holds
   the answer; it belongs in `deliberately_conflated` beside this one, with its own citation.
3. **Two exemption buckets now differ only by direction, and both are hand-maintained.** The
   dispositions file already records the loader answer per carrier. Deriving the buckets from it
   was considered and rejected: the field is prose, and a control that reads prose by substring is
   wrong in both directions. Recorded so the next pass does not re-consider it from scratch.
