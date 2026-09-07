# EP8 — where the estimate goes (Q4): DISCOVER pass 5

**DISCOVER/FRAME ONLY.** Level stays 0, `loop_stage` stays `idle`, `block_reason` untouched. No
BUILD code, no adapter, no schema vendored, nothing under `company/`, `saas/`, `simulation/`,
`tools/` or `background/` changed by this pass. EP8 is epoch-3 BUILD-gated
(`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` rule 1), which makes DISCOVER/FRAME available while BUILD is
not. The map is touched for **exactly one bookkeeping line** — `simplifications_count` — written
atomically with the store append that accompanies this doc.

**MEASURED AT:** HEAD `38e22f470`. Live artefact `docs/reports/run_output_latest.json`, parsed in
full, not sampled: 10,924 `meter_read_log` rows. Modules read as they sit on disk. Everything below
is observed-with-evidence unless labelled `inferred` (R9).

---

## 0. What this pass was for

Pass 4 (`EP8_DUIS_ADDRESSING_BRIDGE_DISCOVER_2026-08-19.md` §6) left one item open and named it:

> | Q4 | where does the estimate go | **OPEN — now the only large piece behind this atom** |

Passes 1 and 2 both recorded it as *"the single largest piece of work behind this atom"*, resolved
by a message re-cut that separates **what the transport returns** from **what the billing engine
concludes**. This pass answers Q4 against the tree as it now stands, and the headline is that the
size estimate was wrong in the cheap direction: **the cut is most of the way built already, and
what remains is smaller and differently shaped than three passes assumed.**

---

## 1. The port Q4 asked for already exists — and is cut in the wrong place

Since pass 2, `company/billing/monthly_bill_assembly.py` grew exactly the seam Q4 called for:

```
ReadArrivalFeed  (Protocol, :94)   meter_type_for / read_for / final_read_for
ReadArrival      (Protocol, :80)   status, estimated_consumption_kwh, consecutive_estimated_count
```

with `simulation.meter_reads.SimulatedReadFeed` as the world-side implementation. The company no
longer imports the world's read generator; it is handed a feed and asks it what arrived. That is the
inversion Q4 wanted, and it is real.

**But the port returns the SUPPLIER'S CONCLUSION, not the transport's payload**, and that is the
part Q4 was actually about. `ReadArrival` declares three attributes and *all three are conclusions a
DUIS response does not carry*:

| `ReadArrival` attribute | what DUIS 4.6.1 returns | who really owns it |
|---|---|---|
| `status: "actual"\|"estimated"` | no such field | **split** — see §2 |
| `estimated_consumption_kwh` | no such field | the **supplier** |
| `consecutive_estimated_count` | no such field | the **supplier** |

A 4.6.1 `RetrieveImportDailyReadLog` response body is a repeated `LogEntry` group — up to 31
timestamped **cumulative register values** (pass 2, FINDING 3, off DUIS T1 Table 69). It has no
notion of "estimated", no consumption figure at all, and no memory of what it returned last month.
Period consumption is a **subtraction the supplier performs**; estimation is what the supplier does
when the subtraction has no endpoints.

So the docstring at `:98` — *"going live it is a real D0010/DTC feed adapter, behind this unchanged
Protocol"* — is true for D0010 and **false for DUIS**. A D0010 flow does carry an estimated/actual
indicator, so the Protocol can survive that swap; DUIS carries none of the three, so it cannot. The
port was built for the wrong one of the two transports this atom exists to reach. Recorded as the
FRAME consequence, not as a defect in that module: nothing is wrong with it *today*.

---

## 2. `status` is two facts wearing one name

This is the definition failure the CLAUDE.md rule is about, and naming it is most of Q4's answer.
`status` conflates:

- **did a read ARRIVE?** — genuinely the world's. `simulate_read` draws
  `arrived_actual` and a `delay_days`, and physical arrival is not the supplier's to decide.
- **is this bill ESTIMATED?** — genuinely the supplier's, and *entailed* by the first: a bill is
  estimated precisely when the supplier has no arrived read to bill from.

