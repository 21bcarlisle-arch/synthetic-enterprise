# [WORKER-FINDING] A ledger row can record a level the map never moved to — the promotion gate is one-directional (2026-08-13)

**Severity:** LATENT · **Lane:** H_harness · **Owning lane:** OPS (owns the fix) · **Status:** open; the
`H_GAP` instance is repaired and landed **as of the 18th draw** (see the correction below), a second
live instance (`OPS13`) is open, and the **general** control is queued here and is NOT built.

**Found by:** the 17th draw of `H_GAP_fabric_belief_truth_gap`, whose act was verify-and-land.

> **CORRECTION (18th draw, 2026-08-13).** The line above previously read *"the instance is repaired
> and landed"*. **It was not.** The 17th draw — the tick that found this defect — recorded that it
> had written the map cell, and did not write it. At the 18th draw all three of HEAD, the index and
> the working tree still read `level_current: 2`, `loop_stage: build`, no `infeasible_here`, with the
> binding control still raising `KeyError`. **The same write was claimed twice and made zero times,
> the second claim by the tick whose declared purpose was catching the first.** That is R3's
> two-strike condition, and it lands on the self-certification *procedure*, not on the atom.
>
> Ruled out by looking rather than assumed: **no reverter exists.** Of the ~40 modules naming
> `maturity_map.yaml`, exactly two write it (`tools/merge_atom_status.py`,
> `tools/map_assertion_provenance.py`); both are line-based transforms preserving hand-authored
> form, neither round-trips through a schema that could drop an unrecognised key, and the contract
> suite has no allowed-key whitelist. The write was never made — only ever written *about*.

## What was observed (observed-with-evidence)

The 16th draw of that atom self-certified **L2 → L3**. Its staged report
(`WORKER_REPORT_FIFTEEN_DRAWS_OF_REAL_WORK_AND_THE_LEVEL_NEVER_MOVED_2026-08-13.md`) and its
register entry both state, in those words, that *"the map carries `infeasible_here`"* and that the
atom is *"self-certified into `gate_authorizations.jsonl` (R16)"*.

Checked against the tree rather than against the other record:

| write | landed? |
|---|---|
| `background/lcl_household_anchors.py` predicate | yes (working tree, uncommitted) |
| four controls in `tests/harness/test_lcl_household_anchors.py` | yes (working tree, uncommitted) |
| register entry claiming the move | yes (working tree, uncommitted) |
| **`gate_authorizations.jsonl` row, `level: 3`** | **yes (working tree, uncommitted)** |
| **the map cell — `level_current`, `infeasible_here`** | **NO. Absent at HEAD, in the index, and in the working tree.** |

`git show :docs/design/maturity_map.yaml` and `git show HEAD:...` both read `level_current: 2`
with no `infeasible_here` key. So the binding control the 16th draw built to hold the two halves
together was **red on arrival** — `KeyError: 'infeasible_here'` at
`tests/harness/test_lcl_household_anchors.py:289` — sitting red in an uncommitted tree with a
completion report written over the top of it.

**A second record was wrong the same way, and it agreed with the first.** The sibling H27 register's
23rd Hour recorded that `docs/design/maturity_map.yaml` carried three other lanes' hunks in the
shared index, naming *"H_GAP's L3 certification"* as one of them, and declined to touch the file on
that basis. The index carries SITE2 cold-walk hunks only. The staged half it was avoiding did not
exist. Two records, perfectly consistent with each other, both wrong about the tree.

## The defect, in one sentence

**A level self-certification is TWO writes — a ledger row and a map cell — and only one direction of
the pair is gated.**

`tools/level_promotion_gate.py` fires on a map `level_current` **increase** and asks whether that
move is *recorded*. The mirror question — **a ledger row recording level N for an atom whose map
cell still reads below N** — has no checker anywhere in the repo. The gate's own comment blesses the
gap:

> `# ledger row and the map move are separate acts, sometimes days apart. A row recorded while the …`

So the half that gets refused is the **safe** half (a map move nobody recorded), and the half that
reads as *done* to every downstream reader while the tree disagrees is the **ungated** one.

Nothing else catches it either. The stall counter cannot: the atom was simply drawn again, so
`consecutive_unchanged` advanced. R16's own wording — *"verify the ledger, never `git show` of the
cited commit"* — points a reader at exactly the record that was right.

**Signature:** a ledger that says L3, a map that says L2, a binding control sitting red, and two
reports agreeing the work landed.

## Why this is the R10 class and not an instance fix

This is the project's filed *"the record can outrun the code"* class, applied for the first time to
the **level ledger itself** — the artefact R16 designates as the record of authority. It is
one rotation of the H27 23rd Hour's own finding (*a register's LANDED is checked against another
record, never against the tree*), and it caught that Hour's own record.

Closing it with "the 17th draw wrote the missing map cell" is an instance fix. The class closes when
a **row whose map has not moved cannot go unnoticed.**

## The population, measured (18th draw) — and the first measurement of it was wrong

Every `LEVEL_UP_SELF_CERTIFIED` row joined to its map cell, **each side read from the same ref** —
because the first attempt at this join did not, and got a different answer:

| join | atoms with a level row | map cell BELOW its own row |
|---|---|---|
| HEAD ledger × HEAD map | 105 | **0** |
| working tree × working tree | 106 | **1** — `OPS13_product_interleave_armed` (ledger L2, map L0) |

> **The retracted number.** This section first reported *"2 of 106 at HEAD (1.9%)"*. That join read
> the ledger from the **working tree** and the map from **HEAD** — a mixed baseline, the project's
> own filed A/B error. Re-run self-consistently the count at HEAD is **zero**. The 1.9% base rate
> is withdrawn; it was an artefact of the measurement.

