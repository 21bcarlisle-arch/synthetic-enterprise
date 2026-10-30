**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Preregistration: the fifth cold read, on the 3dc5a92948 book (2026-10-30)

Written before any page is rendered for the reader and before the reader is briefed. Item
`fifth-cold-read-on-the-3dc5a92948-book` (DIRECTION row `the-fifth-cold-read`). The reading that grades
it will be `records/SEAT_READING_THE_FIFTH_COLD_READ_ON_THE_3DC5A92948_BOOK_2026-10-30.md`.

**The premise, re-measured.** 9cd0765bb7 released this read because the book did not exist. It now
does: `/var/tmp/fresh-run-out-3dc5a92948/DONE.json`, `/var/tmp/fresh-grade-3dc5a92948/ALLDONE`, and
the grade and page build are on origin (74d6c0759c, 51a39fd752, 128149f343). Leg one is recorded as
met in substance on this book (0 unexplained, 8 excepted rows). No cold read has seen these pages.

**The pages.** `/var/tmp/grade-3dc5-pages/tree/site/`, built from this book at 3dc5a92948 with the
fixed `_owed_past_due` (74d6c0759c). Served at 127.0.0.1:8791 (8765 is held by another process, so
it is not used). The committed `site/` is untouched until the 2 Nov publish.

## Method

- Leg two: list the eight slots from that `explore_cast.json`, each valid with its household or
  empty with its failing check, graded by the reader and then by the seat on the record.
- Leg three: ruling step 6, the fourth read's route (`/var/tmp/fourth-read-scripts/render.mjs`).
  - Render every cast moment with Playwright.
  - Six households are drawn with `random.Random(20261031).sample` from the picker's 752, less the
    four earlier reads' 25 (727 left): **PROS-2023-0291, PROS-2020-0012, SYN-2016-051,
    OCC-7c2500b09b7b, SYN-2016-279, OCC-392d56a03faa.**
  - Two are added by name, because the DIRECTION row asks for them by name: OCC-2f64fad94fe7 (N8, N9)
    and SYN-2016-550 (the fourth read's invalid debt slot). PROS-2019-0246 (N1) and SYN-2016-210 (this
    book's debt slot) are already in Section A.
  - A fresh Opus agent reads only the packet, as a GB retail-energy professional, priors first.
  - The seat checks every key quote against the packet, then classes each objection new or known.
- **What counts as a new class:** an objection the seat confirms on the record or in the page code,
  that no earlier read's O/N list, open finding or domain-invariant row already names. Storage-heated
  single-rate billing (item 3) and E1's 179 are filed, so neither is new.

## Predictions

| # | prediction | range |
|---|---|---|
| P1 | slots filled (known from the grade record, so this is a check, not a forecast) | 6 of 8; empty: ev, storage_heating |
| P2 | the reader grades the debt slot (SYN-2016-210) | valid, because it passes all four checks |
| P3 | objections | 20–45 |
| P4 | new classes confirmed in the record or code | at least one (each of the four earlier reads found one) |
| P5 | N1, N8, N9 by name | none recurs: PROS-2019-0246's amount to pay nets its EBSS credit; OCC-2f64fad94fe7 prints a non-zero committed rate and one meter home |
| P6 | SYN-2016-550 | prints one owed figure per moment, but still carries an unpaid 2018 bill held flat (the first read's O27, existing) |
| P7 | the exit-test legs | leg two MET; leg three NOT MET (follows P4), so the stretch does not exit |

P4 and P7 are written against our own thesis, as F11 asks. If P4 is refuted, the read meets leg three.

## Results

*(Filled in the reading, beside each prediction.)*
