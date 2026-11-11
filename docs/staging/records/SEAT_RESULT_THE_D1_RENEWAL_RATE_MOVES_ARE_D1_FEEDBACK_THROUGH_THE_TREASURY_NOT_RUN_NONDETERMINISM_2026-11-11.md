**Severity:** LATENT · **Lane:** A_strategy_governance · **Claim:** `the-renewal-rate-moves-under-d1-are-attributed-by-a-placebo-book`

# The D1 renewal-rate moves come from D1 feeding back through the treasury, not from run nondeterminism

**The question** (filed in e58699ec9, row 7): the e1587ec5b book (D1) moves renewal unit rates by
0.001p to 0.01p from 2020-21 against the 068b5e3cc8 book. Two causes were open. (a) D1's
collections change reaches pricing. (b) Run-to-run nondeterminism at one commit. The filed
prediction for the placebo book (e1587ec5b with b47832f7e1 reverted) was: (a) gives 0 moved
invoices, (b) gives a comparable count.

**I did not run the placebo book.** Data already on disk answered both legs at no compute cost:

1. **(b) is refuted at the most recent commit we can test.** Two runs at `a6b7a0fd47`
   (`run_output_a6b7a0fd47_20261104T173613Z` and `..._173649Z`) were launched 36 s apart as
   separate processes. 128 of their 131 top-level sections are byte-identical. The other three
   are timestamps only (`_cache_meta.generated_at_utc`, `generated_at`,
   `producing_commit.resolved_at`). That matches the 15 Oct Q0 result: X0 against A, with 0 of
   39,084 bills differing in any field.
   *Residual:* if nondeterminism came in between 4 Nov and 10 Nov, this pair cannot see it. The
   positive mechanism below covers that gap.
2. **D1 is the only runtime change between the arms.** `git diff 068b5e3cc8 e1587ec5b` touches
   seven non-test, non-site files:
   - `background/live_payment_triad.py` is D1. `simulation/run_phase2b.py` imports it.
   - `background/gap_metric.py` is imported by the run. Its change (1439de6409, D9) only adds a
     table and a function, and nothing in the run calls either.
   - `learning_loop.py`, `sanity_daemon.py`, `delivery_seat.py`, `generate_billing_ledger.py` and
     `generate_proof_data.py` are not in the run's import path.
   - Both outputs carry `imports_off_commit.paths: []`.
3. **The positive mechanism is traced in the raw run outputs:**
   - **2016–2019:** `years[*]` is identical in every field, including `treasury_end_gbp` and
     `hedge_fractions`.
   - **From 2017-11:** the world's collections journeys differ (D1's own effect, e.g.
     ACC-SYN-2016-382's overdue 140.24 → 68.26). These are dunning amounts and move no P&L.
   - **2020:** `treasury_end_gbp` differs by **£0.96**, because D1 changes when cash arrives.
     `hedge_fractions` differ on three legs.
   - **First moved strike:** SYN-2016-445 electricity, renewal on 2020-10-03. Its start hedge
     fraction is 0.87274435 against 0.87274500. The struck rate before the desk
     (`unit_rate_original`) is 124.09361 against 124.09298 £/MWh. The desk floors it at that
     cost, so it is billed as 12.4094p against 12.4093p.
   - Every later move descends from that point: 2,121 bills and 204 original-rate moves in
     `dynamic_pricing_log`.

**So the answer is (a), through a different channel from the one the prediction named.** The
prediction said value-based renewal or the default belief read the book's payment experience.
The channel is book-wide: D1 changes cash timing, which moves the treasury, which moves the hedge
fraction, which moves the capital cost on the naked fraction priced into the strike.

- **The per-customer reading is refuted.** In 53 of the 54 legs whose rate moved, no payment or
  collections event on the page differs before the leg's first rate move.
- **The reverse also holds.** 337 customers have collections differences and no rate move.

*Not traced:* the exact function that turns treasury into hedge fraction. The 2020 hedge-fraction
move on the very leg that is struck first is the evidence.

**Counts, by definition.** Page ledgers `/var/tmp/grade-d1/arm` against `/var/tmp/grade-d1/cross-068`:
- 336 invoices move their printed unit rate.
- 679 move a contracted-term rate.
- 54 legs move, counting a gas leg as its own `…g` id.

e58699ec9 says 341 invoices on 35 legs. I did not reconstruct its definition. The difference does
not bear on the attribution.

**What follows.** Nothing changes in any decision. The moves are real model behaviour: a pricing
input responds to the cash consequence of a collections rule. This does have one consequence for
grading. **Any world change that moves cash timing will move renewal strikes from the next
renewal after the treasury diverges.** A one-variable grade should expect sub-penny rate moves
downstream of any collections change and not read them as a code miss. Scripts are in
`/var/tmp/placebo-d1/` (`walk.py`, `attrib.py`, `earliest.py`).
