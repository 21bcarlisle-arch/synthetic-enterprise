# SEAT RESULT — the 154-account book was in git all along, and the belief is flat across it

**Severity:** FINDING (publishable; no defect in running code)
**Date:** 2026-09-22
**Lane:** Lane 0 delivery —
`the-companys-churn-belief-is-flat-across-the-book-where-the-world-responds-nine-fold`
**Landed:** see the commit this record is part of.

---

## What was outstanding

The drawn item asked three things. Two landed earlier today: where the step is and what produces
it (`7179a7087`), and a published statement of it on the arms page (`cff89ebaf`). The third was
explicit and was NOT discharged:

> GET THE REAL BOOK'S EAC DISTRIBUTION — the 154 settled billing accounts behind
> `site/data/value_arms.json` — and state how many of them fall on each side of that step.

Both prior artefacts say so in terms. `churn_belief_size_response.json` carried
`population_is_not_the_published_arms_book`: *"whether the 154-account book fell differently
against the knee is NOT ESTABLISHED"*, and the page carried the same caveat in amber. The stated
reason was that the per-account rows are not persisted and reconstructing them means re-running
the arms — a run that takes hours.

## The premise was wrong, and it was wrong in the cheap direction

**The rows are persisted. They are in git.** `site/data/customers.json` is one row per billing
account; it is regenerated on each run; and the run artefact records the commit its modules were
bound at, in `producing_commit.commit`. `git show b329e702b:site/data/customers.json` is the book
the published arms were scored over. No re-run, no reconstruction — the bytes the run was reading.

This is the cheapest class of finding this project keeps re-learning: an honest *NOT ESTABLISHED*
that was never re-asked. The first pass was careful and correct about everything it measured; what
it did not do was ask whether the thing it wanted was versioned. Two commands settled it.

## It is reconciled before it is believed

A commit-pinned blob is an **inference** about which book ran, not an observation of it —
`producing_commit` records which CODE was bound, which is an excellent reason to expect the roster
at that commit and not a measurement of it. So `arms_book` recomputes the four counts the run
independently published about its own book (`book_identity.control_arm`) from the blob, and
refuses with the mismatching field named if any disagree.

| count | the run recorded | the roster at `b329e702b` | HEAD's book |
|---|---|---|---|
| `billing_accounts_settled_in_window` | 154 | 154 | 164 |
| `with_an_electricity_leg` | 136 | 136 | 146 |
| `with_a_gas_leg` | 90 | 90 | 98 |
| `dual_fuel` | 72 | 72 | 80 |

All four agree exactly, and the current book fails all four. The reconciliation is what turns the
inference into evidence, and it is not decorative: pointing this at the current file would have
silently measured a different population — the exact failure the first pass was being careful
about, entered through the repair.

## The answer

Over the **154 accounts the published arms were actually scored over**, at the declared £3,000
bill knee:

- **217 of 226 supply legs sit below it** (96.0%), where the company's belief has no consumption
  term at all.
- **217 of 224 DOMESTIC legs** — so the company's per-customer churn belief cannot tell apart any
  but seven of the households in the book it trades.
- Over those same accounts the world's own `churn_position_multiplier` spans **11.28x**, because
  it scales the price differential by each household's own annual spend.
- The asymmetry is unchanged and is the sharper half: both legs above the knee in the SME segment
  are in the one segment the world does NOT read a household bill for. The belief varies exactly
  where the world does not.

The tree's current 164-account book gives 235 of 242 and 11.57x. **The conclusion does not turn on
which book is used** — which is worth saying plainly, because it means the first pass's published
sentence was not wrong, only about the wrong population. What changed is that the page's counts
are now about the page's own accounts, and the amber caveat has inverted into a provenance line.

## The mutation that was silent, and why it was a MISSING LEG

`_roster_at_commit` was mutated to ignore its argument and return whatever the checkout holds —
the "about the right size" fail-open this whole reconciliation exists to stop. In a clean worktree
it was **SILENT**: all eight legs green, every published figure correct.

The cause is a coincidence worth recording. HEAD's *committed* `site/data/customers.json` is
itself a 154-account book, so in any clean checkout the mutation reconciles perfectly. Only in the
shared tree — where a daemon has regenerated the working copy to 164 accounts — does the same
mutation measure the wrong population and say nothing. **A control that is green in a worktree and
blind in the tree it guards is the worst of both.**

Not an equivalence, and not taken as one. Repaired by pinning the property instead of today's
agreement between two books: a commit that cannot exist must produce nothing
(`_roster_at_commit("0"*40) is None`). The mutation is caught after the repair.

## What this still does not say

- **It does not price the gap**, and nothing here is an instruction to make the belief vary. R12.
- **`BILL_STRESS_THRESHOLD_GBP` still has no origin.** It is on this repo's own no-origin debt
  list and `churn_model`'s docstring justifies it with *"the threshold where empirically customers
  start actively switching"*, citing nothing. Where the knee falls is set by that number. Reported
  again rather than re-picked: replacing an unsourced number with a different invented one is not
  a repair.
- **The bill used is an upper bound** (whole annual revenue, standing charge included; the model's
  input takes the standing charge back out). It overstates the model's input and can therefore
  only move legs INTO the above-knee set, so the 217-below count is safe in the direction claimed.
- The epistemic wall is untouched either way. A real supplier meters its own customers, which is
  why the world's own `churn_position_multiplier` calls consumption *"something the company can
  legitimately act on."*

## Pointer

- Measurement: `tools/churn_belief_size_response.py::arms_book`
- Artefact: `docs/observability/churn_belief_size_response.json` → `arms_book`
- Control: `tests/tools/test_churn_belief_size_response.py::test_the_arms_book_is_identified_and_a_near_miss_is_refused`
- Surface: `site/capabilities/index.html`, the flat-churn-belief block, via
  `site/data/value_arms.json` → `churn_belief_size`
- Predecessors: `7179a7087` (the measurement), `cff89ebaf` (the first publication)
