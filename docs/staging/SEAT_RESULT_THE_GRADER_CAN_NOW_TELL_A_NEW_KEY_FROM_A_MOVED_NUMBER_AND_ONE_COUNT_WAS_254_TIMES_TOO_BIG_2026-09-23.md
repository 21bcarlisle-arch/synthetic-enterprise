**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — the Lane 0 direction
`a-regenerated-json-artefact-can-never-be-graded-superseded`, plus two findings it turned up

# The grader can tell a new key from a moved number, and one of its counts was 254× too big

**The work is done.** `refresh_to_head`'s data door no longer answers "supplies N leaves HEAD does
not have" to a regenerated artefact whose every figure moved. It asks the two questions separately
and answers both. Pre-registration for this is
`SEAT_PREREG_THE_JSON_GRADER_REPAIR_2026-09-23.md`, written before any of it was measured; four of
its six predictions held, one was refuted, and the refutation is the more interesting half.

## What was wrong

`stale_copy_refusal._json_leaf_names` names a JSON leaf `keypath=<digest of value>`. That is right
for the question it was cut for — *are these the same document* — because a changed value then
reads as both a name supplied and a name dropped, so no copy with an unlanded edit can be silently
written over. `refresh_to_head.judge_copy` then asked a **different** question of the same set —
*what does this copy hold that the base does not* — as `work_names - head_names`, and called the
answer *"JSON leaves HEAD does not have"*.

An edited number lands in that difference beside a key the base never had. Every value in a
regenerated artefact is edited. So **no regenerated JSON could ever be graded superseded**, and the
verdict it got, `refused_supplies_names_head_lacks`, names `isolate_hunks --keep N` as its remedy —
a door with nothing to select on a document whose every line is a value. Structural, not
incidental. Last stretch made that refusal honest (it said in its own text that it counts the two
alike); this makes it true.

## What changed

- `stale_copy_refusal._json_leaves` — one walk, `key path -> value token`. `_json_leaf_names` welds
  the two halves; `json_leaf_delta` holds them apart. Both readings come off the same walk, so
  nobody can re-derive key paths by splitting name strings — which is correct for every key in this
  repository and silently wrong for the first one containing an `=`. There is a leg for that.
- `stale_copy_refusal.json_leaf_delta` → `LeafDelta(novel, edited, dropped)` over key paths.
- `refresh_to_head.RIVAL_VALUES` — the state `SUPPLIES_NEW` was absorbing. The copy binds no key
  path the base lacks and disagrees about values at keys they both bind. Still a refusal; it now
  names the two real options (land the copy whole with `--content`, or let the base win under
  `--base-wins`) instead of a door that cannot open.
- `Verdict.edited`, rendered `~ key  <- BOTH BIND THIS KEY; THE VALUE DIFFERS`, distinct from
  `gains`'s `+`.

**The branch boundary did not move, and that is deliberate.** An edited key path contributes
`k=<new digest>` to `supplies`, so `supplies` is non-empty exactly when `novel or edited` is.
`--base-wins` reaches precisely the copies it reached before, on the same clock evidence. This
changes what a copy is *told it is*, not what it is *permitted to do*. The consent gate on a door
that destroys bytes is untouched — repairing a grade is not a licence to widen a write.

## The two live copies, before and after

| | value-names "supplied" | key paths it actually adds | values changed | key paths dropped |
|---|---|---|---|---|
| `domestic_shift_response_arc.json` | 5 | **0** | 5 | 2 |
| `self_clearing_alarm_census.json` | 1,778 | **7** | 1,771 | 1,719 |

The second is the refuted prediction. I predicted 0 novel keys there and it holds 7
(`state_paths.*.readers` / `.failure_writers`). So the refusal on that file was *true all along* —
it does hold structure HEAD lacks — and what was wrong was its **magnitude**: 1,778 against 7, a
factor of **254**. On the first file the refusal was simply false. Both failures are the same
conflation; only one of them was visible as a wrong verdict, which is why it took thirteen listings
to land.

