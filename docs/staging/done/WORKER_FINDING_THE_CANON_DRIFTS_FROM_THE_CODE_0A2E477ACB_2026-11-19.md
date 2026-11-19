**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 2 · **Atom:** `A45_the_canon_is_a_standing_subject`

# The canon page and the code disagree on 5 registered claim(s) (2026-11-19)

**Found by.** `tools/canon_drift_check.note_line`, run by the daily self-note. Minted by the check itself, keyed `0A2E477ACB` on the set of red claims, so the same drift is filed once.

| Claim | Verdict | Page | Detail |
|---|---|---|---|
| served page | SUPERSEDED | site/harness/index.html | 'non-commercial' -- the 21 July mission; §16 Mission |
| served page | SUPERSEDED | site/harness/index.html | '80 founders' -- the book before 6 Oct; §16 Book size |
| served page | SUPERSEDED | site/harness/index.html | 'director twin' -- the twin as approver; §16, void since 29 July |
| served page | MISQUOTED | site/harness/index.html | canon 'Each step fires from the one before it, not from me remembering'; page reads 'Each step fires from the one before it... deliberately breakable and shown to go re' |
| served page | MISQUOTED | site/harness/index.html | canon "Good management of renters and won't pay (but can) can create as much value ... as other value add."; page reads "Good management of renters and won't pay (but can) can create as much value... (people phases re-cut along the merit or" |

**What each verdict asks.** OVER_CLAIM: the page says more than the code does -- correct the page (a director document takes a `Director-doc: correction` trailer) or restore the code. SUPERSEDED: the code moved past the page -- the page under-claims. UNBOUND: the register's anchor sentence left the page -- rebind the row. ERROR: the probe could not run, so nothing is known. REMOVED: a row left the register without a `retired` reason. LAPSED: the atom that would build a mechanism the page says is missing has moved -- re-read the sentence, then bind it with an absent claim, correct it, or re-judge at the new level. A served-page SUPERSEDED or MISQUOTED row: the site presents a withdrawn framing as current, or a canon line in words the canon does not use -- correct the page, or mark told history with `data-canon-history`.

**Done means.** `python3 tools/canon_drift_check.py` reads none of the rows above as red. Full report: `docs/observability/canon_drift.json`.

## Done (2026-11-19, autonomous worker)

**Cause.** No code drift. All five rows sit in the director-asks ledger on the Harness page. That ledger quotes dated asks, abridged with "...", including asks that canon has since superseded. `1ce3a4a442` (18 Nov 14:31) made `tools/director_asks_ledger.render_html` wrap both ledger lists in `data-canon-history`, so the site leg reads them as told history. The working-tree `site/harness/index.html` was rendered at 18 Nov 10:09, before that fix. It sat uncommitted with the old unmarked lists, and the check reads the working tree. HEAD's page carries none of the five phrases.

**Action.** I re-rendered the page in place with the current generator (`python3 -m tools.harness_page_figures`). The page now carries `data-canon-history` on both ledger lists. The rest of its diff is the publish-owned figure blocks refreshed to today's counts. The page is publish output, so I did not commit it; the next publish commits it.

**Evidence.** `python3 tools/canon_drift_check.py`: "30 claims checked · 0 drifting", and the site leg reads "every served page holds" across 88 pages against 149 canon quotes.

**Reverse.** Restore the pre-render copy from `/tmp/harness_before_rerender.html`. Don't do this: it reintroduces the five rows.
