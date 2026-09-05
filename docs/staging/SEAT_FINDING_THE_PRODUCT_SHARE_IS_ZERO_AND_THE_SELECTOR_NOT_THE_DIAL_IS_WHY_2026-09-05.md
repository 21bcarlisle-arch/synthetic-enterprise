**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** unminted

# The product share is 0%, and the selector — not the dial — is why

**Found:** 2026-09-05, delivery seat, actioning `DIRECTOR_CANON_PRODUCT_AND_MACHINERY_2026-09-05`
§4 ("measure the split, with the ratio itself becoming a finding when it goes wrong"). Measured with
`tools/product_machinery_split.py`, written for it.

---

## The measurement

```
  last  50 commits: product   0  machinery  39  neither  11   product share   0.00%   BELOW FLOOR
  last 100 commits: product   0  machinery  70  neither  30   product share   0.00%   BELOW FLOOR
  last 200 commits: product   3  machinery 140  neither  57   product share   2.10%   BELOW FLOOR
  last 400 commits: product  15  machinery 255  neither 130   product share   5.56%   BELOW FLOOR
```

**Zero product commits in the last hundred.** The director's reading of the night — sixty-six
commits, none on R1 — was if anything generous.

## And it is not a recent regression

Over the trailing 2000 commits, in 72 overlapping 200-commit windows:

```
min 2.10%   p25 11.11%   median 16.03%   p75 20.25%   max 28.74%
```

**The product share has never once reached 25%.** This is the standing state of the project, not a
bad week. It also means the floor could not be derived from the record: a threshold set at any
percentile of that distribution would go green on the pathology. It is set at 25% as a target whose
authority is the canon, and it is red today at 0.00%, correctly.

## The cause, and it is mechanical

The re-rank moved eleven atoms to dial 45. The dial orders atoms **within** the final draw, and four
rungs return before that draw is ever reached. One of them was doing something sharper than
ordering: **RUNG 1c, the BLOCKING-finding lane exclusion, was removing the three core R1 atoms from
candidacy entirely** — `EP17_varied_population_draw`, `PB4_engagement_separated_from_elasticity` and
`PB5_pounds_or_percent_resolved` all sit in lane `W2_customer_generator`, and a BLOCKING finding sat
in that lane. They could not be drawn at any dial.

So the director's own diagnosis — *"the weights moved and the selector didn't"* — is confirmed, and
the mechanism is more specific than a weighting problem: the atoms were not outranked, they were
excluded.

## What changed

1. **RUNG 1c exempts product-priority atoms** (`_drop_lane_blocked`). A blocking finding still
   excludes ordinary same-lane feature work and may no longer exclude what the director ranked
   first. Unconditional rather than threshold-gated, because the canon's own test for essential
   machinery — a reader's page broken, or the machine unable to land work — is *already* the
   priority-zero rungs, and `_priority_zero_active` is their exact enumeration. Anything still
   sitting in rung 1c has by construction failed that test.
2. **RUNG 1e: an unread director document preempts every self-filed finding.** The staging RANK was
   never the problem and checking that first stopped a fix to the wrong thing —
   `staging_rooms.work_queue` already ranked the canon 1st and 2nd of 76. What it lacked was
   PREEMPTION: a BLOCKING finding draws itself, while a director canon carries LATENT severity and
   is seen only at orientation, which does not arrive while machinery keeps preempting.
3. **The floor**: `_product_starvation_stretch`, keyed to a product atom being NAMED in a commit.
4. **The split**, measured by `tools/product_machinery_split` and quoted on the rung that fires.

## Three things I got wrong building this, kept because each is the class

- **A scope-keyed starvation detector would have been fail-open and I wrote it first.** Measured
  over the same twenty hours: 148 commits, zero naming a product atom, and **123 file-touches
  inside a product atom's declared `file_scope`**. The R-set's scopes include `tools/`,
  `docs/design/` and `simulation/` — what machinery work touches all day — and three of the eleven
  declare no scope at all. It would have read "product progress is happening" continuously.
- **The unread-document rung reported two false positives from a 400-commit window.**
  `DIRECTOR_CONSOLE_2026-08-31` and `_2026-09-01` had been cited, four days and 400 commits ago. On
  a PREEMPTING rung a false positive costs exactly the product time the rung defends. Now keyed to
  the whole history. It also had to learn that `DIRECTOR_CONSOLE_*` files are auto-generated
  verbatim captures carrying severity RECORDED — nothing ever cites them, so a prefix-keyed rung
  would have preempted on two machine-written records forever and never drained.
- **I wrote a derivation for the floor citing a distribution I had not measured** ("0.09 to 0.62,
  median 0.30"). The numbers were written to justify a threshold already chosen. The real
  distribution is above and refutes it. It is recorded in the constant's own comment, because the
  rule it broke is the one the file enforces.

## What would close this

The product share crossing 25% on a 100-commit window, with `tools/product_machinery_split` as the
falsifier. It is red now and should stay red until the lanes actually move.

Not written as a **Discharged:** field, deliberately — that field is a claim the repair has landed,
and the ratio is still 0.00%.
