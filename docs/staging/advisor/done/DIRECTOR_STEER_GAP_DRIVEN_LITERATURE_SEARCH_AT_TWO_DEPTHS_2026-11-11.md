**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Gap-driven literature search, at two depths (2026-11-11)

**Type:** STEER, through the advisor channel. It adds to the 5 Nov reading habit (`DIRECTOR_STEER_A_STANDING_EXTERNAL_READING_HABIT_AND_THE_KNOWLEDGE_TAB_TAKES_THE_MAPS_SHAPE_2026-11-05.md`). The director's words, from chat on Wed 11 Nov:

- 08:08 GMT: "Is it worth us look at long lists of academic papers and listing candidates for knowledge? In energy, behaviour etc etc."
- 08:10 GMT: "Also we don't have to read the whole thing. Abstract may be fine for less directly relevant stuff. Then summarise further. So some knowledge is detailed. Others is more an aggregated and citations for work on theme for us"

## The outcome wanted

The published research behind our gaps is found systematically and used at the depth each gap deserves. It is not a library for its own sake.

1. **Pull from the gaps.** Each open GAP is a search question. The knowledge map mentions GAP 34 times at `4bfc2fa`, across 86 pages, and this week added more: battery and EV operating-mode shares, adoption response to advice and support, hassle tolerance, and carbon definitions. List candidates with the free scholarly APIs: OpenAlex (open) and Semantic Scholar. Rank by relevance, recency, citations and study type. Nothing in the tree uses these APIs yet.
2. **Two depths, his distinction:**
   - **Detailed.** A gap that directly sets a constant, a mode share or a world response gets the top two or three papers read in full. Their findings, ranges and caveats go into the knowledge page, with an evidence grade: meta-analysis or randomised trial, then large observational study, then modelling, then opinion. Note whether each is UK evidence.
   - **Aggregated.** A theme that only informs our thinking (wider behaviour, adjacent markets, background) is read at abstract level. It is summarised further into a short themed synthesis per topic, saying what the field broadly finds, where it disagrees, and the list of citations. It is not a paper-by-paper digest.
3. **Seed with UK sources first:** CREDS (energy demand), UKERC (including its systematic reviews), SERL (smart-meter research), Energy Systems Catapult and Behavioural Insights Team trials, and Ofgem and Citizens Advice research.
4. **Just in time.** List candidates for every gap now, since that is cheap. Read when the gap's build comes up. A gap whose build is months away has its list, not its reading.
5. **One home.** Candidates and verdicts go in the reading log against their gap. Detailed findings go in the knowledge page that uses them. Themed syntheses live under the Knowledge tab's relevant section, as knowledge-layer pages with trust grades. They are not a separate library.

**First in line:** this week's new gaps, which are operating modes, adoption and hassle, and the carbon definitions. Two more go with them:
- **Z.ai (11 Nov), for the reading log:** structure plus a language model, testing agents in real environments, and AMiner's authority ranking. Confirms existing direction; nothing to adopt.
- **A check prompted by GLM's blank-infilling idea:** do our world checks test against data held back from fitting, or against the data the world was fitted on? If the latter, say where.

## Budget

Part of the monthly reading rota, alternating with the harness topics, and capped. Report spend in the Monday note line.

## Risk

Touches: the reading habit, the reading log, knowledge pages and new themed synthesis pages.
Blast radius: knowledge pages only.
Probable failure modes:
- Abstract-level claims written up as if they were findings. An aggregated synthesis says "abstract-level" on its face and never sets a constant.
- An evidence grade inflated by citation count. Grade by study type, not popularity.

Proportionality: reversible and narrow — just do it.

— Director steer, 11 Nov 2026, his words above; the design and drafting are the advisor's.

## Done

(Worker tick, 11 Nov.) **The method and the first-in-line lists are in place. Listing for the other gaps is still owed.**

- **One home.** A second part of the reading log, `docs/institutional/reading_log_against_the_gaps.md`. It sets out the
  two depths, grades evidence by study type (never by citations), works just in time, and seeds from UK sources first.
  Part one's header now points to it.
- **Candidates listed with OpenAlex**, which needs no key. Each query was run twice: UK-affiliated authors only, then
  unrestricted. Semantic Scholar returned 429 to unkeyed requests, so it is not used yet. The lists cover all four
  first-in-line gaps: operating modes, adoption, hassle and the carbon definitions. The strongest candidates were read at
  abstract level and graded from what the abstract says.
- **Z.ai** has a row in part one: "already have; nothing to adopt".
- **The GLM check** has a first pass in part two. The answer is mixed. The grid-carbon future and the price residual axis
  are chosen on a held-out year. The departure level is graded against the same published band it was fitted to, which is
  calibration and not validation. A census of every fitted world quantity is listed as owed, not built.
- **Owed:**
  - candidate lists for the queued gaps, which part two names;
  - the UK grey-literature seeds (SERL, CREDS, UKERC, Catapult, BIT, Ofgem, Citizens Advice), which OpenAlex does not index;
  - full reads when each gap's build comes up. G1 to G3 are held behind the exit test with the 10 Nov asset steers.
- **Budget:** about 15 OpenAlex queries out of its free shared daily allowance. No money was spent and no key was
  registered.
