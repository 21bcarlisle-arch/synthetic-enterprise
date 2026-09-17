**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — disposition the launch register in the self-clearing-alarm census)

**Discharged:** 2026-09-17, lane 0 delivery — all three judgements this finding names are built and mutation-proven. Falsifiers: `tests/background/test_an_unreadable_launch_register_is_never_an_empty_board.py::test_every_prior_the_register_can_be_in_is_REACHABLE`,
`tests/background/test_an_unreadable_launch_register_is_never_an_empty_board.py::test_a_relaunch_over_an_unreadable_register_PRESERVES_the_bytes_it_rebuilds_over`,
`tests/background/test_an_unreadable_launch_register_is_never_an_empty_board.py::test_check_REFUSES_an_unreadable_register_rather_than_reporting_a_clean_board`,
`tests/background/test_an_unreadable_launch_register_is_never_an_empty_board.py::test_the_deadman_PAGES_on_an_unreadable_register_and_never_clears_the_alarm`,
`tests/background/test_an_unreadable_launch_register_is_never_an_empty_board.py::test_an_EMPTY_REGISTER_is_a_clean_board_and_an_EMPTY_FILE_is_not`

**What was built.** `background/launch_liveness.load_register` is the honest reader — `episode_prior`'s
partition, `item_type=dict`, so a PARTLY-right register is UNREADABLE and not readable-with-junk;
`load` keeps its lossy signature and its docstring now names the four callers for which that is
correct and the two for which it is not. `record` preserves the bytes before the rebuild and the
row it writes carries `prior_register` saying where they went, so a reader of the register can see
the loss. `check` raises `RegisterUnreadable` rather than returning the clean board, and
`deadmans_switch._check_launch_liveness` has an explicit branch that PAGES on its own standing-condition
key instead of reaching `clear_transition`. `unregistered_live_units` was already correct and is
untouched, as the finding asked.

**Two things this turn found that the finding did not say, recorded beside it rather than folded in.**
(1) `launch_liveness.UNREADABLE` — a PROBE verdict, meaning `systemctl` could not be run — and
`episode_prior.UNREADABLE` — the REGISTER FILE's verdict — are both the string `"unreadable"` and
would have compared equal. The import is aliased `PRIOR_UNREADABLE` so no later edit can conflate a
broken probe with a broken file. (2) The repair made an existing control in
`tests/background/test_launch_liveness.py` go red *because the code became more honest*:
`test_a_death_and_a_completion_in_one_pass_both_get_their_own_route` asserted `not cleared` over
EVERY key the cycle touches, and the new register key is correctly cleared on the same pass. Its
property was always about the death's own key, so it now names `_LAUNCH_LIVENESS_KEY` — the shape
the `_LAUNCH_LANDED_KEY` leg two functions below already used. Re-proven against the defect it was
written for. Two sibling assertions had the same coarse shape and were narrowed with it, because
after this change `assert cleared` would have passed on a cycle that never cleared the liveness key
at all — a fail-open my repair would otherwise have introduced into a control it did not touch.

# The launch register's loader reads five different priors as "no launches", and the next `record()` writes the rest of the register away

**2026-09-16, scheduled tick, worker seat.** Found while writing `.launch_records.json`'s row in
`docs/design/self_clearing_alarm_dispositions.json`. The disposition itself is `benign` and that is
correct — it answers the episode question, and the episode question is not where this path's harm
is. Filed rather than fixed: `background/launch_liveness.py` is under live uncommitted edit by
another lane at this hour, and rewriting the function they have open would sweep their work.

## The reading

`launch_liveness.load` is, at HEAD:

```python
try:
    resolved = Path(shared_tree_live_record(path or RECORDS_PATH))
    data = json.loads(resolved.read_text(encoding="utf-8"))
except Exception:
    return []
return data if isinstance(data, list) else []
```

Five distinct facts collapse to one answer, and it is the flattering one:

| prior | `load()` |
|---|---|
| ABSENT — no file | `[]` |
| EMPTY — zero bytes, the signature of an interrupted write | `[]` |
| TRUNCATED | `[]` |
| `null` — parses, so no `except` ever sees it | `[]` |
| a non-list object | `[]` |

**That sentence is not mine.** The function's own docstring, written the same day by the
shared-tree redirect, already says it: an empty `except` returning `[]` makes an unreadable file
"indistinguishable from `no launches`: the flattering answer twice over". The redirect repaired the
PATH and left the `except` exactly as it was, so everything below is invariant to that lane landing.

## What it costs, run rather than reasoned

Measured against a clean extract of `2ec310fd8`, on a temporary path, with a `live` record for
`longjob-A` on disk and the file then truncated:

```
record('longjob-B')   ->   file holds ['longjob-B']      A survived: False
                           bytes preserved anywhere?     NO
```

`record` is load → drop-by-job → append → save. On an unreadable prior it does not fail, does not
warn, and does not keep the bytes: it writes a one-element register over whatever was there. Every
other launch record is gone, including any `live` claim.

**A destroyed `live` record is a claim that can never be contradicted** — which is the single thing
this module exists to abolish. Its own header counts four launches of one job whose "the run is in
flight" sentence stood for hours because nothing in the architecture could re-ask it.

## The instrument that is wrong, which is why this is BLOCKING

`check()` is the same read-modify-write, and on a truncated register it returns `stale=0`. That is
not "we could not tell"; it is the clean board. Its caller, `deadmans_switch._check_launch_liveness`,
then takes:

```python
if not stale:
    clear_transition(_LAUNCH_LIVENESS_KEY)
    return
```

So the register losing its own contents reads, all the way to the alarm, as every launch accounted
for. `check()`'s docstring is careful in exactly the neighbouring case — it refuses to settle a
claim on UNREADABLE or UNKNOWN because "we could not tell" is not permission to overwrite what the
launch said — and the loader one frame below hands it an emptiness it cannot tell from an empty
board. The argued refusal is not reachable from a corrupt file at all.

Of the three consumers, exactly one fails loud on the same emptiness: `unregistered_live_units`
reports the running unit UNREGISTERED, because its refusal is keyed to what systemd says is running
rather than to what the file says. That is the shape the other two want.

## The repair, which exists and is not applied

`background/episode_prior.py` was built for precisely this, and five carriers already use it:

* `load_list_prior(path, item_type=dict)` returns `(records, verdict)` and tells ABSENT from
  UNREADABLE — the records here are dicts, not the `str` the existing callers pass.
* `preserve_unreadable(path)` keeps the bytes before the rebuild overwrites them.

What each caller should DO with UNREADABLE is a per-carrier judgement and `episode_prior` refuses to
guess it, correctly. The judgements this path needs:

* `record` — must still write (a launch that is not recorded is the state `launch_long_job` kills a
  healthy job to avoid), but must preserve first and say so. ABSENT and UNREADABLE take the same
  ACTION and are different ANSWERS.
* `check` — must NOT return `stale=0` on UNREADABLE. An unreadable register is not a clean board,
  and the caller must not reach `clear_transition` on it.
* `unregistered_live_units` — already correct; leave it.

## What this finding does not claim

It does not claim the disposition is wrong. `.launch_records.json` carries no episode clock any
write can shorten: `launched_at` is never differenced by any reader, there is no consecutive-failure
counter, and the severity the page carries (`died:{len(died)}`) is counted over what systemd settled
on that call. `benign` is the right verdict on the episode question. This is the other question —
the one `_scope_of_benign` exists to say a `benign` row has not answered.
