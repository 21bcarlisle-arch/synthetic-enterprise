# The four salvaged worktrees hold nothing unlanded

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

*Worker, 2026-10-05, drawn item `bind-the-heartbeat-steers-landing-and-the-salvaged-worktrees`.*

## Heartbeat row

`the-heartbeat-leaves-main-per-the-directors-steer` is bound to `3cc1281c4` (an ancestor of
origin/main) and its window disposed as premise-spent: that commit resolved the steer as a
measurement (only four runtime files ever collide, so no separate daemon checkout is needed now).

## The four SALVAGE commits

The item asked for each worktree to be locked with a verdict. **None of the four worktrees exists any
more** — they were reaped after `fork_salvage` tagged them, so there is nothing to lock. Their
bytes survive only as local tags `salvage/worktree-agent-<id>`, on no remote ref. Each was diffed
file by file against origin/main:

| Worktree | Tag | Salvaged paths | Verdict |
|---|---|---|---|
| agent-a8d680d38d1b13aa5 | `af7b2fdef` | `docs/market_research/ev_solar_and_batteries_as_products.md`, `_draft/ev-solar-and-batteries-as-products.json` | **Already landed.** The `.md` is blob-identical on origin; the draft JSON equals the `ev-solar-and-batteries-as-products` entry in `site/data/knowledge_topics.json`. Both by `666ed5fe0`. |
| agent-ac644f84641851c1c | `e1fb47bb9` | `docs/market_research/communications_sentiment_and_nps.md`, `_draft/communications-sentiment-and-nps.json` | **Already landed**, same test, same commit. |
| agent-ac88a852da9c24f8c | `dcf543fb7` | `docs/market_research/home_moves.md`, `_draft/home-moves.json` | **Already landed**, same test, same commit. |
| agent-a9438a8c3dfb9f678 | `5ec6f3a8b` | `docs/observability/ntfy_digest_queue.jsonl` (2 lines, untracked runtime file) | **Disposable.** Two routine `[LANDED]` digest notices for `09e2bf07f` and `b0f6922eb`, both on origin. |

The `.se_worktree_owner` file in each salvage is ownership metadata, not work.

So no work was lost when the worktrees were reaped, and nothing needs pushing. The four tags can
be deleted at any time (`git tag -d salvage/worktree-agent-<id>`); they were left in place because
deleting them is not needed for anything.

**Reverse:** nothing was changed outside this file and the draw ledger.

**Re-checked and landed by the delivery seat, 2026-10-05.** This file was left untracked in the
shared tree, with no landing running. The seat checked each verdict again against origin/main
before carrying it: the three `.md` blobs show no diff from origin; each `_draft/*.json` entry
equals `site/data/knowledge_topics.json`'s `pages[<slug>]` on origin; and the two digest lines
name commits on origin. The heartbeat binding was re-run too (it bound the seat proposal path).
