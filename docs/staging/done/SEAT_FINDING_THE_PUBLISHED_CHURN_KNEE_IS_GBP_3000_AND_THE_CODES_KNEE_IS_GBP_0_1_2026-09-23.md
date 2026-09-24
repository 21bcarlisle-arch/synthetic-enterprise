**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — found by the instrument built in this turn, on its first live run

# The published churn knee is GBP 3,000 and the code's knee is GBP 0.1, and the page still says the belief is flat

**Found** by `tools/published_feed_regeneration_check --working-tree`, built in this turn to close
the blindness that wedged the publisher. The chain it was pointed at came back DIVERGES on 35 keys
and only ONE of them is the working-tree edit it was built for. The other 34 are this.

**Not fixed here.** The producer `tools/churn_belief_size_response.py` is dirty in the shared tree
under another lane's edit, and the remedy is a judgement about what the artefact and its site door
are now STATEMENTS ABOUT — which belongs to whoever owns the churn belief, not to the commit that
built the instrument.

## The measurement

`tools/churn_belief_size_response.knee()`, run in the shared tree at HEAD `0637be0f1`:

| probe rate | `knee_kwh` published | `knee_kwh` now | `knee_prev_annual_bill_gbp` published | now |
|---|---|---|---|---|
| 150 GBP/MWh | 20000.5 | **1.0** | 3000.1 | **0.1** |
| 250 GBP/MWh | 12000.1 | **1.0** | 3000.0 | **0.2** |
| 400 GBP/MWh | 7500.6 | **1.0** | 3000.3 | **0.4** |

`the_knee_is_a_bill_not_a_consumption` regenerates **False**. It is published **true**.
`kwh_spread_across_the_probe_rates` regenerates **1.0**. It is published **2.67**.

The same figures reproduce identically in a `--shared` clone at HEAD, so this is HEAD's own code and
not another lane's dirty working copy: `company/crm/churn_model.py` is clean, and the divergence is
the same in both HEAD mode and working-tree mode.

## The cause, and it is a landing working correctly

`fc390b918`, *"the churn belief hears household size now, on a published basis"* — the director's
own instruction, measured, sourced to Ofgem/BMG *Understanding Consumers' Energy Tariff Choices*,
and correct. Before it, `estimate_churn_probability` returned identically 0.150000 from 1,500 to
9,000 kWh. After it, the belief responds to consumption everywhere, so the probe that looks for the
lowest consumption at which the derivative becomes non-zero returns the bottom of its search range —
1.0 kWh — at every rate. **There is no knee any more. That is the point of the landing.**

## What is wrong is everything downstream that still describes the old belief

1. `docs/observability/churn_belief_size_response.json` — never re-run since the landing. Its
   `knee`, `book`, `arms_book`, `partition` and `reading` blocks all describe the flat belief.
2. `site/data/value_arms.json` — copies that block through byte for byte via
   `tools/generate_value_arms_data._churn_belief_size_response`, and was regenerated *after* the
   landing, so it carries a `generated_at` of 2026-09-23 over a reading measured against code that
   no longer exists. **A stale intermediate republishes as a fresh-looking feed.**
3. The published sentence itself: *"The company's churn belief is FLAT in household size for {flat}
   of this book's {legs} domestic supply legs ... identically zero below GBP 3,000 of previous
   annual bill — an absent term."* The absent term is no longer absent.
4. `site/test_the_flat_churn_belief_reaches_the_reader.py` — the whole door is keyed to the flat
   belief. Its subject has changed, so it must be **re-derived, not re-pointed**.

## Why this is BLOCKING

It is a live misstatement on a public surface, and it is the load-bearing one: the flat-belief
finding is what the arms page offers as the reason *"the choosing has nothing to find"*. The page
publishes a diagnosis of the company that the company no longer matches, under a fresh timestamp.

## Why nothing caught it

The same blindness this turn's work repairs, one layer up. `published_feed_regeneration_check` did
not walk this chain at all — `grep -c churn_belief` on it was **0** — because the artefact lives in
`docs/observability/`, not `site/data/`. It is walked now
(`WATCHED_DERIVED_ARTEFACTS`), which is how this was found.

It is deliberately NOT in `COVERED_DERIVED_ARTEFACTS`, because promoting it today would red every
commit in every lane for a defect in none of them.
`test_a_watched_derived_artefact_that_reproduces_must_be_promoted` reds the moment the artefact is
regenerated, so the promotion cannot be forgotten and the empty set is not itself the evidence.

