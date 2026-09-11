**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

# PRE-REGISTRATION — does P6's −2.45% come from FEWER accounts or DIFFERENT ones?

**Filed 2026-09-11, delivery seat, with both arms running and neither artefact on disk.** Checkable:
the two run outputs are `/var/tmp/p6_out_cull.json` and `/var/tmp/p6_out_matched.json`, and at the
moment this file was written `ls` returned *no such file*. The arms were launched ~3 minutes before
this was typed; the predictions below were fixed before any figure existed.

Grades the follow-up `SEAT_RESULT_P6_THE_CHOSEN_BOOK_IS_2_45_PERCENT_WORSE_ON_GROSS_MARGIN_2026-09-11.md`
filed as *"the one-variable follow-up that would separate them is a third arm"*.

---

## What P6 left unattributed

| | ARM A — cull | ARM B — chosen | Δ |
|---|---:|---:|---:|
| Gross margin | £383,688.97 | £374,295.73 | **−2.45%** |
| Settled accounts | 91 | 83 | −8 |
| Customer-years spent | 427.56 | 427.33 | −0.05% |

Two things moved together — **how many** accounts and **which homes**. P6 says so itself and
declines to attribute the number. This is the arm that separates them.

## ARM C, and why it is one variable against each of the other two

**ARM C — the home-blind cull, matched to the chosen book on every nuisance.** Selection is the same
systematic `int((j+1)r) > int(j*r)` positional rule ARM A uses — blind to every attribute of every
home — but applied *within each campaign year*, at that year's chosen-arm count, with the rule's
phase chosen to match the spend.

Solved on the real 500-candidate pool at the run's own base seed (20260724), before launch:

| | ARM A cull | ARM B chosen | **ARM C matched** |
|---|---:|---:|---:|
| Settled accounts | 91 | 83 | **83** |
| Customer-years | 427.562 | 427.335 | **427.332** |
| Mean tenure (cy/account) | 4.698 | 5.149 | **5.149** |
| Year mix (2016→2025) | 4/6/8/13/13/11/3/11/15/7 | 9/6/6/12/11/9/5/5/16/4 | **9/6/6/12/11/9/5/5/16/4** |
| Accounts shared with B | 12 | — | **13** |
| Sees the homes? | no | **yes** | no |

* **C against B is WHICH HOMES, and nothing else.** Count, year mix and customer-year spend are all
  held — spend to **0.0006%** — and only 13 of 83 accounts are common. The single remaining
  difference is that B chose its accounts by looking at the fabric axes and C could not see them.
* **C against A is HOW MANY**, with the selection principle held: both are blind to the homes.

**A prefix truncation was tried first and REFUSED.** Truncating the candidate pool to its first 449
entries also gives 83 accounts at 427.17 cy, and it books **zero accounts in 2025** — the exact
structural hole `_with_year_cover` exists to prevent. That is a second variable, so the spend match
would have been bought with a year the arm cannot reconstruct at any weight. Recorded because the
rejected construction is the one a reader would otherwise assume was used.

**The phase is tuned to the NUISANCE, never to the outcome.** The first stratified draft left a
−0.881% spend gap, a third of the effect being measured. Sweeping the systematic rule's starting
phase closed it to −0.0006%. The phase is chosen against customer-years — a quantity fixed before
any run — and the gross margin it is supposed to explain was unknown and unrunnable at the time.

---

## The predictions, fixed before the answer

**I am predicting against the drawn item's own reading, and that is deliberate.** The item says
*"the total follows the SIZE, not the composition"*, on the grounds that gross margin fell 2.45%
while customers fell 6.37%, so per customer the chosen book is richer. **Per customer is the wrong
denominator.** All three arms spend the same customer-years by construction, so the size of the
book is already held; dividing by head-count re-introduces the tenure difference that the fixed
budget created. Per customer-**year** the chosen book is £875.9 against the cull's £897.4 — it is
**poorer**, by 2.4%, which is the whole of the effect. If that reading is right, composition carries
almost all of it.

* **PC1 — composition carries more than half.** `|GM_C − GM_A| < |GM_C − GM_B|`; equivalently
  **GM_C > £378,992.35**, the midpoint.
* **PC2 — and nearly all of it.** The size leg is small in absolute terms:
  **`|GM_C − GM_A| / GM_A < 1.0%`**, i.e. GM_C ≥ £379,852.08. This is the sharp form and it is the
  one I expect to be graded hardest.
* **PC3 — the bad-debt leg is composition, not size.** ARM C's bad debt is nearer ARM A's £11,675.76
  than ARM B's £14,400.86: **BD_C < £13,038.31**. P6 flagged +23.34% on a smaller book as its most
  interesting unexplained number; if the chooser pulling in tails is what causes it, a home-blind
  arm of the same size should not show it.
* **PC4 — the comparability control, and it can void the other three.** Bills issued in ARM C are
  within **±1.5%** of both ARM A's 10,924 and ARM B's 10,841. Bills track customer-years, which are
  held across all three arms by construction. **If PC4 fails the arms are not spend-comparable and
  PC1–PC3 are withdrawn rather than graded** — a decomposition over arms that did not buy the same
  thing is not a decomposition.

**PC5 — the falsifier, and it is not about the chooser at all.** ARM A is being re-run in this
worktree, concurrently with ARM C, purely as a reproduction check: it must return
**£383,688.97 gross margin to the penny**. This worktree is a new variable — a different checkout,
a different day, a different process pair — and the published ARM A figure was produced somewhere
else. **If ARM A does not reproduce, ARM C is uninterpretable and the whole table is withheld**,
exactly as P6's own concurrency falsifier was written.

## What this arm cannot say

It cannot say the chooser is wrong. The case for choosing was 1.553× on worst-axis KS and was never
a margin case. This arm prices that choice; it does not re-open it. Both arms run `SIM_FAST_MODE=1`,
identically, so the **differences** are clean and the absolute pounds are not comparable to
`docs/reports/run_output_latest.json` and must not reach a page as a headline.
