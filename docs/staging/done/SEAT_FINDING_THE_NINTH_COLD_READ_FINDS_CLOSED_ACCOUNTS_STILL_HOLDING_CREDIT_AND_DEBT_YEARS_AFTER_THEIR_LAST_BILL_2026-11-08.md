**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** `home-moves` -- `docs/market_research/home_moves.md` §8.8a

# The ninth cold read finds closed accounts still holding credit and debt years after their last bill (2026-11-08)

**Found by.** The ninth cold read's O20 and O7, on the af31e73fa7 book.
- SYN-2016-250 is "Owed on 4 Jul 2025 £-236.74", a credit, with supply ended in 2021.
- SYN-2016-428 owes £111.93 from 2019.
- SYN-2016-035 holds a credit on electricity and a debt on gas, never offset.
- On the mover SYN-2016-527, "£36.31 owed" is followed by "We have refunded the credit on your closed account".

**This is a known class, recurring.**
`done/SEAT_FINDING_THE_CREDIT_REFUND_LOG_AND_THE_LEDGER_DISAGREE_ON_WHICH_MOVERS_ARE_OWED_2026-10-25.md` found that
the refund log and the ledger keep two books of who is in credit. On a 60-account run, 7 of 34 move-outs closed in
credit with no refund, and one debtor was refunded. That finding is in `done/`. Its symptom is on this book.

**Measured over every page.** The pages are `/var/tmp/ninth-read/tree/site/data/customers/`. The measure is
accounts whose last bill ends 1 year or more before the as-of date (4 Jul 2025), with a balance of at least £5 either way.
- 806 accounts have no bill for a year or more.
- **213** of them still hold a **credit**, £15,694 in all. GSoP reg 6D requires a refund. A credit the ledger holds
  with no refund is a breach the refund measure cannot see.
- **208** of them still hold a **debt**, £21,554 in all, neither collected nor written off on the page.
- No row grades a closed account's balance.

**What I cannot yet say:**
- whether the debts are written off in the company's accounts and only the page ledger fails to show it;
- whether the refund log paid the credits and the ledger dropped them (the 10-25 mechanism).

**Next.** The fix re-reads the 10-25 finding's §8.8a choice 4 against this book. One balance must decide both the
refund and the write-off. A blind row for "a closed account's balance reaches zero by a refund, a collection or a
write-off within a stated window" is owed. It was not in this read's blind batch, so it is still to write.

## Prediction, filed before the split was measured (2026-11-08)

"Most are level-DD legs, the cash is right and the closing balance is wrong." Stated so it can fail:
- more than half of the 421, by count, pay by direct debit;
- on those, every collection on the page matches a DD instalment, and the balance is the residue of the
  last instalments against the final bill. Nothing in the cash is invented; what is missing is the close
  (a refund of the credit, a final collection or a write-off of the debt).

## The split, measured after the prediction (2026-11-08)

Same pages, same measure. Reproduced exactly: 806 legs with no bill for a year or more, and 421 holding £5 or
more, 213 in credit (£15,694.35) and 208 in debt (£21,554.18). Script: `/tmp/closed_split/probe.py` and
`split.py`. "Level DD" means fewer than half of a leg's DD collections equal the bill they are keyed to.

| Payment method | Credit legs | Credit, £ | Debt legs | Debt, £ |
|---|---|---|---|---|
| Level direct debit | 213 | −15,694.35 | 207 | 21,406.32 |
| Not DD (receipt) | 0 | 0 | 1 | 147.86 |
| **All** | **213** | **−15,694.35** | **208** | **21,554.18** |

**Is it the cash or the closing balance that is wrong?**

