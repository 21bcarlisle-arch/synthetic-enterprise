# Startup anchors -- computed freshness

Generated: 2026-09-26 by `tools/startup_anchor_freshness.py`.

Every age below is computed from this repository's history at HEAD. **Do not use the HTTP
`last-modified` header of any of these URLs to judge freshness**: the GitHub Pages mirror
uploads the whole `docs/` tree as one artefact, so any publish restamps every file in it,
and a document untouched for a month is served with today's date.

**If you are orienting, read this table first.** It is the whole set of surfaces the
machine keeps current, and what each one is for. Anything not here is either static or
not maintained -- so it tells you what the project IS, not what it is currently doing.

| Anchor | What it is for | Last really changed | Age (days) | Verdict |
|---|---|---|---|---|
| `docs/PROJECT_OVERVIEW.md` | This document | 2026-09-17 | 9 | FRESH |
| `docs/reports/ANNUAL_REPORT.md` | The book's own annual report, regenerated each publish | 2026-09-26 | 0 | UNDATED |
| `docs/market_research/ASSUMPTIONS.md` | Every sourced assumption the world is built on, with its anchor and its gaps | 2026-09-06 | 20 | OLD |
| `docs/status/LATEST.md` | What just happened and what the machine is working on now | 2026-09-26 | 0 | FRESH |
| `docs/status/STARTUP_ANCHORS.md` | The computed age of every anchor on this page, and what each is for | 2026-09-26 | 0 | FRESH |
| `docs/status/SEAT_STRETCH_LOG.md` | Why each stretch of work went the way it did — the corrections, what was stopped short of, the reasoning behind a call | 2026-09-25 | 1 | UNDATED |
| `docs/direction/DIRECTION.yaml` | What the delivery seat is currently steering by, and what it has recorded as wrong | 2026-09-26 | 0 | UNDATED |
| `docs/direction/decisions.jsonl` | The append-only record of decisions taken, oldest to newest | 2026-09-26 | 0 | UNDATED |
| `docs/status/PROJECT_STATE.txt` | Build state — current phase and test count, generated each publish | 2026-09-26 | 0 | FRESH |
| `docs/institutional/knowledge_map.md` | What we know and what we have NOT established, with the gaps named | 2026-09-25 | 1 | UNDATED |
| `docs/operations/MAINTENANCE.md` | The monthly maintenance runbook this machine operates under | 2026-07-06 | 82 | UNDATED |

`FRESH` recent · `OLD` genuinely old and honest about it (not a defect) · `UNDATED` states
no date of its own, so this table is the only age a reader gets · `LIES` its own date is more than 3 days from its real one · `MISSING` not in HEAD.

## The header's stated figures

The sentence under the title states four quantities. Each is graded against the range its
own named source took over the 3 days either side of the
date that sentence declares -- so a figure computed when the header was written agrees, and
one typed from memory does not.

| Figure | Stated | Its source could have said | Verdict |
|---|---|---|---|
| commits | 10,474 | 10,144 – 10,763 (`git rev-list --count`) | AGREES |
| lines | 960,622 | 925,703 – 990,639 (newlines across every `*.py` in the git index) | AGREES |
| modules | 2,948 | 2,898 – 3,000 (the count of `*.py` in the git index) | AGREES |
| tests | 36,838 | 26,731 – 36,838 (CLAUDE.md's Build line, floored by the test functions in the git index) | AGREES |

`AGREES` inside the band · `OVERSTATES` / `UNDERSTATES` a number its own source never carried in that window · `UNGRADED` the source did not exist that far back, so this figure is unchecked and the reader is told so rather than reassured · `SOURCE_GONE` the source existed and stopped being readable inside this window, which is a refusal rather than an unchecked figure -- nobody chooses for a source not to have existed yet, and somebody chose this · `BELOW_THE_INDEX_FLOOR` the figure is smaller than the number of test functions the repository actually contains, which no collection can be.

**These four verdicts are not all worth the same, and the reader is owed that.** `commits`, `lines` and `modules` are graded against git, which nobody can type into. `tests` is graded against another hand-typed line -- CLAUDE.md's Build stamp -- so its band is only as independent as that line is, and it is floored, but not capped, by the index. An `AGREES` on `tests` therefore rules out a count that is too small and does not rule out one that is too large: a figure inflated in both documents at once would still read as agreeing. That gap is named rather than papered over.
