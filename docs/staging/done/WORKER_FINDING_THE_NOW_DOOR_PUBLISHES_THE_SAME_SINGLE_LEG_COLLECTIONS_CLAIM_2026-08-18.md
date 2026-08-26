# WORKER FINDING — the /now/ door publishes the same single-leg collections claim

**Severity:** LATENT · **Lane:** H_harness

LATENT, not BLOCKING, and the distinction is deliberate: the defect is live on a public door and the walk's sibling was graded MAJOR by three personas, but nothing in any lane is mid-promotion on the strength of this chip, and the fix is a port of a mechanism that already exists and is already controlled. It should be drawn, not held behind.

**Found:** 2026-08-18, worker tick, while closing `coldwalk:site2_arrears_counters_contradict_the_accounts_own_timeline` on SITE2_two_sided_wall_exhibit
**Owner:** the `/now/` door lane — `site/now/index.html`, `site/now/test_now_door.py`
**NOT SITE2's:** outside its `file_scope`, its own door tests, its own R11 obligation. Re-homed rather than fixed out of scope.
**Rank:** after SITE2's two remaining open findings. It is the second live instance of a class SITE2 has now closed on its own page, so the fix is a port, not a design.

## What was found

`site/now/index.html:365-376` renders, for household C1:

```js
var cases=h.arrears_cases||[];
chips.push('<span class="chip">'+esc((h.payment_channel||"").replace(/_/g," "))+'</span>');
if(h.failed_payment_count!=null){
  chips.push('<span class="chip">Payments: <b>'+num(h.failed_payment_count)+' failed'+...);
}
chips.push('<span class="chip">Arrears: <b>'+(cases.length?...:"none")+'</b></span>');
```

`h` is `company.json`'s `household` block. That block is **one leg** — `commodity: "electricity"` — and it publishes `payment_channel: "direct_debit"`, `failed_payment_count: 0`, `arrears_cases: []`.

So the live door renders **`direct debit` · `Payments: 0 failed` · `Arrears: none`** for a household whose gas leg publishes the opposite.

## The measurement (observed, not inferred)

Read from the published records this same site serves:

| | `site/data/customers/C1.json` (electricity) | `site/data/customers/C1g.json` (gas) |
|---|---|---|
| `reaction_chain` arrears events | 0 | 8 — two complete four-step cascades |
| cases opened | 0 | 2 (`arrears_payment_missed` 2016-11-15 £43.66; 2018-09-15 £26.84) |
| `ledger.entries` payment methods | `direct_debit` ×72 | `standard_credit` ×68 |
| `ledger.entries` notices | 0 | 4 `notice` + 2 `arrears_resolved` |

Every chip on `/now/` is true of the electricity leg and false of the household it names.

`site/now/test_now_door.py:286` currently *pins* the defect:
```python
assert f"{h['failed_payment_count']} failed" in chips, chips
```
— it asserts the chip equals the single-leg block, so it cannot fail on this.

## Why it is the same class, not a coincidence

SITE2's page had the identical three claims from the identical block, and three blindfolded personas led with the contradiction independently (`coldwalk:site2_arrears_counters_contradict_the_accounts_own_timeline`, MAJOR). Closing it as an instance on one door would leave the class alive on a second live public surface — which is exactly what R10 forbids.

## Recommendation — and what I would do

**Port SITE2's producer, do not re-derive it.** `site/customers/index.html` now carries `window.__householdCollections(legs)`: the sole producer of every collections claim on that panel, derived from the per-leg reaction chains, counting a case by its **opener** (`arrears_dd_failed` / `arrears_payment_missed` / `arrears_invoice_disputed`, because C4 and C7 publish interleaved cascades that run-pairing would merge), fail-closed on an unclassified arrears event, with the `company.json` block reconciled **leg to leg** and any disagreement published rather than silently resolved. `site/customers/test_wall_exhibit.py` section 18 is its control, including a mutation suite and a checker run against the page as it shipped.

Three sub-items, in order:

1. `/now/` fetches the household's legs (it already fetches per-customer data elsewhere on the door) and derives the three chips from them. If it cannot fetch the gas leg, the chips must **name the leg** rather than wear a household caption — the scope rule SITE2's money tiles already apply.
2. `site/now/test_now_door.py:286` stops asserting the chip equals the single-leg block and starts asserting it equals the household's own record, derived independently in the test from the published JSON. R15 both ways: restoring the block as the source must kill it by name, and a household clean on every leg must still get its "Arrears: none".
3. R11 on the live `/now/` door — the deployed pixel, not the repo file.

**Two design notes worth carrying over, because both cost SITE2 a cycle:**

- The leak-string list must be written from the **defect's** vocabulary, not the repair's. SITE2's first draft was read off the fixed page and passed against the shipped one.
- A **per-leg** line and a **household** claim must not share a phrase, or no control can tell a scoped statement from the household-wide one it exists to forbid.

## Evidence

- `site/now/index.html:365-376` (the three chips), `site/now/test_now_door.py:286` (the pin)
- `site/data/company.json` → `household` (`commodity: electricity`, `failed_payment_count: 0`, `arrears_case_count: 0`, `arrears_cases: []`, `payment_channel: direct_debit`)
- `site/data/customers/C1.json`, `site/data/customers/C1g.json` (the table above)
- The closed sibling: `docs/observability/sanity_adjudication_ledger.json` → `coldwalk:site2_arrears_counters_contradict_the_accounts_own_timeline`, and `docs/design/simplifications/SITE2_two_sided_wall_exhibit.yaml` (2026-08-18 HARDEN entry)
