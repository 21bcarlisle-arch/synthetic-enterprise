# A gate compared a point estimate to its band, and certified 14 of 120 real subpanels it could not resolve

**Severity:** BLOCKING · **Lane:** H_harness
**Discharged:** `tests/harness/test_premise_two_level.py::test_the_GATE_REFUSES_A_POINT_ESTIMATE_WHOSE_INTERVAL_STRADDLES_ITS_BAND` — the gate now compares the interval, not the point estimate, and the falsifier fails if it stops
<!-- DISCHARGED 2026-08-12 by a worker tick drawn at RUNG 1c. This document reported a
     defect AND its repair in the same breath; its severity header stated the state the
     Hour FOUND, and nothing re-read it afterwards, so it went on refusing level-raises in
     H_harness after the instrument it named was trustworthy again. The falsifier below was
     RUN GREEN before this line was written. -->

**Atom:** `H_GAP_fabric_belief_truth_gap` (L2→L3 draw, worker tick, 2026-08-11)
**Eighth Expert Hour.** Directed question set verbatim by the seventh.
**Outcome: it found something, so the level stays 2.**

Every figure below is `observed-with-evidence`, out of `tools/couple_fabric.py` on this
atom's own published populations. Nothing here is inferred from the source.

---

## The defect

`panel_mirror_is_attributable` decides whether the panel mirror's verdict — flip or no
flip — may be read as a statement about the panel at all. Its money half compared
`panel_mirror_weight_artefact` (the weight-only null's share of the mirror's per-premise
movement in the deciding margin) to a 50% band **as a point estimate**, with no statement
of whether the panel could resolve which side of the band that share sits on.

Measured on real subpanels of the 200-premise population the ledger publishes. That
population's own share is **0.7307**, comfortably above the band, so every honest answer
on a subpanel drawn from it is `unattributable` or `unresolved`:

| n | point rule says `attributable` | of which carry a DECISIVE money verdict | interval reading says `attributable` |
|---|---|---|---|
| 20 | 50% | 0 | 21 of 120 |
| 30 | 37% | — | — |
| 50 | 30% | 16 | 2 of 120 |
| 100 | 15% | **14** | **0 of 120** |

On the worst of them the share was estimated from **four moved homes** and its 95%
interval was **[0.000, 1.000]** — the whole of the range the band divides — and the gate
certified the mirror anyway.

The 14 at n=100 are the ones that cost a reader something: a certified mirror that does
not flip publishes *"no composition effect"* as a finding.

**The failure signature is NOT the fourth Hour's "flat in N".** The point rule's error
rate does fall with N. It is that the point rule **never learns it cannot resolve** — at
n=100 the interval reading certifies 0 of 120 panels while the point rule still
certifies 14.

## The repair

Three states, because *"measured above the band"* and *"this panel cannot tell"* are a
finding about the instrument and a statement about the evidence, and a reader acts
differently on them (this mirror is wrong for this panel / get more homes).

- `panel_mirror_weight_artefact_resolution` — reads the interval: `hi <= band` →
  attributable, `lo > band` → unattributable, else `unresolved`.
- `panel_mirror_attribution` — combines both channels, worst first.
- `panel_mirror_is_attributable` — now `== "attributable"`. An unresolved panel never
  certifies.
- **Fail-closed on a missing interval** (an unavailable check is a failed check; a
  four-home panel is where a point estimate is worth least, not most), with one
  exception: the exact zero corner, where the mirror moved the margin on no premise and
  the share is a reading rather than an estimate.

**One-directional by construction:** it can only withdraw certification, never grant it,
so no verdict this gate released before is newly released now.

## The always-red risk was searched, not assumed

The suite's own proof that this gate *can* pass —
`test_the_WEIGHT_ARTEFACT_GATE_CAN_PASS_so_it_is_not_an_ALWAYS_RED_DETECTOR` — rested on
a panel reading **0.4711 on [0.414, 0.561]**: inside the band by 0.029, spanning it. So
the demonstration that this control is not always-red was itself a panel that could not
resolve the band.

A resolved pass had to be found or the repair would have *been* the defect. Searched the
way the fifth Hour searched: 700 draws of the flipping family, 13 flip a resolvable
verdict into a different resolvable one, 8 of those are resolved-faithful.
`_flipping_population` now defaults to the tightest — 60 homes, share **0.1690 on
[0.123, 0.230]**, wholly under the band. The 2×2's flipped+faithful cell, the one the
whole mechanism exists to protect, had been pinned on a panel that could not resolve the
fidelity it asserts.

## R15 — and one mutation survived, which is the reusable part

Six source mutations, md5 byte-clean restore (`2ab549446cbef0b86e3ebe9f34d6444a`), 9
green on the same selection unmutated. Each fires its own named test: gate reads the
point estimate again (the exact defect reinstated) / unresolved counts as a pass / a
missing interval falls back to the point estimate / the disclosure keyed back to the
point estimate / the exact zero corner forced through the interval / unresolved
collapsed into unattributable.

