# SEAT FINDING — the control refused the stale capture and the page went on printing a band verdict

**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

BLOCKING by construction, not by choice: clause 2 of `background/finding_severity` says a finding
whose claim is that an instrument in this area is untrustworthy may not grade itself down. The claim
here is that `tools/measure_departure_level.py` printed a whole-book band verdict off a capture its
own control had already refused.

**Class:** `figures_on_a_superseded_clock` (primary), `controls_that_cannot_fail` (secondary)
**Filed:** 2026-09-03, delivery seat, Lane 0, second tick — born archived, existing classes.
**Subject:** `tools/measure_departure_level.py::main` vs `::world_book_rate_pct`.
**Discharged:** `tests/architecture/test_a_capture_may_only_judge_the_world_that_produced_it.py::test_the_printed_page_refuses_on_the_same_grounds_as_the_band_control`,
`tests/architecture/test_a_capture_may_only_judge_the_world_that_produced_it.py::test_the_page_and_the_control_take_their_verdict_from_one_gate`
— 2026-09-03, same commit as the defect's discovery, both mutation-proved in both directions.

---

## What happened

`5554c2910` repaired the capture-staleness class by adding two refusals — did this capture run under
the anchor block that is live, and is it fully committed. Both went into `world_book_rate_pct`,
which is what the band control reads. Neither went into `main`, which is what a **human** reads.
`main` kept applying `account_denominator_refusal` alone.

That is invisible for as long as the shipped default happens to be fresh — which is exactly the
condition a re-fit destroys, and a re-fit is the documented remedy this instrument itself
recommends. Re-fitting the anchor block made the then-default capture stale in **9 of its 10
years**, and the two readings came apart inside the same process —

```
$ python3 -c "import tools.measure_departure_level as m; print(m.world_book_rate_pct())"
({}, 'this capture ran under a superseded level anchor in 9 year(s) of 10 ...')

$ python3 tools/measure_departure_level.py     # the same module, the same capture
  ── THE WHOLE BOOK: every departure on either route, over the accounts on the book ──
  2024     12.5–16.1       13.84       9.68        62        1        5   inside
```

The control said *I cannot tell*. The page said **inside**.

## Why this is the same defect as the one it lives inside

`SEAT_FINDING_THE_INSTRUMENT_JUDGES_THE_WORLD_ON_A_SUPERSEDED_CAPTURE_WHOSE_SVT_HALF_IS_IN_NO_COMMIT_2026-09-03.md`
established that a whole-book reading of *"OUT OF BAND, HIGH, in 8 of 8 — the world departs 1.3×
harder than the GB record"* reached a direction file and was very nearly acted on by re-fitting in
the wrong direction.

**That reading was read off the printed page, not off the control.** So the repair for the class
left live the exact surface through which the class had done its damage. A reader — human or the
next tick — runs the tool, gets eight confident rows and a verdict, and has no way to learn that
the band control at the same commit refuses to produce one.

CLAUDE.md: *"Fail closed, and say so on the surface. 'We cannot tell' is a result. It belongs on the
page, not in a footnote."* The refusal existed and was correct; it simply was not on the page.

## The repair

One gate, `book_reading_refusal`, called by both `main` and `world_book_rate_pct`. Not the refusal
trio copied into `main` — that is this repo's VAT shape (one requirement, several implementations,
one repaired and the others left live), and it is precisely how these two came apart.

`main`'s existing "both routes readable and still no reading" branch already prints the refusal
verbatim, so the page now says:

```
  This capture sees both routes and STILL cannot be read on an account denominator:
  this capture ran under a superseded level anchor in 9 year(s) of 10 -- 2016: ran at 3.05362,
  live block says 4.12042 (3 row(s)); ...
  Until that is established, the table above is the renewal route alone.
```

## And the first draft of the control was fail-open on its own mutation

Recorded because it is the more useful half of this document. The parity control's second leg first
read the function source as **text** and asserted `"book_reading_refusal" in source`. Run against
the mutation it exists to catch — narrowing `main`'s gate back to `account_denominator_refusal`
alone — it **passed**, because the explanatory comment one line above the mutated call still
contained the name.

A control a comment can satisfy is the catalogued tautology. It now parses the AST and asserts an
actual `ast.Call`, and both legs fire on both mutations:

| mutation | behavioural leg | one-gate leg |
|---|---|---|
| narrow `main`'s gate to `account_denominator_refusal` | **FIRES** | **FIRES** (text version: survived) |
| drop `stale_anchor_refusal` from the shared gate | **FIRES** | **FIRES** |

## What is NOT claimed

- **Not** that the page was wrong on every previous run. While the shipped default was fresh, the
  two paths agreed. The defect is that nothing made them agree, not that they always disagreed.
- **Not** that the other two instruments still defaulting to the superseded capture are fixed here.
  `tools/fit_departure_hazards.py` and `tools/split_price_response_by_curve_position.py` both still
  name `c2_departure_factors.json`; `tools/fit_year_level_anchor.py` was the third and is repaired
  in this commit, by importing the instrument's default rather than carrying a second copy of the
  path. The remaining two need their own read, as the companion finding said.

## The fitter's own default, and why the gap WIDENED before it was closed

`tools/fit_year_level_anchor.py` defaulted to `c2_departure_factors.json` throughout. That was
survivable while it was merely one version behind. It stopped being survivable when `712ae5323`
repointed `measure_departure_level.DEFAULT_TABLE` at `c5_refitted_departure_factors.json`: from
that commit the tool that **solves** the anchor and the tool that **judges** it read different
captures two generations apart, and a re-fit run the documented way —
`python3 -m tools.fit_year_level_anchor`, no argument — would have been solved against the
superseded capture and then graded against the current one. Both exit zero. Both print a plausible
table. Nothing anywhere says the two tables describe different worlds.

Repaired by **importing** `measure_departure_level.DEFAULT_TABLE` rather than writing the correct
string a second time, so the next repoint cannot reach one tool and miss the other. Safe in that
direction: `measure_departure_level` does not import the fitter, so there is no cycle, and
`test_the_FIT_is_not_gated_by_this_because_fitting_on_the_previous_anchors_is_what_a_fit_is` still
holds — the fitter takes the instrument's *capture*, never its *refusals*.

## What this tick did NOT do, recorded so the next reader is not misled

The re-fit itself, and the re-capture it needs, were landed by a **concurrent lane** at `712ae5323`
while this tick was running. This tick computed the same fit independently from the same committed
capture and got **byte-identical values to six decimals**, which is recorded in the pre-registration
as a reproducibility result. It is not a claim to have landed them.
