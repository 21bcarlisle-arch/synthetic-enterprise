**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Class:** `uncommitted_and_orphaned_work` (primary)

# The knee refutation was already landed, and the one leg nobody held was the knowledge map

**Claim:** `land-the-bill-stress-knee-refutation-before-it-is-lost`
**Disposition:** the drawn pile is spent; the residue splits three ways and only one part had no
holder. That part is landed here. Released against the two successors named below.

## What the item asked for, and what the bytes say

The item named three paths as "finished and sitting loose in the working tree". All three are at
origin, in two commits, neither of them this turn's:

| path | the item's word | the record |
|---|---|---|
| `docs/market_research/is_there_a_bill_level_at_which_switching_rises.md` | untracked, 16,673 bytes | landed `0637be0f1` |
| `tests/company/test_the_bill_stress_threshold_carries_its_origin.py` | untracked, 8,173 bytes | landed `0637be0f1` |
| `company/crm/churn_model.py` | modified, 53 insertions | landed `fc390b918` (`git log -S` on the docstring's own words) |

`0637be0f1` also carried `tools/domain_constant_origins.py` and the substring baseline, which is
why `BILL_STRESS_THRESHOLD_GBP` left the no-origin list. The draw ledger's `not_done` was reading
the SHARED tree's dirty copies, and those copies are two other lanes' LIVE work, not this item's
unlanded pile. **A dirty path is not an unlanded path, and the path-check tag says so in terms**
(*"it does NOT establish whose work it is"*) — the reading that closed this was `git log -S` on the
landed text, not the dirty/clean grade.

## The sub-ask about the page is held, built and staged, by somebody else

`site/data/value_arms.json`'s `churn_belief_size.the_thresholds_own_origin` does still read
"NOT ESTABLISHED" **at HEAD**. It does not in the shared tree: the full refutation sentence is
already there and already `git add`ed (`M ` in the index, 88 lines), together with
`site/test_the_flat_churn_belief_reaches_the_reader.py` (149 lines) and the producer
`tools/churn_belief_size_response.py` (455 lines) that generates it. That is
`the-refuted-bill-stress-knee-is-unbounded-beside-a-saturating-size-term` mid-flight — its
churn_model diff introduces `BILL_STRESS_MAX_RATIO` and `bill_stress_uplift_ceiling()`, and the
producer is the other half of the same landing. Writing that sentence here would have been a second
copy of a rewrite already staged, and landing it would have collided with a 455-line producer diff.
**Not taken, and the reason is the successor, not the difficulty.**

## The leg with no holder: the knowledge map never pointed at the research

The item's own FINISHED clause included *"the map/knowledge layer points at the research from the
constant"*. The constant points at the research (`churn_model.py` lines 50, 88, 396–398); the
research declares its topic and `tools/knowledge_layer_gate.py` enforces that. **Nothing ran the
other way.** `grep` across `docs/`, `*.yaml` and `*.json` for the research filename returned two
hits — a staging record and a frozen census row — and zero from `knowledge_map.md`. A refutation of
a domain shape that reached no knowledge-map row is the `saas/opex_ledger.py` failure exactly: a
sourced finding on disk, and nothing telling the next reader to look.

Landed here as a single row in **Domain: Market Switching and Customer Flows**, the single home for
the origin of `BILL_STRESS_THRESHOLD_GBP`. It separates the two answers the subject has, because
collapsing them is how this gets re-read wrong: **NOT ESTABLISHED** (no published bill level at
which switching rises — Ofgem cuts switching seven ways and never by bill size) and **ESTABLISHED
AND REFUTING** (Ofgem/BMG n=3,235 puts spend↔propensity at −0.07 to +0.05; DESNZ QEP 2.7.1 has
15.57% → 3.06% across 2021→2022 while every bill rose).

The gaps column states both CIM w6 ratios **with what each divides by** — arrears at 6.8% is 1.28×
the 5.3% population base and 1.6× the 4.2% no-debt cell — because those two are quoted for each
other elsewhere in this repository, and they are not the same quantity.

## Which door was needed, and the stale-copy clock reading it produced

Ordinary `surgical_land` from the isolated worktree, on HEAD bytes. No `--content`, no
`isolate_hunks`, no `refresh_to_head`: the worktree's copy IS HEAD's, which is what the isolation
buys. That is the answer the item asked for and it is the uninteresting one.

**The interesting clock reading is one the item did not ask about, and it is live.**
`docs/institutional/knowledge_map.md` in the SHARED tree has mtime `2026-09-18 16:07:06` against a
last commit to its own path of `2026-09-19 22:30:54` (`651454d79`). The working copy **predates the
landing**, and its diff is pure reversion: it removes the 2026-09-19 SVT→fixed-edge correction (and
restores the refuted *"the sim has no SVT→fixed edge at all"* cell), the two-sided internal-
conversion band, and the whole *"What a conversion decision at a cap boundary IS"* row. Any lane
that commits that path by pathspec reverts three landings and my row with them.

**This is a `predates landing` copy and its door is `python3 -m tools.refresh_to_head
docs/institutional/knowledge_map.md`, in the shared tree.** Not run from here: it is a write to
another writer's tree, and the diff being pure reversion is a judgement I made by reading it, not a
verdict the clock issued. Recorded so the next seat in the shared tree runs it rather than
rediscovering it — and so that if my row goes missing, this paragraph is why.

## Disposition

Released. `the-refuted-bill-stress-knee-is-unbounded-beside-a-saturating-size-term` carries the
bound and the page sentence; `discharge-the-standing-publish-red-in-the-shared-tree-...` carries the
regeneration. Neither needs this id, and holding it would have cost a second turn re-deriving that
the refutation landed yesterday.