**One survived the first sweep** — the disclosure mutation. That *is* the defect this
Hour caught in its own repair an hour after landing it: a clause left keyed on
`share > band` while the gate had moved onto the interval, so a panel reading 71% on
[21%, 136%] printed *"above the 50% band"* and *"cannot resolve which side of the 50%
band"* in one sentence, joined by "and". It survived because **both fixtures agreed
between the two rules** (one under the band and unresolved, one over it and resolved).

> **R10 CLASS:** a control set with no population where the controlled thing varies is a
> control that cannot fail. The sixth Hour's own finding, arriving inside the test
> written to pin the eighth's.
>
> **SIBLING:** when a gate moves onto a new statistic, its DISCLOSURE inherits the
> retired one unless someone re-asks what the sentence is keyed to.

The separating panel is not exotic: over the band point-wise, unresolved by interval —
the shape of the row this atom actually publishes (0.7307 on [0.359, 0.902]).

## No published figure moved, checked not asserted

Both rows re-taken on their own declared population (`--seed 17 --unit-rate 7.4
--population 200 --population-seed 17`, read back off the row per the `refresh_args`
mechanism) **after** the code landed, the only ordering under which the row comes out
`current`. Gap 0.4269 / 0.4042, forgone GBP 548,919 / 451,832, misranked 11, declined
89 / 73 — every measured figure to the bit. Two-level still RED on
`L2.4_scale_spread_p90_p10`, the birth condition holding, not a regression.

Both rows read `panel_mirror_is_attributable=False` before and after. The whole ledger
diff is `measured_at`, `run_git_commit`, the two new attribution fields, and the one
`MIRROR INCONCLUSIVE` sentence whose **claim** changed: it said the artefact was measured
above the band; it now says the panel cannot resolve which side of the band it sits on.

Suites: 238 in the atom's own file, 317 across it and its three siblings;
`epistemic_verifier` PASS 553 files. Ledger reconciles clean at 14 of 14 (W1_5 went stale
by the same producer edit and was re-taken — two stamp fields, zero measured figures).

Commits `a322429d1`, `b2917ea8a`, `b6daaa939`.

---

## Two site-lane reds cleared, because they REFUSED this landing

Not queued — the machine was blocked (SELF_INTERRUPT_DISCIPLINE's interrupt case).

**1. The world-anchor probe called a live host dead.** `https://www.elexon.co.uk/data/`
answers **403** — a WAF method-block, which the probe has *always* classified as ALIVE —
but does not answer inside its 6s budget. The classifier folded that TIMEOUT in with DNS
and TLS failure, so a live believability anchor was published as rotted and the site lane
refused every landing.

This is the same class as the fabric finding above, and got the same repair: **an
inconclusive reading may not be published as a measurement.** A timeout is now retried
once at 3× before anything is concluded, then reported as `slow` — named in the text,
never counted as dead — with a vacuity guard that SKIPS visibly rather than passing green
if no anchor resolved at all. R15: one source mutation (the timeout folded back into
`unreachable`) fires the new named test, md5 byte-clean; the offline test pins all three
outcomes.

> This is this project's own named class — *a wrapper timeout below the work it wraps
> decides the verdict* — with a new consequence: it wedged an unrelated lane.

**2. A derived artefact was committed ahead of its input, at HEAD.**
`site/data/proof.json` carried `outcome_source_stamp` `2026-08-11T19:04:44Z` while its own
input `site/state/live_portfolio.json` was stamped `2026-08-10T16:59:32Z`. Two
live-surface tests were therefore red **on HEAD**, and the site lane refused every commit
touching a site-consumed ledger. Already filed as a class
(`WORKER_FINDING_A_DERIVED_ARTEFACT_CAN_BE_COMMITTED_AHEAD_OF_ITS_INPUT_2026-08-10.md`);
this is a live instance of it wedging a lane. Cleared by landing **both halves** of the
pair the publisher had already regenerated consistently in the tree (both
`2026-08-11T20:08:27Z`) — never one half, which is how it got there.

---

## Opener for the ninth Hour, and it is this Hour's own deliberate non-move

The **register** channel of the gate still has no interval at all:
`panel_mirror_register_infidelity` is compared to its band as a bare point, exactly as
the money channel was until today. It reads `0.000e+00` by algebra under the
level-preserving reflection, so the question is not whether it is wrong but whether a
term that is **zero by construction on every branch either published population takes**
can carry half a gate — the third Hour's own note that measuring an algebraically-zero
quantity does not make it failable, never followed up.

**Also named, not touched:** `panel_mirror_weight_artefact` is called a SHARE and is not
bounded by 1 (the authored row reads 80% on [73%, 122%]), because the sign flip can
oppose the re-composition premise by premise. Readings over 1 are real and informative,
and the word "share" does not admit them.

**Not a defect, and recorded so the next Hour does not re-derive it:** on every population
searched where the caveat can fire (188 fixture parameterisations plus 24 threshold-heavy
ones, all with a decisive money verdict and ≥5 moved homes) the minimum interval upper
bound was **0.637**. A resolved money-channel pass on a *decisive* population was reached
only by the flipping family. That is a real property of this instrument, not a bug — but
it means the pass branch is narrow, and a ninth Hour reading the gate as routinely
passing would be reading it wrong.
