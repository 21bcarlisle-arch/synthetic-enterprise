**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# RESULT — the alarm document is no longer its own state store; the nine collisions are still there, deliberately

**Landed as `dd7c9c2e7`** — `background/alarm_repetition.py`, `.gitignore`,
`docs/observability/substring_source_scan_baseline.json`, and
`tests/background/test_clearing_an_alarm_document_must_not_destroy_its_history.py`, bound to the
claim. Verify with `git show dd7c9c2e7:background/alarm_repetition.py | grep ALARM_STATE_FILE`
rather than this note's word for it — a result note describing its own landing proves nothing.

Drawn as `separate-the-repeating-alarm-state-store-from-its-published-staging-document` (Lane 0
delivery, 2026-09-24). Grades and continues
`SEAT_RESULT_THE_ALARM_ABOUT_THE_TREE_NOT_ADVANCING_IS_WHAT_STOPS_THE_TREE_ADVANCING_2026-09-24.md`,
which established the loop and named the obvious fix as the wrong one.

## What the item asked, and what it got

> *Give `background/alarm_repetition.py` a state store on an UNTRACKED path and derive the
> `docs/staging/WORKER_FINDING_REPEATING_ALARM_*.md` document from it, so clearing the document is
> lossless.*

Done. `docs/observability/.alarm_repetition_state.json`, `.gitignore`d beside
`.notify_transitions.json`, keyed by **document stem** — the filename with its filing date stripped,
which is exactly the identity `_live_finding_for` already treats as one condition. The document is
now a rendering: `document_counts`, `last_observed` and `last_attention` answer from the store
unioned with whatever the rendering still carries, and `escalate()` replays the store's dated lines
into a document it has to re-create.

**The measurement that says it worked**, run against the live population at seeding:

| | |
|---|---|
| documents absorbed | **11** |
| family members recorded | **176** |
| earliest observation retained | **2026-09-15** |
| documents whose store answer ≠ their document-only answer | **0** |

That last row is the migration invariant and the reason this is safe to land: the store is a
SUPERSET of the documents, and today it is an *identical* superset. Nothing was reinterpreted.

## The four decisions inside it, and why each went the way it did

**1. The seed is a merge, not a migration script.** Every document filed before the store existed
absorbs itself the first time anything touches it. There is nothing to run and nothing to remember,
and a document filed after it re-seeds harmlessly because union with what you already hold is the
identity. `_refresh_counts`'s third placement branch was the precedent: a branch that only runs
during a migration is dead code the day the migration finishes.

**2. Reading seeds, and that is the one place in the module where a read writes.** The alternative
— seed only on the next FIRING — leaves a window per family in which clearing still loses history,
and the window is as long as that family's cadence. The direction this fails in is a redundant write
to a file nothing merges.

**3. `_write_state` carries `escalate()`'s pytest guard, not a similar one.** The split opened a
SECOND door into the real tree that the original guard did not cover: merely *counting* a real
document would have written the live store. Under pytest against the real staging directory the
readers now stay pure and answer from the document alone — which is the old behaviour exactly, so
no test can be made to pass by the seeding.

**4. `_close_episode` is the one forgetting path, and it is not subtraction.** `escalate()`
deliberately does not search `done/`: a condition returning after archival is a NEW episode and an
R3 two-strike signal. The store has to make the same cut or the returning document's header would
claim continuous observation across the gap — the same error arriving through the store instead of
through the filename. The closed episode is kept *beside* the live entry, because the second strike
is only legible against the first.

## THE COLLISION IS STILL THERE, AND THAT IS THE DECISION, NOT AN OMISSION

Nine tracked documents are still ` M` against origin's own copies of themselves, and
`advance_shared_tree` still refuses the fast-forward. **This commit does not clear them and does not
add the stem to the generated-paths oracle.** The prior finding's central argument is why:

> The published artefact IS the state store. There is no `.json` behind it. Clearing the file does
> not lose a regenerable rendering, it loses the alarm's entire history.

