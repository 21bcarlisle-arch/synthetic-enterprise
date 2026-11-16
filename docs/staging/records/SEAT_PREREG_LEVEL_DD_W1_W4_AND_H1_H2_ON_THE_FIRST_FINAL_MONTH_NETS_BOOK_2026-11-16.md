**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`

# Pre-registration: LEVEL_DD s.9.8 W1/W4, and H1 against H2, on the first book that carries `final_month_nets` (2026-11-16 16:45Z)

Written before any book carries 123df0734. The 16 Nov record
(`SEAT_RESULT_THE_16_NOV_BOOK_ON_LEVEL_DD_W1_W4_2026-11-16.md`) left W1 and W4 ungraded. It also left H1 and H2
apart: H1 is that the page balance cannot see the world's ask, and H2 is that 37d934286's branch does not fire
on a book. 123df0734 adds the instrument for both.

**The premise is not spent; it is waiting.** At 16:37Z no book carries 123df0734. 123df0734 is on origin/main
(13:29Z). The newest book, `run_output_f7e17b1316_20261116T070501Z.json`, began at 07:05Z, before 123df0734 landed. The
sim runner has been deferring each cycle to `longjob-value-test-candidate-a-flag0-twin` (declared 660 min, at
455 min at 16:33Z), so the next scheduled run starts at about 20:00Z at the earliest. I did not launch a run
myself. The run has no population knob, so the smallest run that answers this is a full book, and a second
full run beside a declared 11.5 GB job is the cgroup case the runner defers to avoid.

## What each figure counts (said before dividing anything)

- **A row** is one mover leg's final-month bill as the world presented it (`LivePaymentTriad.final_month_nets`).
  `ever_level` means the leg is on `_legs_ever_level`. `ledger_balance_gbp` is read only for those legs, and
  negative means credit.
- **W1, primary:** `netted_ledger_credit_legs` and `netted_ledger_credit_gbp`. These are the legs, and the pounds,
  where the ledger credit took more off the face than the waiting credit-bill credit would have. That is the branch
  firing. Band as amended on 14 Nov: **168 to 213 legs, GBP 4,030 to 4,990**. Shown beside it, not graded: every
  ever-level final bill with any credit taken. The band was calibrated on "final bills the page said the credit
  covered", and that population includes waiting credit.
- **W4:** SYN-2016-244's row. `ask_gbp` must be in **GBP 30 to 45**. Reconstructed from the book's inputs it would
  be 35.70. Reverse-F is not counted from the run JSON alone. It is the netted legs that the page still refunds after the
  final bill, which is the page-chain read below. Its band stays **0 to 3**.

## Decision rule for H1 and H2, partition stated before reading

Over ever-level rows, three cells: **credit available and fired** · **credit available, not fired** (credit
available = `-ledger_balance > waiting + 0.005`) · **no credit available**.

- **H2 holds** if `fired == 0` while `available > 0`. The branch is dead on a book. If any available leg is not
  fired, that is H2 *in part*. Credit taken is capped at the face, so an available leg can fail to fire only when
  its face is no more than its waiting credit. Each one is named and checked for that.
- **H1** is read against the F set from `desk.py` on the same book (the R5 desk-written-off accounts still printing
  owed). **H1 holds** if at least one F account has a fired leg and still prints owed: the world netted, and the
  page did not see it. **H2 explains F** for F accounts with an ever-level final leg that did not fire. F accounts
  with no ever-level final leg are **neither**. Their F cause is outside this branch, and that is a finding of its own.
- **Both** (H3): F splits across the first two cells. The grade reports all three counts and does not pick a winner.

Prediction, filed now: **H1 dominates.** Most F accounts have a fired leg and still print owed. The reason is the
evidence already in hand. SYN-2016-225 owes 159.20 and -482 owes 33.23, the same to the penny on a book without the net and on one
with it. A world-side net that reached the page would have moved at least one of them. Refuted if fired legs are
fewer than half of F's ever-level legs.

## The reader (`/var/tmp/fmn/read_fmn.py`, kept here because /var/tmp/w14 is already gone)

It refuses by name on a book that does not carry 123df0734 (exercised: the 8a300fa561 book, rc=1). On a synthetic
payload, every cell of the partition was taken.

```python
"""LEVEL_DD s.9.8 W1/W4 and H1-vs-H2 from a run JSON's final_month_nets.
argv: run_output.json [desk.json with {"owing": [account ids]} from desk.py on the SAME book]"""
import json, sys, subprocess
d = json.load(open(sys.argv[1]))
pc = d.get('producing_commit') or {}
pc = pc.get('commit') if isinstance(pc, dict) else pc
anc = subprocess.run(['git', 'merge-base', '--is-ancestor', '123df0734', str(pc)]).returncode == 0
print('book', sys.argv[1], 'producing_commit', pc, 'carries 123df0734:', anc)
f = d.get('final_month_nets') or (d.get('summary') or {}).get('final_month_nets')
if not anc or f is None:
    sys.exit('REFUSED: this book does not carry 123df0734 / has no final_month_nets, so W1/W4/H2 are not readable on it')
rows = f['rows']; lvl = [r for r in rows if r['ever_level']]
fired = [r for r in lvl if r['netted_ledger_credit']]
avail = [r for r in lvl if r['ledger_balance_gbp'] is not None and -r['ledger_balance_gbp'] > r['waiting_credit_gbp'] + 0.005]
print(f"legs {f['legs']} ever_level {len(lvl)}; ledger credit beyond waiting on {len(avail)}; fired {len(fired)}")
print(f"W1 primary: netted_ledger_credit_legs {f['netted_ledger_credit_legs']} GBP {f['netted_ledger_credit_gbp']}  (band 168-213, GBP 4,030-4,990)")
alt = [r for r in lvl if r['credit_taken_gbp'] > 0.005]
print(f"W1 secondary (ever-level final bills with any credit taken): {len(alt)} GBP {round(sum(r['credit_taken_gbp'] for r in alt), 2)}")
for r in [r for r in rows if r['leg'] == 'SYN-2016-244']:
    print('W4 SYN-2016-244', r, ' (band ask GBP 30-45)')
print('H2 partition: avail-but-not-fired', len([r for r in avail if not r['netted_ledger_credit']]), '| fired', len(fired), '| no credit available', len(lvl) - len(avail))
if len(sys.argv) > 2:
    owing = set(json.load(open(sys.argv[2]))['owing'])
    fa = {r['account_id'] for r in fired}; la = {r['account_id'] for r in lvl}
    print(f"H1: F accounts {len(owing)}; with a fired leg {len(owing & fa)}; ever-level but not fired {len((owing & la) - fa)}; no ever-level final leg {len(owing - la)}")
```

Run: `python3 read_fmn.py <run_output.json> <run_output.ledger.json.desk.json>`. Make the desk file with
`/var/tmp/repay-truth/desk.py` after the page chain (`/var/tmp/fab-ab2/chain_full.py`) has run on the same book.

**Reverse.** Delete this file. No code changed.