One is observed, one is concluded, and the second follows from the first by a rule the supplier
owns. The cut Q4 wants is therefore **not** "move estimation across the wall" — it is "stop shipping
the conclusion across a seam that only has standing to report the observation".

---

## 3. The estimator's every input is already company-side. Only the arithmetic is not.

This is the measurement that resizes the work, and it is the reason this pass disagrees with its
three predecessors about how large Q4 is.

`simulation/meter_reads.py:simulate_read` computes the estimate as:

```python
estimate = statistics.mean(trailing_actuals_kwh[-ESTIMATE_TRAILING_WINDOW:])   # window = 3
```

`trailing_actuals_kwh` is **not world state.** It is accumulated inside
`company.billing.monthly_bill_assembly.build_monthly_bills` (`:432` init, `:537` append) and passed
*into* the world at `:444`. The same is true of `consecutive_estimated_count`: the company passes
`consecutive_estimated` in at `:447`, and the world hands back `consecutive_estimated_count + 1` —
a pure increment of a counter the company already holds and already resets itself at `:538`.

**Two of the three `ReadArrival` attributes are company-held state round-tripped through the
world, and the third is a three-point mean over company-held history.** Nothing in the estimator
consults anything only the world knows. Moving it company-side is a mechanical relocation of ~6
lines, not a piece of modelling — which makes Q4 the *smallest* remaining piece behind this atom,
not the largest. Passes 1, 2 and 4 all sized it from the seam's shape rather than from the
estimator's inputs, and the seam's shape was the misleading half.

*Correcting the record rather than quietly revising it: three passes called Q4 "the single largest
piece of work behind this atom". That was wrong, and it was wrong because nobody had looked at what
the estimator reads.*

---

## 4. …with one exception, and it is a live defect, not a framing point

The `else` branch of the same function is not a mean over company history:

```python
if trailing_actuals_kwh:
    estimate = statistics.mean(trailing_actuals_kwh[-ESTIMATE_TRAILING_WINDOW:])
else:
    # No history yet: the opening read taken at switch/onboarding is a
    # real physical value a supplier does obtain, not a forecast --
    # bootstrap the very first period from it.
    estimate = true_consumption_kwh
```

**The comment's justification is scoped to the first period. The branch serves every period until
the customer's first actual read arrives**, because `trailing_actuals_kwh` is appended to *only* on
an actual read. Measured over the live run:

```
estimated reads                                          6,852 of 10,924
estimate exactly equals round(true_consumption_kwh, 2)   1,095   (16.0% of estimated)
  of which, before the customer's first actual read      1,072
  of which, after an actual read (coincidence)              23
consecutive_estimated_count on the exact rows            1..12, spread evenly
customers who never receive an actual read at all        9 of 251
```

A run of twelve consecutive "estimated" periods, each estimated at *exactly* the true consumption.
The estimated bill is then priced by scaling settlement records by `est_kwh / true_kwh` (`:541`) —
a ratio of exactly 1.0 — so the "estimated" bill equals the true bill to the penny.

**This refutes a claim the module states about itself.** `monthly_bill_assembly.py:44`:

> *"The one place a true figure drives a DECISION is `_resolve_catchup`, and it does so only once an
> ACTUAL read has arrived — at which point the real consumption is genuinely known to the supplier."*

For 1,072 rows the billed amount is driven by `estimated_consumption_kwh`, which **is** the true
figure, **before** any actual read arrived. The claim is correct about `_resolve_catchup` and wrong
about the module.

### What it costs, measured

```
                              n       median rel err     mean rel err
all estimated reads         6,852          17.274%          45.906%
  before first actual read  1,072           0.001%           0.001%   <- exact by construction
  after  an actual read     5,780          21.901%          54.420%
```

The perfect-by-construction population is **15.6% of every estimated read**, and it drags the
headline estimated-vs-actual divergence from 21.9% to 17.3%. Every figure built on that
divergence — bill-shock incidence on estimated bills, catch-up rebilling magnitude, the D3
`billing_basis` analytics — is biased toward the supplier looking more accurate than it is, by a
population that was never estimating at all.