| Check | Credit legs | Debt legs | Reading |
|---|---|---|---|
| Ledger entries sum to the printed balance | 213 of 213 | 208 of 208 | The page's arithmetic holds |
| Every DD collection is a scheduled instalment; any after the final bill fall within 95 days of it | 213 (65 with a collection after the bill, 63 of them within 35 days, 3 with two or three) | 207 (31 with one after, all within 35 days) | **The cash is right**: an instalment in flight at the final bill is normal practice, and it is owed back |
| A refund, final collection or write-off brings the balance to zero | 0 | 0 | **The closing balance is wrong**: the close is missing |
| Per-bill walk: every bill on the leg marked paid | (n/a) | 207 of 208 | The debt exists only on the page's level-DD running balance. `closing_balances` and the refund log read the walk, so neither sees it |
| Write-offs on these legs, against the balance the page held the day before | 89 write-offs; 20 made while the leg was in credit | 84 write-offs, every one smaller than the balance | The write-off reads a failed bill's face, a third figure |

Cause, in one line: §8.8a choice 4 assumed "nobody in the run pays a level DD". The level-DD schedule (N20)
changed that, and the close still reads the per-bill walk. The previous published book (0a6391d186, before the schedule) reads
1 credit and 0 write-off breaches on the same row. **Corrected beside the claim above:** "whether the refund log paid the
credits and the ledger dropped them". It did not. The log reads the per-bill walk, which holds no credit for these legs.

**The prediction, graded: CONFIRMED.** "Most are level-DD legs, the cash is right and the closing balance is wrong."
- 420 of 421 are level-DD legs.
- No collection is invented.
- On every leg the balance stands because nothing closes it.

One refinement the prediction did not make: on the debt side the page is right and the company's
own per-bill book is wrong. It holds the bills as paid, so the company does not see the debt.

## The knowledge and the row (2026-11-08)

- **Knowledge.** `docs/market_research/home_moves.md` §8.8b covers one balance at close. A credit is refunded
  within 10 working days of the later of the final bill and the last collection. A debt is collected with one last
  DD, then pursued or written off at the same balance. A write-off is never more than what is owed.
  How long a debt is held before it is written off is a GAP (G8.14). The rules are published on the
  site's home-moves topic.
- **Row.** `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` (`docs/design/DOMAIN_INVARIANTS.yaml`), graded on the page by
  `tools/domain_invariant_runner.ev_closed_account_balance`. It is checkable now: the page carries the final-bill
  dates and the running balance, so it did not need to wait for the build. On af31e73fa7 it checks 1,549 and breaches 184. Of those,
  146 are domestic legs closed from 1 May 2019 still in credit 10 working days after close (£21,287), and
  38 are write-offs above the balance owed. A further 244 are standing debts, flagged and not breached (£25,117). The
  94 credit legs closed before 1 May 2019 are outside reg 6D's deadline and are not breached, though the money is
  still owed. Excepted at 184 in `DOMAIN_INVARIANT_EXCEPTIONS.yaml`, retired by the build.
- **The row was not written blind.** I had read the page files and the runner, not the billing code. The ruling asks for
  blind rows; a blind reader's twin is still owed.

**Build: not in this item.** Level DD step 2b has only its first increment on origin, and §8.8b choice 6 builds
the close on its schedule. Owed when 2b lands: the close reads the page's running balance, one balance decides the
refund, the last collection and the write-off, and the row grades 0 on a fresh run.

## The close lands, and its prediction (2026-11-09, filed before any book carries it)

**Built.** A level-DD leaver closes on its one balance: the per-bill walk plus what its bills asked less what
the bank paid (`arrears_engine.level_collection_difference`, matched month by month as the page matches them).
A credit goes to the refund log, with the reg 6D clock run from the later of the final bill and the last
collection. A debt is written off up to that balance, newest bill first; no more is written off than is owed,
and the page posts what was written off, not the case. A shortfall no bill holds stays a standing debt (the
last collection is §8.8b choice 3, still unbuilt). Test:
`tests/simulation/test_a_level_dd_leavers_one_balance_is_refunded_or_written_off.py`, one control over the
four fates first.

