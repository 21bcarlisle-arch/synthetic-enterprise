**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Make the site understandable and impressive to someone in energy or tech who has never heard of the project (2026-10-22)

**Type:** STEER, through the advisor channel. The director's words, from chat on Thu 22 Oct:

- 07:24 BST: "Can you please review the website content and recommend how to make it more understandable and impressive for people not aware of the project but in energy or tech."
- 07:29 BST, on the advisor's review below: "Do it"

**When:** item 1 now. A false claim on a live page is breakage (P7). Items 2–9 land at or before the Monday 26 Oct publish, beside the week's feature work. The words are yours to write, under canon. This document says what to fix and the shape he agreed. It does not supply the copy.

---

## What the advisor found (on origin/main, site/ source, 22 Oct)

The data refreshes daily: the 19 Oct dual-fuel run is published. The words do not. `site/index.html` last changed on 15 Oct, and much of its prose is older than that. The canon v4 steer of 12 Oct said "The site: About and the front door take their claims from canon v4 at the next Monday publish." That has not happened yet.

## WORK THIS CREATES

1. **Correct the stale and contradictory claims now.** Each one is a factual correction against canon v4 or the current record:
   - **The headline** "An energy company built and run by AI, to find the cheapest tonne of carbon left." is the withdrawn framing. Canon v4 decision 4: carbon's public face is the household's saved and could-save CO₂, and £/tCO₂e is an internal diagnostic. Lead with M1, verbatim, with M11 beside it.
   - **"Whose book this is"** ("as of 24 August 2026", "Until this week … industrial and commercial … more than 98% of the revenue") is two months old. The book is now 400 dual-fuel-correct founder households.
   - **"Time does not appear in this project at all."** This contradicts M3.
   - **"today every property is one national shape rescaled"** (The world). Check it against `fabric_physics` and the W1 work, and correct it.
   - **The carbon contradiction.** The score block says "the carbon meter is designed but not yet wired". A paragraph above says "The half-hourly instrument now runs". State one truth.
   - **"the results live on Proof"** (Knowledge intro) points at a page that no longer exists.
   - **"A supplier with this few accounts…"** (Explore). Check it against the new book size.
   - Anything else on any page that canon §16 marks superseded. Run the canon-against-canon check over the site, not only over the standing pages.
2. **Open with what it is, in two lines,** before any caveat. Today the page opens "No customers. No licence." The honesty stays, one layer down. The shape: an AI-built and AI-run GB energy supplier, running against ten years of real market data, that can only learn what a real supplier could. Then M1. Then M11, the project's own claim that software can be grown and can maintain itself.
3. **A proof strip near the top: four or five numbers, generated at publish and never typed.** Candidates:
   - half-hourly periods settled (about 168,000);
   - the years, 2016–2025, including the 2021–22 crisis;
   - households in the book;
   - tests and commits;
   - days since a human last wrote code, if the record supports that claim. If it does not, leave it out.

   Each number carries its clock, as the site already does.
4. **Show it working before the caveats.** Two or three short stories, each linking to its evidence. One is the dual-fuel episode of 17–19 Oct. The book was found to be 1% dual fuel against the published 72%, from the CMA and Ofgem figures. It was researched, corrected, and given checks so it cannot drift silently again, inside a day. Choose the others on the same test: a real finding, honestly framed, that a domain reader would respect.
5. **Speak to both audiences by name.**
   - **Energy readers:** what is modelled faithfully today, what is not yet, and how it compares with how a real supplier works. Settlement, the price cap, hedging, debt, home moves and the dual-fuel rules.
   - **Tech readers:** the build itself. The Harness page says it is "the part of the project with the most to say to someone who does not care about energy at all", yet it sits last in the navigation. Bring it forward as a co-equal way in, and rename it in plain words, for example "How it builds itself". Keep the URL or redirect it.
