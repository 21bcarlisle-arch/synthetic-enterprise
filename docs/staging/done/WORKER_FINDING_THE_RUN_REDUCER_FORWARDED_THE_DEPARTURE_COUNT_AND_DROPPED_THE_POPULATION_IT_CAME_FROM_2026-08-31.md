**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `give-the-c2-reason-mix-its-svt-route`

# The run reducer forwarded the departure count and dropped the population it came from

**Filed 2026-08-31, delivery seat, Lane 0.**
Subject: `saas/reporting/annual_report.py::extract_report_data`.
Control: NOT LANDED. The claim this line carried on 2026-08-31 was that a control landed with the
repair; it did not, and neither did the repair. The original sentence is quoted verbatim, with the
measurement that refutes it, in the 2026-09-16 correction at the foot of this document. It is
dropped from here rather than left standing because this block is the claim surface the landed
manifest check reads, and a false LANDED redirects the next reader away from the live cause.
Consumer that was already refusing: `tools/population_anchor.py`, publishing `covers_svt_route:
false` in `site/state/population_anchoring.json`.

---

## The finding

`extract_report_data` forwarded `svt_departures` and did not forward `svt_decisions`.
`simulation/run_phase2b.py` returns both — the SVT departures that fired, and every SVT segment
decision behind them — and the reducer named only the first. So `docs/reports/run_output_latest.json`
carried **49 SVT departures and no SVT decision list at all**: a numerator with no denominator, from
which no rate can be formed.

**The consumer already said so, in as many words, and that is exactly why nothing went red.**
`tools/population_anchor` refuses — *"this run output carries no `svt_decisions` list, so the SVT
route's DENOMINATOR is unrecorded and no rate can be formed on it. Its `svt_departures` list holds 50
departures — a COUNT, in a population that was never written down"* — and that refusal is published
today. The refusal is honest and it is the right behaviour on a blind artefact. But **a consumer
declining to answer is not a control over its producer.** It is a symptom, and where it surfaces it
reads as a property of the world rather than of one reducer function twelve modules away.

## Why it survived a repair aimed directly at it

`svt_departures` was added to this same reducer, on this same day, by a commit whose own comment
names the class: *"the reduced artefact published 82 churned accounts against 32 churned rows and
the other 50 had no cause, no roll and no probability anywhere a reader could reach."* That repair
had a control — `test_a_churned_account_has_a_departure_record.py` — and the control went green.

**The leg someone had built a control for went green; the leg nobody had one for stayed red and
silent.** A route can account for every departure it reports and still be unable to state a rate.
The two are one line apart in the same dict literal, and one of them had a test.

That is the generalisable shape, and it is not about SVT: *when a repair forwards a numerator, ask
in the same breath what its denominator is and whether anything grades it.* A control over the
numerator cannot fail on a missing denominator, however close together they sit.

## The repair

One key, forwarded **without a default**:

```python
"svt_decisions": phase2b.get("svt_decisions"),
```

`.get(key, [])` was the obvious form and it is the fail-open reinstated. An empty decision list is
reported by `departure_population.declare_rows` as `covers_svt_route: true` over a denominator of
zero — an unobservable population arriving as a measured absence. Absent must stay `None` so the
downstream refusal keeps naming its own cause. The asymmetry with `svt_departures` (which does
default to `[]`) is deliberate: an empty numerator is not a claim about a rate, an empty denominator
is.

## What the control grades, and what it deliberately does not

The subject is **the reducer**, not `run_output_latest.json`. That file is written by
`background/sim_runner` on its own cadence, so a control keyed to it could not go green until some
other lane happened to run the world — and until then it would red every commit in the tree,
including commits with nothing to do with this. A gate slower than the tree's landing cadence never
converges. The artefact-side claim has its own reporter already, and it is a rendered one:
`covers_svt_route` in `site/state/population_anchoring.json` says on the surface whether the run it
was built from could see the route.

**So this is the observable consequence and it is not yet visible:** that field still reads `false`
and will read `true` on the first run produced by a tree carrying this commit. It was `false`
because of this defect, not because of anything about the world.

## A mutation that did not fire, and what it was

The first draft's second mutation — `phase2b.get("svt_decisions", [])` — **survived, green**, with a
docstring claiming it fired. The fixture passed `svt_decisions=None`, so the key was *present* with
value `None` and `.get`'s default was never reached. A world that predates the recorder does not set
the key at all. Fixed by deleting the key from the fixture; both mutations now fire, verified.

Recorded here rather than quietly corrected because it is the same class as the finding: a control
whose fail branch is reachable only by a route the fixture cannot take.

## What this does not close

Two things, both named rather than fixed:

1. **`tools/population_anchor` has no reason string for an EMPTY `svt_decisions`.** `None` gets a
   named refusal; `[]` becomes `covers_svt_route: true` with `svt_unreadable_reason: null`.
   `departure_population.load_svt_decisions` already handles the equivalent case on the file path —
   an empty sibling returns `([], reason)` — and `population_anchor` does not mirror it. It cannot
   fire while the world puts anyone on SVT, which is exactly why it should be closed before it can.
2. **The C2 reason-mix half of this claim.** `docs/reports/c2_departure_factors.json` still has no
   `_svt_segment_decisions.json` sibling; a capture against the current world was running when this
   was filed. That half is a second seat's, working the same claim id in an isolated worktree.

---

## CORRECTION 2026-09-16 — this document reached the record for the first time today, and its discharge claim does not hold

This file has never existed in any committed ref, in either staging room. It was written on
2026-08-31, sat untracked for sixteen days, and was swept up by the staging archival adjudicated
this tick. It is committed here rather than deleted, because a record nobody can reach is the
defect the 2026-09-16 archival landing exists to end — but it is committed with its own central
claim measured and refuted, not passed through.

**The claim, verbatim as filed.** The header block read *"Control landed with it:
tests/saas/reporting/test_a_departure_route_carries_its_denominator.py"*, and the finding's body
describes the reducer repair as made.

That sentence has been replaced in the header, not merely annotated, and the reason is itself the
lesson: the header block is what `tools/landed_manifest_check.py` reads as this document's claim
surface, and it refused this commit on exactly that line. A correction three hundred lines below a
false LANDED does not reach the reader the LANDED misdirects — nor the control. The claim is kept
here, where prose is prose, and dropped from where it is read as an assertion.

**Measured against git, 2026-09-16 — NEITHER half is landed:**

| what the document asserts | state at HEAD |
|---|---|
| the control landed | the file is on disk, dated 2026-08-31, and is in **no** commit |
| the reducer forwards `svt_decisions` | the working tree forwards it; `HEAD`'s copy of the reducer has **no occurrence of `svt_decisions` at all** |

So the finding is not discharged and the filing of it was itself an instance of the shape the
project keeps paying for: an uncommitted archival is not evidence of a discharge, because the
`done/` move IS the discharge. The document's own subject — *a repair forwarded a numerator and the
denominator it came from stayed behind* — happened a second time to the record of the repair.

**Therefore the finding's severity is RECORDED and this note is not a release.** The live work is
unchanged and is owed by `W2_customer_generator`: land the reducer change and the control together,
in one commit, and only then does `tools/population_anchor.py` stop publishing
`covers_svt_route: false`. That is a producer change in another lane's file, and this tick — a Lane
0 adjudication of a staging archival — is not the turn that should make it. Filing the measured gap
where the next reader will find it is what this turn owes.