## The census, with its composition and the instrument change named

Run over the shared tree `/home/rich/synthetic-enterprise` immediately before and immediately after
the change, same process, same base:

    losses          18 before  →  18 after     (prediction 4 held)
    by rule         predates_landing 6 · predates_landing_by_clock 7 · predates_landing_carrying_some 5
    by suffix       .py 9 · .md/.yaml 7 · .json 2
    skipped         384

**Do not read 18 against the 19 / 20 / 25 / 27 in the neighbouring notes as a trend.** Those were
taken on different tree states with a differently-scoped instrument; this one moved by construction
and the prediction that it would not move was registered before it was run, precisely so a number
that *did* move would be a finding rather than a result. The census count could not move, because
its `.json` rows come from `clock_judge`, which never computed `gains` at all — the repair is in
`judge_copy`'s data branch, which the census does not call.

## The named control did not move

`simulation/premise_population.py` is `.py`, not JSON. Its verdict is byte-identical before and
after in both flag positions: `refused_supplies_names_head_lacks`, 5 genuinely novel Python names,
`isolate_hunks --keep 1 --keep 2` as the door, and `--base-wins` correctly refusing it because a
landable hunk exists. Prediction 5 held. If the repair had moved this, it had leaked.

## Finding 1 — the three files the item names were already spent

The commissioning item cites `svt_drift_belief_grade.json` and the two `ladder_churn_factors*.json`
at 234 / 2,706 / 14,236 "names HEAD lacks". **All three are byte-identical to HEAD on the shared
tree** and have been since commit `cdb1db0ab`; the door answers `already_at_head` for each. The
figures in the item are not reproducible and the instances were spent before the draw. The class
was not, which is why this was still worth doing — but a draw that grades its own pile is the only
reason that was known in the first minute rather than the fortieth.

## Finding 2 — the census still names a permanently shut door for 7 of 18 rows

Not this item's class, recorded because it was measured on the way past and nothing else will see
it. Nine of the eighteen rows name `refresh_to_head` as their remedy. For **seven** of them
(`.md` and `.yaml`) that door answers `refused_no_reader` — by construction, and it can never
answer anything else. This is the same shape `Loss.names_the_refresh_door` was cut for on
2026-09-22, and its docstring records the same count: *"the census printed a door that was
permanently shut for 7 of 21 paths"*. That repair built a **grader** for the mis-naming and did not
close it. The seven are `weather.md`, `ANNUAL_REPORT_IMPORT_DEBT.md`, `A49_...yaml`,
`knowledge_map.md` and three staging results. Either the door grows a reader for prose, or the
remedy for a no-reader suffix stops naming it — but "we can see it is wrong" is not a fix.

## Legs, and the mutation they were proven against

    tests/tools/test_stale_copy_refusal.py
      test_a_changed_value_is_not_counted_as_a_key_the_base_lacks
      test_the_delta_survives_a_key_that_contains_an_equals_sign
      test_the_delta_fails_closed_on_an_unparseable_side
    tests/tools/test_a_json_blocker_...py
      test_the_json_verdict_partition_is_reachable_every_way_on_one_tree_state  (now FOUR-way)

The partition leg is the one that matters. It shipped asserting three states over four document
shapes, which is exactly the reading a two-shapes-one-state collapse is invisible to — it passed
throughout the defect's life. It now asserts four distinct states and, separately, that *supplies a
row HEAD lacks* and *same keys, one value rewritten* are not given the same verdict.

Mutation run: collapsing `if delta.novel:` back to `if delta.novel or delta.edited:` — i.e.
restoring the old undifferentiated verdict — reds five legs across the two files, the new partition
control among them. The four legs that pinned the old state string were repaired to the new one
rather than deleted; each keeps its destructive byte-check (the edit survives the refusal)
*above* the state assertion, because that is the property and the state name is today's answer.
