**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# The self-audit declared a correction on every row, and nothing in the tree carried it — the section the director called empty was the one section `validate()` said nothing about

*Delivery seat, 2026-09-03. Grades the director's console report of the same morning, checked
against the record rather than taken.*

---

## 1. The report, and what it actually was

> *"One defect in the seat itself: DIRECTION.yaml's `wrong` section is five empty rows. The
> self-audit isn't being populated, and it's the field that makes the seat correctable. Fix that
> first."* — Director, 2026-09-03

**The text was never empty.** Measured across every committed version of the file:

| | |
|---|---|
| Committed `DIRECTION.yaml` records | 40 |
| Self-audit rows in them | 211 |
| Rows with an empty or missing `what` — **the reported shape** | **0** |
| Rows with no `corrected` verdict | **3** |

Also checked and populated: all 69 orientations in `docs/direction/decisions.jsonl` carry a
non-empty `wrong` list; `site/data/delivery.json` served 212 entries; the **live** page at
`https://poesys.net/data/delivery.json` served 211, fetched with a cache-defeating nonce. There is
no artefact in this project, served or committed, on which that section renders as five empty rows.

**The correction half was empty everywhere, which is the half he named.** Three separate legs:

1. **`validate()` said nothing about `wrong` at all.** It checks `focus` field by field
   (`id` and `why`), `not_now` field by field (`what` and `why`), the timestamp, and target-shaped
   keys at arbitrary depth. `wrong` had no clause. Five rows of `{}` would have validated, been
   committed, been recorded, been published, and read from outside **exactly like five errors
   honestly declared**. The failure he described was one this tree could not have distinguished
   from health — which is the same thing as the control not existing.
2. **`corrected` was dropped at the first hop.** `background/delivery_seat.py` recorded
   `"wrong": [r.get("what") for r in parsed.wrong]`. `git grep -n corrected` across `background/`,
   `tools/`, `site/` and `tests/` returned **no reader of the field anywhere in the repository**.
   The seat wrote a verdict on 211 rows and 211 of them were thrown away one line downstream.
3. **The verdict was reconstructed, never graded.** `build_brief` handed the orienting session
   `previous_focus` and `previous_focus_drawn` — and never the previous errors. So every
   `corrected: true` in the record was written from whatever that session happened to remember,
   and an error nobody remembered left the record with **no verdict at all**, silently, with
   nothing anywhere able to notice it had stopped being listed.

So: he was wrong about the artefact and right about the mechanism, and the smaller true version of
his report is in the 18:30 record of 2026-09-02 (`83c63ac58`), where **3 of 6 rows carried no
`corrected` field** and it was accepted without comment.

## 2. Why it was invisible, which is the reusable half

This is `feedback_counting_events_cannot_see_an_empty_event` in a new subject. Every surface over
the self-audit **counted** its rows — the page rendered 212 cards, `read_decisions` returned them,
the empty-state branch guarded against there being none — and **not one of them read a row**. The
same shape as 29 empty merges lighting up every liveness surface: presence was measured, content
was not.

It is also `feedback_a_ratchet_with_no_floor_cannot_fail`, inverted. A section with no validator
cannot fail. It had been accumulating rows for 40 records and its correctness had never once been
tested, in a file where the two sections either side of it are both checked field by field.

And the third leg is the shape `previous_focus_drawn` already exists to catch, one field over: *a
steer that quietly did nothing looks identical from outside to a steer that was taken.* The seat
measures whether its own last steer bit. It did not measure whether its own last errors were fixed.

## 3. What changed

- **`background/direction.py`** — `validate()` gains a `wrong` clause: every row must be a mapping
  with a non-empty `what` and a **boolean** `corrected`. Boolean and not merely present, because
  `corrected: "not yet"` reads as corrected to every consumer that tests it for truth. The refusal
  names the row index, so four good rows and one empty do not read as "the section is bad".
- **`background/direction.py`** — new `wrong_rows(row)` reads a recorded orientation's audit in
  **both** stored shapes. `decisions.jsonl` is append-only, so the 69 pre-change rows are read, not
  rewritten; their correction state is genuinely **unknown** and is returned as `None`. *"We did
  not record whether this was fixed"* and *"this was not fixed"* are different claims, and folding
  the first into the second would publish 212 false accusations against our own record.