## The remedy, for the lane that owns it

Re-run the producer, then re-derive the reading and the site door against what the belief now does —
`docs/market_research/is_there_a_bill_level_at_which_switching_rises.md` is the reading the new
origin sentence points at, and it is the one that refutes the knee's SHAPE, which is now also what
the code says. The prediction worth writing down first: with the size term live, the belief's spread
across the book should be comparable to the world's 11.6x rather than 1.0x, and if it is not, the
new term is not reaching the population the page is about.

---

## DISPOSITION 2026-09-24 — discharged, and the residue is a different subject

Landed `6fd5aa1dc` (merged and pushed as `19bf3e20b`). All four named remedies are done, and the
measurement that establishes it is below rather than the assertion that they look done.

| # | Remedy | State |
|---|---|---|
| 1 | `churn_belief_size_response.json` re-run since `fc390b918` | **done** — landed here; `the_belief_is_flat_below_a_knee` is now `false`, `the_belief_goes_deaf_above_a_saturation` `true` |
| 2 | `value_arms.json` copies the block through | **done** — landed here, same commit |
| 3 | The published sentence | **done** — `reading` now composes from the deafness census: the belief HEARS size for 216 of 226 legs |
| 4 | `site/test_the_flat_churn_belief_reaches_the_reader.py` re-derived | **already done at HEAD** — 15/15 green, and it asserts against the feed's fields, not the page's prose |

**A fifth the finding did not name, and it was the live misstatement.** `site/capabilities/index.html`
argued the page's own block ordering from *"the belief is exactly flat in household size for 235 of
244 supply legs"* in three places — two HTML comments and, load-bearingly, the JS comment justifying
the **unconditional amber** on the churn-belief block. That third one did not merely go stale: it
justified an unconditional colour with one of two states, so it would have read as a licence to
branch the moment anyone noticed the condition had failed. All three now name the CHANNEL and leave
the reading to the block that renders it — keyed to the property, not to today's answer, which is
the rule that was broken when a count was copied out of an artefact and frozen beside it.

## `COVERED_DERIVED_ARTEFACTS` stays `{}`, and that is the measured answer, not an unfinished list

The draw that produced this pass asked for the promotion. **It is not owed, and the control saying so
is working.** `check()` over `WATCHED_DERIVED_ARTEFACTS` returns **DIVERGES**, not `AGREES`, so
`test_a_watched_derived_artefact_that_reproduces_must_be_promoted` is correctly quiet. Promoting
today would still red every lane for a defect in none of them.

**What diverges is the interesting part, and it is no longer this finding's subject.** Captured in
full rather than from the verdict's own sample — `_verdict` truncates `changed` to 10 while
`n_changed` reports 46, so the sample is not the population and reading it as one would have
inverted this conclusion:

```
FULL CHANGED: 46      TOP-LEVEL: Counter({'book': 46})
non-/book keys: (none)
```

**All 46 are under `/book`. Zero under `/knee`, `/reading`, or the flat/deaf booleans.** The knee
block this finding is named for now reproduces EXACTLY. The artefact is stale against the *book* —
164 billing accounts and 242 resi legs in the committed bytes against 154 and 224 regenerating now —
not against the code. That is book drift, a distinct subject with a distinct owner, filed as
`SEAT_FINDING_THE_CHURN_BELIEF_ARTEFACT_NOW_DIVERGES_ONLY_ON_ITS_BOOK_2026-09-24.md`.

## What was spent before this pass started, recorded because the draw asserted otherwise

* The draw's headline — *land the two artefacts, which NOW carry `the_belief_is_flat_below_a_knee:
  false`* — was **spent**. Both booleans were already at `origin/main`. The working copy of
  `churn_belief_size_response.json` moved 8 lines of re-run numeric jitter and nothing else.
* The draw's WHY — *the checkout is 13 behind because `origin_reconcile` refuses over these
  uncommitted paths* — was **spent mid-pass** by another lane's `surgical_land --merge` (PID
  3611198), which reconciled the tree to 0/0 while this pass was measuring. The live refusal in
  `.publish_gate_state.json` was `push_never_landed`, not the uncommitted paths.
* `--working-tree churn_belief_size_response` returns `WROTE_NOTHING`, which is **not** evidence the
  artefact fails to reproduce: it is a different standpoint from the one the control uses. Read as a
  verdict it would have justified exactly the wrong conclusion about the promotion.
