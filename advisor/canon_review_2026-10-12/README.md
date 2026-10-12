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
| Reconciled theme documents (5 of 11) | **Complete.** Full documents. | `reconciled/`: harness rules, world-fidelity method, operating model and governance, communication and director interface, run discipline and scale |
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
