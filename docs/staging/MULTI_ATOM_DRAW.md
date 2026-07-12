# MULTI_ATOM_DRAW — width must come from the map, not the advisor (P0, completes R3)

**Staged:** 2026-07-12 15:0x by advisor, director-prompted. Sequence AFTER the
draw-filter fix (ADVISOR_ANSWER_CANNOT_DRAW), which is its precondition.

## The structural problem
The supervisor draws ONE atom per turn. One atom = one lane = serial BY
CONSTRUCTION. Every burst of parallelism this weekend came from the advisor
hand-feeding parallel work, or from the agent choosing to fork inside one
task — never from the machine itself. That is why repeated "be wider"
instructions decay back to serial within the hour: they nag a design instead
of fixing one. **Width must be a property of the granting model, not a
standing exhortation.**

## Requirement (mechanism is yours)
The self-refill draw must be capable of granting MULTIPLE concurrent atoms per
cycle, with one agent per atom, whenever their file-scopes are disjoint. The
map currently holds ~30 idle atoms — the raw material for width is sitting
there unused.

Constraints (not designs):
1. **Disjointness is the safety rule**, and it must be checked, not assumed:
   two atoms may run concurrently only if their declared file-scopes do not
   intersect. Atoms should therefore declare their file-scope (this may be a
   schema addition — that is fine).
2. **The wall composes with this for free:** sim-lane and company-lane atoms
   are disjoint BY DEFINITION (the founding law). Those are always safely
   concurrent. Use that.
3. **Single-writer per tree preserved** — integration remains serialized; if
   concurrent writes cannot be made safe in one working tree, use whatever
   isolation is real (worktrees, forks-and-merge, staged sequencing). Do not
   pretend disjointness that does not hold — the collision-avoidance judgment
   shown this morning was correct and must not be lost.
4. **Verification does not fan out:** the full suite runs once per integration
   boundary, not per fork.
5. **Read-only atoms (discovery, red-team, charter, cold-walks) have no
   collision risk at all** and should be drawn freely alongside any build.

## Definition of done
Draw grants N>1 where safe; file-scope declared in the schema; a test proving
two disjoint atoms are granted concurrently and two overlapping atoms are NOT;
digest reports atoms-drawn-per-cycle. Then let it run: the map has 30 idle
atoms and ~13 hours before reset — the machine should be filling that itself,
without the advisor queueing work for it. **The test of success is that the
advisor stages nothing tonight and the map still moves.**
