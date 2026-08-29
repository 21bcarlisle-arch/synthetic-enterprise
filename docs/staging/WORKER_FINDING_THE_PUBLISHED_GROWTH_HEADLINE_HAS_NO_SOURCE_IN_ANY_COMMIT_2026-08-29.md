**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `A46_book_depth_is_a_curriculum_question`

# The published growth headline has no source in any commit, and re-rendering it on this box does not reproduce it either

Lane 0 direction of 2026-08-29 asked, after landing the run path, whether **90 booked / 172 on the
book / rate 0.1789 / net £154,164** reproduce from HEAD. Three of those four were answerable
without running anything, and two of them are **no**.

This is class `uncommitted_and_orphaned_work`, arriving on a **public surface** rather than in a
module: the artefact is committed and live, and the only file that can author it is in no commit.

## The measurement

`site/data/book_growth.json` is committed and on the site. Its sole input is
`docs/observability/book_growth_campaign.json`, read by `tools/generate_book_growth_data.py:331`.

    $ git status --porcelain -- docs/observability/book_growth_campaign.json
    ?? docs/observability/book_growth_campaign.json
    $ git check-ignore -v docs/observability/book_growth_campaign.json   # rc=1 — NOT ignored

It is untracked and *not* gitignored, so this is an omission and not a design choice.

Re-rendering to a temp path from the working tree (never touching `site/data/`):

| field | LIVE (committed, on the site) | re-render, working tree |
|---|---|---|
| `settlement_sample_rate` | **0.1789** | **0.1771** |
| `settlement_funnel_wins` | 505 | 510 |
| `settlement_wins_refused` | 415 | 420 |
| `totals.quotes` | 2737 | 2760 |
| final `book_after` | **172** | **175** |
| Σ per-year `wins` | 90 | 90 |

**Verdict on the four headline figures.** *90 booked* reproduces. *172 on the book* does **not** —
it re-renders as 175. *0.1789* does **not** — it re-renders as 0.1771. (*net £154,164* is the
annual report's, answered separately.)

## Why it cannot reproduce from HEAD at all

From a clean checkout the input file does not exist, and the generator swallows that:

```python
try:
    campaign = json.loads(src.read_text(encoding="utf-8"))
except (OSError, ValueError):
    campaign = None
```

`build(None)` returns `available: False` with

> "no campaign record on disk — **no run has assembled a book since this generator was wired**, so
> there is no growth curve to render."

**The refusal names a reason and the reason is false.** A run *did* assemble a book — that is where
the live 90/172/0.1789 came from. The record simply never reached a commit. This project's rule is
that a refusal must name its reason so the refusal itself can be found wrong; here the named reason
misdirects to the one explanation that implies nothing is broken. On a fresh checkout the growth
page goes blank and tells the reader the company has never grown.

## Why the number moved between the two renders

Established by the 2026-08-29 ceiling-probe finding, and it applies unchanged here:
`live_population._resolve_campaign` writes that path **absolutely**, from every process that
assembles a book, and the live producer assembles one every ~25 minutes. The page was rendered at
`07:47:25Z` against one campaign; a later producer overwrote the file. So the published headline is
not merely unreproducible from HEAD — it is **not stable on this box**, and nothing on the page
says which campaign it was rendered against.

## The third answer, which is the smaller half

Even within the committed page, the rate is not derivable from the page's own rows: the rows fold
to 90/505 = **0.1782**, while the page states **0.1789** and instructs the reader to *"divide a
booked count by 0.179"*. `generate_book_growth_data.py:238` takes the rate from the campaign record
while folding `settlement_funnel_wins` from the years — deliberately, under SITE_CONSTITUTION rule
3 ("this file renders, it does not author"). That rule is right, but rendering an authored scalar
*beside* a fold of the same quantity publishes two answers under one label. Same shape as
`figures_on_a_superseded_clock`, on the site surface.

## What follows

Not repaired in this turn — recorded with the measurement that establishes it, because the fix is a
judgement about provenance rather than a patch:

1. **The campaign record must reach a commit alongside the page it authored**, or the page must
   carry the campaign inline. A published figure whose only source is a mutable untracked file at a
   fixed absolute path cannot be reproduced by anyone, including us.
2. **The `except (OSError, ValueError): campaign = None` branch must distinguish absent from
   malformed**, and must not assert why. "No run has assembled a book" is a claim the generator is
   not in a position to make.
3. **The page should state which campaign it rendered against** (a hash or stamp), so a reader — or
   the next session — can tell drift from a defect.

The control landed this turn (`simulation/settlement_clocks.scalar_row_disagreements`) does **not**
cover this: its subject is the run dict, and this defect is between an authored scalar and a fold
in a rendered artefact. Naming that gap here rather than widening the control on a guess.
