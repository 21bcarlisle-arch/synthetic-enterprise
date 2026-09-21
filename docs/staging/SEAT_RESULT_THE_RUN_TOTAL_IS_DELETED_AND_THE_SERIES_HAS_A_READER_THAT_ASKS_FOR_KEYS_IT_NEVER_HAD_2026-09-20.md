**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
"run history total is a floor not a total and nothing renders it"

# The run total is deleted, and the series turned out to have a reader that asks for keys it never had

**Delivery seat, 2026-09-20, claim
`run-history-total-is-a-floor-not-a-total-and-nothing-renders-it`. Predictions in
`docs/staging/records/SEAT_PREREGISTRATION_DOES_AN_UNTRUNCATED_SOURCE_OF_THE_TRUE_RUN_TOTAL_EXIST_2026-09-20.md`,
written before the measurement and left uncorrected beside these results.**

---

## 1. The premise, and the duplicate-claim note

**Both cited commits are ancestors of `origin/main` and the premise is NOT spent.** `03dd8c49e`
(the page deletion) and `858f38dd7` (the measurement) are the *evidence* this item stands on, not
the work it asks for. §4 and §6 of `858f38dd7`'s result document filed the surface decision
explicitly and deliberately: *"deleting a published field on my own judgement is the wrong
direction to be decisive in. **Filed.**"* Taking it is this turn.

The duplicate-work note named one live claim — **this item's own id**, reported as already held
because `.seat_work_in_hand.json` is not written by the draw. The fourth consecutive Lane 0 draw to
report itself this way. Not a rival. Carried on.

## 2. The decision: `run_history_total` DELETED, `run_history` KEPT

The asymmetry is the whole result, and it is not the one I expected to be able to justify.

**`run_history_total` is gone from `site/data/dashboard.json`, and `count_run_history_total` is
gone with it.** Censused tree-wide before deleting, not within `site/`: the single line
`"run_history_total": count_run_history_total(),` was the **only** reference to that key in any
code anywhere. Written on every publish cycle, committed on every publish cycle, read by nothing.

**`run_history` stays**, because it has two live readers — see §4 for the second one, which I
predicted did not exist.

## 3. Option 2 was measured and is refuted: no untruncated source exists

The item was right to insist this be measured. It was closer than I expected.

| candidate | verdict |
|---|---|
| `docs/reports/run_output_*.json` | **NOT a ledger.** 7 files, each a whole-simulation output (23–108 top-level keys: `starting_treasury_gbp`, `years`, `per_customer_lifetime`…). Not one run-per-entry. **P1 held.** |
| git history of `run_history.json` | **1041 distinct `git_hash` across 86 committed revisions** — 10.4× the published 100, **and still provably a floor. P2 held, including the "provably" half.** |
| anything else | none. **P3 held.** |

**Why 1041 is provably a floor, not merely suspected to be one.** `858f38dd7`'s revision holds 100
entries of which **100 are new** against the union of everything committed before it. A revision
that is entirely new against all its predecessors means the 100-entry ring buffer **turned over
completely** between commits, so the runs it dropped in between are in no revision and are
unrecoverable. The same shape appears at `6d3e3ec69` (+39 new onto a full file). The gaps are
structural, not statistical.

**So a floor cannot be made into a total by working harder at it.** It can only be deleted or
labelled — and `">=100"` is a label with no reader, which buys nothing, changes the field's type,
and leaves a standing invitation for a future reader to render a floor as a total. The 1041 figure
additionally needs `git`, and `surgical_land` gates an extract with **no `.git`**, so a build-time
recompute would fail closed in exactly the tree where the publish happens. **P4 held; option 3
wins.**

## 4. P6 REFUTED — the series does have a reader outside `site/`, and it asks for three keys the producer has never written

I registered P6 as this turn's refutation condition: *"If a consumer of either field exists that I
have not found — anything outside `site/` that renders, exports or reports it to a human — the
deletion is wrong."* **It fired.**

`tools/generate_shadow_html.py::build_project` reads `dash["run_history"]` and renders a
"Run History" table of git / date / net margin. It survived the 2026-08-20 ruling that deleted
`site/project/`, because the ruling retired the *generator from the publish cycle* and deleted
`site/shadow/` — and left `docs/shadow/` committed.

**And all three of its key reads have always missed.** Measured, not inferred:

| `build_project` read | producer writes |
|---|---|
| `r.get("git", "")` | `git_hash` |
| `r.get("date", "")` | `generated_at` |
| `r.get("net_gbp", 0)` | `net_margin_gbp` |

`append_run_history` has built the entry with those five keys since it was written, and
`extract_run_history` passes them through untouched. So every row rendered
**blank / blank / `£0`**, and `docs/shadow/project/index.html` — committed, and served by
`.github/workflows/`'s GitHub Pages job, which uploads **`docs/` whole** — carries **ten rows of
"£0 net margin"**, last written 2026-08-20 in `cd4da3219`. Verified on the committed bytes.