That sentence is now false, which is the whole point — but it became false **in this commit**, and
permitting the clear is a different act from making it lossless. Doing both at once would mean the
first live application of the losslessness claim was also the act that destroyed the only copy of
what it was protecting. The order is: make it lossless, prove it, *then* permit.

**The next increment, named precisely** so nobody has to re-derive it. The deadman's own log states
the blocked leg:

> advance: **6 of 11 blocking path(s) could NOT be proven lossless**, so clearing the 5 that could
> would touch files and still not advance.

`origin_reconcile._split_generated` classifies `WORKER_FINDING_REPEATING_ALARM_*` as *authored*
("holder work"), which is what makes them unclearable. With the store landed, that classification is
now **wrong on the facts** and the next turn's work is to change it and re-measure the blocking set.
The exit test is available and cheap: the nine dirty documents clear, the tree fast-forwards, and
the next firing of each family rebuilds its document with the same counts it carried before.

## The gate refused twice and both refusals were right

Written down because the first was a shape worth keeping and neither was a lint.

**1. `test_live_ledger_guard`'s bound went 56 → 64 and none of the eight was what it looked like.**
The census skips any module whose source lacks the word *observability*; putting the store's path
in this file flipped the **whole module** into the population, dragging in six writers that had
been there all along and were never counted. This is the *silently-scoped guard* shape from the
other direction — the scope filter is a substring, so a module joins or leaves the population on a
word rather than on a behaviour. Exactly **one** of the eight is a genuine live-ledger write.

The fix is the one the control's own message names — widen the guard, not the bound. Every write in
the module now goes through **one door**, `_write_document`, which calls `guard_live_ledger_write`:
a no-op for a staging document, a refusal for the store. Eight scattered `write_text` calls were
eight places to forget it. `_write_state`'s hand-rolled `PYTEST_CURRENT_TEST` check is **deleted**
for the same guard — it recognised one hard-coded path where the guard recognises the whole
directory, so a second store added tomorrow would have been unprotected by a check that looked like
it covered the class. Re-measured against a **clean HEAD extract** and not this tree (which carries
four other lanes): 56, with `alarm_repetition` contributing zero.

**2. The substring-scan floor went stale AND grew** — the delegation shape that file's own prose has
now recorded five times. `_observation_dates` and `document_counts` no longer carry the
read-and-match; `_merged_entry` and `_replay_history` do. Rows swapped **by hand**, net 378 → 378,
never `--freeze`.

## Two of the item's own claims, re-asked

**Its cited evidence file resolved to nothing on disk.** The item names
`docs/staging/records/SEAT_RESULT_THE_ALARM_ABOUT_THE_TREE_NOT_ADVANCING_IS_WHAT_STOPS_THE_TREE_ADVANCING_2026-09-24.md`.
It is absent from this checkout and present at `origin/main` — which is itself an instance of the
defect the item is about, arriving in the draw prompt rather than in a log. Read with
`git show origin/main:<path>`, not `cat`. Every claim it makes was confirmed.

**"55 modules behind" is a boot-sha drift, not a base distance, and it does not reproduce as one.**
Measured here: `git diff --name-only HEAD origin/main` is **25** files, **3** of them in
`background/`. The 55 is `reconcile-watch`'s report of how far each *running daemon's booted code*
trails, which a fast-forward does not fix and only a restart does — the prior finding says so
explicitly, and the item's summary compressed the two into one number. The fast-forward is still
worth having; it is just not what makes the 55 go away.

## The control, and what makes it able to fail

`tests/background/test_clearing_an_alarm_document_must_not_destroy_its_history.py` — 9 tests, all
of which delete the rendering and assert the derived counts survive. Keyed to the PROPERTY, not the
mechanism: not "a store exists", not "the json has these keys", because a control of that shape goes
green the day the mechanism stops working.

`test_MUTATION_without_the_store_the_history_IS_lost` removes the store first and asserts the loss
(5 observed days and 2 members collapse to 1 and 1). Without it the suite would prove only that
`escalate` writes a document. It is also the defect as it stood before this commit, stated as a
passing test — so the record of what was wrong cannot rot away from the record of the fix.
