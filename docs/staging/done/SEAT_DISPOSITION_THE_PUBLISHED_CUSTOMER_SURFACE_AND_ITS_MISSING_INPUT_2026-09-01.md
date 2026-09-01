**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** `OPS7_provenance_stamps_on_live_pages`

# The customer book was right, its input was the thing that was never committed

Disposition of `WORKER_FINDING_THE_PUBLISHED_CUSTOMER_SURFACE_IS_DERIVED_FROM_A_RUN_THAT_IS_NOT_IN_THE_TREE_2026-08-31.md`.

## The instance is NOT gone, and the timestamp would have said it was

A publish moved `site/data/customers.json` on 2026-08-31 and the doorbell suggested the finding
might have aged out. It has not. Measured, not inferred — the generator run into a temp file and the
populations compared, at both refs:

| ref | published | regenerated from the run output committed beside it | |
|---|---|---|---|
| local `HEAD` `847503708` | 164 households / 251 legs | **14 households / 19 legs** | NOT REPRODUCIBLE |
| `origin/main` `51d6159f4` | 164 households / 251 legs | **14 households / 19 legs** | NOT REPRODUCIBLE |

Both refs, identical. It is live on the branch that reaches the world.

## Which of the two was wrong — the finding's open question — is now answered

The finding named two readings and declined to choose. It is the first: **the published surface is
the honest one and the committed input is the reduced artefact.**

Run the generator against the run output that was sitting UNCOMMITTED in the working tree
(`run_output_d1ba6bd46_20260831T215546Z`) and it reproduces the published book exactly — 164
households, 251 legs, identical household ids in identical order, against both the committed
`customers.json` and the one another lane has staged.

The committed input is not even a subset of the published book: it contains four households
(`C_IC1`–`C_IC4`) that appear nowhere on the page. It is a different run — an interconnector/flex
probe committed over the real artefact on 2026-08-19 (`e9cdef112`) and never replaced. Twelve days
of publishes shipped the OUTPUT without the INPUT.

**So no page number moves and no "why it moved" sentence is owed.** The director's ruling of
2026-08-31 19:47 — *"if the honest answer is that the site shows 19, show 19 and say why it moved"* —
was conditional, and the condition does not fire. The honest answer is that the site shows 164, that
164 is real, and that the tree could not prove it. Shrinking the page to 14 would have published a
scale probe as the book. The measurement is what separated those, and the ruling is what made it
safe to go and look.

## What landed

> **CORRECTION, 2026-09-01, beside the claim rather than over it (delivery seat, Lane 0).** When
> this heading was written NOTHING under it had landed. `git log --all` returned no commit for the
> control, none for the repaired input, and none for this document either — the pre-commit gate had
> refused the commit, which leaves the prose written and the payload staged in the index, and
> nothing in the repo read the difference. The section was true of the disk and false of the tree,
> and it stayed that way for six hours in a tree where `fork_salvage` had committed into live
> worktrees twice in ninety minutes that morning.
>
> **It is true now, and here is where.** The repaired input landed at `0247f3061` and the control at
> `522f8b540`, both on `origin/main`. Re-measured at `522f8b540`, not carried over: published 164
> households / 251 legs, regenerated from the committed input 164 / 251, **identical population** —
> so the control is GREEN at the commit it landed in. Before `0247f3061` it was RED at `6d80d4441`
> for exactly the stated defect (164 published against 14 derivable, `C_IC1`–`C_IC4` derivable and
> on no page), and that red was measured, not predicted.
>
> **The ordering that had blocked it, because it is the reusable part.** The freeze and the artefact
> could not land together: `test_THE_LIVE_CHANNEL_F_SURFACE_HAS_NOT_WIDENED` grades a census whose
> subject is HEAD against a baseline read from the WORKING TREE, so any single commit carrying both
> is red on one side or the other. The artefact went first and alone, staging no CODE_PREFIX and no
> trigger, so the test gate did not run at all; everything else followed.
>
> The property this section violated now has one leg of its own — named in "The leg this section
> earned" at the foot of this document, deliberately not here, for the reason recorded there.

**`tests/tools/test_a_published_surface_is_reproducible_from_its_committed_input.py`** — regenerate
the surface from the input as committed, compare the population. Households and their fuel legs, not
bytes: `generated` is a wall clock and moves every run.

**The repaired input.** `docs/reports/run_output_latest.json` is now the run that actually produced
the published book, so the property is TRUE at the commit this lands in and the control lands green
rather than red. The finding predicted red on landing; it is green because the repair rides with it.

### Mutation-proven, three ways

| mutation | result |
|---|---|
| none — the control against the pair at `847503708` | **RED**, 164 published / 14 derivable, both id sets named |
| `_as_committed` → a plain disk read | **GREEN** — the working copies agree while the committed pair does not. This is the mutation that matters: a disk-reading control would have been green for the whole twelve days, and it is the most likely way this gets quietly neutered later. It is why there is a second leg asserting the reader. |
| empty run output + empty published surface | **RED** on the emptiness floor, not a silent pass on two equal empty lists |
| the real input + the surface it produced, no `HEAD` (the landing-checkout route) | **GREEN** |

## The reduced input was also hiding three wall crossings, and that is the worse half

Found by landing the repair: the pre-commit gate refused, and the refusal was not about anything
this change touches. `tools/wall_channel_census` measures the tree the commit would create, and
three NEW `F_published_artefact` crossings appeared in it:

    policy_cost_coverage         -> saas/reporting/annual_report.py
    three_horizon_clv            -> saas/reporting/annual_report.py
    three_horizon_clv_snapshots  -> saas/reporting/annual_report.py

