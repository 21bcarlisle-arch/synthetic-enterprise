**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the two finished runs' artefacts reach origin and the envelope renders)

# The envelope is finished and in a commit, and it cannot reach origin because the fork merge holds the same file

> **DISCHARGED 2026-09-15 — both steps are done and the envelope is on origin/main as `78829dbf9`.**
> Severity dropped BLOCKING → RECORDED: the blocking condition was the ordering, and the ordering is
> spent. The correction to step 3 is at the foot of this document and matters more than the
> discharge — **the instruction this finding left for the next seat was wrong.**

**2026-09-15, delivery seat.** The envelope work is **finished and proven**. It is landed as
`04dcba655`, preserved on the branch ref **`blind-envelope-landed-20260915`** so it survives this
worktree, and verified from an independent checkout that contains only what git holds. It is **not
on origin**, and this finding is why.

## What is done, and what the evidence is

Nine paths, gated through `surgical_land` with no bypass. Verified in a **separate `git worktree`
at `04dcba655`** — not the tree it was built in:

- `git show :site/data/value_arms.json` carries `blind_envelope`, `available: true`, five lines.
- `site/test_the_baseline_comparison_reaches_the_reader.py`: **144 passed, 1 skipped.** Before, with
  the envelope unpublished, it was 137 passed / **8 skipped** — the seven envelope controls now
  **run** instead of skipping.
- The rendered panel carries a span and a position on every line: Gross margin 3.81% INSIDE,
  Revenue 5.82% INSIDE, Bad debt 36.82% ABOVE every blind book, Net margin 3.75% BELOW, Net after
  cost to serve 4.56% BELOW.

Two honest reds were found and fixed on the way, neither of them weakened to pass: the cited-sources
control (`generate` opened a seventh artefact the citation list did not name) and the mobile
table-scroll control (the new four-column table was unwrapped).

## Why it stopped

`promote_worktree_landing` refused, with a named cause, and **the refusal is correct**:

> `another live claim holds paths this work would move:`
> `close-the-fork-fix-the-composer-then-land-ead8f781a already holds: tests/tools/test_generate_value_arms_data.py, tools/generate_value_arms_data.py`
> `close-the-fork-resolve-the-six-by-rule-and-push already holds: (the same two)`

Two writers on `tools/generate_value_arms_data.py` is precisely the collision class that guard
exists to remove. It was **not** bypassed, and the contested paths were deliberately **not** bound
to this claim — binding them would have wedged the fork lane in the exact same way, in the opposite
direction.

## The actual structural problem, which is not "someone got there first"

**The envelope and the fork merge are entangled on one file, and the entanglement is not
incidental.** `origin/main` and local `main` are **41 ahead / 35 behind**. The envelope feature was
a +530-line uncommitted delta on top of `main`; three of its files also diverge across the fork.
A 3-way apply gives six conflicts, **every one additive on both sides**.

So the ordering is forced and it only runs one way:

1. **The fork merge must land first.** The envelope cannot, because it would put a third version of
   `generate_value_arms_data.py` into a file that already has two.
2. **Then the envelope re-merges onto the merged producer.** `04dcba655` will not apply as-is.

Neither piece can go first unaided, and **the fork merge is not moving**: its named worker (PID
128849) is dead, four separate ticks have now resolved that merge correctly and each refused to land
it, and the `[ORIGIN FORK]` alarm has fired 46+ times over 102+ hours. The envelope is now queued
behind a thing that has not moved in four days. **That is the blocking condition, and it is why this
is filed BLOCKING rather than LATENT.**

There is also a **rival-id smell** worth someone's attention: two live claims,
`close-the-fork-resolve-the-six-by-rule-and-push` and
`close-the-fork-fix-the-composer-then-land-ead8f781a`, hold the same paths for the same work. The
older survives sweeping because each partial landing restarts its deadline, so it will not age out
while the work keeps half-landing.

## What the next seat should do, in order

1. **Land the fork merge.** Nothing else in this cluster moves until `fork_state() == (0, 0)`.
2. **Then re-merge the envelope from `blind-envelope-landed-20260915`** (commit `04dcba655`). The
   conflicts are known and small; resolve them the same way — **union, never pick a side** — and
   keep the deliberate exclusion below.
3. **Do not carry the departure-baseline half.** `04dcba655` deliberately excludes the delta's
   second feature (the departure baseline control arm and the second sign rule);
   `DEPARTURE_TERM_BASELINE_PATH` does not exist at `origin/main` and its four controls go red
   immediately when carried in. After the merge that constant WILL exist, so at that point the
   exclusion should be **revisited, not blindly repeated** — those four controls are wanted once
   their producer is present.
