# [WORKER FINDING] The wall census pins customer identifiers as a schema, so the wall widens every time the company wins a customer

**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** unminted
**Found:** 2026-09-01, by the delivery seat, after the pre-commit gate refused the same commit three times.

## Class registration

Belongs to `controls_that_cannot_fail`.

## What was found

`tools/wall_channel_census.py`'s channel-F **nested schema** check pins, for every top-level
run-output key a business module reads, the set of **nested field names** beneath it. The
baseline is shrink-only: a field name in the tree and not in the baseline is a WIDENING and
refuses the commit.

Several of those keys are **maps keyed by customer**. `clv_snapshots`, `per_cid_pnl` and
`per_cid_comm_pnl` are `{customer_id: {...}}`, so their "nested field names" are customer
identifiers. The check's own report says so in its refusal:

    WIDENED on channel F -- `clv_snapshots` now publishes C3_2, PROS-2016-0042, PROS-2016-0067,
    PROS-2016-0099, PROS-2016-0121, PROS-2017-0065, PROS-2017-0084, ... [continues for 800+]

**So the wall widens every time the company acquires a customer.** That is the world working
correctly. The control cannot tell a new data-carrying mechanism crossing the wall — the thing
it exists to catch — from the book growing by one account.

## Why this is BLOCKING and not a nuisance

**It had hard-blocked every `.py` commit in the tree.** The census step runs whenever any `.py`
path is staged, and it refused three consecutive landing attempts of unrelated work this
morning. A second lane hit the same wall and filed `6fed05942` — *"three of the five controls
are red at HEAD, and 'land it red' has no route here"*.

The only remedy the control offers is `--freeze`, and the refusal message calls that out
itself: *"a freeze without a reason is an amnesty."* But the honest reason here is *"the company
acquired 800 customers"*, which is not a wall decision at all. So the control forces a choice
between two bad moves: re-freeze a customer list on every run (which makes the baseline a
snapshot of one run's book, and the control vacuous for its real subject), or leave the tree
blocked.

**An 848-line re-freeze was sitting uncommitted in the working tree when this was found**, almost
all of it customer identifiers. That is the control's own remedy, taken, and it is why the
uncommitted diff was so large.

## Why it is this class

*Key a control to the property, not to today's answer* is a standing rule here, and its stated
symptom is exactly this one: **a control pinned to the current state goes red when the code
becomes more honest and stays green when the claim rots.** A wall census that reds on customer
growth and would be silent on a genuinely new nested field arriving inside an
identifier-keyed map is that, precisely.

The nested check is a good idea. Its subject is wrong for three of its keys.

## The repair, and it is not a re-freeze

**Partition the pinned keys by whether their nested names are a SCHEMA or a POPULATION.**

* A key whose nested names are field names — `ledger_pnl`, `management_accounts`,
  `trading_book` — is a schema, and pinning it is right and stays right.
* A key that is a map keyed by an entity — `clv_snapshots`, `per_cid_pnl`, `per_cid_comm_pnl` —
  has no schema at that level. Its schema is one level deeper: the field names inside a *value*.
  **Pin that instead**, over the union of values, and the control gets its real subject back: a
  new field appearing on a per-customer record IS a widening, and a new customer is not.
* The partition must be DERIVED, never a hand-kept exemption list, or it is the same
  silently-decaying list one level up. The derivable property: a key whose nested names are all
  identifier-shaped and whose value objects share a field set is a population map.
* Whichever way it is done, it needs a **population floor** on the pinned keys, so the repair
  cannot quietly pin nothing.

## Disposition taken

**Re-frozen to unblock the tree, under protest and with the protest recorded in the artefact
itself.** `docs/design/wall_channel_census_baseline.json`'s `_meta.nested_freeze_note` says what
was re-frozen, that it was re-frozen against one tree, that it is a control keyed to today's
answer, and that this document is the repair. The channel-C and channel-F top-level changes in
the same commit were ruled individually with reasons rather than swept — see
`_meta.last_freeze`.

That is a decision, not a fix, and it is recorded as one: the baseline will go stale again on the
next run that changes the book, and this finding stays open until the partition above exists.
