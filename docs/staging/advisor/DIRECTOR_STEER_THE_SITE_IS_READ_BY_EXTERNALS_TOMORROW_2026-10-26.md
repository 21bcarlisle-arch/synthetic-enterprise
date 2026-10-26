**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The site is read by externals tomorrow: fix what a newcomer trips on today, and stop asking the director what canon G5 says is yours (2026-10-26)

**Type:** STEER, through the advisor channel. These are the director's words from chat on Mon 26 Oct:

- 13:27 GMT: "I am expecting externals to look at the website tomorrow so really want the website looking good and up to date today."
- 13:35 GMT: "Also the website says 11 decisions waiting on me?!"
- about 13:40 GMT, answering the advisor on the open questions: "What do you recommend? Is it valid to even be asking me these questions?"

The advisor rendered the published site from origin at 27bcc82c. It used Playwright at 1366×900 and 390×844 and ran a cold read. Every page that carries a run stamp now says 26 Oct (run 4ae8da9b0f). The earlier cold-read items that came from a stale checkout have been dropped. What remains is listed below in priority order.

**Deadline:** landed and published before the end of today, Mon 26 Oct. Prefer small, safe edits to restructures. Leave nothing half-done on a public page. Anything not landed by tonight goes on a dated list in this file's Done section, not into a page.

## 1. The director's queue: apply G5 to it (the "11 questions" panel)

How it's built says: "At this publish (24 Oct 2026), **11** questions wait on him." `DIRECTION.yaml` now has **13** `for_the_director` items open. Canon G5 (ruled 12 Oct) reserves six kinds of action for the director: real money, real people, real-world commitments, irretractable public claims, credentials/security, and destroying evidence. Its rule for everything else is "act, record how to reverse it, say what you did". The advisor's answer to his 13:40 question is **no**. Most of these are not his to rule.

- **Not reserved. Close them yourself on your own recommendation, record how to reverse each one, and report it in the next reading:**
  1. C34 sharing retention price, keeping both floors;
  2. the capital-115 / C14 corrections, treated as corrections, with the prospect cap and founder book as what sizes growth;
  3. W3 responsiveness change (1), selection at acquisition, with no new number;
  4. the dated CLV discount rate (0.10 to Sep 2023, then 12.3%, both ends reported);
  5. EP17 seeds 61113–61118 under the 15 Oct ruling;
  6. the two-reader non-blocking review trial;
  7. the capped randomised retention experiment;
  8. steps 8–13 of `priority_order.yaml`, which match the advisor's 25 Oct steers;
  9. keeping 7,700 MB / `founder_unit: households` with the stated watch.
- **Reserved. These stay on his list:**
  - Cloudflare Web Analytics on poesys.net. It concerns real visitors' data on his account. The advisor recommends switching it off before tomorrow.
  - The plan tier. It is real money. The advisor recommends staying on the £100 tier.
  - The HF token. It is a credential and is pending his "done".
  - The front-door GitHub link. It touches his July private-repo plan. The advisor recommends **holding it until after tomorrow's visit**: the repo exposes the staging and advisor files raw, and the site already carries the evidence.
- **On the page:** compute the count live at publish from `DIRECTION.yaml`. Show the reserved items only, with the G5 class next to each. Rename the panel "Waiting on the director (reserved actions only)". Update the frozen test in `tests/tools/test_harness_page_figures.py` to match.
- **Record it as a harness finding:** the seat has been sending G5-delegated calls to the director. Add a classifier check: a `for_the_director` row must name its G5 class, or it is not raised.

## 2. Correctness a reader can see

- **Explore, the "What the supplier committed to" panel.** It shows "Unit rate 6.27 p/kWh" on a Standard Variable tariff. The same panel shows "Range offered that year £94.01 – £179.47/MWh", and the cost breakdown above it shows Energy 6.27p + Network, policy and levies 5.20p. **6.27p is the energy component, not the tariff's unit rate.** Show the tariff's actual unit rate. If the tariff record only holds the energy component, label it "Energy component of the unit rate" and add the all-in rate beside it. Add a reader test: the unit rate is at least the sum of its cost components.
- **"62 published knowledge pages on how the GB market and its households work"** (home). Eight of the 62 are other-market pages. Suggested wording: "62 published knowledge pages: 54 on how the GB market and its households work, 8 comparing other markets with GB". Use the live counts.
- **"Built in the last 1 days"** and other "1 days"-style plurals (Capabilities). Fix the pluraliser once, sitewide.
- **"UK"** where GB is meant (Capabilities, gas industry systems row). Leave "UK Link" alone, because that is Xoserve's product name. Change other uses to GB.

## 3. What an outsider should not have to read

- **Knowledge index and topic pages: remove "Built by <atom>" from every card (62 instances).** Move the flags/verification census table (28 packs, 522 flags) from the index into a linked "How these pages are checked" page. Keep one plain line on the index, for example: "Every figure carries its source. Figures we have not yet checked against the primary source are marked as unchecked on the page." Per-page verification badges stay.
- **Capabilities is 25,263 words and about 40,000 px tall.** Do not rewrite it today. Do these three things:
  - **(a)** Collapse every section below the capability table and the value test into closed `<details>` elements, each with a one-line summary.
  - **(b)** Strip file paths (`docs/…`, `….py`; 12 + 9 instances) and bare commit hashes (25) from the visible text. Keep them in a "Show the evidence" toggle where they matter.
  - **(c)** Remove any "Fixed in the last N days to <date>" block whose date is not today's publish. If it is generated, generate it at publish.
- **Lead Capabilities with its best result.** Put the value test first. It splits the advantage honestly: the choosing is +£11,345, which is value **made**, and the price level is −£6,101, which is value **moved**. Suggested opening paragraph:
  > "The question this project tests is whether deciding customer by customer creates value or only moves it. On the same book, run three ways, per-customer choosing was worth +£11,345 over flat rules; charging a higher flat level was worth −£6,101, which is value moved, not made. Both are shown, with the spread across draws, below."

  Use the published figures from the live data, not these numbers typed in.
- **Home "New this week".** It uses internal language ("the director's points", "a hand-drawn file"). Suggested wording:
  - "A single map now links each of the business's ideas to the code, checks and pages behind it. Its first pass over payment collection found overlapping modules, several of which nothing calls; they are being removed."
  - "The front-door diagram is now generated from the model itself, so it cannot drift from the code."

  Drop the "price, in the director's points" line from public view.
- **The home model diagram** still shows internal codes (M1, G1, R5, R6 …). Show plain names on the diagram and keep the codes in the hover/detail view only.

## 4. Mobile (390 px)

Horizontal scroll is still true on Capabilities, `knowledge/payments-and-direct-debit/` and `knowledge/switching-mechanics/`, so wide tables push the page sideways. Give every table a wrapper with `overflow-x:auto` and `max-width:100%`, and let `pre`/`code` wrap. Add the `hscroll=false at 390 px` check for every published page to the post-publish readers.

## 5. Data still on the previous run

`site/data/dashboard.json`, `site/data/delivery.json` and `site/data/capabilities_door.json` still reference run 8b6fea024 (19 Oct). Either regenerate them from 4ae8da9b0f at this publish, or confirm in the Done section that no page a visitor reaches reads them.

## Not to do today

- No new pages.
- No restructure of navigation.
- No change to any run figure.
- The `/model/` path has no `index.html` and serves a directory listing locally. It is not linked from anywhere, so either add a redirect to `/model/map/` or leave it, but confirm the deployed host does not list the directory.

## Done

(The seat records here what landed, with commits, and what was deferred, with dates.)
