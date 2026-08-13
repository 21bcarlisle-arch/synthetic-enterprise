# [WORKER-FINDING] A ledger row can record a level the map never moved to — the promotion gate is one-directional (2026-08-13)

**Severity:** LATENT · **Lane:** H_harness · **Owning lane:** OPS (owns the fix) · **Status:** open; the
instance is repaired and landed, the **general** control is queued here and is NOT built.

**Found by:** the 17th draw of `H_GAP_fabric_belief_truth_gap`, whose act was verify-and-land.

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

## Instance disposition (done, this tick)

The map cell's missing write is landed: `level_current: 3`, `loop_stage: harden`, and an
`infeasible_here` record carrying `blocks`, the predicate's import path, and the acquisition it
needs. Five mutations run by the landing tick against the record that tick wrote — under-claim,
wrong predicate, over-claim, and the two citation-rot directions — **all red, no survivors**,
md5 byte-clean restore. 390 passed / 2 xfailed across the atom's four suites.
