**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `unminted`

# The comparison found the validator wrong three times, and not once was the arithmetic wrong

*Delivery seat, 2026-09-03. Work items 4 and 5 of
`DIRECTOR_BRIEF_INDEPENDENT_BILL_VALIDATION_2026-09-02`, which had been "not started" across three
reports.*

---

## 1. What landed

**Item 4 — the comparison.** `tools/bill_validation_comparison.py` joins the two exports and the
curtained validator, and files every difference as a finding about the biller. It is not behind the
curtain, and it does not need to be: §4.2 constrains the VALIDATOR's import graph; §4.3 constrains
an ORDER, which is a property of a process. So the order is enforced — `compare_account` produces
the reconstruction and takes its digest **before** the statement is fetched, and the statement is
reached through a callable that is not invoked until then. A test drives it with a statement source
that raises if reached early, so §4.3 is a thing that can fail rather than a sentence.

**Item 5 — the schedule.** `background/bill-validation.{service,timer}`, hourly, `Persistent`,
declared in `schedule_manifest.yaml`. Installed and armed: `schedule_reconciler` reports **0 drift
alarms, 19 OK**, and the timer's next firing is on the clock. The declaration is what makes item 5
checkable rather than claimed — an undeclared unit reports `UNDECLARED_UNIT` and an unarmed one
reports `UNIT_NOT_ENABLED`, which is precisely the difference between a validator that ran once and
one that runs every cycle.

There is no sampling mode on the scheduled path. `--limit` exists for tests and a limited run says
so in its own output, because a validator with a coverage dial is one whose coverage becomes a
decision somebody makes under time pressure. It costs **under two seconds** for 251 accounts and
11,549 bills, so there was nothing to trade away.

## 2. The first full run found 310 differences, and every one of them was the validator

| | |
|---|---|
| claims compared | 69,294 |
| AGREED | 57,435 |
| DISAGREED | **310** |
| UNCHECKABLE | 11,549 |

Every difference was **exactly one penny**. Fifteen were on the two reconstructible money lines,
and **fifteen out of fifteen were in the biller's favour** — a one-sidedness that reads like a
systematic overcharge and is not one. Under a fair coin that is about 1 in 33,000, which is exactly
why it was worth looking at rather than reporting.

**Three separate defects, each found only by fixing the previous one and re-running.**

1. **Banker's rounding.** Every instance sat on an exact half-penny (38.735, 11.625, …). Python's
   builtin `round()` goes to the even penny; `saas/money.quantize_gbp` declares ROUND_HALF_UP in
   `Decimal` and says why. The validator had silently inherited the language default. Repairing it
   took the line differences 15 → 1.
2. **Float subtraction.** `8303.3 - 8090.8` is exactly **212.5** kWh in decimal and
   **212.4999999999991** in binary float, so the energy line came out at £40.544999999999824
   instead of exactly £40.545 — a hair *below* the boundary, rounding down, one penny out. Fixing
   the rounding had not fixed this: the subtraction had already lost it.
3. **Float multiplication.** Fixing the subtraction moved a **second** bill from
   agreeing-by-luck to disagreeing, because `212.5 * 19.08 / 100` in float is 40.544999999999995 —
   the multiply reintroduced the error the subtraction had just stopped making. Its float volume
   had previously landed *above* its boundary, so it had been agreeing for the wrong reason.

**Not one of these is an arithmetic error.** Every formula was right at every stage. This is the
brief's own thesis demonstrated on the brief's own validator: *"each piece is locally plausible and
the whole quietly stops adding up"* — and it took a second independent implementation to see it,
because nothing about a single implementation says which side of a half-penny it lands on.

**§4.4 anticipated this exactly**: *"Where the validator is shown to be wrong, that is itself a
finding — about the published rules, the export's completeness, or an ambiguity in a concept."* The
concept is **how money is rounded**, and it is filed as a gap in §5 below.

## 3. What survives, and the cause is NOT established