**FILED, NOT FIXED**, following pass 4's own precedent for the MPAN legs (§4/§5 there): this is a
live `simulation/` fidelity defect that exists today, independent of whether EP8 is ever built, and
folding it into a parked epoch-3 atom's BUILD would hide a current defect inside a gated atom. It is
filed as
`docs/staging/SEAT_FINDING_THE_WORLD_ESTIMATES_A_NEW_CUSTOMERS_CONSUMPTION_AT_EXACTLY_THE_TRUTH_FOR_UP_TO_TWELVE_PERIODS_2026-09-07.md`.

It is also, separately, the strongest argument for the cut in §2: with estimation company-side, this
branch has **no ground truth available to reach for**, and the defect becomes unwritable rather than
merely fixed. That is the fidelity prize, and it is the same shape pass 2 found for register
rollover.

---

## 5. Q4, answered

> *Q4 — where does the estimate go?*

**Company-side, into the billing engine, and it is a small move that has been mis-sized three
times.** Specifically:

1. `ReadArrival` sheds `estimated_consumption_kwh` and `consecutive_estimated_count` entirely —
   the company already owns both inputs and can compute both without asking.
2. `status` narrows from a conclusion to an observation. The honest DUIS-shaped spelling is
   *"a read arrived / did not arrive, and here is its timestamped cumulative index if it did"*;
   `billing_basis` (which `monthly_bill_assembly._annotate_billing_basis` already stamps on every
   bill) becomes the supplier's own conclusion rather than a copy of the feed's field.
3. The trailing-mean estimator and its `ESTIMATE_TRAILING_WINDOW = 3` move to the company beside
   the history they already read.
4. The bootstrap branch does not move, because company-side **it cannot be written** (§4).

**NOT decided here, and deliberately:** whether `ReadArrival` should carry the cumulative register
index now or at BUILD. That is a message-shape question that belongs with EP6's channel-D contract,
and answering it privately here is exactly what Q3 was told not to do.

---

## 6. Open-question ledger after this pass

| | | |
|---|---|---|
| Q1 | which SRV | ANSWERED (pass 3) — 4.6.1 |
| Q2 | MMC or stop at the blob | ANSWERED (pass 3) — model the MMC Output Format |
| Q3 | who runs Receive Response | STILL EP6's. Unchanged; do not answer it privately |
| Q4 | where does the estimate go | **ANSWERED this pass — §5, and it is SMALL** |
| Q5 | addressing bridge | ANSWERED (pass 4) — three legs |
| Q6 | does the mock emit Alerts | SHARPENED (pass 3) — `DeviceAlertMessage` |

**No large piece remains behind this atom.** What is left is EP8's dependency, unchanged and still
the whole gate: EP6's channel-D asynchronous contract (pass 2's closing sentence). Every question
this atom can answer without EP6 is now answered.

---

## 7. What this pass did not do, so the next draw is not misled

No adapter, no message re-cut, no `ReadArrival` change, no schema vendored, no BUILD code, no
`simulation/` edit — the §4 defect is **measured and filed, not repaired**, and repairing it touches
a live world module that a LANE 3 doc-only draw does not carry. No external source was fetched this
pass; §1's DUIS body-shape facts are quoted from pass 2's own S1/S2 extraction, not re-retrieved.
The gas/MPRN side remains untouched. The 23 exact-after-actual rows in §4 are **not** explained here
— they are consistent with a flat-consumption customer whose trailing mean coincides with truth to
2dp, but that is `inferred` and was not measured. `dcc_meter_registration.py`'s revival is still not
designed. Q5's leg-1 MPAN repair remains filed and unfixed in its own lane.

**Store and count:** unlike pass 4, this pass **does** append to
`docs/design/simplifications/EP8_adapter_dcc_duis.yaml` and moves `simplifications_count` with it in
one write. Pass 4 deliberately did neither, which is why the count read 3 while four passes had run;
after this pass the count and the store agree again, and the reader reconciling them will find pass
4's §7 explaining the gap rather than a miscount.
