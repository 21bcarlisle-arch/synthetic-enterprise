**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** `G14_half_hourly_grid_carbon_intensity_aligned_to_settlement`

# The published carbon page is built from a grid intensity feed that is not committed (2026-11-11)

**Found by.** The worker building the CO1 embedded-thermal line tried to regenerate `site/data/explore_carbon.json` in a
clean worktree at origin 63ede2e3bb. It used only committed inputs, all of which were last written by the same publish
commit (e816040ce8).

**What it is.** The committed feed reads `counts` measured 3, with 6 measured account-days. Rebuilt from origin's committed
`docs/market_data/grid_intensity_feed.json`, it reads **0 measured**, and the grid, accounts and counts sections move.
Rebuilt the same way with only the intensity feed swapped for the shared tree's **uncommitted** copy, it reproduces the
committed counts exactly. So the page published at e816040ce8 rests on an input that is not in the repository. The shared
tree's copy was written at 16:34 GMT on 11 Nov (693 insertions, 1,030 deletions against HEAD). The committed copy last
changed on 5 Oct (a687ba8775).

**It is a recurrence.** `done/SEAT_FINDING_THE_COMMITTED_GRID_FEED_IS_NINE_DAYS_BEHIND_THE_ONE_ITS_OWN_DERIVED_PAGE_IS_BUILT_FROM_2026-09-04.md`
was the same shape, and it named a part as "NOT closed by this pass". It is also the sibling of 4f68a644fd/cbd8ace4ff,
where a publish shipped a run input that did not match its pages.

**I cannot yet say** which process wrote the 16:34 copy: the feed's own generator, a test, or the publisher. Nor whether
the newer feed or the committed one is the correct input.

**Consequence.** Nobody can reproduce the published carbon page from the repository. Any lane that regenerates it from a
clean checkout publishes a regression, as this one would have. That is why commit "The customer carbon figure gains its
own line ..." (0849f1427e) did not regenerate the feed, and why its line will not render until a publish does.

**Recommended next.** Find the 16:34 writer. Then either commit the regenerated intensity feed with its provenance, or
stop the publisher from reading an uncommitted one. The control is one leg: the publisher refuses to build a page from a
tracked input whose working copy differs from HEAD, and names the path.

**Done means.** `python3 -m tools.generate_explore_carbon`, run in a clean worktree at origin, reproduces the committed
`counts`.

Reverse: delete this file.
