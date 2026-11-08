**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: plant each no-evidence gate's own defect, and judge the rest of the stale-copy and site-lane refusals, for the 11 Nov gate review (2026-11-08)

*Delivery seat, 2026-11-08, claim `run-the-11-nov-two-reader-and-gate-review`. Written and landed before any
plant was run or any further refusal judged. It covers the two things the 7 Nov record
(`SEAT_RESULT_WHAT_PREDICTS_A_DEFECT_AND_WHAT_EACH_COMMIT_GATE_HAS_CAUGHT_FOR_THE_11_NOV_REVIEW_2026-11-07.md`)
says must happen before any gate is named for retirement. The review itself is due on or after 11 Nov. This
is its evidence, gathered now because the transcripts behind the refusal events expire after about 30 days.*

## Part A — plant the defect (the 13 gates that showed no evidence)

**What a plant is.** For each gate, the smallest change to this isolated worktree that IS the defect the gate's
own hook comment names. The change is staged in the worktree's own index and is never committed. Then every
step of the pre-commit chain is run in turn on that one plant, each with its own exit code recorded. Before that,
the whole chain runs once on a control: a staged one-line change to a scratch doc. That shows which steps are
already red on the base, so a step that was red before the plant is not counted as catching it.

**What each outcome means:**
- **own gate passes the plant:** the gate cannot fire on its own defect. It is dead as wired.
- **own gate refuses, and so does another step:** the gate is redundant for this plant. The other step is named.
- **own gate refuses, and nothing else does:** the gate is the only line of defence. Its 30 days with no
  refusals reads as deterrence, or as a defect class that simply did not occur. The data cannot separate those
  two. Either way, it is not a candidate for retirement.

**The site-lane gate is not run on any plant.** None of these plants touches `site/`, so it would not trigger.
**The test gate is run in full.** It is the likeliest second line of defence.

**Predictions, written before any run:**

1. The size-ratchet gate passes its own plant. Its baseline says `rollout_state: warn`, and in that state the
   hook comment says it "does NOT block". Its zero refusals is by design, not evidence.
2. Every one of the other 12 refuses its own plant.
3. At most 4 of the 12 are redundant on their plant. The likeliest are the map-shaped ones, because a map
   edit selects `tests/design/`: scope-evidence, file-scope-generated-paths, consolidation-rhythm (a closing
   level move also trips the level-promotion gate) and moap-coherence. Company-network-isolation is the
   likeliest code-shaped one.
4. The two commons gates are not redundant. Their own hook comments argue that test selection does not reach
   a commons artefact.
5. Status-honesty and ruling-archive-question are not redundant.

## Part B — the remaining stale-copy and site-lane refusals

The 7 Nov sample judged 6 of 58 stale-copy refusals and 6 of 38 site-lane refusals. The rest, 52 and 32, are
judged with the same rubric and the same categories: real, rule, fault, not a refusal, unclear. The judging uses
the event text already extracted to `/var/tmp/gate_review/events.json`, so it does not depend on the transcripts
surviving.

6. Stale-copy: at least 5 of the 52 are real. Each would be a landing that a stale copy would have reverted. The
   guard's whole purpose is that catch.
7. Site-lane: at most 3 of the 32 are real, and at least half are fault.
8. If prediction 7 holds, the site-lane gate becomes the one candidate for a recommendation to the director. It
   would not be retired. The recommendation would be to narrow its trigger or move it off the commit path. That
   decision is his, through `for_the_director`.