6. **Translate or drop internal vocabulary on reader-facing pages.** The wall, seams, curtain, delivery seat, stretch, atoms, rungs, tick and seat should become plain words. For example, "the company only sees what a real supplier could see" instead of "the wall". Internal terms may stay where the page is about the machinery, but explain each one the first time it is used.
7. **The honesty stays, one click down.** "We cannot tell yet" is a credible result and stays. Say it in a line, with a link to the full account, instead of four paragraphs on the front door. Never remove a caveat; move it to where the reader who wants it will find it.
8. **The front door works without JavaScript.** "Loading the latest run…" shows a search engine, a link preview or a script-blocked reader nothing. Render the headline figures and the proof strip into the HTML at publish, with JavaScript adding only interaction.
9. **Deploy only what readers need.** About 70 test and helper scripts are publicly served from `site/`, for example `/ia_register.py` and `site/test_*.py`. They are served as text and never executed, and the repository is public, so this is hygiene rather than a security issue. Leave them out at the deploy stage (`tools/assert_deployed_bytes_are_served.py --stage`) and in the Pages manifest, with a check that fails if one ships. Note for the record: the site runs no PHP and no server-side code, so the October PHP2Shell flaws (CVE-2026-109618 and CVE-2026-109619) do not apply to it.

## Checks

- A canon-against-site check: no superseded line presented as current on any served page, and quoted canon lines verbatim. This is the canon-alignment mechanism extended to `site/`.
- A cold-reader test before Monday's publish. Have the strongest model read the front door with no context, once as an energy professional and once as a technologist, and answer three questions: what is this, what has it shown, why should I believe it. Record the answers and fix whatever they get wrong. This is a review, not a gate.
- No figure is typed by hand. The existing rule stands.

## Report

One stretch-log entry with:
- each stale claim corrected, before and after;
- the new front-door structure;
- the proof strip's sources;
- the stories chosen and why;
- the vocabulary changes;
- the no-JS render;
- the deploy exclusion and its check;
- the cold-reader answers.

— Director steer, 22 Oct 2026, his words above; the review and drafting are the advisor's.

## Progress: item 1 landed 2026-10-22 (seat executor); items 2-9 are handed on, so this file stays open

Each stale claim, before → after:
- **Headline.** Before: "An energy company built and run by AI, to find the cheapest tonne of carbon left." After: what it is, in two lines ("A GB energy supplier, built and run by AI, living through ten years of the real market", followed by what it settles and what it can see). Then M1 verbatim, then M11 beside it, linking to the Harness page. The "No customers. No licence." paragraph follows.
- **Whose book this is.** Before: "as of 24 August 2026 … Until this week … more than 98% of the revenue". After: the book is households, most of them on both fuels. The I&C suspension is told as history. The August settlement-ceiling detail (the 19% funnel and the cache) is replaced by the standing caveat: the book's size is set by this machine, not by the market. `data-mix-claim` is unchanged, so the publish gate still recomputes it.
- **Time.** Before: "Time does not appear in this project at all." After: "Time is defined but not yet measured", in household minutes per kind of task, never pounds (M3). `site/test_home_door.py` now pins the new state, and that pin was mutation-checked red against the old sentence.
- **The world.** Before: "today every property is one national shape rescaled … fabric-physics rebuild is the current top priority". After: where the weather store covers a household, its electricity comes from a per-building thermal model under its own local weather, and its gas heating split comes from the same model. Outside that coverage, homes still use the rescaled national shape. On the §14 seed-1 flat run (`bc1e6ad78`), 378 of 719 electricity supply points were fabric-eligible and 329 were refused for "no weather archive". No figure is typed on the page.
- **The carbon contradiction.** Before: "the carbon meter is designed but not yet wired". After: household emissions are measured, and abatement is not (CO4). The score heading changed from "£ per tonne abated" to the CO1 framing. £/tCO₂e and the £273 yardstick stay, as a diagnostic, not the headline.
- **Knowledge intro.** Before: "the results live on Proof", a page that no longer exists. After: Capabilities and Explore.
- **Explore, "A supplier with this few accounts…".** Checked and left as it is. A book of a few hundred households is still not a realistic business.
- **Canon §16 sweep.** Every served `site/**/*.html` was searched for the superseded mission framings ("cheapest tonne", "carbon abatement through", "non-commercial", "public domain", "grown toward go-live", "80 founders"). The only hit was the headline above. The mechanised canon-against-site check is handed on.
