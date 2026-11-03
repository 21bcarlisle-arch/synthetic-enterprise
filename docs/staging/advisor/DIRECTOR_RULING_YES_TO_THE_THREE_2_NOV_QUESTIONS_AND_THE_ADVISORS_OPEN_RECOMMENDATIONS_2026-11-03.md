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
