# Canon review, 12 October 2026: what was salvaged

This bundle holds everything recovered from the first attempt at the canon tidy-up. That attempt ran 21 sub-agents on Fable 5.1, hit the five-hour session limit (HTTP 429), and lost its working container. Nothing from it reached `main`. Everything here was rebuilt from the session transcript, which kept the sub-agents' final reports and every file the main session read back from disk.

## What the first attempt did

1. It inventoried 209 files: 187 director documents, the console captures, and the seven standing canon documents.
2. Eight sub-agents extracted 961 rulings and claims, each with a date, source, kind and theme.
3. It split those extracts into 14 theme files.
4. It reconciled the themes in two waves. Each reconciliation marks every ruling standing, superseded, lapsed or one-off, and lists conflicts for the director plus good rulings that have dropped out of sight.

## What survived

| Item | State | Where |
|---|---|---|
| Reconciled theme documents (5 of 14 themes) | **Complete.** Full documents. | `reconciled/`: harness rules, world-fidelity method, operating model and governance, communication and director interface, run discipline and scale |
| Theme extract files for the other themes | **Complete** raw extracts, not yet reconciled | `themes/`: mission and thesis, world-vs-supplier wall, knowledge first, priority and arc, CLV and commercial, product vs machinery, and fairness/pricing + carbon + other in one file |
| Second-wave reconciliations (3) | **Summary only.** The full documents were lost with the container. | `agent_reports/`: priority-and-arc, CLV-and-commercial, knowledge-first |
| Second-wave reconciliations cut off by the limit (4) | **Not done** | product vs machinery, mission and thesis, world-vs-supplier wall, fairness/carbon/other |
| October delta for the first five themes | **Not done** | (agent cut off) |
| Final report from every sub-agent | **Complete** (summaries of most important, forgotten and contradictory rulings) | `agent_reports/` |
| Briefs (extraction method, reconciliation method) | **Complete** | `inputs/bash_row1483…`, `inputs/bash_row1497…` |
| Director's own words, filtered from the input logs | **Complete** | `inputs/director_words_filtered.md` |
| Four-principles audit as read | **Complete** | `inputs/four_principles_audit_as_read.txt` |
| Status message sent mid-episode | **Complete** | `status_message_sent_mid_episode.md` |

## Lost for good

- The eight raw per-batch extract files (961 entries). Their content survives in `themes/` for the seven unreconciled themes, and in reconciled form for the other five. The raw extracts for those five themes are gone, but they are no longer needed.
- The full text of the three completed second-wave reconciliations. Their summaries survive.

## What is left to do

1. Reconcile the seven theme files in `themes/` with the brief in `inputs/bash_row1497…`. The three with summaries can be redone quickly against them.
2. Apply the October delta to the five reconciled themes, using the October console words and the four-principles audit.
3. Merge everything into one consolidated canon: the standing rulings by theme with sources, a list of forgotten good rulings, the conflicts for the director to rule on, and a "where this lands" list for each standing document.
4. Verify every citation against the repository, then stage.

## Lessons for the next attempt

- Run fan-out sub-agents on Sonnet, not Fable, and keep them to the recovered files rather than re-reading the repository.
- Push intermediate files to this branch as each step finishes, so that a lost container costs nothing.

## Progress since the salvage (12 Oct, second attempt)

- **All 14 themes now reconciled.** The seven theme files were reconciled on Sonnet helpers, using the recovered brief and only the recovered files plus current copies of the standing pages. Fairness/pricing, carbon and other were split back into their own files. That makes nine new documents in `reconciled/`, each folding in the October console words.
- `work/october_log.md` was regenerated from `inputs/director_words_filtered.md` with the lost script (64 entries, cited R-L-01..R-L-64). `work/reconcile_brief.md` is the recovered brief.
- **Merged into one canon:** `v4/DIRECTOR_CANON_v4_PROPOSED.md`, a proposed version 4 of `docs/design/DIRECTOR_CANON.md`. It has 168 numbered principles in 14 sections, with the October console words folded in, a new Phases section, and §15 listing 14 decisions for the director plus 12 items owed to him.
- **Quote check** (`tools/quote_check.py`, reports in `work/`):
  - chapters: 1,051 of 1,124 quotes verbatim in the repository; the rest are close paraphrases or quotes of extract notes;
  - canon v4: 257 of 257 verbatim.
- **Alignment steer, draft:** `v4/DIRECTOR_STEER_CANON_V4_ALIGNMENT_DRAFT.md`. It is staged only after the director rules.
- **Ruled and staged.** On 2026-10-12 the director answered "Agree all" to the fourteen decisions. Both documents were staged on main at `e89a772`: `docs/staging/DIRECTOR_CANON_V4_2026-10-12.md` and `docs/staging/DIRECTOR_STEER_CANON_V4_ALIGNMENT_2026-10-12.md`. Copies are in `staged/`.