**295 VAT differences**, all exactly one penny, net **−£1.33** across the whole book (in the
customer's favour): 214 where the biller charged less than the statutory rate on the printed base,
81 where it charged more.

The obvious explanation is that the validator computes VAT on the base of **rounded printed lines**
while the biller computes it upstream on **unrounded** components. That was tested, not assumed:
reconstructing the base from unrounded values reproduces the biller on **137 of 295**. It is
therefore recorded as a candidate and not as the cause.

**And the experiment cannot be pushed further from here.** Two of the three base components can be
had unrounded; the third is the bundled network-and-policy line, which nothing can reconstruct, so
the "unrounded base" I could build is still partly rounded and the test is underpowered by
construction. **The uncheckable line does not merely block rebuilding VAT — it blocks diagnosing a
VAT difference.** That is a sharper statement of the §3 residual than the original brief made, and
it belongs in `WHAT_THE_BILL_VALIDATION_CANNOT_CATCH.md`.

They are not smoothed. There is no tolerance beyond `PENNY = 0.005`, which is the resolution of the
quantity and not a band inside which disagreement is forgiven. "295 bills disagree by a penny each"
and "the arithmetic agrees" are different statements and only the first is true.

## 4. A defect my own test caught, on a branch I had called impossible

`_claim` computed `observed - expected` unconditionally. Every claim carries numbers except
`period_alignment`, whose two sides are **date ranges** — so the only path that would ever have hit
it is the one whose own comment says it is structurally impossible, and it would have raised
`TypeError` instead of reporting the misalignment. It was caught by the test written for that path.
That is the argument for writing a test for a branch you believe cannot be taken: the branch is
taken the day the belief stops being true, which is the day nobody is watching.

## 5. The knowledge gap this opened, filed rather than filled

**No artefact in `docs/domain_artefact_library/regulatory/` states a rounding convention for a
domestic energy bill.** Both sides silently inherited one from their language, and they differed.
The validator now declares ROUND_HALF_UP explicitly, with `ROUNDING_SOURCE` saying plainly that it
is *"declared by this module, not read from a published record ... the one input to this
reconstruction that is a convention of ours"*.

It is declared and not imported, deliberately. `saas/money` has exactly this function and the
curtain forbids importing it — and rightly: copying the **rule** is legitimate, importing the
**implementation** would make the two sides agree by construction on every boundary, which is the
tautology the whole exercise exists to avoid. If the rule itself is wrong, both are wrong together
and this design cannot catch it.

**The open question for the knowledge layer:** does HMRC or Ofgem publish a rounding rule for a
domestic energy invoice, and if so is it half-up on each line or on the invoice total? Until that
is established, the convention is ours and is labelled as ours.

## 6. Adjacent, not fixed here

`tests/tools/test_the_curtained_validator_rebuilds_the_bills_without_us.py` and two billing tests
carry population floors of `>= 11_000` bills. A live simulation run rewrote the ledger to **10,993
invoices** at 08:45 today and all four went red — **0.06% below the floor**. The floors are right to
exist and are pinned to one run's book size, which is a simulation output that legitimately varies;
a floor that trips on a 0.06% wobble is a floor that gets lowered on sight, and a floor that gets
lowered on sight has stopped being a control. The property they want is *"the ledger has not
collapsed and nothing was silently skipped"*, which a fraction-of-the-ledger check states and an
absolute count does not. **Not repaired here** — it is three other tests' subject, the ledger change
is another lane's uncommitted work, and the repair is a different argument from this commit's.

## 7. What a reader should not take from "57,450 agreed"

11,549 claims — one per bill — are **UNCHECKABLE**, and the report says so on its own last line
rather than in a footnote. The network-and-policy line bundles DUoS, TNUoS, BSUoS, RO, FiT, CfD, CM
and smart metering behind one figure that no published artefact reconstructs. Half of every bill in
this book has never been independently checked and this design cannot check it. The agreement that
does exist is real, it now carries a run id, a commit and a clock (§4.6), and it covers the two
money lines, the volume behind them, the VAT rate against published law, and the bill's own
internal identity. It does not cover the largest pass-through line on the bill.
