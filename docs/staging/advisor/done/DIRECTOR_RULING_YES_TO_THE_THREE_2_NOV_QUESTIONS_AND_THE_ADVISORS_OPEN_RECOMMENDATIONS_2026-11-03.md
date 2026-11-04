**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] Yes to the three questions raised on 2 Nov, and to the advisor's open recommendations (2026-11-03)

**Type:** RULING, through the advisor channel. The director's words, from chat on Tue 3 Nov:

- 17:46 GMT, after the advisor set out the three open `for_the_director` rows with a recommendation of yes on each, plus its earlier recommendations still awaiting his word: "Yes to all your recommendations"

## A. The three open rows: all yes

1. **`your-2-nov-ruling-to-register-with`: yes.** Amend W11 in `docs/design/DIRECTOR_CANON.md` to the row's proposed wording, verbatim: "No personal microdata in the repository, the site, the world or the company. Licensed, de-identified survey microdata may be read on this machine outside the repository, under its licence, and only non-disclosive aggregates (fitted loadings, cross-tabs meeting the depositor's cell rules) leave it." This is a director document changed on his word: use the `Director-doc: his-words` trailer and cite this file.
   - **Order matters.** First amend W11. Then reword the public pitch claim, and every page or document that states "no household data has entered the system", to "no household record leaves a licensed local store". Only then download any file. Run the canon drift check over every quote of W11.
   - The licence's own conditions (storage, access, deletion, no linkage) are rules this machine keeps. Record where they are kept.
2. **`the-next-world-additions-ranked-30-oct`: yes.** The order as proposed, after the correctness exit test. Under the row's own note, the W11 yes lifts life stage and precarity: re-rank them against reputation with that in mind, and say where they land.
3. **`the-design-read-of-the-value-test`: yes.** All three amendments, with the other four fixes landing in the same pass.

Close all three under the 28 Oct rule (work id, done-means, due).

## B. The advisor's earlier recommendations, which this "yes" also covers

These are not urgent. Rank them yourself. None goes ahead of the correctness exit test.

1. **The naive organ may ask whether work connects to the purpose.** Your 2 Nov repair was right and kept `is_purpose_claim` unchanged. But that filter is a substring match. It declines "does this work move enterprise value?", which questions a link to the purpose and does not question the purpose itself. The organ's live catch of the no-caller class on 13 Jul ("what decision rule actually consumes the physics forecast's output?") was exactly that kind of question. Make the line separate *questioning the goal* (always declined) from *questioning whether something serves the goal* (askable). Prove both branches on real wording.
2. **Two practices from Predbat** (springfall2008/batpred, read on 31 Oct: personal-use licence, so ideas only and no code):
   - **A replayable run snapshot.** Predbat lets a user dump the full planner state, replays it against the current code, and keeps good cases as golden regressions. No Poesys run leaves a snapshot that can be replayed. The run ledger exists and nothing calls it. Weigh whether the run ledger, completed, becomes this.
   - **A test-order hunt.** A shuffler finds tests that pass or fail depending on run order and bisects each failure to its culprit and victim. With about 39,000 tests and concurrent lanes in one tree, measure first whether order dependence exists here. If it does not, say so and stop.
3. **For the map design (`DIRECTOR_STEER_THE_MAP_..._2026-10-24.md`):** NVIDIA's Auto Ontology (Apache-2.0) uses a model to *propose* concepts, and to spot one concept defined differently in different places, then certifies each before it counts. Consider proposing-then-certifying to draft the register's first 100–150 concepts and to find several-homes candidates. No tooling is implied. Its heavy stack (web app, Postgres with vector search, hosted models) is not wanted.

## Risk

Touches: canon W11 (a director document, on his explicit word), the public pitch claim and every quote of it, `for_the_director`, and later the naive organ's purpose line and the harness items in B.
Blast radius: one public claim reworded, and a licensed data store on this machine outside the repository. Nothing in B touches the world or the supplier.
Probable failure mode: a household-level file reaching the repository, a test fixture or the site. Before the first download, add a control that refuses any commit carrying the downloaded data's files or their row-level contents, and prove it fires. A second failure mode: the pitch claim left in its old wording somewhere after the amendment.
Proportionality: contract-touching — implement with the named mitigations (amend, then reword, then the control, then download).

— Director ruling, 3 Nov 2026, his words above; the drafting is the advisor's.

## Done

*4 Nov, the autonomous worker, claim `w11-amended-and-the-pitch-claim-reworded`.*

**A1, in the order he set.**
- **W11 amended**, verbatim from the row, in `docs/design/DIRECTOR_CANON.md`, with the `Director-doc: his-words` trailer citing this file. `CLAUDE.md` quotes the new wording.
- **The pitch claim reworded** to "no household record leaves a licensed local store" wherever it was stated as a present fact: `PURPOSE_PITCH_V4.md`, `SITE_CONSTITUTION.md`, `f2_explaining_what_we_do_simply.md`, `f3_volunteer_programme_mechanics.md`, `POPULATION_COVERAGE_JOINT_STRUCTURE.md` (marked beside the claim), and `docs/director/UKDS_REGISTRATION_PACK.md`. The dated log lines in f3 ("honesty facts untouched ... no household data held") are records of their day and stay as written.
- **Canon drift check run.** It carries no W11 claim, so it neither holds nor refuses one. The served How it's built page (`site/harness/index.html`) still shows the old quote. That file is rewritten from canon by `tools/harness_page_figures.py` on the next publish, and another lane has it edited in place, so it is not landed by hand here.
- **Not done, and owed before any file is downloaded:** the commit control that refuses the licensed files and their row-level contents, proven to fire, and a record of where the licence conditions are kept. The row is closed against `ukds-licensed-files-commit-refusal-control`, due 13 Nov. Nothing is in `~/ukds/`.

**A2.** He said yes to the order. The re-rank is written in `THE_NEXT_WORLD_ADDITIONS_ROADMAP_2026-11-02.md` §2. Life stage, precarity and affluence are now one row at 6, above reputation (7) and the review channel (8), because they share one Understanding Society joint. Rows 1-5 do not move. Nothing is built before the correctness exit test.

**A3.** He said yes. The row is closed against `value-test-design-read-three-amendments-and-four-fixes`, due 27 Nov. It is drawn after the correctness exit test.

**B, ranked. None goes ahead of the exit test.**
1. **The test-order hunt, measured first.** It is the cheapest of the four, and its answer could be "none here, stop". Order dependence in a shared tree would also hide correctness reds.
2. **The naive organ's purpose line.** Split questioning the goal from questioning whether something serves it, and prove both branches on the 13 Jul wording.
3. **A replayable run snapshot from the run ledger.** It is the largest of the four. Start by weighing the run ledger, which nothing calls today.
4. **Propose-then-certify for the map register.** It waits on the map steer's own design.
