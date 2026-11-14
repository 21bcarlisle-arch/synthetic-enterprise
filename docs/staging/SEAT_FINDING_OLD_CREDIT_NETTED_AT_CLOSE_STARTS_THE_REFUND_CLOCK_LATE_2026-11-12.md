**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`
**Knowledge:** home-moves -- `docs/market_research/home_moves.md` s.8.8d (the refund waits for its money)

# Old credit netted at close starts the refund clock late (2026-11-12)

*Found while grading `n29-setoff-ceiling-graded-on-fresh-book`. It is the one of the five
`INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` breaches that a fresh run will not clear.*

## What was seen

On SYN-2016-139, origin 90279e5318's pages over the 6fe7827ab2 run read:

- 13 Apr 2022: the final bill INV29537 is raised for 11.52. The balance is −32.04.
- 27 Apr 2022: "Direct debit returned", 0.00. On the same day, `credit_applied` 0.00 reads: "Account credit of
  GBP11.52 (the household's payment of 2021-05-07) netted against this bill".
- 12 May 2022: refund 32.04.

The runner starts reg 6D's clock at the last bill or cash on the page, which is 13 Apr. Ten working days later is
29 Apr, and the account is still 32.04 in credit then. The run's refund log reads `request_date` 2022-04-27 and
`breached_reg_6d_deadline` False.

## Why

`balance_settlement_from_outcomes`'s `money_in_out` (`simulation/arrears_engine.py`, the `arrived` loop) counts a
`kind == "repayment"` credit on the day the walk sets it against a bill. cab13bbd18 wrote that on purpose, naming
this account: "SYN-2016-139's 11.52, dated May 2021, settles an Apr 2022 return". 9392920e60 (fix 2) then ruled
the opposite for the page: "Cash that arrived before an arrears case opened is credit already on the account, not
that case's repayment". So the page shows it as credit that was already held, while the walk still dates it as
money arriving.

Fix 2 and s.8.8d point the same way. Reg 6D runs from the final bill. A credit, under SLC 27.16, exists once the
money does, and here the money arrived in May 2021. Applying credit the account already held is not money in.
So the refund was due by 29 Apr, and the world paid it 9 working days late without recording a reg 6D breach.

## The size of the class

1 of 176 closing refunds on this replay is a breach. This finding has not counted the legs where the same rule
moves the request day but the refund still lands inside the page's clock. Those carry the same defect, with no
row able to see it.

## Recommendation (a reversible world fix, not built here)

1. Amend s.8.8d first (K8): credit the account held before the final bill is not money in.
2. Then let `money_in_out` skip a repayment credit whose own cash day falls before the bill it settles. That is
   the date fix 2 already reads.
3. Pre-register the count of request days that move, and the reg 6D breaches that appear, on a replay before a
   run.

**Built 2026-11-14** (REPAYMENT_POSTING_AREA_MAP s.8). Steps 1 and 3 were done as written. Step 2 was done more simply: `money_in_out` dates every repayment credit by its cash day. On the r98 replay, 23 money-in days move earlier and 3 refunds are paid earlier, SYN-2016-139's on 29 Apr 2022.

Until the fix lands, `DOMAIN_INVARIANT_EXCEPTIONS.yaml` holds the row at a ceiling of 1, scoped by name to this
account, so the 16 Nov publish is not refused for a traced defect. A second breach still refuses.

**Reverse.** Delete this file and the SYN-2016-139 exception.

## Landing "Reg 6D's refund clock starts on the day the final bill is issued" (item `the-final-bill-issue-day-has-one-home-beside-bill-due-date`)

**Attempt 6, 13 Nov.** Salvage ce230b3926 (8 files) was cut to its 5 work paths and applied to a
detached worktree at origin/main a84639ed46 (`/var/tmp/wt-final-bill-issue-day`). Origin had not
touched those paths since the salvage's base, so it applied cleanly. Attempts 1-5 left no cause on
record. One likely cause: the shared checkout sat 2 commits behind origin, and `surgical_land`
refuses a commit on a primary that is behind. This attempt avoids that by landing from the
worktree. The new control passes (2), and so do 29 neighbouring tests.
`test_every_journey_opens_the_day_after_a_bill_the_ledger_made_due` fails identically on CLEAN
origin a84639ed46 (4 journeys: PROS-2016-0020, SYN-2016-325, SYN-2016-005, SYN-2016-024), so it is
not this change. It is the red recorded on 10 Nov in SEAT_FINDING_THE_DESKS_WRITE_OFF_... (3 then).
If the gate selects it, this attempt is refused for that red, not for the fix. The attempt's pid
and outcome follow.

- **Attempt 6 ended: REFUSED, after 90 s, before any test ran.** Unit
  `longjob-the-final-bill-issue-day-has-one-home-beside-bill-due-date`, ExecMainPID 1175646, exit 1.
  `[surgical-land] REFUSED: MESSAGE GATE RED (rc=1)`. `[director-doc-gate]`: the move of the
  `DIRECTOR_STEER_...` advisor file to done/ is a rename with an edit, and the message had no
  `Director-doc:` trailer. The cause is the landing's own message, not the fix.
- **Attempt 7:** the same tree, with `Director-doc: record` and `NEXT:` trailers added. Its pid
  and outcome follow.
- **Attempt 7 ended: REFUSED, after 30 s.** Unit pid 1192389, exit 1. The message gate passed.
  The tree gate's targeted tests passed (14 passed, 2 skipped). `[archive-question-gate]` refused
  the advisor steer's move to done/: it carries 2 open director questions in
  `open_question_register.json` ("Has the website updated?", "Is this per customer or on a random
  size sample?"). Again the cause is the bundled move, not the fix.
- **Attempt 8:** the fix alone. The advisor steer stays in place until its questions are closed.
- **Found before attempt 8:** `fork_salvage` committed this worktree's uncommitted fix as SALVAGE
  10cde4711c (15:36Z, `--no-verify`, on the worktree's detached HEAD). Attempts 6 and 7 gated on
  top of it. A landing there carries an ungated commit as a parent, so it must not reach origin.
  The worktree was soft-reset to a84639ed46 before attempt 8, with the same bytes staged. Salvage
  ce230b3926, which this fix comes from, was made the same way. Earlier attempts that started from
  a salvaged worktree may have died on that parent.

**Attempt 9, 13 Nov (worktree `/var/tmp/se-seat-executor` on origin/main db80910fa0).** The salvage
worktree was gone; the hunks came from SALVAGE d0025cb49f, whose base a84639ed46 is on origin and
whose six paths origin has not touched since. Stray paths (context handshake, fidelity ledger,
test_execution_log) dropped.

- **Why the selection control was red.** Not the page edit:
  `test_the_k8_page_no_longer_selects_the_full_simulation_run_through_its_citers` is red on clean
  origin. 3af02a2dd1 added a comment citing `home_moves.md s.8.8e` to
  `tests/simulation/test_run_phase4c_on_phase2b.py`, and `data_surface_tests` selected any test naming
  the page anywhere, comments included. Fix, as a class: a test that names a document only in a
  comment is not its guard (`_names_it_outside_comments`; a docstring still counts). Its control
  covers every branch, and mutating the filter to keep everything turns both controls red.
- **Measured selection** (seconds summed from `/var/tmp/final-bill-timing/per_file.tsv`): all
  paths together 77 files, 4,311 s. That is over the limit, so this attempt lands it in three parts,
  serially: (1) the gate fix and this finding, 47 files, 580 s; (2) home_moves.md, 26 files, 2,666 s
  (it still pulls `test_run_phase2b.py`, 994 s, through `simulation/run_phase2b.py`, which names
  the page in code); (3) the simulation fix and its control, 51 files, 1,645 s. Prediction: each
  part finishes inside 3,600 s. The attempt log follows.
- **Attempt 9, part 1 (gate fix + finding; 47 files, 580 s predicted): landed 1778f1ce6.** Unit
  `longjob-final-bill-land-1-gate`, pid 909320. It queued about 10 minutes behind another commit
  gate, then ran from 20:29:16 to about 20:41 GMT (about 12 min) and exited 0. Promoted to origin from
  db80910fa.
- **Attempt 9, part 2 (home_moves.md + this note; 27 files, 2,682 s predicted):** pid and outcome follow.
- **Attempt 9, part 2: landed ceed1aa38.** Unit `longjob-final-bill-land-2-page`, pid 1189083. It
  queued about 5 min behind another lane's gate, then ran from 20:45:30 GMT for about 44 min (2,682 s
  predicted) and exited 0. Promotion was refused twice because origin moved during the gate. Gated
  merges 9879d3041 (pid 1776665, about 2 min) and 3f4a1f79f (about 1 min) followed, and 3f4a1f79f
  was promoted.
- **Attempt 9, part 3 (simulation fix, its control and this note; 52 files, about 1,661 s predicted):**
  outcome follows.
  **Landed ceeefa596** (unit `longjob-final-bill-land-3-sim`, 22:12 GMT, gate-rc 0). Its receipt
  reads `tests: 7 passed in 0.18s`, far below the 52 files predicted. That gap is not explained here:
  read the receipt's selection before trusting the per-file sums for the next sizing. The turn that
  landed it ended before promotion. Origin had moved by 2 commits that touch none of its paths. A
  gated merge, 99c8e05dd (unit `longjob-final-bill-land-4-merge-1`, about 60 s), was promoted at about
  22:58 GMT and bound to the claim. **The fix is on origin ahead of the 16 Nov 04:00 book.**
