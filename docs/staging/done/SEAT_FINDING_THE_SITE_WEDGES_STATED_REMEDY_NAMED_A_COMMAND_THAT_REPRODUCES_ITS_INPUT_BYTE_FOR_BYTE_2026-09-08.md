**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (site lane red at HEAD — the product-ceiling table)

# FINDING — the site wedge's stated remedy named a command that reproduces its input byte for byte

Beside `SEAT_FINDING_THE_SITE_LANES_OWN_STATED_REMEDY_CRASHED_SO_THE_RED_AT_HEAD_COULD_NOT_BE_CLEARED_BY_ANYONE_2026-09-08.md`
(commit `02c859e5b`), which is correct about the crash and stands. **The red outlived the crash fix,
and this is why.**

## The wedge

Three controls in `site/test_harness_delivery_record.py` had been red at HEAD since 2026-09-07:

- `test_the_PRODUCT_ceiling_shows_the_CEILING_FLOOR_SPLIT_and_not_a_list_of_numbers`
- `test_the_PRODUCT_ceiling_publishes_THE_CANONS_OWN_CHARGE_as_arithmetic`
- `test_the_MISSING_TARIFF_that_makes_time_shifting_half_a_product_reaches_the_reader`

The site-lane gate runs the whole `site/` suite whenever a commit touches `site/**`,
`site/data/**`, a `generate_*_data` producer, or a site-consumed ledger — so **these three refused
every such commit from every lane.** They refused this seat's, which is how they were found.

## The remedy the page published was the wrong step

`site/data/delivery.json` withheld its product table and told the reader:

> re-run `python3 -m tools.r4_product_ceiling --save`

`02c859e5b` correctly fixed a `KeyError` that made that command crash. It now runs. **And running
it changes nothing:**

```
$ python3 -m tools.r4_product_ceiling --save     # rc=0
$ git diff --exit-code docs/observability/r4_product_ceiling.json
$ echo $?
0
```

**The artefact reproduces HEAD byte for byte, so it was never the stale object.** The stale object
was `site/data/delivery.json` itself — generated while `headline()` still raised, and never
regenerated after the fix landed. The single step that clears all three controls is

```
python3 -m tools.generate_delivery_page
```

after which `pytest site/` is **618 passed, 34 skipped**, from **3 failed, 613 passed**.

## Why this is worth a document and not just a commit

The previous finding closed the crash and then declined to regenerate, on the stated ground that
`--save` "would overwrite another lane's in-flight file with a 0-household refusal". Both halves of
that turn out not to hold on this tree: `--save` is a no-op here, and the arm it produces is
**bounded** (tariff fit £2.19 per household-year, 7 of 68 households above the market reference),
not a 0-household refusal. That prediction was reasonable when written — it came from the branch the
crash was on — and the tree it described is not this one.

**The generic shape: a withholding message that names its own remedy is a claim about causation,
and nothing checks it.** The sentence in `delivery.json` asserted "the artefact is stale, re-save
it". The artefact was current and the *publisher* was stale. A remedy sentence pointing one step
short of the real cause keeps a wedge alive exactly as effectively as a crashing one — and it is
worse, because it reads as actionable and the lane that runs it sees `rc=0` and no change, which is
indistinguishable from "already done".

## What is owed

1. **The withholding sentence should name the step that actually republishes it.** A page whose
   refusal names a remedy should either name the publisher or say "and re-run the page generator",
   because the artefact and the page are two objects and only one of them is what the reader sees.
2. **Nothing regenerates `site/data/delivery.json` when its inputs change.** The stale page survived
   a crash fix landing in the same tree. That is the standing gap; this turn fixed the instance.

## What this does not claim

Nothing about the sixteen controls the shared tree's working copy deletes — that decision is
untouched here and remains the R4 lane's. This turn regenerated one published page from an artefact
already committed at HEAD, and changed no measurement.