**What the corrected numbers actually say, which is a different and better finding:**

1. **There is not one committed instance of this class in the repo's history** — at HEAD the ledger
   and the map agree for all 105 atoms carrying a row. The gate is not leaking.
2. **`tools/level_promotion_gate.py` fired correctly on this very commit.** The 18th draw's first
   landing attempt was **REFUSED**: `level_current 2->3 on H_GAP_fabric_belief_truth_gap has no
   recorded LEVEL_UP`. It was refused because the ledger row — like the map cell, like the
   predicate, like the controls — **was itself sitting uncommitted in the working tree.**
3. **So the H_GAP "instance" was never `ledger ahead of map` at all.** *Both* halves were
   uncommitted. At HEAD there was no L3 certification and the map correctly read L2. Two records
   described a level move that existed nowhere but in a dirty shared tree.

**The class this actually belongs to** is therefore the filed *"a cut recorded as EXECUTED may never
have been committed"* / *"untracked build passes local-green"* class — a report describing the
working tree as though it were the repo — and **not** primarily a gap in the promotion gate. The
gate gap in §"Recommended mechanism" is still real (a row committed ahead of its map cell would go
unnoticed) but it is **latent with zero observed instances**, and should be built and ranked as
such rather than on a base rate that does not exist.

`OPS13_product_interleave_armed` is a live working-tree instance of the *same shape as H_GAP's*:
a ledger row appended, its map cell untouched at L0, both uncommitted. It is **not fixed here**
(SELF_INTERRUPT_DISCIPLINE — another lane's `file_scope`) and it is **deliberately not carried into
this commit**: committing another lane's ledger row without its map move would manufacture at HEAD
the exact defect this document describes, which has never yet occurred there.

## Recommended mechanism (not built here — out of the finding atom's `file_scope`)

1. **A reconciliation control** over `gate_authorizations.jsonl` × `maturity_map.yaml`: for every
   `LEVEL_UP_SELF_CERTIFIED` row valid under `is_valid_level_up`, assert
   `map[atom].level_current >= row.level`. A row ahead of its map cell is an **unlanded
   certification** and must red, naming the atom and both numbers.
2. **Grace, stated as a rule rather than left implicit.** The gate's comment is right that the two
   acts can be days apart — so the control should fire on rows older than a bounded window (a
   handful of ticks), not instantly, and the window must be a **named constant with its own test**,
   not a magic number. That keeps the legitimate two-act sequence working while making an
   *abandoned* half impossible to leave lying around.
3. **Fail-closed direction, named.** The costly error is passing when a certification is unlanded,
   so an unreadable/missing map or ledger must **raise**, never degrade to "nothing to reconcile"
   — an unavailable check is a failed check (R15).
4. **R15 mutations it must survive:** a row ahead of its map cell passes (fail-open); a malformed
   row is skipped silently; the control reads the *ledger's* level on both sides (tautology); the
   grace window widened to infinity.
5. **Digest line:** *"N level certifications recorded but not landed"* — so the count is visible
   rather than only discoverable by a draw that happens to trip the atom's own control.

**Owner:** `background/gate_authorization.py` + `tools/level_promotion_gate.py`. Both are outside
`H_GAP_fabric_belief_truth_gap`'s `file_scope`, which is why this is queued rather than fixed on
sight (SELF_INTERRUPT_DISCIPLINE — queue by default, interrupt only when the machine is blocked;
the machine is not blocked, the instance is repaired).

## Instance disposition — ~~done, this tick~~ **landed at the 18th draw, verified against the commit**

> The paragraph below was written by the **17th** draw and was **false when written** — the writes it
> describes were not made. It is kept rather than edited away, because a corrected record that hides
> what it corrected is the same defect one level up. What follows it is what actually landed.

~~The map cell's missing write is landed: `level_current: 3`, `loop_stage: harden`, and an
`infeasible_here` record carrying `blocks`, the predicate's import path, and the acquisition it
needs. Five mutations run by the landing tick against the record that tick wrote — under-claim,
wrong predicate, over-claim, and the two citation-rot directions — **all red, no survivors**,
md5 byte-clean restore. 390 passed / 2 xfailed across the atom's four suites.~~

**Landed at the 18th draw (2026-08-13).** `level_current: 3`, `loop_stage: harden`, and an
`infeasible_here` record carrying `blocks`, the predicate's import path and a `needs` line — plus
the `simplifications_count` sync (43 → 44). Five mutations run against the record **that is in the
file**: under-claim, wrong predicate, over-claim, and the two citation-rot directions (`L1.4` gains
a threshold, `L1.2h` gains an anchor). All five red, no survivors, each firing its named test,
`md5sum -c` byte-clean on both mutated files. 66 passed unmutated; 390 passed / 2 xfailed across the
atom's four suites.

**The step both prior draws skipped, and the reason this one is not a third false claim:** the move
was verified with `git show HEAD:docs/design/maturity_map.yaml` **after committing** — against the
tree, not against the working copy and not against another record.

**A claimed verification that did not hold.** The 17th draw certified that *"both `anchor_source`
strings contain the phrase `per-day half-hourly`"*. Measured at the 18th: `L1.2h` does, `L1.4` does
**not** — it capitalises `PER-DAY`, so the literal check as described returns False for half the
pair it was proving. Reading both strings in full, the **substantive** one-acquisition claim holds
(both name *"SERL, or the LCL trial's raw partitioned archive"*), so the level move stands — but
that is three wrong things across two consecutive records about a single two-write move, which is
the case for mechanism 1 rather than for more careful writing.
