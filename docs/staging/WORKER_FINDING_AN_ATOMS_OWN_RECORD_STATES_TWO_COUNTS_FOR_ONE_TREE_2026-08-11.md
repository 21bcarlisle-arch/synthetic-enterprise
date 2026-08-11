# [WORKER-FINDING] An atom's own record states two different counts for one tree

**Found:** 2026-08-11, during KNIFE3 step 17, while reading step 16's `exit_evidence` to establish
where the pass had actually got to before writing step 17's.
**Disposition:** QUEUED per SELF_INTERRUPT_DISCIPLINE. Not fixed on sight, and the reason matters:
**the code was right throughout.** Nothing was mis-cut; only the record disagreed with itself.
**Rank:** backlog. Promote if any planner/digest mechanism is found to READ an atom's
`exit_evidence` counts (see "What makes this worse than cosmetic" below — it is currently read by
humans and by the next worker, which is bad enough).

## Observed, with evidence

`docs/design/simplifications/KNIFE3_wall_crossing_paydown.yaml`, the `exit_evidence` field as it
stood at commit `57cb9d872`. Its **headline**:

> STEP 16 (...) 2 EDGES CUT, 41 -> 39 LIVE (39 -> 37 direct; the 2 indirect deliberately UNMOVED
> for the third consecutive step ...). LEVEL DELIBERATELY STILL 0: 39 of 91 remain live

Its **EVIDENCE paragraph**, ~38k characters later in the same single-line field:

> tools/wall_crossing_dispositions.py rc 0 reporting '45 live crossings (43 direct, 2 indirect via
> a bridge package); 91 ruled (cut 46, owed 45, grandfathered 0)'. level_current stays 0: 45 of 91
> still live

**39 and 45 cannot both be the live count of one tree.** The live figure at that commit was 39
(confirmed: `tools/wall_crossing_dispositions.py` on the tree at `57cb9d872` reports 39). The
`45 / cut 46 / owed 45` block is carried over verbatim from an earlier step — it is step 13-era
arithmetic, still sitting under a step-16 headline.

## Why the code stayed right while the record drifted

This is the interesting half, and it is a compliment to a design decision rather than only a defect.
The register itself refuses to hold the count by hand — `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md`
§4 says so explicitly: *"The live count is not maintained by hand here —
`tools/wall_crossing_dispositions.py` prints it from the walker on every run, and the two numbers
disagreeing is itself the failure the tool exists to raise."*

That protection is real, and it held: every `cut`/`owed`/`grandfathered` **ruling** is checked
against the walker in both directions, and `--at-head` checks it against the committed tree. So the
part a tool reads could not drift.

**`exit_evidence` is the part no tool reads.** It is a prose field, appended to by hand, one step at
a time, and it is where the count went stale — the same asymmetry as the already-recorded class
"the record can outrun the code", except here the record did not outrun the code so much as *lag
it while quoting itself as current*.

## What makes this worse than cosmetic

`exit_evidence` is the **hand-off surface**. Its own first sentence is addressed to the next worker:
*"this atom is PARTIALLY built and must NOT be re-drawn as if from zero."* A worker who trusts it to
say how far the pass had got would have read 45 live and 45 owed — six edges of phantom work — and
either re-derived the wrong remaining set or concluded the register and the store disagreed and
stopped to reconcile them. Step 17 caught it only because it independently ran the walker first,
which is the discipline that should not be load-bearing for reading a record.

Class: **one name, two numbers** — a single quantity carrying two values in one artefact, where
neither is labelled as of-a-different-date.

## What a fix looks like

The tempting fix is "be careful when appending" — an exhortation, which CLAUDE.md says will
evaporate. The mechanised options:

1. **Stop restating derived counts in prose at all.** Have `exit_evidence` cite the tool
   (`wall_crossing_dispositions.py`) rather than quote a number, for any figure the tool prints.
   Cheapest, and it removes the drift surface instead of policing it.
2. **A store-contract check that any `N live crossings` / `cut N, owed N` string in an
   `exit_evidence` field agrees with the walker.** Narrow, and it can FAIL on its own defect (R15):
   inject the stale 45 and it must red.

**Recommendation: (1), with (2) only if a second instance appears.** (1) deletes the class for this
atom; (2) is a control whose subject is prose, which is the shape that rots. Note that (1) applies
to *derived* counts only — the narrative record of what was cut and why is the field's actual job
and must stay.

**Reversible:** an edit to one YAML field, or one added test. `git revert` undoes either.