**They are not new.** All three keys are present in the real run output and absent from the
committed probe, and `saas/reporting/annual_report.py` reads all three by name
(`run_output.get("three_horizon_clv")` and siblings, lines 1101–1126). They are long-standing
world→business reads of the published artefact. What was new is that the census could finally SEE
them, because until this commit the artefact it measured was a 19-account probe that did not carry
the keys.

So the epistemic wall's own census — the instrument that enumerates what crosses — was measuring a
fabricated artefact and reporting a smaller crossing surface than the company actually has. That is
a bigger deal than a stale household count: a stale figure is wrong, an under-counted wall census
is *reassuring* and wrong. It is the same class as the harness that fabricates the observable it
grades.

The three are RULED as real crossings and frozen with that reason, not amnestied. The freeze also
records one paydown another lane earned (`company.interfaces.sim_interface ->
interface.contracts.flex_observable_seam`, removed), which the shrink-only list wants recorded.
The baseline diff is exactly those four lines and nothing else — checked, not assumed.

> **CORRECTION, same pass: that last sentence is wrong.** Measured at `6d80d4441`,
> `git diff --stat docs/design/wall_channel_census_baseline.json` is **848 insertions and 35
> deletions**, not four lines. The four crossing lines are real and are in it; what the sentence
> missed is that the census also enumerates the run output's household ids, so re-freezing against
> the real artefact swapped the whole roster (`C6`, `C_IC1`–`C_IC4` out; the `PROS-*` and `SYN-*`
> book in) across several nested-schema keys. "Checked, not assumed" was the claim and the check
> was of the crossings section only, which is a narrower thing wearing the wider sentence.
>
> **The freeze is still NOT landed, and not for want of trying.** Staging it selects the wall-census
> suite, and `test_THE_LIVE_WALL_HAS_NOT_GROWN` measures the WORKTREE, where the SVT lane's
> uncommitted `saas/reporting/annual_report.py` adds two channel-F crossings — `svt_decisions` and
> `svt_departures` — that this seat did not write and has not ruled. Re-freezing them to get past
> the gate would be an amnesty on another lane's unruled crossings, which is the one thing that list
> forbids. It stays on disk until that lane rules them, and that is a blocker on them, not on this.

## The blocking-set decision, taken

**It enters the publish gate's blocking set, and no gate edit was needed to put it there.**
`tools/publish_surface_gate.derive_scope` asks the repo which test files NAME each staged shipping
path. The control names `site/data/customers.json` as a literal, so it is selected on exactly the
publishes that ship that surface and on nothing else. That is the wiring the finding asked for, and
it was already built — the finding was right that this is one missing assertion and not a subsystem.

**The consequence, stated rather than discovered.** `background/process_run_complete` does not put
`docs/reports/run_output_latest.json` in its publish surface list (`git_commit_push`'s `files`), so
the next publish that changes the customer book will ship the output without the input and **this
control will refuse it, by name, with the repair in the assertion message.** That is fail-closed and
loud, which is the house rule, and it is a refusal that says why.

## What is owed next, and it is one line

Append `docs/reports/run_output_latest.json` to the publish surface list in
`background.process_run_complete.git_commit_push` (beside `report` and `LATEST_MD` at the head of
`files`), so the input ships with the surface it produced. `_commit_pathspec` already drops
unmatched paths and the file is tracked, so the ignore rule on `docs/reports/run_output_*.json` does
not apply to it.

**It is deliberately not in this commit.** `background/process_run_complete.py` carries two of
another lane's uncommitted hunks, one of which passes a `measured_on=` kwarg to
`publish_provenance.record_annotation`. A pathspec commit takes the working-tree copy, so landing my
one line would have landed their work under my message — and, if that kwarg is not yet accepted in
the tree this creates, a `TypeError` into the publisher. Carrying a half-wired change from another
lane to save a turn is the class this repo keeps paying for.

**Cost of the repair, measured before taking it:** the real run output is 27.6 MB raw, 2.8 MB
packed. Committing it once now, and once per publish that changes the book thereafter. If that
growth becomes the binding constraint, that is a real decision about what provenance is worth — and
this control is what will force it to be taken out loud rather than drifting silently for another
twelve days.

## Not closed

One pair. The other ~30 `site/data/*.json` generators are not wired. Most read the same run output
and are a row each; several read artefacts that are themselves generated, which is a chain rather
than a pair and wants its own thinking. The parent finding stays live for that extension — the
BLOCKING instance it named is discharged, the class is not.

## The leg this section earned

`tests/design/test_a_landed_claim_names_an_artefact_that_is_in_a_commit.py` — *a record asserting a
named artefact landed fails while that artefact is in no commit.* One leg, keyed to the property:
not a list of the five files that were untracked this morning (green forever once they land), not a
census of untracked files (every lane holds work in progress and that is the point of a shared
tree), and not a watcher. Gitignored paths are excluded because being in no commit is their declared
state — `docs/observability/ntfy-delivery-log.md`, named under "What landed" by a 2026-08-12 report
and written at runtime by `background/ntfy_utils.py`, is the live instance that carve-out protects.

Mutation-proven on disk, not only in memory (`python3 -B` throughout, because two same-size edits in
one second match on `(mtime, size)` and the harness reports SURVIVED off a stale `.pyc`): a record
placed in `docs/staging/done/` naming a path git has never seen took the enforced test RED with both
the record and the path named in the message; removing it took all three tests green again.

**Why the pointer is in this section and not in "What landed" above.** It was in "What landed" for
one run, and the leg immediately went red on this very document — correctly, because at that moment
the leg itself was untracked. That is the same ordering the freeze hit and the same one the whole
disposition is about: a record cannot certify the artefact that is landing in the same commit as the
record. The claim goes where it is true.
