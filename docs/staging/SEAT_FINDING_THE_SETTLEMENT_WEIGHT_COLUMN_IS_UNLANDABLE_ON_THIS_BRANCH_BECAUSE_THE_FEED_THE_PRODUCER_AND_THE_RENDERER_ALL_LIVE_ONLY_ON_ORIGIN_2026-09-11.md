**Severity:** LATENT · **Lane:** H_harness

# FINDING — the `settlement_weight` column is unlandable on this branch: the feed, the producer, the renderer and the door all live only on `origin/main`

**Found 2026-09-11, delivery seat, while holding the Lane 0 item whose second piece asks for it.**

## The drawn ask, and the claim underneath it — which is TRUE

The item's second piece:

> `settlement_weight` now reaches every published row of `site/data/book_growth.json` and
> reconstructs each year's funnel wins EXACTLY (24/32/46/70/72/59/20/56/83/38) while settled counts
> are nowhere near proportional (9/6/6/12/11/9/5/5/16/4) — but the capabilities chart does not
> render it as a column.

**Checked against `origin/main`'s feed and it is exact in all ten years:**

| year | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | total |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| settled `wins` | 9 | 6 | 6 | 12 | 11 | 9 | 5 | 5 | 16 | 4 | 83 |
| `settlement_weight` | 24.0 | 32.0 | 46.0 | 70.0 | 72.0 | 59.0 | 20.0 | 56.0 | 83.0 | 38.0 | 500.0 |
| `funnel_wins` | 24 | 32 | 46 | 70 | 72 | 59 | 20 | 56 | 83 | 38 | 500 |

`settlement_weight − funnel_wins` is **0.0 in every year**, totalling 500.0 over 83 settled
accounts. The reconstruction property holds and the reader genuinely cannot see it without opening
the JSON. **The ask is sound. It is the landing that is impossible from here.**

## Why it cannot be landed on this branch

`main` and `origin/main` have diverged — **32 commits local-only, 31 origin-only, none shared** —
and every part of this change is on the far side:

| path | state on local `main` |
|---|---|
| `site/data/book_growth.json` | the **old cull feed**: `wins: 4` for 2016, **no `settlement_weight` key at all** |
| `tools/generate_book_growth_data.py` | does not produce the field (96 lines behind) |
| `site/capabilities/index.html` | **rewritten by 244 lines on origin** |
| `site/capabilities/test_capabilities_door.py` | 180 lines behind |
| `simulation/settlement_choice.py` | **does not exist locally** — the whole chooser is origin-only |

A column added here would read a key the local feed does not carry, so it would **render nothing on
the live bytes** — the door test would be grading its own fixture rather than the lift. And it
would be purely additive work sitting on the one file the other side has rewritten, which is
[the shape where a merge adopting one side's rewrite silently deletes the other's additive work].

## This is somebody's live work, and that is why I did not touch it

A sibling seat is **holding the reconciliation right now**, under the claim
`the-stretch-split-seven-and-seven-and-the-prereg-exists-twice`, with an explicit instruction to
merge `origin/main` and resolve five named conflicts — among them
`simulation/net_new_acquisition.py`, the chooser's own call site. Landing a capabilities-chart
change into that merge from a second lane is the collision that item exists to avoid.

## The remedy, and its ordering

**This piece is blocked on the merge, not on the chart, and it should be done immediately after it
— not before, and not by a second lane in parallel.** Once `rev-list --count HEAD..origin/main` is
0:

1. render `settlement_weight` as a column beside `wins` and `funnel_wins` in
   `site/capabilities/index.html`;
2. the door test must grade the **published bytes**, and it must be able to fail — the honest
   control is that the column's rendered value equals `funnel_wins` in every year **and** that
   `wins` does not, since a column that merely renders *a* number would pass with the settled count
   in it. The two series differ in nine of ten years on this feed, so the mutation is available.

**What NOT to do:** add the column defensively so it renders only when the key is present. On this
branch's feed that is a column that renders nothing, guarded by a test that cannot tell the
difference between "absent" and "correct".

*The measurement half of the ask is done and recorded above, so the merge inherits a verified claim
rather than an unchecked one.*
