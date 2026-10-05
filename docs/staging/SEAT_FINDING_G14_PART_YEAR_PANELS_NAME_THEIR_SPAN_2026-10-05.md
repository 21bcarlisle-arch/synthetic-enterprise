**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** `G14_half_hourly_grid_carbon_intensity_aligned_to_settlement` · **Claim:** `g14-explore-partial-year-panels-say-the-year` (Lane 0 delivery)

# Explore's part-year carbon panels now name the span their comparator covers

The duplicate-work note at draw time named this id as already held. The holder was this
invocation's own pid, and nothing else was working on the panel.

**What was wrong** (the G14 Expert Hour second re-take graded it MINOR and must-fix): two of the six
household-day panels fall in a part year: C8's summer day (2016, covering 1 Mar to 31 Dec) and C9's
hardest day (2025, covering 1 Jan to 7 Jun). Their flat comparator is the mean over only those
dates. The panel still called it "the year's average" and "the annual-average method", and said
"Across 2025 as a whole" over 7,582 half hours. The timed kg was right throughout; only the
yardstick's name was wrong.

**What changed:**
- `Footprint.partial_level_spans` in `company/carbon/half_hourly_footprint.py` records the covered
  span of every part-year level that priced a read. It reads `grid_intensity_level`, the one owner
  of the level. It is empty for whole years.
- `tools/generate_explore_carbon.py` carries it onto each row as `level_covers`, or `null` for a
  whole year. The spread sentence and the comparator share the span, because `year_stats` and the
  level are normalised over the same half hours (7,582 and 14,564 in both).
- `site/explore/index.html`: a part-year panel now says "average intensity over 1 Jan 2025 to 7 Jun
  2025 (the part of 2025 the published record covers, not the whole year)". It says "that part-year
  average", "× that average", and "From 1 Jan 2025 to 7 Jun 2025, the part of 2025 the published
  record covers". Whole-year panels are unchanged.
- `site/data/explore_carbon.json` was regenerated. The only diff is the new field on six rows,
  plus the timestamp.

**Door test:** `site/test_explore_second_clock.py::test_a_PART_YEAR_comparator_is_named_as_its_span_and_never_as_the_year`.
It checks each row's `level_covers` against the feed's published `covers`. It then renders the
household that has both kinds of day and asserts three things: the span is named, "as a whole"
is absent for the part year, and the whole-year label survives on the other day. That last check
proves the branch is not taken everywhere. Mutation `var part = null;` → red (see the commit).
