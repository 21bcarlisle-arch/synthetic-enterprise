**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

*RECORDED, not LATENT: this is a pre-registration and refutes nothing on its own. It exists so the
finding filed beside it can be shown to have been designed before its answer was known.*

# Pre-registration: what the band control's stale subject must show

**Filed 2026-08-31, delivery seat, Lane 0, BEFORE writing the new legs or running any mutation.**
Subject: `tests/architecture/test_switching_rate_commons.py`.
Instrument: `tools/measure_departure_level.py` (`world_realised_rate_pct`, `world_book_rate_pct`,
`reading_population`), all landed `b8e6ba32d`.

---

## What is already observed, and is therefore NOT a prediction

Measured before this file was written. Recorded here so nothing below can be mistaken for it.

**On the committed subject `docs/reports/c2_departure_factors.json`** (the artefact the band
control actually reads): the capture has no `_svt_segment_decisions.json` sibling, so it predates
C1b. `reading_population()` reports `covers_svt_route: False`, `population: "renewal decisions
only"`, `share_of_departures_visible: None`. `world_book_rate_pct()` returns `({}, <refusal>)`.
`world_realised_rate_pct()` returns eight years, every one of them sitting exactly on its band's
HIGH endpoint, and `test_the_worlds_realised_departure_rate_is_inside_the_published_band` is
GREEN.

**On the two-route capture `docs/reports/ladder_churn_factors.json`**: the whole book is OUT OF
BAND in all eight full years — 2017 +0.26, 2018 +2.52, 2019 −1.76, 2020 −2.17, 2021 −1.17, 2022
+8.50, 2023 +4.86, 2024 +0.52 percentage points against their bands. 2022 has ZERO renewal
decisions, so the renewal-only column prints `nan` there and the 2017–2024 summary mean is `nan`.

So the control is green on a one-route artefact from a world that no longer exists, while the
comparable quantity — the one its own band was always about — misses the record in every year it
can be computed for. **Neither fact can make the control red today.** That is the defect. It is
not "the world is wrong"; the world being wrong is filed separately and is blocked on
`18a09617d`'s SVT market-invariance. It is that *nothing in the file can tell a reader which of
those two worlds its green came from.*

## The repair, stated before it is built

Three legs added to the band control, keyed to the property and not to today's answer:

1. **The register must name the population its principal subject is over.** `_PRINCIPAL_SUBJECT`
   currently reads *"the world's own realised departure rate"* — a whole-book name on a
   renewal-decision reading. The leg reads `reading_population()` and requires the register key to
   carry the route qualifier whenever the declaration says a route is unreadable.
2. **The whole-book level is held to the band**, on `world_book_rate_pct()`. Red today for a named
   cause that cannot be discharged in this lane, so `xfail(strict=True)` — this repository's own
   device, and the one the existing docstring records having used for the pre-anchor 3.15x gap.
   **The marker is the thing to delete, never a target.**
3. **The refusal must not degrade to the flattering reading.** `world_book_rate_pct()` refuses with
   a cause rather than returning the renewal reading under a whole-book name.

## Predictions

Each is a mutation, and each names the leg it must fire. Filed before running any of them.

**P1 — the rename mutation fires leg 1.** Setting `_PRINCIPAL_SUBJECT` back to a whole-book-sounding
name, with the instrument's declaration unchanged, makes leg 1 RED and no other leg move. If it
fires nothing, the leg is checking a string against itself.

**P2 — the flattering-fallback mutation is reported LOUDLY by leg 2, not silently absorbed.**
Making `world_book_rate_pct()` fall back to `world_realised_rate_pct()` on refusal puts eight
in-band years under the whole-book name. I predict leg 2 then reports a **strict-xfail FAILURE**
(XPASS), not a quiet pass — i.e. the fallback cannot buy a green here. If instead it reads as a
pass, `xfail(strict=True)` is the wrong device and the leg must be re-shaped.

**P3 — a causeless refusal fires leg 3.** Making the refusal return an empty string, so the
whole-book reading is missing with no reason attached, makes leg 3 RED. A refusal that does not
name its reason is the shape CLAUDE.md requires against, and if leg 3 cannot see it the leg is
only counting the empty dict.

**P4 — the rename breaks nothing else.** I predict the other legs of the file stay green after
`_PRINCIPAL_SUBJECT` is renamed, because the string is module-local (grepped: two occurrences, both
in this file). If any leg outside the three new ones moves, the register key was load-bearing
somewhere I did not look and that is itself the finding.

**P5 — the whole file is red at HEAD for no other reason.** I predict the file is currently green
in full, so any red after this change is mine. If it is already red, that is a pre-existing wedge
and belongs in the record before I touch anything.

---

*Answers go in the finding filed beside this, beside the prediction and not in place of it.*