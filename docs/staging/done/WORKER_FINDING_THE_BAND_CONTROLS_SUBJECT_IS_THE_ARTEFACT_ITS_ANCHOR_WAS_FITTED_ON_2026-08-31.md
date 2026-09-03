**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `give-the-c2-reason-mix-its-svt-route`

# The band control's subject is the artefact its anchor was fitted on

**Filed 2026-08-31, delivery seat, Lane 0. Found by obeying a lane instruction whose stated premise
was false — the instruction was right for a reason it did not know.**
Subject: `tests/architecture/test_switching_rate_commons.py::test_the_worlds_realised_departure_rate_is_inside_the_published_band`,
`docs/reports/c2_departure_factors.json`, `simulation/departure_level_anchor.py`.

---

## The measurement, which is the whole finding

`tools/measure_departure_level.world_realised_rate_pct()`, read off the **committed**
`c2_departure_factors.json` and off a **fresh capture of the current world**, against the published
band:

| year | published band | committed artefact | fresh capture |
|---|---|---|---|
| 2017 | 13.5 – **14.0**% | **14.0000%** | 14.0595% |
| 2018 | ? – **20.0**% | **20.0000%** | 20.1460% |

The committed artefact sits on the band's high endpoint **to four decimal places, in every year**.
That is not the world agreeing with the record. `YEAR_LEVEL_ANCHOR` was *fitted* to each band's high
endpoint on this very table, so the control is comparing the fit's own output against the fit's own
target. **It reads 14.0000 against 14.0 by construction.**

The control's docstring already knows the second half of this — it says room above is 0.00pp in all
ten years and that any upward move fails. What it does not say is that its subject is a **frozen
artefact**, so no upward move can ever arrive. The only event that can turn this control red is
someone re-running the capture, and nothing in the tree re-runs the capture.

## It is not stale by a little

Re-capturing on the current world (460 renewal rows / 80 departures, against the committed 465 / 79)
puts 2017 **out of band at +0.10pp**. The world moved under the anchor — several world commits have
landed since `71242c941`, including `2eeaa69ea` on household consumption levels — and the control
could not notice, because it was reading the old world's file rather than the world.

Note the raw 2017 renewal counts are identical in both captures (11 of 57). What moved is the
per-row `realized_churn_probability` — the world's departure **level**, not its roll. A count-based
check would have seen nothing at all here.

## Why this is the control-that-cannot-fail shape, not just a stale file

Three properties compose into a green that cannot go red:

1. the subject is a committed artefact, not the live world;
2. the artefact is the output of the fit whose target the control checks against;
3. the anchor is fitted to the band's **high endpoint**, so the measured value lands exactly on the
   threshold and the comparison is an equality dressed as a containment.

Any one alone is survivable. Together they make a control whose PASS branch is reached by
construction. It is keyed to today's answer — the artefact — rather than to the property, *"is the
live world still inside the published band"*.

## What I did NOT do, and why

I did not land the fresh capture. It is a true reading and it turns this control red at clean HEAD,
which wedges every lane's commits until the anchor is re-fitted. The control's own failure message
names the repair — *"re-capture and re-fit, do not widen the band"* — and the re-fit
(`tools/fit_year_level_anchor.py`) changes a world constant, which then moves the world, which then
requires re-capturing again: a fixed-point iteration of ~5-minute runs, and more than one turn.

So the tree keeps the artefact it had and this finding is the surface. The fresh capture is
reproducible in one command: `python3 -m tools.capture_departure_factors docs/reports/c2_departure_factors.json`.

**Recommendation, and I will carry it out unless the director objects:** re-fit the anchor against
the current world, iterate to a fixed point, land capture + anchor together, and then re-key this
control to the live world rather than to a committed artefact — because a control whose subject is
frozen is measuring the freezer.

## Correction to the lane draw that produced this

The draw asserted *"the data is not missing, it is under another capture's name"*, and instructed a
re-capture to make the SVT sibling exist. **That premise is false** — confirmed empirically here:
the run carries no SVT recorder and wrote no sibling, exactly as
`WORKER_PREREGISTRATION_WHAT_RE_RUNNING_THE_C2_CAPTURE_ON_THE_CURRENT_WORLD_MUST_SHOW_2026-08-31.md`
predicted. The C2 declaration is unchanged and still honest.

The instruction was nonetheless worth obeying, for a reason neither it nor I anticipated: running
the capture is what exposed the frozen subject above. Filed beside
`WORKER_FINDING_A_FOREIGN_SVT_SIBLING_IS_WHAT_MAKES_THE_ACCOUNT_DENOMINATOR_CONTROL_PASS_2026-08-31.md`,
which is the same class one artefact over.
