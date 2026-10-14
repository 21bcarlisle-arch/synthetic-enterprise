# The 6ab998ad7 run was held by the weekly window; the figures reached the live page on the 2248e3baf run

**Fate (2026-10-14):** DONE -- a record; the 6ab998ad7 run goes out in the next weekly window.

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

*Worker, 2026-10-14 ~00:40Z. Disposition of the delivery item `the-6ab998ad7-publish-reaches-the-live-page`. No code changed.*

**The item's premise is spent, and the publish happened by a different route.** The item expected the
6ab998ad7 run (launched 20:10Z) to be the first publish able to clear the site lane. Before it
finished, the publish wedge's re-queue published the **2248e3baf run** (134447Z) at 21:53Z as
`ed3dadd9d`, which is an ancestor of origin/main. That is the first figures commit since 2026-10-05, so the
ENOSPC fix (`0d5304e98`) held on its first real publish.

**The 6ab998ad7 run was HELD, not refused.** It finished at 22:05Z (6932 s, 89 MB). The publisher
archived its marker (`docs/staging/done/run_complete_20261013T201010Z.md`) under the weekly window:
`_content_publish_window()` answers *"this week's figures reached origin 2026-10-13T21:53Z; the next
publish opens Mon 2026-10-19 04:00 BST"*. That is the director's 2026-09-26 rule working as designed.
The sim-runner line "Auto-process published nothing ... held for the weekly Monday publish window" says the same. There was no
site-lane output to read and nothing to fix. `df /tmp` was not at issue.

**What I checked on the live site (poesys.net), 2026-10-14:**

| Check | Result |
|---|---|
| `site/data` regenerated on origin | `ed3dadd9d` touches 1,999 `site/data` paths; `capabilities.json` stamped `git_commit 2248e3baf`, `generated_at 2026-10-13T21:21:45Z` |
| Live equals origin | byte-identical: `/capabilities/index.html`, `/data/capabilities.json`, `/data/module_graph.json`, `/harness/module-graph/index.html` |
| Deploy | Cloudflare deploy for `ed3dadd9d` **failed** (Pages 25 MiB file limit). Fixed by `b1c3e4832`, hand-dispatched at 22:59Z (success); push deploys since then have succeeded |
| D48 renders (chromium, the page's own JS, live) | `#billacc-dd` visible: "153 of 422 direct-debit accounts asked for their balance lost some of it, 36.3% (95% 31.8% to 40.9%), £33,770 in all ..."; feed source `run_output_2248e3baf_20261013T134447Z.json` |
| Module-graph door renders (live) | `/harness/module-graph/` linked from `/harness/`; `#mg-stats` "modules 1,232, edges 2,397, through the seam 57, company reads world round the seam 0, **world reads company round the seam 4 !**" |
| Door suites | `site/capabilities/test_capabilities_door.py` + `test_the_capabilities_reading_is_visible_to_a_browser.py` + `tests/tools/test_module_graph_census.py`: 59 passed |

**Open item, not this one's to act on.** The module-graph page publishes four world→company imports
round the seam (`simulation.customer_events` → `company.crm.churn_model`, `saas.churn_model`,
`saas.home_move_win_rate`; `simulation.run_phase2b` → `company.policy.decision…`). The door shows these
on purpose, and I have not checked whether a finding already covers each one.

**What comes next.** The 6ab998ad7 figures go live at the Monday 2026-10-19 04:00 BST window, or with
whichever later run supersedes them. Since `c701d8605` (01:08 BST today), a run whose imported bytes
were not measured at launch publishes "on its stamp alone" with a log line. A run measured as dirty
is refused. Runs launched before that commit predate the reading.
