**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# PRE-REGISTRATION — whether any capture on disk can judge the live seven-year anchor block

**Filed 2026-09-02, delivery seat, BEFORE the run and before reading any of its output.** Written
against committed docstrings and the two strict `xfail` reasons in
`tests/architecture/test_switching_rate_commons.py` only. No measurement of band margins, whole-book
rates or SVT sibling contents has been taken at the time of filing.

## Why this run, and what changed since the direction was written

The drawn direction's two named "owed" items are **already repaired at HEAD** and this was verified
before filing, not assumed:

* `simulation/departure_level_anchor.py` is **clean** against HEAD (`git status --porcelain` empty),
  and HEAD carries the **seven-year** block plus the FITTED/`UNFITTED_YEARS` partition landed at
  `d374b1977`. The direction's premise — that the tree carries a ten-year block and the fit exists
  only in a staged document — is stale.
* `docs/design/UNLANDED_WHOLE_BOOK_LEVEL_ANCHOR_BLOCK_2026-09-01.md` is **committed** at `9238075d9`
  and byte-identical to HEAD. "Land that document first" is already discharged.
* `tools/population_anchor.py`'s `yr2022.get("sim_churn_rate", 0.0)` **measured zero is gone**,
  replaced by a `None` read with a named `rate_2022_unavailable` reason. The direction records it as
  "verified still present this orientation"; it is not present.

So the collision decision the item was drawn for has been taken. What has **not** been settled is
whether that decision can be *checked*, and that is what this run is about.

## The question

`YEAR_LEVEL_ANCHOR` is fitted by `fit_year_anchor_on_book` on a **whole-book union** target — both
departure routes combined within an account, meaned over ACCOUNTS. Two strict `xfail` legs hold the
band verdict open, and they read **two different quantities**:

* `test_the_worlds_realised_departure_rate_is_inside_the_published_band` reads
  `world_realised_rate_pct` — a mean over **renewal DECISIONS** on `docs/reports/c2_departure_factors.json`.
  Its reason names the discharge route as *"re-fitting `YEAR_LEVEL_ANCHOR` against the committed
  capture"*.
* `test_the_whole_book_departure_level_is_inside_the_published_band` reads `world_book_rate_pct` —
  the union over ACCOUNTS. Its reason gives cause (1) as *`c2` is a capture with no SVT sibling, so
  no whole-book reading can be taken off it at all*.

A whole-book fit and a renewal-only verdict are not the same quantity — the module's own docstrings
say so four times over. **If the first leg's named discharge route cannot in principle discharge it,
that reason is instructing every future reader to run a re-capture that will not work.**

## Predictions — each a MOVE, each falsifiable, filed before the run

1. **P1 — the renewal-only leg is below the band in every readable year, and the sign is
   systematic, not noisy.** All seven readable years read BELOW their published low edge, none
   above. Refuted if any year sits inside its band or above its high edge.

2. **P2 — the renewal-only reading cannot be brought into band by any re-fit of
   `YEAR_LEVEL_ANCHOR`, and the reason is structural.** Specifically: the renewal route is a
   sub-population of departures, so its rate is bounded above by the whole-book rate the anchor is
   fitted to. Refuted if the renewal reading exceeds the whole-book reading in any year on a
   capture where both are readable.

3. **P3 — `world_book_rate_pct` REFUSES on `c2` with a named cause**, because `c2` has no SVT
   sibling on disk. Refuted if it returns a reading.

4. **P4 — this is the finding: NO capture on disk can judge the live block on the whole-book
   quantity, because the two properties required live in different artefacts.** `c2` ran under the
   live block (its `sim_level_anchor` column matches all seven fitted years) but has no SVT sibling;
   `ladder_churn_factors.json` has the sibling but its `sim_level_anchor` column carries the
   **retired ten-year** values, so a whole-book reading off it judges the predecessor table, not the
   live one. Refuted if any capture on disk both (a) has a readable SVT sibling and (b) carries the
   live block's values in `sim_level_anchor`.

5. **P5 — the correct disposition is therefore "we cannot tell", not a re-key and not a widened
   band.** The remedy is a re-capture under the live block WITH its SVT sibling. Refuted if a
   discharge is available from artefacts already on disk.

## Constraints this run must not violate

* No constant is pasted, edited or deleted in `simulation/departure_level_anchor.py`. **Discharged
  by pasting `git status --porcelain` and `git diff --stat` for that path, not by recalling my own
  behaviour.**
