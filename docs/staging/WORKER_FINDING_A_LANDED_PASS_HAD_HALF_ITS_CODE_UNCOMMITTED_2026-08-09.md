# [WORKER-FINDING] KNIFE pass 1 was recorded LANDED in a committed doc while half its code sat uncommitted — and the SPOF commit that caught this caught only the other half

**Found:** 2026-08-09, at the start of the `KNIFE2_customer_straddle` draw.
**Disposition:** the instance is FIXED (committed as part of this tick, see below). The CLASS is QUEUED.
**Rank:** propose top-of-backlog. This is the second occurrence of the same class in one day and the
first one's fix did not generalise.

## Observed, with evidence

`docs/design/KNIFE_HOTSPOT_PASSES.md` §4 is committed and says pass 1 **LANDED**, with a delta
(`reporting_monolith` 3 edges → 0, `wall_crossings` 107 → 104) and a green ratchet suite. All of
that is true **of the working tree**. It was not true of `HEAD`:

```
$ git show HEAD:tests/architecture/test_epistemic_wall_ratchet.py | grep -A3 'LEGACY_COMPANY_READS_SIM.*frozenset({'
    ("saas.reporting.annual_report", "simulation.run_phase4c_on_phase2b"),
    ("saas.reporting.segment_report", "simulation.run_segments"),

$ git show HEAD:saas/reporting/annual_report.py | grep -n '^from simulation'
41:from simulation.run_phase4c_on_phase2b import main as run_phase4c_on_phase2b
```

So at HEAD the class-(a) allowlist was still populated and the reporting module still imported the
simulation run harness — i.e. **class (a) was not at zero on committed main**, which is the single
headline claim pass 1 made. Four files carried the uncommitted half:
`saas/reporting/annual_report.py`, `saas/reporting/segment_report.py`,
`simulation/run_phase4c_on_phase2b.py`, `tests/architecture/test_epistemic_wall_ratchet.py`.

## Why the existing guard did not catch it

Commit `83a55b750` is literally titled *"KNIFE1 SPOF: the three composition roots existed in one
working tree only -- commit them"*. Someone spotted this exact hazard and fixed it — **for the
files pass 1 created**. The `tools/run_annual_report.py` / `run_segment_report.py` /
`run_phase4c_pipeline.py` roots were untracked, so they were visible to `git status` as `??` and
were swept up by a "commit the new files" instinct.

The other half was different in one respect that turned out to decide everything: those four files
already existed. They showed as ` M`, indistinguishable from the routine churn of a shared working
tree with several daemons writing to it. **The remedy was shaped by how the omission was
discovered, not by what caused it** — and the cause (a pass's edits spanning new AND modified
files, committed by category rather than by pass) was left in place for the modified half.

## The class, stated so it is not re-derived a third time

Two known classes intersect here and neither one alone predicts it:

- *"Untracked build passes local-green"* — a green suite proves nothing about `origin`, because the
  suite reads the working tree. Covers the untracked half.
- *"The record can outrun the code"* — a committed document asserting a mechanism `HEAD` does not
  contain. Covers the document.

What is new is the **partial** case: a commit that discharges a pass's SPOF for some of its files
leaves the pass looking closed, so the next reader (this one) starts a dependent pass on top of a
tree whose foundation is local-only. `KNIFE2`'s exit criterion is stated *relative to pass 1*
("104, after pass 1 takes the return edge"). Had this machine died before this tick, both passes'
code would have gone with it while the committed record claimed one of them was done.

## What closing it needs

**Not** a bigger `git add`. The standing rule is the opposite — commit specific paths, never a
broad add, because concurrent writers share this tree.

The mechanisable version is a **close-time check, not an exhortation**: when a pass/atom is
recorded LANDED, verify the claim against `HEAD` rather than the working tree. Concretely, and
cheaply: the KNIFE ledger already recomputes every hotspot from the tree — pointing it at a
`git archive HEAD` export (the technique the ruff-ratchet finding already used to attribute its
drift) would have printed `reporting_monolith 3 edges` against a document saying 0. Same probe, one
different root. R16's shape applies verbatim: *verify the ledger, never `git show` of the cited
commit* — here, verify the tree at HEAD, never the tree under your feet.

## Instance disposition

Committed during this tick as its own commit, ahead of the KNIFE2 commit, so the two passes land
in their real order and pass 1's claim becomes true of `HEAD`. The full suite was run once over
both together (KNIFE2's integration run), which is the evidence for the pair.
