# WORKER FINDING — one named quantity, two different numbers, nothing comparing them

**Date:** 2026-08-09 (worker tick) · **Atom:** `H27_payment_belief_gap` Expert Hour, second pass
**Class:** a real-world quantity published by two dimensions of one instrument, over different
populations, with the source asserting they were the same measurement.
**Status:** class closed (`SHARED_QUANTITY_CONTRACT`); the alignment is atom
`D16_ageing_negative_population_is_unexcluded`. H27 held at L2 on this, mechanised via `depends_on`.

## The finding, observed with evidence

`tools/couple_w2_11_d5.py` prints, in one output block:

```
[detection] ... false_flag_rate 0.0269 = 21 of 782 never-flaggable cases wrongly flagged
            = the wrongful-dunning exposure
[ageing]    ... overstated_arrears_rate 0.0951 over 1062 truly-current
            = the wrongful-dunning exposure
```

Two numbers, 3.5x apart, under one name. `background/gap_metric.py` asserted in a source comment
that they were "literally the same numerator". They are not: **measured case by case** at 400
customers / seed 7, the two numerators share **seven** cases.

**Why they differ, and it is not arbitrary.** The denominators sit in an *exact* containment —
`1062 == 782 + 280` — because D11 established that an invoice paid past its grace date genuinely
*was* unpaid past grace, so a flag on it was **correct**, and excluded those 280 cases from the
detection dimension's populations. That rule was applied to the detection dimension **only**.
Ageing carries no exclusion band at all, so **94 of ageing's 101 false ageings land inside the
excluded band** — 93% of one dimension's published wrongful-dunning exposure is composed of cases
the sibling dimension of the same instrument holds the company was **right** about. Conversely 14
of detection's 21 are absent from ageing's numerator: the belief sides differ too (detection is
EVER-FLAGGED, 439 cases; ageing is the `as_of` snapshot, 229).

Reproduced at seeds 7 / 11 / 23 and at two reconciliation-grace windows (5 and 12 days): the
containment holds every time, the rates diverge every time (3.5x / 2.4x / 5.9x).

**Provenance (R9, inferred not observed):** the identity claim was recorded against the *pre-D11*
instrument, and D11's own reshape moved one side of it in the same change without updating the
sentence. Whether it held exactly before D11 has not been re-measured here.

## Second finding — the sibling publish path was left behind, again

`main()`'s `--write-ledger` branch overwrote the measured `det.note` with:

> "HEADLINE = DD/non-DD failure DETECTION gap (fraction of true payment failures the company
> **never observes** through the seam — the no-remittance blind spot)"

D10 measured that description **false** (`n_undetected == 0` on seeds 7/11/23; the residual is
detections the company *un-made* under oldest-first allocation), and D11 then made it wrong a
second way — the headline is a balanced error over two directions, not a fraction of failures.
Both this path and `background/live_payment_triad.py::measure_and_write` write the **same bare
ledger key** the Proof door reads, so whichever ran last decided what a reader saw. The live one
was corrected on 2026-08-09; this offline sibling was left behind **and had no test at all** — the
identical defect, in the identical shape, one file over from where it had just been fixed.

## What was delivered (HARDEN — R12: no published number moved)

Detection balanced error stays 0.0134 (seed 7); the ageing measures are unchanged.

1. **The false identity claim is corrected at source** in `background/gap_metric.py` with the
   case-level decomposition — not reworded.
2. **The CLI publish path appends to the measured note instead of clobbering it**, and has the
   test it never had.
3. **The class is closed (R10)** by `SHARED_QUANTITY_CONTRACT` plus a control that:
   derives both sides from the two **scorers' own components** (no recomputation — R15
   independence); measures the declared containment across seeds *and* grace windows; requires an
   undeclared divergence to name an owning atom; and sweeps the **rendered** summaries so a third
   dimension printing the phrase without registering **fails**.
   R15 both ways: the register is proven falsifiable on two lies (populations declared coincident;
   denominators declared equal), the phrase sweep is proven to fire on a de-registered real
   emitter, and a missing dimension **raises** rather than comparing what is left.

The containment is declared **exact** on purpose, so that D16 landing **breaks its own
declaration** and forces a rewrite — rather than slipping past a control phrased loosely enough to
cover both worlds.

**Evidence:** 66 tests in `tests/tools/test_couple_w2_11_d5.py`; 126 across the gap/triad suites;
2147 passed, 4 skipped, 2 xfailed across `tests/tools`.

## Method note worth keeping

The first version of the CLI-path test banned the substring `"never observes"` — and **failed on
the honest sentence that negates it**. That is the AO2 `"none"` shape: a bare regex refusing a
truthful record. The assertion now tests the *claim* (the affirmative description must be absent,
its correction must be present), not the words.

## Why H27 is still L2

L3 is the claim that this harness measures what it says it measures. An instrument that says one
thing twice and means two different things does not carry that claim, and a reader taking either
figure as "what wrongful dunning costs this company" is misled by whichever they read.
`depends_on: [D16_...]` makes that hold a mechanism rather than an exhortation; the queue did not
shrink — D16 is drawable and the draw now points at it (verified against `supervisor`'s own
`_dependencies_met` logic).

D11's registered open question (`missed_failure_rate` structurally 0.0000, so the balanced error is
currently half a measurement) was the starting point this Hour was told to take, and it is real —
but it is **not** what holds the atom: it is an honestly-declared property of a world where
reconciliation catches every failure at due+grace, and D11 already proved by mutation that the
direction *can* fire.
