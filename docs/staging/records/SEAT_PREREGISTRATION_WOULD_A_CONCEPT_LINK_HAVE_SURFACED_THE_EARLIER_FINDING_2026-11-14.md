**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: would a concept link have surfaced the earlier finding? (2026-11-14)

*Filed before the tagger exists or has run. Steer:
`docs/staging/advisor/DIRECTOR_STEER_WOULD_LINKING_FINDINGS_TO_CONCEPTS_HAVE_CAUGHT_OUR_REPEAT_DEFECTS_MEASURE_IT_2026-11-14.md`.*

## Facts read before the run

- `docs/design/the_map/concepts.yaml` was created on **24 Oct 2026** (ebc3c34e2e). It now holds **71**
  concepts, not 76 as the steer says.
- Today's register has no concept whose prefLabel or altLabel carries "VAT" or "bill shock". "Direct
  debit" appears in `collect.amount` only as the multi-word labels "setting the direct debit amount",
  "dd amount" and "direct debit review".
- Every member of all three families was filed before 24 Oct.

## The property

A later finding L is **caught** if some earlier finding E in its family, filed on a strictly earlier
date, carries at least one concept tag that L also carries. A family is **caught** if most of its
later members are caught. Beside each catch I report how many staging items were filed under the
shared concept up to L's date, because a list of 400 is not memory.

**Tagger.** It uses `tools/the_map._terms` and `_term_pattern`, the module search's own matching.
Text A is the filename words plus the H1 title. Text B is A plus the first 1,500 characters of the
body. A is primary, because it is what the finding says it is. The tagger writes nothing to the
staging files.

**Two registers.** *Strict:* the register as of L's filing date, from git. Before 24 Oct there is no
register, so nothing is tagged. *Hindsight:* today's register. That is an upper bound, and the steer
names it as the main failure mode.

## The families, fixed before tagging (filename selection, from `docs/staging/**`)

1. **VAT.** Findings (`*FINDING*`) whose filename carries `VAT` as a word.
2. **Half-month first direct debit / stub-period amount.** `*FINDING*` or `*RESULT*` filenames carrying
   `HALF_A_MONTH` or `_STUB_`, excluding the harness's own `WORKER_RESULT_*DRAWN_WORK*`.
3. **Bill shock.** `*FINDING*` filenames carrying `BILL_SHOCK`.

## Predictions

| Family | Strict | Hindsight, text A | Hindsight, text B |
|---|---|---|---|
| VAT | not caught (no register) | not caught: no VAT concept, and any shared tag will be broad | not caught |
| Half-month DD | not caught (no register) | not caught: titles say "first direct debit", not "dd amount" | caught, through `collect.amount` |
| Bill shock | not caught (no register) | not caught: no concept | not caught |

Overall prediction: **strict 0 of 3; hindsight 0 of 3 on A and at most 1 of 3 on B.** By the steer's
rule (two of three), that means **drop it**. I also predict the deeper reason: the repeat defects were
*not named concepts at all* when they repeated, so a link to a concept cannot surface them. The
working lever would be minting the concept, which is the second-home check the register already has.
