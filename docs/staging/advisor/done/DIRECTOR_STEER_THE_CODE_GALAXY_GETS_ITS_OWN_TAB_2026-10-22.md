**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The code galaxy gets its own tab, linked from the home page (2026-10-22)

**Type:** STEER, through the advisor channel. It goes with this afternoon's `DIRECTOR_STEER_THE_FRONT_DOOR_SHOWS_THE_AMBITION_AND_WHAT_HAS_BEEN_BUILT_2026-10-22.md`. The director's words, from chat on Thu 22 Oct:

- 15:01 BST: "I also want a tab with the code galaxy map, and a link to it at an appropriate point on the home page. It looks cool!"

**When:** with the front-door rewrite, deployed this week.

---

## What it means

1. **A top-level tab.** The module graph now sits under How it's built at `site/harness/module-graph/` ("How the code is wired"). Promote it to its own item in the main nav, in plain words, for example "The code". Keep the old URL working with a redirect. The navigation must stay usable at phone width.
2. **It should look like a galaxy.** What the director built with the advisor in July, and liked, is a force-directed view:
   - every module is a star, sized by lines;
   - imports are the links;
   - the big hubs form clusters;
   - edges that cross the wall stand out.

   Make that the first view: full width, animated as it settles, pan and zoom, tap a star to see its module, size and edges. Keep the current layered view, with world left, company right, machinery along the foot and the wall as a bar, as a second view behind a toggle, because it explains the wall. Keep the census tables below both views.
3. **Generated from HEAD at every publish,** from `tools/module_graph_census.py` and `site/data/module_graph.json`, as the 9 Oct instruction already requires. Above the picture, give a short generated caption: the number of modules, lines and import edges, and the number of edges that cross the wall through the seam and round it. Give each figure its clock.
4. **Link it from the home page** in the "Built and run by AI" section, next to the figures for what has been built. That is the point where a tech reader has just read the build's scale and wants to see it. Use one line plus a small static thumbnail of the galaxy, rendered at publish, so the link works without JavaScript and shows in link previews. Wording along the lines of "See the code: every module a star, every import a line →".
5. **Performance.** The page has to load and settle quickly on a phone. If the full graph is too heavy, show the largest modules first and fill in the rest, and say how many are shown.

## Report

Include this in the front-door stretch-log entry: the new tab, the redirect, the thumbnail, the caption's figures, and the load time on a phone-sized viewport.

— Director steer, 22 Oct 2026, his words above; the drafting is the advisor's.

## Done

*Autonomous worker, 22 Oct 2026, evening. All five items landed in one commit, built on top of
the seat executor's front-door rewrite (`bee0abf1a8`). This tick waited for that landing rather
than editing `site/index.html` under it.*

1. **The tab.** The page moved to `site/code/` and "The code" is the sixth nav item, rendered into
   all 40 pages from `site/ia_register.py`. Six items do not fit one 360px row: measured in
   headless chromium, Home sat about 30px off the left edge where nobody could reach it. So below
   420px the items take two deliberate rows of three (`site/brand/brand.css`). They were measured
   at 320, 360, 400, 430, 560 and 768px, and every link was on screen at each width.
   **Redirect:** `/harness/module-graph/` and its slashless form go to `/code/` with a 301. The
   control that held `_redirects` to one rule now names each rule with its reason. How it's built
   links the new tab.
2. **The galaxy is the first view.** Every module is a star sized by lines, imports are lines,
   seam crossings are blue and the four that go round it are red, all on a black ground. The
   view runs the full width of the screen and supports pan, pinch or scroll zoom, and tap. Tapping
   a star shows its module, its side, its lines, what it imports and what imports it, and how many
   of its edges cross the wall. Unwired modules form a dim outer ring rather than being hidden. The
   layered view (world | wall | company, machinery along the foot) sits behind a toggle, and the
   census tables come after both views.
3. **Generated at publish.** `tools/module_graph_census.galaxy_layout` lays the graph out once a
   week (Fruchterman-Reingold, seeded so the same code draws the same sky, about 13 s). The PNG
   thumbnail is `site/code/galaxy.png` (1200x630, the link-preview shape, and the page's
   `og:image`). The publish step writes it and now commits it too: it is not JSON, so the
   `site/data/*.json` glob would have redrawn it every week and committed it never. The caption
   reads, at 1044c8fe0: **1,251 modules · 523,088 lines · 2,495 import edges · 60 cross the wall
   through the seam · 4 go round it · all 1,251 shown**, with the commit and generation time
   beneath. These figures count non-test modules under the analysed roots, which is why they do
   not match the advisor's "about 3,500 Python modules", a count that includes tests.
4. **The home page link.** In "Built and run by AI", the rewrite's text link to the old URL is now
   the static thumbnail plus "See the code: every module a star, every import a line →", pointing
   at `/code/`. It is a plain `<img>`, so it shows without JavaScript.
5. **Phone.** At 360x740 (DPR 2, local static server, no network throttling) the swirl finished
   at **1.46 s from navigation start**, with no page errors. All 1,251 stars are drawn, so
   largest-first was not needed. The layout is computed at publish, so the phone draws a settled
   picture and runs no physics. The opening swirl shows the picture arriving; it is not a
   simulation. Over a real mobile network the 173 KB feed comes first, and that leg is still to
   be measured on the deployed page.
