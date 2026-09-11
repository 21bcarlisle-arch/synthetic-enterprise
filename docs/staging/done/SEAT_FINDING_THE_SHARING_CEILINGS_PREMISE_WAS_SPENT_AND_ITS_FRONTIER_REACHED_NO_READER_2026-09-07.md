**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# The sharing ceiling was already built and landed; what was left was the half of it no reader could see

**Found:** 2026-09-07, delivery seat, claim `a49-ceilings-the-sharing-side-of-r3`.
**Instrument:** `tools/tou_sharing_ceiling.py` (landed at `6fb5f64f3`, unchanged by this turn).

## The premise was spent, and the re-measure says so

The item drawn for this turn asked for *"a ceiling instrument for the SHARING side: what a
time-of-use tariff could be worth, to the household and to the company, on this book — before any
ToU product is built."*

**It was already built.** `6fb5f64f3` — *"the sharing side of R3 gets a ceiling: 7.4x the carbon,
and a third of the book could be sold it"* — is an ancestor of `origin/main` and landed under this
same claim id in an earlier turn. It carries the instrument (769 lines), its suite (382 lines), the
artefact, the pre-registration, the finding, and the `/harness/` publication.

I re-ran the measurement from this worktree rather than trusting the artefact, per the standing rule
that a landed claim's own measurement is re-run from the other tree before it is called complete.
**`docs/observability/tou_sharing_ceiling.json` reproduced byte-identically** — `git diff` returned
nothing at all, not merely nothing substantive — and its 55 controls pass here. The published
headline is real: £51.36/household-year created at a shiftable share of 1.0, £13.33/MWh avoided over
1,520 whole days of Elexon MID, clearing its skill-free null by 5.04x at the median of 60
matched-panel draws.

*(This reproduction was not pre-registered. It is a byte-comparison against a committed artefact
with a binary outcome and no free parameters, so there is nothing a prediction could have
disciplined. Recording that judgement rather than leaving it implicit.)*

The prior turn's pre-registration is properly reconciled beside its answer, including the part that
went against it: the predicted floor of 3x was missed by the worst draw at 2.97x, and the finding
records that rather than widening the range afterwards. That is the discipline working.

**So I did not do the work twice.** What follows is what re-reading the landed work found still open.

## What was actually missing: the sharing side reached no reader

The instrument computes `sharing_frontier` — how the created value divides between household and
company at each pass-through — and `the_interior_optimum`, the conclusion that the company's take is
zero at *both* ends and therefore maximised strictly in the interior.

**Neither reached any reader.** `/harness/` published the *size* of the missing tariff (£51.36, 7.4x
the carbon, 22 reachable households, £1,125 across the book) and stopped there. A grep of the page,
the delivery feed and its generator for `frontier`, `pass_through` or `pass-through` returned
nothing.

That is precisely the defect the previous commit on this thread was written to fix, arriving one
level down: *an instrument nobody reads is an orphan.* The landed finding's own "what is next" names
it as item 1 — *"`/harness/` should carry the frontier beside the two ceilings already there"* — and
explicitly defers it. It was still deferred.

And it is not a cosmetic gap. The item's brief was *"worth … to the household **and to the
company**"*. The company half is exactly the frontier. The published page bounded what the tariff
creates and said nothing about how any of it would be shared — which is the same
value-created-without-an-instrument-of-sharing shape that opened this whole thread, reproduced
inside the fix for it.

## The trap in publishing it, which is why the rows are not published

The obvious move — render the frontier's rows — is wrong, and quietly so.

The frontier holds the created value **fixed**. Its rows are therefore conditional on the shift
happening at all, and its `pass_through: 0.0` row reads:

> household £0.00 · **company £51.36**

Published as a row, that says the company banks the entire ceiling by passing nothing through. It
cannot: at zero pass-through a household's bill is identical whenever it draws, so nothing moves and
nothing is created. The £51.36 in that row is a share of a value that does not exist in that world.

Publishing it would be **value TRANSFERRED dressed as value CREATED** — CLAUDE.md's first
consequence of the mission, inverted, on the company's own surface: *"Transfer is not creation.
Charging someone the cap moves value without making any."*

So the rows do not travel. What travels is the identity, bound to the two endpoints that make it a
decision, as one block that cannot render in pieces.

## What landed this turn

1. **`tools/r4_product_ceiling.py`** — the `if_a_time_of_use_tariff_existed` arm gains
   `the_split_is_an_identity`, `the_optimum_is_interior` and `where_the_optimum_sits`, read from the
   instrument and never recomputed. `the_split_is_an_identity` is **derived**: it checks that the two
   shares sum to the created value at every row, so it goes false if the frontier ever stops being an
   identity. Keyed to the property, not to today's answer. The block carries
   `why_the_frontier_ROWS_are_not_published_here` so the next session does not re-add them.
2. **`site/harness/index.html`** — renders *"And sharing it creates nothing"* with the interior-optimum
   conclusion and its named gap, gated on the derived flag. Verified against the **real** feed, not a
   fixture.
3. **`site/test_harness_delivery_record.py`** — two controls, both mutation-proven below.

The instrument itself is untouched. Nothing about the measurement changed; only whether anyone can
read the half of it that was already there.

## The controls, and the poison round that proves they can fail

Run before claiming them, because "survived" is ambiguous and a control that has never failed is not
yet a control.

| mutation | control | fired |
|---|---|---|
| hardcode `the_split_is_an_identity` to `True` | `..._is_DERIVED_from_the_frontier_and_can_go_false` | ✅ `assert True is False` |
| drop the sharing sentence from the page | `..._reaches_the_reader_and_the_frontier_ROWS_never_do` | ✅ text absent from rendered panel |
| ship the frontier rows into the payload | same | ✅ rows detected in the delivery payload |

The first control drives the derivation **twice from one artefact shape** — the real frontier where
the shares sum, and a poisoned one where they do not — because a flag only ever asserted true is a
flag no mutation can fail. The second asserts both the presence leg and the withheld leg, so a page
that renders the claim unconditionally reds.

73 tests pass across `site/test_harness_delivery_record.py`, `tests/tools/test_r4_product_ceiling.py`
and `tests/tools/test_tou_sharing_ceiling.py`.

## What this does NOT say

- **Not that the ToU tariff should be built.** Unchanged from the landed finding: £51.36 is a ceiling
  at a shiftable share of 1.0 that no household has, it is gross of half-hourly settlement and a
  smart-meter rollout, and only the wholesale leg is counted.
- **Not where the company's optimum sits.** The endpoints give the *shape* — strictly interior — and
  that needs no elasticity. *Where* needs the shift response as a function of pass-through, and
  nothing in the knowledge layer, the commons or the market research establishes one. It is published
  as a named gap and is now visible to a reader, which it was not before.
- **Not that the frontier is a measurement.** It is an identity, asserted in code. The page says so
  in those words so no reader takes a point on it for a finding.

## What is next on this thread, and I am not asking

**The shift response as a function of pass-through** is now the only thing standing between the
frontier and a decision, and it is a question to research rather than a value to pick — the same
class of gap as the shiftable share, and the two multiply. That is the next increment, and it is a
knowledge-layer question before it is a code one.
