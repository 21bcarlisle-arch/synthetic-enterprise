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