**This corrects the prior finding beside its claim.** `858f38dd7` §4 concluded *"nothing is wrong
on the live site, since no figure is"*, and the drawn item repeated it: *"no wrong figure is on
the live site, since no figure is"*. **That was scoped to `site/` and it is false for `docs/`.**
Cloudflare Pages serves `site/` (clean — `site/shadow/` does not exist); GitHub Pages serves
`docs/` (not clean). Two roots, one of them checked. It is the same shape the prior finding
diagnosed — a frame built from where the last reader looked — one layer further out.

**Why nothing could notice.** `.get` with a default never raises, and the money column's default
was `0` — a *plausible* figure. The page read as a working page showing a flat run of zero-margin
builds. This is ARM 2 of `tools/structural_blank_guard.py`'s class (`d.get(k, 0)`, substituting on
a **missing key**) on a producer that guard's registry does not cover, because its registry is
derived from the nullable-CLV producer.

**Repaired**: the three key names, and the numeric default is gone — `_gbp(None)` and `_cls(None)`
already render an em dash, so a missing margin now states itself as a blank instead of as a belief
the company does not hold. Printed at real inputs before shipping the control, per the standing
rule: the ten rows now read `ea3de3efe / 2026-09-18 / £157,807` … `87c485285 / 2026-09-19 /
£158,278`.

## 5. The controls, and the mutation each one was written for

`tests/tools/test_the_shadow_run_history_renderer_reads_keys_the_producer_writes.py`, four legs.
Each mutation was run separately so that no leg is credited with catching a defect a different leg
found:

| mutation | legs that fired | legs that correctly did NOT |
|---|---|---|
| key name only (`net_margin_gbp` → `net_gbp`, no default) | the class leg + the instance leg | the blank leg (an absent default still renders `—`) |
| numeric default only (correct key, `, 0` restored) | the blank leg **alone** | the other three |
| `run_history_total` restored to the payload | the payload leg **alone** | the other three |
| `run_history` dropped from the payload | the payload leg **alone** | the other three |

**Keyed to the property, not to today's answer.** The class leg derives the permitted key set from
`append_run_history`'s own `entry = {...}` AST. Add a sixth ledger field tomorrow and the renderer
may read it with no edit here; rename one and this reds. A control listing today's three names
would have gone green on precisely the rename that broke the page. Both derivations **raise** on an
empty result rather than returning it — an empty producer key set would make the membership test
vacuously true, which is the fail-open this class dies of.

**The non-vacuity leg is on the LIVE artefact**, because the other three pass fixtures in and would
all stay green if `run_history` were dropped from `dashboard.json` altogether.

## 6. What the deletion forced elsewhere, and the witness that had to move

`count_run_history_total` had six test sites and seven prose sites. All are repaired; **no code
reference to it survives anywhere in the tree.**

**The witness that mattered.** `tests/background/test_the_census_lost_five_hits_to_the_parameter_
seam.py::test_the_published_run_count_has_a_reader_on_record` asserted the census records
`...::count_run_history_total` as a reader of `run_history.json` — and its own docstring argued
that keying to a *named function* rather than a count was the durable choice. It was not: it
borrowed the state of a live artefact as its witness, and the artefact was deleted. Repointed at
`extract_run_history`, which is genuinely more durable — it is the sole surviving reader on the
publish path **and** its output is separately asserted non-empty by the committed-together control.
Mutation-proven both ways: green on `extract_run_history`, red on the deleted name.

**The fixture that hid the original defect, replaced rather than deleted.**
`test_count_run_history_total_counts_full_history_not_truncated` — whose *name* is a direct claim
about truncation — was green throughout on a **37-entry** fixture, because it pinned the READER
while the truncation is in the WRITER. Its replacement uses **137 entries**, which **straddles the
writer's 100 cap**: a loader that truncated at 100 now reds. A fixture below the cap cannot tell
"read everything" from "stopped at the cap", and that is the whole reason the old one was useless.

## 7. What is NOT fixed, stated plainly rather than left to be discovered

**The £0 rows are still on the served page after this commit.** The renderer is repaired, but
`generate_shadow_html` was retired from the publish cycle on 2026-08-20, so nothing regenerates
`docs/shadow/project/index.html`. The repair is **inert on the published bytes** until someone
disposes of `docs/shadow/`. Reachability, measured: `docs/index.html` does not link to it, but
`docs/shadow/index.html` links `/shadow/project/`, so the mirror is self-navigable once entered by
URL. That is why this is graded LATENT and not BLOCKING.

