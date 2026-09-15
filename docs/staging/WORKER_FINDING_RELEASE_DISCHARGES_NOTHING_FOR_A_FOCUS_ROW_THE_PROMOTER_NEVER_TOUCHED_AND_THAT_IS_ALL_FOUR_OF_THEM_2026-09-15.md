**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# FINDING — `--release` discharges nothing for a focus row the promoter never touched, and that is all four of them

**Filed 2026-09-15 by the autonomous worker**, on the THIRD consecutive draw of
*the-blind-envelope-the-reader-gets-is-the-one-the-arms-were-re-run-for*. The premise was spent
before the first of those three. The defect is not in the drawn work — it is that the lane cannot
execute the cure its own doorbell prescribes.

## The premise, re-measured on origin's own bytes

The draw predicted its own answer: *"At this orientation it prints `False` with a `why_not`
beginning '5 of these 5 books'"*. It does not, and has not since `5421e028e`:

```
$ git show origin/main:site/data/value_arms.json | python3 -c "...['blind_envelope']..."
ORIGIN  available: True   why_not: None
INDEX   available: True   why_not: None
HEAD    available: True   why_not: None
```

No bytes were written and the feed was NOT regenerated, per the draw's own instruction for this
branch. Recorded as `--premise-spent` against `5421e028e`, which the previous turn never did — it
wrote the disposition for a *different* focus id and left this row's window unnamed.

## The mechanism, and it is not the one the previous turn named

The previous turn concluded the cause was *"an unreleased claim"*. That is wrong, and re-releasing
would have produced a fourth draw. `--release` **was** called. It discharged nothing.

`delivery_lane.retire_continuation` calls `seat_continuation.retire`, whose subject is a
continuation ENTRY. `delivery_lane._focus` reads `DIRECTION.yaml` **directly** — the promoter is
not the only route to a draw — so a focus row drawn that way has no entry to mark. `retire` returns
False, `_retired_ids` never sees the finish, and the row is offerable again the instant the claim
sweeps.

`_retired_ids` names this limit in its own docstring and then argues it is not reachable:

> Every id that reaches Lane 0 through the promoter has an entry, so the live population is covered

**That sentence is false, and it is false of the whole live population.** Measured against
`direction.unreachable_focus`:

| offerable focus row | continuation entry? |
|---|---|
| `the-blind-envelope-the-reader-gets-is-the-one-the-arms-were-re-run-for` | **none** |
| `site4-reaches-l2-once-the-archival-that-blocks-it-is-in-the-record` | **none** |
| `the-level-scan-must-predict-the-refusal-from-the-tree-the-gate-reads` | **none** |
| `the-three-absent-control-rows-have-three-different-causes-not-one` | **none** |

Four of four. The stated cover is the empty set. In the draw ledger, 25 of the 48 `source: focus`
rows were drawn more than once.

**This is the R15 shape where a control's own docstring is read as evidence about itself.** The
limit was named honestly and then dismissed by an unmeasured population claim, and the dismissal is
what nobody re-checked — for nine days.

## What it cost

| when | what |
|---|---|
| — | `5421e028e` lands the work and binds it to the claim |
| +45 min | redrawn. That tick re-derives it as already done, files a result, releases |
| +25 min | **redrawn again**, still carrying the pre-land measurement as present-tense fact |

Two whole invocations to establish that a landed thing had landed. The draw's own closing paragraph
predicts this exactly and prescribes `--release` as the cure.

## The repair

`seat_continuation.retire_focus_row` writes a tombstone for a focus row nobody handed over, and
`retire_continuation` falls back to it. It is a second function rather than a widening of `retire`
because `_retired_ids`' objection — that a discharge must not report *"retired the continuation"*
about an id no continuation ever held — is correct, and is an objection to the NAMING, not the
mechanism. The record carries `focus_row_tombstone: true` and says it was never handed over. It is
keyed to `oriented_at` exactly as `retire` is, so it is **not a veto over the director's focus
list**: a seat that re-orients and still names the row gets it back.

