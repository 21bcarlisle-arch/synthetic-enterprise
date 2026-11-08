**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The archive-question gate now reads `advisor/done/`, and 64 rulings archived before it carry his quoted questions with no register entry (2026-11-08)

**Claim:** `widen-the-ruling-archive-gate-to-advisor-done`, from
`docs/staging/records/SEAT_RESULT_PLANT_THE_DEFECT_ON_THE_NO_EVIDENCE_GATES_AND_THE_REST_OF_THE_STALE_COPY_AND_SITE_LANE_REFUSALS_2026-11-08.md` Part A.

## What changed

- **`tools/ruling_archive_question_gate.py`** gates both archives, `docs/staging/done/` and
  `docs/staging/advisor/done/`. An archival (add, rename or copy into either) is refused for any open
  question. An edit to a ruling already archived is refused only for a question **the edit adds**
  (one not open in the HEAD copy). If the HEAD copy cannot be read, the edit is gated as an archival.
- **`background.open_question_register`** extracts only `?`-sentences inside the director's quoted
  words (a straight-quoted span inside one paragraph, or a curly-quoted span). The two old forms
  (a list under a heading that names "questions"; any `?` under a DECISION heading) are gone. Its
  active set now includes `docs/staging/advisor/`, so his questions in a live ruling show in the
  daily note before archival, not first at the gate.
- **16 dispositions** were recorded in `docs/observability/open_question_register.json`: 13 for the
  six rulings the draw named, and 3 for the live correctness ruling. `open_questions()` on this tree
  is 0.

## What the item got wrong, measured before it was acted on

The item assumed narrowing would shrink the set to the six rows the register counted. **It grows
it.** With the old extractor, 6 `advisor/done/` rulings had open questions, and every one was a false
positive from the advisor's drafting. Examples: the heading "THE FOUR RESERVED QUESTIONS" made every
ruling line a question, and a list of the seat's closures became 15 questions. With his quoted
words only:

| archive | rulings with an unregistered quoted question |
|---|---|
| `advisor/done/` | 46 (41 after today's dispositions) |
| `done/` | 18 |
| `advisor/` (live) | 1, the correctness ruling: dispositioned now |

Of the six named rulings, `YES_TO_THE_THREE_30_OCT` carries no quoted question. The other five carry
13 between them. Two of those are not his. They are example strings the advisor quotes in the 2 Nov
ruling, and they are closed as `wrong` with that reason. That is the known false-positive cost of
the quoted-words rule.

## Why edits to archived rulings are not refused outright

The 64 rulings were archived before the gate read his quoted words. Their questions were answered
in prose in each ruling's Done section, not in the register. Refusing every later edit to one of
them (a factual correction, a path sweep) would block a lane that did not create the debt. Instead
the gate holds its own property: nothing is archived with an open question, and no edit adds one.
`tests/tools/test_ruling_archive_question_gate.py::test_an_edit_refuses_only_the_question_it_adds`
asserts all three legs (legacy edit passes, added question refuses, unreadable HEAD falls back to
the archival rule) before it checks what each one says.

## Owed

- **The backlog.** After today's 13, 136 quoted questions in 59 archived rulings have no disposition. Most are answered in
  their ruling's Done section. Some may never have been answered. Spot-checks suggest
  "why wasn't this picked up automatically?" (code-review steer, 24 Oct) and "Does debt sit with
  supplier or dno?" as candidates. The honest next step is a census: read each Done section against
  its quoted questions, and record `answered` with a pointer, or raise the ones that were never
  answered. It is not on the gate's path. It is the register's only route to the "no question left
  unanswered" ruling's own acceptance test for October's rulings.
- **Known gap:** a ruling written in his voice without quotation marks yields no questions. None has
  arrived that way since the advisor channel opened on 15 Oct.

## How to reverse

Revert the landing commit. The register's dispositions are additive and keyed per question, so
the old extractor ignores them.