**Two dispositions are open and I am recommending, not taking, one.** (a) Delete `docs/shadow/`,
which *completes* the 2026-08-20 ruling — its own retirement comment objects to "an INTERNAL
surface that was nonetheless published at a second root on the public site, carrying the full
internal vocabulary — exactly the hidden page the ruling is about". (b) Regenerate it, which acts
*against* that stated intent. **I recommend (a).** I have not taken it because the ruling's author
deleted `site/shadow/` and left `docs/shadow/` in the same commit, and I cannot tell from the tree
whether that was intent or oversight — and it is a public-surface deletion, which is the direction
the prior seat correctly declined to be decisive in. Handed off.

**CORRECTION, written beside the claim rather than replacing it.** This section first said the
two HEAD-reds below were *"carried, not absorbed"*. **That was wrong and they are fixed in this
commit** — not by a change of mind but because the plan was impossible: a changed test file selects
itself, and the witness repair in §6 *must* be in this commit, so its file's other leg had to run.
The original measurement stands — both were red at HEAD in a clean `git archive` extract and
neither is reachable from the run-history diff — and the conclusion drawn from it did not.

**`test_a_files_contents_never_become_an_alias_of_its_path`** — a real defect in
`self_clearing_alarm_census._scan_module`. `raw = p.read_text()` fails the `_is_path_shaped`
screen (correctly) and then falls into the branch that handles what that screen rejects, which
records the target as an *unresolved call candidate*. So `raw` became a path descriptor and
`other(raw)` was kept as an edge — **the exact taint `_is_path_shaped` exists to stop, arriving
through the branch that handles its rejects.** Fixed by settling it where it is already known: a
callee in `_READ_ATTRS`/`_WRITE_ATTRS` is not an unknown at all — `read_text()` yields contents,
decided by the attribute's own name, with no callee return shape to resolve.

**`test_every_live_hit_is_dispositioned`** — `.delivery_lane_claims.json` was the last
undispositioned live hit, reddening this leg for **every** lane. Dispositioned `real` /
`guarded`: `claimed_at` *is* an episode-start timestamp, `sweep_stale` read-modify-writes the
store its own sweep reads, and the shortening **was live** — `claimed_at` is rewritten by every
draw, so a re-drawn id's already-satisfied commit became unbindable forever (measured twice:
`wire-the-sourced-acquisition-and-retention-costs` / `0850eadcd`, re-drawn 8m39s later). The close
condition is independent of the file, per R15: the id's **first** draw, remembered in
`DRAW_LEDGER_FILE` across releases. Fixed 2026-08-28.

**And my first draft of that row was itself the trap the registry warns about.** I wrote that the
store gets "the same repair the sweep applied to `seat_work_in_hand.claim`/`.release`" — a
`_scope_of_resemblance` deferral, *"an unopened row that reads as asked-and-answered"*. Checked
rather than left asserted: `delivery_lane` binds `claims_mod = background.seat_work_in_hand` and
passes `CLAIMS_FILE` as the **path argument**, so it is not a file shaped like that one, it is
**that module with this path** — which is also precisely why it is a parameter-seam carrier. The
row now says the stronger, true thing.

**The nineteenth censused subject.** This turn's new control is a whole-directory-subject test
(`site`, `tools`), so `test_the_strict_census_stays_discharged` refused the commit that wrote it
and named the remedy. Registered in `CENSUSED_WHOLE_DIRECTORY_SUBJECTS` with its **measured** cost
(4 tests, 0.68/0.78/0.70s over three runs), which is that control working exactly as its own
comment predicted: refused at the commit that makes it, not found a fortnight later.

**`docs/observability/self_clearing_alarm_census.json` still records
`generate_dashboard_data.py::count_run_history_total` as a reader.** It is a generated snapshot,
no gate compares it to a live derivation, and it is rewritten whenever the census next runs.
Deliberately not hand-edited: editing a generated class register by hand lands whatever stale bytes
the working copy holds.

**`PROJECT_OVERVIEW.md`'s two lines about the "Sim runs" KPI** are left as written, as `858f38dd7`
left them — phase history, a record of what was believed on the day, with the correction beside
them here.

## 8. The predictions, against the results

| | predicted | measured |
|---|---|---|
| **P1** `run_output_*` viable | no | **no** — 7 whole-run outputs |
| **P2** git union > 100, provably a floor | yes / yes | **1041, and provably** |
| **P3** no untruncated source | yes | **yes** |
| **P4** decision is option 1 vs 3 | yes | **yes, and 3 wins** |
| **P5** delete the total, keep the series | yes | **yes — and the reason to keep the series was stronger than the one I gave** |
| **P6** no consumer outside `site/` | **refuted** | **`generate_shadow_html.build_project`, reading three keys that have never existed, publishing ten `£0` rows to a served page** |

P5's stated confidence was "high" that the day-old control reads the series. It does, with an
explicit non-vacuity assert. What I got wrong is the part I was most confident about: I wrote that
I would "census the whole tree, not `site/`, because §4 of the prior result is precisely the story
of a frame built from a comment about a surface" — and then registered a prediction that the census
would find nothing. **The census was the right instrument and the prediction attached to it was
wrong, which is the only reason the £0 page was found at all.**