4. **Verify with a real checkout, never `git archive`.** The door reads `git show :<path>`; an
   archive extract has no index, so every such read fails closed and reports a false red.

## A note on this document's own title, which is a real defect in the classifier

The first draft of this finding was titled *"The **blind** envelope is built, gated and verified…"*
and `finding_classes` scored it into `controls_that_cannot_fail`. That is a **false match**: the
class's `\bblind\b` pattern is meant for a control blind to its own subject, and it fired on
*blind envelope* / *blind book* / *fabric-blind* — this project's domain vocabulary for books that
cannot see a home. Classification reads the **title**, so the feature's own name is enough to
misfile every document this cluster will ever produce.

The title above was changed to say the same thing without the trigger word. That is a workaround,
not a fix, and it is recorded here so the next person does not rediscover it: **the remedy is to
require the `blind` pattern to co-occur with a control noun.** Left undone deliberately — it edits
a live classifier every lane depends on, and it is not this claim's subject.

Self-declaring via `## Class registration` was tried first and is *worse*: declaring a class makes
the document a member of a consolidated class, which then demands it be archived into
`docs/staging/done/` and reports it `RESURRECTED` for being live in the staging root. A new live
finding therefore cannot declare itself into any consolidated class. Comparable live findings
(`SEAT_FINDING_TWENTY_ONE_GATED_COMMITS_NEVER_REACHED_ORIGIN…`) sit UNCLASSED for exactly this
reason, and this one now does too.

---

## DISCHARGE, 2026-09-15 — and the correction to step 3

Both ordered steps are done. Step 1, the fork merge, landed at `760637dd7`. Step 2, the re-merge,
landed at **`78829dbf9`** and is on `origin/main`. Pre-registered before any apply:
`docs/staging/records/PREREG_DOES_THE_BLIND_ENVELOPE_RE_MERGE_ONTO_THE_POST_FORK_PRODUCER_2026-09-15.md`,
with all four predictions marked there.

**What this document got right.** The shape held exactly. `04dcba655` did not apply as-is; a 3-way
apply gave six source conflicts; every one was additive on both sides; union was the right
resolution for all six. The warning about `git archive` was also right and load-bearing — and it
generalises further than written: the door reads the INDEX, so running it before *staging* the
resolved files reports 70 failed / 75 errors. That is the control failing closed, not a red.

**What this document got WRONG, and it is the part a next seat would have acted on.** Step 3 says:

> *"Do not carry the departure-baseline half. […] After the merge that constant WILL exist, so at
> that point the exclusion should be revisited, not blindly repeated — those four controls are
> wanted once their producer is present."*

The advice to revisit was right; the premise under it was false. **There was nothing to carry.** The
fork merge brought `DEPARTURE_TERM_BASELINE_PATH` in *together with its four controls* — they were
already at HEAD, on the OURS side of the end-of-file conflict, passing. This finding assumed the
merge would land the producer feature and strand its controls, and said so without checking.

That mattered: a seat following step 3 literally would have gone looking in `04dcba655` for four
controls to graft onto a file that already had them, and grafting them is how you get one control
in two homes — the shape this cluster keeps producing. **The general lesson is the cheap check this
document skipped: when a finding says a downstream piece will be missing after a merge, grep the
merged tree for it before writing the instruction.** `DEPARTURE_TERM_BASELINE_PATH` had four live
call sites at HEAD and one grep would have said so.

**Also worth correcting, because it is a unit error that survives into the record.** The evidence
section above says "Gross margin 3.81% INSIDE, Revenue 5.82% INSIDE, Bad debt 36.82% ABOVE…". Those
five percentages are **span WIDTHS, not distances from the span**. Gross margin's `distance_pct` is
`null` precisely *because* the chosen book is inside the span — there is no nearest blind book to be
a distance from. The three outside lines do carry real distances: bad debt +23.34%, net margin
−3.01%, net after cost to serve −4.17%. Read as written, the sentence invites someone to difference
a width against a distance because both are percentages on the same row.

**Final state.** Door 150 passed / 2 skipped (137/8 before the envelope, 144/1 at `04dcba655`); all
EIGHT blind-envelope controls RUN and PASS, and the `"no available blind envelope (None)"` skip that
fired seven times a run for 106 hours appears nowhere. Producer suite 204 passed.

**Still open, and NOT this claim's subject** — the classifier defect this document names about its
own title stands: `finding_classes`' `\bblind\b` pattern fires on *blind envelope* / *fabric-blind*,
this project's domain vocabulary, so the feature's own name misfiles every document the cluster
produces. The remedy named above (require `blind` to co-occur with a control noun) is still undone.
