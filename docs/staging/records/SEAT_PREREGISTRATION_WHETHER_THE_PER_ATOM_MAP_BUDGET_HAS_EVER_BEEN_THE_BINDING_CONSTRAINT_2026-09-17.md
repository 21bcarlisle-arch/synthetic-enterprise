**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `H41_the_map_ratchet_has_no_ongoing_drain`

# Pre-registration: whether the map's per-atom budget has ever been the binding constraint, or whether the uninformative whole-file ceiling always fires first

**Filed 2026-09-17 by the delivery seat (lane 0), BEFORE running the measurement, while a
sibling lane's drain of the same map is mid-landing.**

## What is already established by arithmetic, and therefore is NOT the question

`tests/design/test_simplifications_store.py` carries two bounds on the map's size:

| bound | value | fires on |
|---|---|---|
| `MAP_SIZE_CEILING` | 409,600 B over both halves | the TOTAL. Names no atom. |
| `MAP_MEAN_BYTES_PER_ATOM` | 1,400 B | the mean. Names the population. |
| `MAP_MAX_BYTES_PER_ATOM` | 12,288 B | ONE atom. Names it. |

The second exists, in its own words, because a whole-file ceiling "twice arrived as a publish
wedge carrying no information about what to fix". But `1,400 x 350 atoms = 490,000 B` against a
409,600 B ceiling: at today's population the mean budget authorises **80,400 bytes the file
ceiling refuses**. It cannot fire first. The crossover is 409,600 / 1,400 = **292.6 atoms**, and
the map holds 350.

That is arithmetic over two constants and needs no measurement — and by this project's own rule
an argument resting on arithmetic over two constants is unfalsifiable, so it is not the claim
being tested here. It is the motive for the claim below.

## The question, whose answer I do not know

**Since the map's population crossed ~293 atoms, has the per-atom budget ever gone red BEFORE
the whole-file ceiling on the same commit?**

## What I predict, written before looking

1. **The population crossed 293 atoms before either of the two known wedges** (2026-08-09 and
   2026-08-10, both recorded in the control's own comment as whole-file breaches). If so, the
   per-atom companion was already unable to bind on the day it was written to fix exactly that
   complaint — it was derived from a *cleaned* map (mean 1,156 over 260 atoms) and the headroom
   it left was consumed by atom COUNT, not by prose.
2. **No commit in the history reds the per-atom mean without also redding the file ceiling.**
   I expect zero.
3. **The per-atom MAX leg (12,288 B) has never fired either**, because the fattest atom I can
   currently measure is well under it — so the one bound that would NAME the atom to drain has
   never named one.

If (2) returns a non-zero count, the diagnosis is wrong and the per-atom control is doing its
job; the finding is spent and I will say so beside this file.

## How it will be measured

Walk the commits that touched either map half, reconstruct both halves at each (`git show`), and
for each compute: atom count, total bytes, mean B/atom, max B/atom — then ask which of the three
bounds each commit's tree violated. Population and byte totals come from
`tools.maturity_map_store` and `tests/design/test_simplifications_store.atom_byte_sizes`, the
same functions the controls use, so the answer is the controls' own verdict and not a re-derived
one.

## Why the answer matters either way

If the per-atom bound has never been able to bind, then every future breach of this ceiling will
arrive the way the two before it did and the way the 2026-09-17 one did: as a red on a tree-wide
test file, naming a total and no atom, at commit time, to whichever lane happened to write next.
Draining the map — which a sibling lane is doing as this is filed — resets the stock and changes
none of that. The remedy would be to derive the per-atom bound FROM the file ceiling and the
live population rather than from a snapshot of a cleaned map, so the informative control is the
one that fires first by construction.
