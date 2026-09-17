**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `H41_the_map_ratchet_has_no_ongoing_drain`

# The map's per-atom budget was built so the size ratchet would stop arriving as an uninformative wedge, and it has been unable to fire first for 297 commits

**Filed 2026-09-17 by the delivery seat (lane 0), while draining the map under
`SEAT_FINDING_THE_MAP_IS_185_BYTES_FROM_ITS_RATCHET_CEILING_..._2026-09-17`. Pre-registered
before measurement:
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_THE_PER_ATOM_MAP_BUDGET_HAS_EVER_BEEN_THE_BINDING_CONSTRAINT_2026-09-17.md`.
Two of three predictions held, one was refuted and is corrected below.**

## The mechanism

`tests/design/test_simplifications_store.py` carries three bounds on the maturity map:

| bound | value | what its refusal tells the reader |
|---|---|---|
| `MAP_SIZE_CEILING` | 409,600 B, both halves | a TOTAL. Names no atom, no field, no author. |
| `MAP_MEAN_BYTES_PER_ATOM` | 1,400 B | the mean. Names the population. |
| `MAP_MAX_BYTES_PER_ATOM` | 12,288 B | **one atom, by name.** |

The second and third were added by H41 for a stated reason, in the control's own words: a
whole-file ceiling "twice arrived as a publish wedge carrying no information about what to fix",
and cannot tell *"the company did more work"* (fine, and the map's whole purpose) from *"one atom
accreted 4KB of prose"* (the thing that actually needs draining).

**But the mean budget is a FIXED per-atom number multiplied by a GROWING population, checked
against a FIXED total.** `1,400 x 350 atoms = 490,000 B` against a 409,600 B ceiling: at today's
population the mean leg authorises **80,400 bytes the file ceiling refuses**. It cannot bind
first. The crossover is 409,600 / 1,400 = **292.6 atoms**, and the map has held more than that
since 2026-08-12.

That is arithmetic over two constants, so by this project's own rule it is unfalsifiable and is
the motive for the measurement rather than its result.

## The measurement

Every commit that touched either map half, both halves reconstructed at each commit with
`git show`, sized with the controls' own `atom_byte_sizes` and `map_text` rather than a
re-derivation — so the verdict below is the controls', not mine. Restricted to the era the
pre-registration named: **population >= 293 atoms, 2026-08-12 to 2026-09-17, 297 commits.**

| | commits |
|---|---|
| whole-file ceiling breached | **3** |
| mean per-atom budget breached | **0** |
| max per-atom budget breached | **0** |
| **per-atom red while the file ceiling was GREEN** (the informative-first case) | **0 of 297** |

Observed range in that era: mean 910–1,385 B/atom; largest atom 10,495–12,221 B.

**Every breach in the era was the uninformative kind.** The bound that would have named an atom
has never once fired first, including on 2026-09-17 when the ceiling cost a full commit cycle to
diagnose and named `tests/design/test_simplifications_store.py` to an author who had touched the
maturity map.

## Correcting a prediction, beside the result

I predicted zero informative-first commits over the whole history. Over the **whole** history
there are 189 — so that prediction was wrong as stated, and the number is only zero once the
population passes 293. The error is instructive rather than incidental: those 189 are the era
when the map held fewer atoms than the crossover, i.e. **the per-atom leg worked exactly as
designed until atom count ate it.** It did not fail. It was outgrown, silently, by the success
of the thing it measures, and nothing anywhere could notice — which is the same shape as the
defect it guards.

## What is NOT wrong here

The **max** leg is alive and nearly bit: it peaked at 12,221 B against a 12,288 B cap — **67
bytes** — and stands at 10,757 B (`SITE1_expert_doors`) today. One atom accreting prose is still
caught and still named. The hole is specifically the mean leg, and with it the whole-file
ceiling's only route to saying *which row to drain*.

## The remedy

1. **Derive the mean budget from the ceiling and the live population instead of from a snapshot
   of a cleaned map.** `MAP_SIZE_CEILING / len(atoms)` is the same constraint as the file ceiling
   by construction — never slack, never a second number to maintain, and it moves as the map
   grows. What it adds over the ceiling is that it is expressed per atom, so its refusal can rank.
2. **Whichever bound refuses, the message must name the fattest rows.** The sizes are already
   computed — `atom_byte_sizes` returns the whole ranking and the control throws it away except
   for the atoms over the max cap. A refusal that ended *"the ten fattest rows are ..."* converts
   the wedge into a drain list, which is the entire difference H41 was reaching for.
3. **Do not lower `MAP_MEAN_BYTES_PER_ATOM` to a hand-picked smaller number.** Today's mean is
   1,170 against a derived 1,170, so any fixed number tight enough to bind is red on arrival —
   which is why deriving it is not a refinement of the current shape but the only version of it
   that works.

## The falsifier

    python3 -c "from tools import maturity_map_store as m; \
      from tests.design.test_simplifications_store import MAP_MEAN_BYTES_PER_ATOM as B; \
      n=len(m.load_atoms()); print(B*n - m.MAP_SIZE_CEILING)"

A positive number is the slack the mean budget authorises above what the file ceiling permits —
i.e. the bytes over which the informative control is guaranteed silent. It is 80,400 today and
grows by 1,400 with every atom minted. Zero or negative means someone has derived it and this
finding is spent.