Controlled in
`tests/background/test_a_finished_continuation_is_not_re_promoted_within_one_orientation.py`. Every
existing test in that file opens with `hand_off_focus`, so every id under test had an entry — which
is why the focus-route control already there could not see this. The new case never promotes.

## The first draft of the repair was a fail-open, and the commit gate caught it, not me

Worth more than the repair itself. The first draft fell back to a tombstone for **any** id `retire`
did not know. `test_release_discharges_the_offer_and_the_claim_over_the_whole_partition` went red on
its rows 3 and 4 and was right to: `--release` on a **typo** would have written a tombstone and
exited 0, spending the one message that means *"the lane cannot see your work"*.

That control is nine days old and its docstring says exactly why it exists — *"a discharge that
fires on everything passes every test of a discharge, which is this project's most-repeated control
defect"*. I then wrote that defect, in the module the control guards, while reading its docstring.

The narrowing is that a tombstone is written only for an id `direction.unreachable_focus` actually
names — which is precisely the population that can be re-drawn, and a re-draw is the only thing a
tombstone saves anything from. Controlled by
`test_a_tombstone_is_written_ONLY_for_an_id_DIRECTION_YAML_ACTUALLY_NAMES`; mutation-proven by
deleting the membership test, which reds that leg and the partition's row 4 together.

The release message was the same error one level up: it still printed *"retired the continuation"*
for a tombstone — the literal false claim `_retired_ids` raises as its objection. It now reads off
`retirement_is_focus_row_tombstone` and says which of the two discharges happened.

## Two of my three mutation predictions were wrong, and they are kept beside the claim

* **fallback removed** — predicted row 1 red, row 2 green; **got both rows red**. The `is True`
  assertion precedes the orientation switch, so it belongs to neither row. Right kill, wrong
  reason, and I had claimed it demonstrated the partition.
* **tombstone omits `retired_at_orientation`** — predicted "silenced for good"; **got the
  opposite**: never discharged at all. A missing stamp fails open, not closed.
* **`written_at: time.time()` instead of 0.0** — predicted and confirmed an EQUIVALENCE, recorded
  as one rather than assumed to be the flattering answer.
* **`_retired_ids` drops `== current_orientation()`** — the mutation I had not thought to run, and
  the only one that kills row 2 alone. Without it row 2 was a leg nothing could show reachable.

## What is NOT done, and one of it must never be

**`execution_mode.fast` / `sim_fast_mode` in `run_identity_fields` — REFUTED for the third time, do
not do it.** `fast` is a bool resolving to `None`, so declaring it reads as coverage and contributes
nothing; `sim_fast_mode` is the raw environment string, so `SIM_FAST_MODE=2026-09-15` would inject a
run-identity token the run does not have. The follow-up's premise is false besides: the arms'
comparability claim rests on `risk_committee`, which **is** declared and **is** read. Already
refused in a dated comment above the declaration and written up at `64b561172`. **This draw carried
it a third time. The tombstone above is what stops a fourth.**

**The `groups` disposition — already written**, at `5421e028e`. `groups=None` is present in
`tools/demand_vector_coverage.py` as it stands at HEAD; there was never anything to restore.

**`tools/landing_pair` refuses the remedy it prescribes.** Found while landing this repair. It
indexes only `--tree` (HEAD) and never considers the OTHER paths in the same landing set, so
naming the companion changes nothing — a consumer and its supplier landing together always refuse,
which is the ordinary shape of any two-file change. Its message says *"Land them together"* and it
has no way to express that. Not blocking here (it gates nothing; `surgical_land` is the real gate),
but every lane that follows its advice hits a wall it cannot pass through.

**The real uncovered comparability hole is `--end-year`**, named in the execution-mode docstring and
still unstamped. That, and not the two refuted fields, is the gap worth closing.