* Neither `xfail` leg is re-keyed to today's readings, and neither is deleted. A reason may be
  CORRECTED where it names an unachievable route; the verdict it holds open stays open.
* The published band is not widened.
* 2022 is not clamped, interpolated, or given an invented anchor.

## What I will do with each outcome

If P4 holds, the deliverable is **not** a green control. It is the marker reason corrected to name
the achievable route, the unachievable one retired in writing, and "no capture on disk can judge
this block" stated on the surface where a reader meets the verdict. That is a result.

---

# GRADING — 2026-09-02, after the run. Two of five predictions refuted; both misses kept.

Run on a clean `git archive HEAD` stem in `/tmp/anchorjudge`, and P1 re-run on a second stem at
`f97c34eb0` (the marker reason's own commit) to separate "the reading moved" from "the reading was
always this".

## P1 — **REFUTED, and it is the most useful thing in this run.**

Filed: *"All seven readable years read BELOW their published low edge, none above."*

Measured: **six ABOVE the high edge, one below.** 2017 15.12% (band 13.5–14.0), 2018 25.77%
(19.5–20.0), 2019 28.10% (20.7–21.3), 2020 38.89% (22.5–23.0), 2021 23.40% (17.9–18.4), 2024 22.34%
(12.5–16.1) are all **over**; only 2023 at 2.81% against 8.9–12.5% is under.

I predicted the sign from the 3.45x-short framing that runs through the anchor module's docstring,
the block's own "moves hard AGAINST the company" paragraph, and the drawn direction. **That framing
is about the whole-book quantity and this leg reads the renewal route; I carried the sign across a
population boundary without checking it.** Exactly the split this project keeps paying for, made by
the person writing the prereg about it.

## P2 — **REFUTED on its reasoning, and not testable as framed.**

Filed: *"the renewal reading is bounded above by the whole-book rate the anchor is fitted to."*

That premise is wrong. `world_realised_rate_pct` means over renewal DECISIONS; `world_book_rate_pct`
means over ACCOUNTS. A mean over a selected sub-population that demonstrably shops is **not** bounded
by the whole-population mean and can exceed it — which is precisely what P1 measured. The
falsification test I filed ("refuted if renewal exceeds whole-book on a capture where both are
readable") is also unrunnable, because P4 establishes there is no such capture.

**The conclusion P2 was reaching for survives its broken reasoning, by a different route:** the
renewal leg cannot be brought into band by re-fitting, because the anchor is fitted to a different
population than that leg reads. Mismatched quantity, not miscalibration. Recording that the
conclusion stood while the argument for it did not.

## P3 — **CONFIRMED.**

`world_book_rate_pct()` on `c2` returns `({}, refusal)` with the named cause *"the SVT route is
unreadable, so a whole-book count cannot be taken at all… It is the renewal-decision population
only, which is no longer the whole book."*

## P4 — **CONFIRMED, and it is the finding.**

`c2`: 7/7 fitted years match the live block, **0** SVT sibling rows, whole-book **not** readable.
`ladder`: **1266** SVT sibling rows, whole-book readable, **0/7** fitted years match the live block.
`c3`: 0/7, 0 sibling rows, not readable. **No capture on disk has both required properties.**

## P5 — **CONFIRMED.**

No discharge is available from artefacts on disk. A re-capture under the live block with its SVT
sibling is the only route, and until it runs "we cannot tell" is the verdict.

## Constraints — discharged by reading the artefact, not by recalling my behaviour

```
$ git status --porcelain simulation/departure_level_anchor.py tools/population_anchor.py
(empty)
$ git diff --stat -- simulation/departure_level_anchor.py
(empty)
```

Neither `xfail` leg was re-keyed or deleted; both remain `strict=True` and both still fail. The seven
margins in the marker reason are **unchanged** — what was added is the direction they came off,
because a bare negative does not say which edge. The band was not widened. 2022 was not clamped,
interpolated, or given an anchor.

## One correction I made mid-run, kept because it changes how the next reader reads the marker

I first concluded the marker's seven margins were **sign-flipped** and was about to file that as the
finding. They are not. `band_margins` returns `(value - lo, hi - value)`; the marker quotes whichever
element came back negative — the HIGH element in six years, the LOW element in 2023 — and all seven
reproduce to the digit at both commits. The marker was right. What it lacked was the direction, and
that is what landed.
