**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The other pages match the new front door: no banner, and written for a newcomer in energy or tech (2026-10-23)

**Type:** STEER, through the advisor channel. It follows `DIRECTOR_STEER_THE_FRONT_DOOR_SHOWS_THE_AMBITION_AND_WHAT_HAS_BEEN_BUILT_2026-10-22.md` and applies the same standard to every other page. The director's words, from chat on Fri 23 Oct:

- 07:18 BST: "The new home and code tabs look good. But now the other tabs look less good. Can you review the other pages. And recommend some improvements? Remove banner. Make more appropriate for energy or tech person who is not familiar with the detail"

**When:** now, deployed before the Monday 26 Oct publish. The home page and the code tab are the standard. Keep the voice confident and factual, lead with what exists, and put the gaps one click down. Nothing is deleted; it moves.

---

## 1. Remove the banner everywhere

`assets/freshness-banner.js` is still loaded by 38 served pages: Capabilities, How it's built, Knowledge and every knowledge page, Explore, The code. Take it off all of them.
- In its place, each page carries the home page's quiet footer line, generated at publish: "Figures from the run of <date> · published every Monday".
- Per-figure clocks stay where a figure needs one.
- Operational publisher state keeps one home, a small status section at the foot of How it's built. It follows yesterday's rule: never read from a stale snapshot, never extrapolated.

## 2. Every page opens the same way

Each page opens with a one-sentence purpose and a short "In brief" box: three to five plain lines saying what a newcomer will learn and the headline fact. Detail follows, with long sections collapsed by default. No "Loading…" above the fold. Render the headline content into the HTML at publish, as the front door now does.

## 3. Capabilities: lead with what it does and how it compares with the real industry

The advisor's read on 23 Oct: the strongest content for an energy reader, "Against how a real GB supplier works", sits under "What is not built yet", which opens with "No customers. No licence." and four paragraphs of caveats. That section is now the bulk of the page. Change the order:
1. **The capability grid**, the same one the home page links to and expanded here. The world and the supplier sit side by side, each function shown as a status card (Live / Building / Planned) with counts, rendered static.
2. **"Against a real GB supplier"** as a table: area | faithful today | not yet | source. Put it near the top. It is the page's best content.
3. **"The path to a real supplier"** replaces "Where the simulation would meet the real industry". Name the real counterparties each doorway would connect to (Elexon/BSC settlement, the DCC and CSS switching, Xoserve, DNOs, Ofgem reporting, banks for direct debits), say what each would take, and whether the specification has been read. This is the go-live story, so tell it with confidence.
4. **What is not built yet**, condensed into one table: area | not yet | what closes it. The value-thesis paragraphs go to one line with a link. The August industrial-and-commercial history becomes a footnote.
5. Remove the internal process phrases ("a gap with no plan beside it is a confession rather than a plan", "this project treats dates as forecasts"). They make sense inside the project and puzzle a reader outside it.

## 4. How it's built: lead with how AI builds and runs it, then the lessons

- **Retitle the page.** The current title is "How this builds itself, and what it keeps getting wrong". Lead with the achievement, for example "How AI builds and runs Poesys".
- **Open with the loop and its scale.** A simple diagram: the director sets direction, the delivery seat writes direction, ticks and builder seats build, gates check, and the result lands. Then generated numbers: commits a week, landings a day, test files, the share of changes that passed the gates first time, the count of checks proven able to fail, and the build since 7 June as a timeline.
- **Last week, in plain English.** Show five to eight highlights of the week's landings, each in one sentence a newcomer understands, generated from the stretch log. This replaces the raw "What it did / decided / got wrong / next" record above the fold. The raw record moves lower, collapsed.
- **Move "Where belief and truth diverge" up** as a key idea. It is "the only number on the site that could not exist outside a simulation". Show the number.
- **Turn the war stories into lessons.** The 20 August cache episode, the stale daemons and the five off-target controls become short cards: what happened, and the rule it created. They are impressive for a tech reader when they are short.
- **Drop the glossary paragraph at the top** (atom, rung, stretch, wall, seam). Use plain words in the body, and keep a glossary at the foot for anyone reading the raw record.
- **Move "What has changed since the director last looked"** off the public page, or to the foot under "For the director". It is internal.

## 5. Knowledge: group it, and say why it matters

- **Group the 34 pages into themes**, for example: markets and prices; households and how they behave; billing, debt and regulation; carbon. Give each page a one-line "why the simulation needs this".
- **Say at the top what makes this knowledge unusual.** Its headline figures are checks the simulated world is tested against every week (`tools/world_claims.py`, steer of 19 Oct). It is not just reading material. That is a strong point for both audiences.
- **Make the review-state badges quieter,** or move them to each page's foot.

## 6. Explore: tell one household's story

- **Pick an interesting household.** Dual fuel, a move, a debt episode or a price shock: one the reader will follow. Narrate it in plain English alongside the panels, and render the first view static.
- **Update "A supplier with this few accounts is not a realistic business"** to the 400-household book. Say plainly what the book's size is, and why.

## 7. The code tab

It is the standard. One check: the caption still shows "Loading the census…" before JavaScript runs. Render the caption's figures and a static galaxy image at publish, as the home thumbnail does.

## Checks

- Run a cold reader on each page, one from energy and one from tech, both new to the project. Ask four questions: what is this page for, what did you learn, how impressive is it and why, and what confused you. Fix whatever confused them. If either summary leads with the failings, the page has not met this steer.
- No served page loads `freshness-banner.js`. Add a control that reds if one does.
- Every figure is generated at publish. The existing rule stands.

## Report

One stretch-log entry with:
- the before and after structure of each page;
- what moved where (nothing deleted);
- the cold readers' answers per page;
- the banner removal and its control.

— Director steer, 23 Oct 2026, his words above; the page review and drafting are the advisor's.
