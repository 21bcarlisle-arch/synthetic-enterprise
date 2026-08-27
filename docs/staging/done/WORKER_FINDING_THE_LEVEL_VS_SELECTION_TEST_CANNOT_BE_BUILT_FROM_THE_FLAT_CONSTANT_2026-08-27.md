# The level-vs-selection test cannot be built by overriding the flat margin, and the attempt nearly published a 9.4× result that was an artefact

**Date:** 2026-08-27. **Author:** the delivery seat.
**Status:** the tool was built, run, disproven and WITHDRAWN in the same turn. No instrument was
landed. What follows is what the attempt established, so the next one does not start here.

## The question, which is still open and still worth answering

With the renewal schedule repaired, the value arm beats flat rules by £7,066 and
`belief_vs_outcome.discrimination_auc` is **0.4653** — below a coin flip. The advantage cannot be
attributed to inference. What the arm demonstrably did was price high: a median margin of
**£44.50/MWh** against the flat rule's **£2.00**.

So: was the advantage the LEVEL it priced at, or the SELECTION it made? The intended test was a
third arm — flat rules at the value arm's own median — holding the level and removing the choosing.

## What was built, and the two confounds that killed it

`tools/couple_price_level_vs_selection.py` overrode `TARGET_MARGIN_GBP_PER_MWH` at all three
binding sites and ran the control arm. On the 2019 window it returned:

```
flat@2.00   net  £14,031.86
value arm   net  £17,099.66   advantage  +£3,067.81
flat@44.50  net  £42,872.76   the level alone gets +£28,840.91
share of the advantage explained by the LEVEL: 9.40
```

A bare price rise appearing to earn **9.4× the arm's entire advantage** is a spectacular result,
which is the only reason it got checked before it got reported. It is an artefact, twice over.

### Confound 1 — the flat path does not clamp to the lawful ceiling

Measured directly, with a ceiling £5/MWh above the base rate:

```
FLAT at target £2.00,  ceiling £105 -> offered £102.00
FLAT at target £44.50, ceiling £105 -> offered £144.50   <-- £39.50 ABOVE the cap
VALUE arm,             ceiling £105 -> offered £105.00   <-- clamped
```

`decide_margin`'s FLAT branch returns before the `lawful` filter that bounds the value arm's
search. So the counterfactual let one arm price above the Ofgem cap while holding the other to
it. That is not level-versus-selection; it is unbounded-level versus bounded-selection.

### Confound 2 — and this one is fatal to the whole approach

`renewal_margin_uplift` — the adapter the live chain actually calls — opens with:

```python
if arm == FLAT_RULES:
    return MarginArmUplift(0.0)
```

**The flat arm applies no uplift at all.** It is not "the arm that chooses £2.00 at a renewal"; it
is the arm that does nothing at renewals, and the £2.00 lives in `price_fixed_tariff`, inside the
BASE rate of every contract.

So overriding the constant does not raise the flat arm's renewal decisions. It raises the base
tariff for **every customer on every contract**, while the value arm's uplift touches the 25
renewals it priced. The two runs differ in population as well as level, and the £42,872 is
measuring "charge the whole book £42.50/MWh more, uncapped" — a different question, and one whose
answer is confounded by Confound 1 anyway.

## What the correct test needs

A genuine third arm inside `renewal_margin_uplift`: **apply a FLAT uplift of the value arm's median
at exactly the renewals the value arm prices**, under the same ceiling. That is a real arm and not
a constant override, because the thing being held constant is the DECISION POINT, not the price.

That is more invasive than a harness counterfactual and it puts a measurement construct next to
the company's decision surface, which is the reason this attempt tried to avoid it. The avoidance
was wrong: the cheap route measured something else and said so only when pushed.

## The other finding, which is real and separate

**The flat arm can offer above a lawful ceiling.** At the shipped £2.00 this is latent — base + 2
presumably never breaches the cap — but nothing in the code prevents it, and the value arm's
identical situation IS guarded. Filed as an observation rather than a repair, because whether it
can bite at £2.00 needs measuring on real base rates and this turn did not do that.

## What this cost, and the one thing that worked

Two confounds, a withdrawn tool and its tests, and a 9.4× headline that would have been wrong.
What stopped it was checking a result *because it was too good*, which took two minutes against
the several hours the tool took to build.

The instrument's own refusal did fire correctly and is worth keeping in mind for the rebuild: it
would have caught a silent no-op override, and it was right to demand the control's net actually
move. It just cannot catch a counterfactual that moves the wrong thing.

---

## The cap-latency question was attempted, and the measurement was the wrong one

This finding closed with: *"whether it can bite at £2.00 needs measuring on real base rates and
this turn did not do that."* It was attempted immediately afterwards. The attempt is recorded
because it failed in an instructive way and would otherwise be repeated.

### What was measured

Every domestic electricity **settlement** record of a full-decade control-arm run, compared
against `get_cap_unit_rate_for_date("electricity", d)`:

```
checked        178,229 records (2019-2025)
above the cap   28,093  (15.8%)

tightest headroom by year
  2019   +£2.29        2021  −£101.40      2023  −£145.11      2025  −£301.78
  2020  +£15.59        2022  −£172.52      2024  −£132.41
```

A 15.8% breach rate against a statutory consumer protection is the kind of number that gets
reported immediately. It should not be, and this one nearly was.

### Why it is not a compliance finding

**The Ofgem default-tariff cap governs default and standard-variable tariffs, and it binds the
OFFER.** A fixed-term contract agreed before a cap change lawfully runs to its end at the agreed
rate; the cap does not reach backwards into a live term.

Checked rather than assumed: `PROS-2019-0050` carries **exactly one distinct rate — £188.59 —
across its entire breach window**. A single constant rate over hundreds of consecutive settlement
days is a LOCKED term, not a default tariff drifting above a ceiling. The comparison was
settled-rate-versus-current-cap, and that is a comparison with no rule behind it.

The 2019 and 2020 headrooms being positive and the crisis years being deeply negative is the same
story from the other side: fixed rates locked before the spike, carried through it. That is the
world behaving correctly.

### The real question, still open, and narrower than the attempt

Does the flat arm ever **OFFER** above the cap **at a renewal**? That needs the offered rate at
renewal points — not settled rates — compared against the cap in force on the term-start date, and
restricted to accounts whose product the cap actually governs. The unguarded ceiling in
`decide_margin`'s flat branch is real either way; whether it can bite is still unmeasured.

### The pattern, recorded because it is the fourth today

Three measurement designs in this one investigation measured something other than what they were
built to answer: the constant override (raised the whole book, not the renewals), the 2019 cap
check (the least informative window), and this one (settled rates against a rule that governs
offers). Each was caught, and each was caught by the same move — asking what the number would have
to mean for it to be true, before writing it down anywhere permanent.

None of them was caught by the code being wrong. Every one ran perfectly and answered a question
nobody had asked.
