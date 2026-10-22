**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] No banner on the front door, and a home page that shows the ambition and how much has been built (2026-10-22)

**Type:** STEER, through the advisor channel. It amends this morning's `DIRECTOR_STEER_THE_FRONT_DOOR_FOR_A_NEWCOMER_IN_ENERGY_OR_TECH_2026-10-22.md`, and item 1 of `DIRECTOR_STEER_THE_FRONT_DOOR_SAYS_PUBLISHING_IS_FAILING_AND_IT_IS_NOT_2026-10-22.md`. Where they differ, this document governs. The director's words, from chat on Thu 22 Oct:

- 14:57 BST: "Why have a banner? No need? Also the claims are really weak they mostly point to faings in the model. The home page is not an impressive summary of what the ambition is and just how much has been achieved"

**When:** now, deployed this week. He has said twice today that he wants the site updated this week.

---

## 1. No banner on the front door

- **Take the freshness and publish-state banner off the home page.** In its place, put one quiet line under the figures: "Figures from the run of 19 Oct 2026 · published every Monday". Generate it at publish.
- **Publisher state belongs on "How it's built"**, as an operational status for those who want it. It still obeys the steer filed earlier today: it is never read from a stale snapshot and never extrapolated.
- **The class fix still stands**, along with the account of Monday's two failed attempts and today's three failed deploys.
- **Other pages keep their per-figure clocks.** Only the alarm banner goes.

## 2. Lead with the ambition and the achievement, not the gaps

The page is accurate, but it is built from caveats. Three of its four "found" items and every "Not yet" line describe what is missing. A reader in energy or tech comes away knowing what is wrong and not what has been done. Honesty here means accuracy: stating plainly what exists and is tested is not overclaiming (C2 still governs any performance claim).

**The shape he agreed, top to bottom:**

1. **The ambition, in one breath.** Can AI build and run an energy supplier on its own, and find value for each household? Then M1 verbatim, and M11 beside it.
2. **What has been built: generated numbers, no hand-typed figures.** The advisor counted these on origin on 22 Oct, so recompute them at publish:
   - about 13,800 commits since the repository began on 7 June 2026, and about 500 in the last week;
   - about 3,500 Python modules;
   - 2,085 test files;
   - 34 published knowledge pages, from about 200 sourced research notes;
   - 168,026 real half-hours settled, 2016–2025, the crisis included;
   - 400 founder households.

   Add whatever else the record supports, such as days since a human wrote code, checks proven able to fail, or lines of code. Use only what can be counted, and give each figure its clock.
3. **A complete supplier, shown as a capability grid.** One line per function, each linking to its evidence: winning customers (quote, credit check, cooling-off, change of supplier), pricing under the cap, hedging the wholesale book, half-hourly settlement, billing on three clocks, direct debits set and reviewed (SLC 27.15), collections and debt (IFRS 9 provision, SLC 27.8D), back-billing and read duties (21BA/21B), capital adequacy, and household carbon per half hour. State each line as what it does. A reader should finish this block thinking "that's a whole supplier".
4. **A world it cannot see into.** A synthetic Britain: households with hidden traits, per-home thermal physics under local weather, home moves and income shocks, all against the real 2016–2025 market. The company learns it only as a real supplier would. This is the design idea that impresses a technical reader, so say it with confidence.
5. **Built and run by AI.** The build loop, the checks that must be able to fail, and self-correction as a strength. The dual-fuel episode stays, as the system finding and fixing its own world within a day.
6. **The open question, in one line.** Does knowing each household create value, or does it only move it? It is being tested and the answer is not in yet. Link to the full account. One line, not a section.

**Move the gaps to where they belong.** The "Not yet" lines in the energy section, the "what is not built" paragraphs and "No customers. No licence." move to Capabilities and "What we know is wrong". Nothing is deleted. The front door keeps one link: "What is not built yet →".

**Tone.** Confident and factual. Write in the voice a strong domain reader respects: specific, with numbers, no hedging on things that are true. The brand line "hides nothing" stays, and it is met by the link to the gaps, not by leading with them.

## 3. Checks

- Re-run the cold-reader test on the new page, with one energy reader and one tech reader, each new to the project. Add a fourth question to the three already asked: "how impressive is this, and why?". Record the answers. If either reader's summary leads with the failings, the page has not met this steer.
- Generate every figure at publish. Check every claim in the capability grid against a test or record that exists.

## Report

One stretch-log entry with:
- the new page structure;
- the generated figures and their sources;
- the capability grid, with a link for each line;
- where each moved caveat now lives;
- the cold readers' answers.

— Director steer, 22 Oct 2026, his words above; the drafting is the advisor's.

## Done

- **Section 1** (no banner; one clock line written at publish): e825e8099.
- **Section 2 item 2** (what has been built, counted from git at publish): bd2ec5e1b.
- **Section 2, the rest** (this commit): `site/index.html` now runs in the agreed order. That is the
  ambition with M1 and M11, then the build and run strips, then a ten-line capability grid, then
  the world it cannot see into, then built and run by AI, then the open question in one line. Each
  grid line links to its page and names its tests in `data-test`. The tests are held by
  `site/test_the_front_doors_capability_grid_names_a_test_for_every_line.py`. The "Not yet" lines,
  the not-built paragraphs, "No customers. No licence." and the book's composition moved, none
  deleted, to `site/capabilities/#not-built`. The front door keeps "What is not built yet ->" and
  "What we know is wrong ->".
- **Section 3**: the cold-reader test was re-run with an energy reader and a tech reader and the
  fourth question. Neither summary leads with the failings. Both readers found the "shown" column
  thin, and the page cannot fix that until the value question resolves. Nine of their factual
  points were checked against the code and fixed. The answers, the fixes, and what was handed on
  are in the stretch-log entry "The front door leads with the ambition and what has been built".
- **Not done here:** the code-galaxy tab (the companion steer of 15:01). The home links to the
  existing module graph for now, and the tab is handed on as its own item.
