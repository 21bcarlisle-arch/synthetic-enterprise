**Severity:** INFO · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# PRE-REGISTRATION — how wide is `comments_are_evidence=True` in `distinctive_lines`, and does the narrow third reading exist?

*Filed by the delivery seat from an isolated worktree (`/var/tmp/se-seat-executor`, HEAD `89e94ec5a`),
2026-09-24, BEFORE running the measurement. Step 1 of the remedy ordered by
`docs/staging/done/SEAT_FINDING_NO_RULE_IN_THE_STALE_COPY_MODULE_CAN_SEE_A_COPY_WHOSE_ONLY_LOSS_IS_A_LANDED_COMMENT_2026-09-24.md`
(landed `89e94ec5a`), which says in terms: "Flipping it at this call site is one character and is
**wrong without a measurement**."*

## The premise, re-measured at draw time

All three commits the item cites (`89e94ec5a`, `aebd8683a`, `8d84c67b5`) are ancestors of
origin/main — but the item's work is a MEASUREMENT and a REMEDY, neither of which those commits
contain. `89e94ec5a` is the finding that COMMISSIONS this work, not its discharge. Checked on the
live shared tree `/home/rich/synthetic-enterprise` (HEAD `3c0e0b315`, `behind=22 ahead=0`):
`tools/stale_copy_refusal.py:582` still reads `not _trivial(ln)` with the default
`comments_are_evidence=False`, and `tools/refresh_to_head.py:616-621` still prints
"it does not predate the last landing there and it deletes no name … an ordinary edit".
**The premise is NOT spent.** The duplicate-work note names this item's own id, held by this seat;
it is the same work, so the work is what I take, not a disposition.

## The population, fixed before the prediction

`git diff --name-only HEAD -- '*.py'` on the shared tree: **52 paths**. That is the denominator and
it is not the answer. The judgement tree is `origin/main` (the finding's own frame — the shared tree
is behind, so `HEAD` is not the landing that matters); I will report `HEAD` beside it.

## The four predictions

**P1 — the flip is WIDE.** Counting comments in `distinctive_lines`' STRONG set makes
**≥ 8 of the 52** paths gain a `judge()` complaint they do not have today, against `origin/main`.
Point estimate **12–25**. "Wide" for the purpose of the finding's step 2 is **> 3**.
*Why: this repository's comment density is exceptional — the module under measurement averages
several prose lines per definition — so nearly every landing adds unique comment lines, and the
finding's own record says clock-staleness is the normal resting state of a shared checkout.*

**P2 — the flip also SUBTRACTS, and nobody has named that direction.** At least **1** path LOSES
its present complaint under the flip. Mechanism: rule 1's refusal leg is
`len(missing) == len(distinctive)`, so adding comment lines to `distinctive` that the copy HAPPENS
to carry breaks the all-or-nothing equality and demotes a `predates_landing` to at best a
clock-gated `predates_landing_carrying_some`. A one-character flag flip is therefore not monotone,
and "is it wide?" is the wrong question asked alone.

**P3 — the target path gains a complaint under the flip.**
`tests/background/test_a_swept_row_names_the_sibling_that_holds_its_windows_commit.py` returns a
`Loss` under the flip where it returns `None` today. *If P3 is false the finding's own diagnosis of
the four-rule blindness table is wrong, and that is the more important result.*

**P4 — the narrow third reading exists and is NARROW.** A reading that asks only *does this copy
hold NONE of a contiguous comment block the landing ADDED, while holding the lines that landing
REMOVED* (a revert, not a rewrite), clock-gated on `taken_before`, fires on the target path and on
**≤ 3 of the 52** in total. The revert-vs-rewrite discriminator is the whole of the narrowness: a
reformat or a re-wrap supplies its own prose, which is neither the landing's added lines nor the
lines the landing superseded, so it cannot satisfy both halves.

## What would refute each

- P1 refuted if the gain count is ≤ 3 — then the flag flip IS the remedy and the third reading is
  unnecessary complexity. I would take the one character and delete the design.
- P2 refuted if no path loses a complaint. That would mean the equality leg is insensitive to the
  flip on this population, which I do not believe and would want to know.
- P3 refuted if the target path stays `None` under the flip. Then the missing reading is not the
  comment filter at all and the finding needs re-opening, not discharging.
- P4 refuted if the narrow reading fires on > 3 paths (it is not narrow, and is a second flag flip
  wearing a longer name) or fails to fire on the target (it does not reach the case it was built
  for, and is dead code).

## What "done" means for this direction — decided here, since no exit test is written for it

Three things, and the third is the one the finding says must happen "either way":

1. This pre-registration, landed, with the measured answers written BESIDE the predictions
   including any that are refuted.
2. Whichever remedy the measurement selects, wired into `judge` with a control that can fail — a
   test whose subject is the target copy's own shape, not today's count.
3. `refresh_to_head`'s `NOT_SUPERSEDED` text stops making a positive claim about evidence no rule
   read. An honest verdict NAMES its unread populations; the present one asserts "an ordinary edit"
   on a reading it never made.