**Prediction.** On the first book whose commit carries this close, `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO`
breaches **10 or fewer** of the 184 it breached on af31e73fa7. **HELD: 2, on 505df564e3** (graded below). Why it could fail: the walk-plus-difference
matched the page's balance at close on 850 of 857 leavers, so about 7 should still miss; more than 10 means
the match on af31e73fa7 does not carry to a book with step 2b's offsets on (b9ad453df). Standing debts are
flagged, not breached, and stay; their count is not predicted. The 184 exception in
`DOMAIN_INVARIANT_EXCEPTIONS.yaml` is retired on that book, not here.

**Why this took five gate attempts.** The landings at pids 2583013, 3152134 and 3995967, then the executor
turns ending 01:16, 05:05, 07:55 and 09:57 on 9 Nov, were each killed, not refused: the journal reads "did not
finish inside 5400s" for every turn on this item. Each turn re-verified the same patch (166 targeted tests in
94 s, then `tests/simulation/test_run_phase4c_on_phase2b.py`, whose fixture alone takes 1,014 s), then began
a gate whose test selection runs that same fixture, and the turn ran out of time. The cure was to land
first: this landing began within 20 minutes of the draw, on bytes the 09:02 turn had already tested.

**Reverse.** Delete this file; revert the row, its evaluator, its exception and §8.8b in the landing commit.

## Graded on the first book carrying the close (2026-11-09)

**Book.** `docs/reports/run_output_505df564e3_20261109T124818Z.json`. `git merge-base --is-ancestor` puts
e0aeece0d (the close) and d8264b525e (the cure fix) under 505df564e3. Ledger:
`/var/tmp/grade-505d/ledger.json`, rebuilt by the cure grade's own chain from the book's locked worktree.
Script: `/var/tmp/grade-505d-closed/grade_closed.py`. It is that chain's `grade.py`, plus the page's final-bill
dates. The chain's grade read this row NOT_IN_EXPORT, because the in-memory page carried no `final_bills`.
The dates are rebuilt the way `generate_customer_reaction_chain` dates a final bill: `issue_date`, or else
`period_end`, of every bill with `final_bill`.

| Book | Close on it | Checked | Breached | Flagged (standing debts) |
|---|---|---|---|---|
| af31e73fa7 (pages, 8 Nov) | no | 1,549 | 184 | 244 |
| 9d7dcfc19c (control, same script) | no | 1,497 | 131 | 278 |
| **505df564e3** | **yes** | **1,505** | **2** | **313** |

**Prediction: HELD.** 2 is at most 10. The control shows the script can fail: on the last book without the close,
the same script reads 131. Attribution is partial. 505df564e3 carries both the close and the cure fix, so the
131-to-2 drop belongs to both together, not to the close alone. No write-off on a closed leg now releases more
than was owed: 0 of the 38 such breaches on af31e73fa7 remain.

**The residue: 2 credits, no over-write-offs.** On both, the close paid a refund, but the refund came out short
of the page's balance:
- PROS-2016-0263g: final bill 14 Sep 2021, page balance −£195.29, refunded £193.64 on 28 Sep, so −£1.65 is left.
- PROS-2017-0351: final bill 22 Nov 2024, page balance −£1,312.24, refunded £1,290.38 on 6 Dec, so −£21.86 is left.

These are the level-match misses the prediction allowed for: the walk-plus-difference did not match the page
on about 7 of 857 leavers. Not yet traced: why the walk-plus-difference falls short on these two.

**Standing debts went up (flag, not breach, and not predicted): 244, then 278, then 313.** A debt that the
close leaves standing is §8.8b choice 3, the last collection, which is still not built. The rise has not
been traced. It goes to that build, not to this row.

**Done.** The 184 exception is replaced by a narrower one in `DOMAIN_INVARIANT_EXCEPTIONS.yaml`, with
max_breached 2. It names the two legs and the trace still owed. This finding moves to done/.