- **`background/delivery_seat.py`** — the record hop keeps `{what, corrected}`; `build_brief`
  carries `previous_wrong`; `CHARTER` says an open error must reappear either still open or fixed
  with evidence, and that a row failing the shape is refused outright.
- **`background/delivery_seat.py:_prompt`** — `previous_wrong` is lifted **above** the
  `json.dumps(brief)[:60_000]` cap, rendered as a list with each row's verdict and an
  `N of M still open` line. It was the thirteenth key of the brief, behind `commits` and behind the
  rendered commit shape: on a long stretch the seat would have been told to grade a list that had
  been truncated off the end of its own prompt, and would have done exactly what it did before the
  field existed. **An input a truncation can silently remove is not an input** — the same lesson as
  the commit list directly above it, which is why it is one comment and not two.
- **`tools/generate_delivery_page.py` + `site/harness/index.html`** — the panel carries
  `corrected`, splits **still open / corrected / correction not recorded** on the card, and heads
  the list with the counts. The third state is on the surface rather than collapsed, for the reason
  above.

## 4. What it reads today, honestly

`what_it_got_wrong()` at this commit: **212 entries, 0 outstanding, 0 corrected, 212 correction not
recorded.** Every recorded row predates the field surviving the hop, so every one of them is
ungraded and the page now says so instead of implying they are all live. **The first graded row
arrives at the next orientation** — which means this fix is a mechanism today and evidence in three
hours, and until that record lands nobody should read the panel as saying the machine has no open
faults.

## 5. What this does not fix

`site/harness/index.html` has a second panel titled **"What we got wrong, and corrected"**
(`<div id="corrections">`), fed from `proof.json`'s `corrections` key. It holds **three** entries,
the newest dated **2026-07-23** — six weeks stale — while 212 recorded errors sit in the panel
above it. The two lists have different subjects (published-claim retractions against the seat's own
self-audit) and that is defensible, but a reader meets "3" under a heading that promises corrections
immediately after meeting "212" under a heading that promises mistakes, and nothing on the page
tells them the lists are about different things. **Not fixed here** — it is a page-copy and
register question, not this mechanism, and folding the seat's audit into a retraction register
would be the wrong repair. Filed as its own item.

## 6. The tests, and the mutation each one names

`tests/background/test_the_self_audit_declared_a_correction_and_nothing_carried_it.py`, 26 legs:

| Leg | Mutation that must fire |
|---|---|
| five `{}` rows, and four other kinds of empty, are refused | delete the `wrong` clause from `validate()` |
| a non-boolean `corrected` is refused | accept any truthy value |
| a populated audit passes; an **absent** one is not an error | refuse an empty section — a clean stretch is allowed |
| the refusal names `wrong[2]` of four good rows | report the section rather than the row |
| the record hop keeps the verdict | revert to `[r.get("what") for r in parsed.wrong]` |
| both stored shapes read, legacy → `None` | return `bool(...)` for a legacy string row |
| the panel splits open / corrected / not recorded | count not-recorded as uncorrected |
| the rendered page shows the state | emit the field to a page that drops it |
| the brief carries `previous_wrong` | drop it from `build_brief` |
| the charter says a vanished error is forgotten, not fixed | remove the instruction |
| **the list survives the 60k prompt cap** | leave `previous_wrong` inside the JSON dump only |
| an empty previous audit says *which kind* of empty | return silence |

Plus one leg appended to `site/test_harness_delivery_record.py`, which renders the real page
against the real feed and asserts the first entry's recorded state appears in the rendering.

## 7. Regression check on the record itself

All 40 committed `DIRECTION.yaml` versions were re-validated under the new clause. **39 pass; one
(`83c63ac58`) is refused**, for the three rows in §1 that carry no verdict. The **live** record
validates, so the seat does not wedge on its next run — checked before landing, because a validator
that refuses the current record would have stopped direction reaching the draw entirely, and
`direction.py` is fail-soft precisely so that never happens.
