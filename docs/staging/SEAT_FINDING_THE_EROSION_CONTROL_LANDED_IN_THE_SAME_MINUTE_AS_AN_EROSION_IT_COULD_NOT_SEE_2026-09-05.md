**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# FINDING — the erosion control landed in the same minute as an erosion it could not see

**RECORDED, not BLOCKING: all 33 deleted annotations are restored in the commit that files this,
and the missing rung is built and mutation-proven in the same commit.** What was lost was a full
turn of measured work — seven carriers' partition measurements, three repairs' evidence, and the
`agent_status.json` roster finding — deleted from the register nine hours after it landed, with
every gate green at every commit in between.

Filed 2026-09-05, delivery seat, Lane 0 claim `census-rows-graded-by-resemblance-2026-09-05`.
**Both halves of this are mine**: the commit that deleted the annotations is the previous
increment of this same claim.

---

## What happened

| commit | time | rows | with `loader` |
|---|---|---|---|
| `c30738d77` sweep the 34 census rows that had never been asked the loader question | 00:47 | 46 | **46** |
| `76665df6e` (merge base) | 06:43 | 50 | **50** |
| `c5d37a190` the census refused a hit with no row and never a row whose hit had vanished | **07:16** | 50 | **50** |
| `9857c0edb` re-audit every census row that closed on a resemblance | **07:16** | 50 | **17** |
| `f7f9d5adc` merge — both sides kept whole | 07:27 | 50 | 17 |
| `origin/main` at the start of this turn | — | 50 | **17** |

`9857c0edb` re-audited the eight rows that had closed on a family resemblance, and was right to:
seven of the eight were wrong about their own carrier. It wrote the whole file back from a copy
taken before the loader sweep landed, so the 33 rows it did **not** re-audit came back without
their `loader` field. Nothing else was lost — no row, no verdict, no `why`, no other field.

The merge eleven minutes later did the harder thing correctly. Its message says so: *"resolved by
taking ORIGIN'S FILE AS THE BASE and re-applying my two purely ADDITIVE keys on top — adopting my
rewrite would have silently deleted all of it, which is the standing merge trap here."* It then
diffed its resolution against the re-auditing side's own copy and found *"exactly two changes"* —
which was true, and blind, because the deletion was already inside the copy it was diffing
against. **The one check that would have caught it is a diff against the merge base**, and that is
the check the standing rule already prescribes for the opposite direction.

## Why nothing could see it

`--check` has four rungs now and had three then. All three were green on all 33 rows:

- `undispositioned()` asks whether a hit has a row with a verdict and a reason. Every one still did.
- `unguarded_real_hits()` asks `real` rows to name a test that exists. 27 of the 33 are `benign`.
- `eroded_dispositions()` asks whether a dispositioned row still has a HIT. Every one still did.

Each rung guards a row's **existence** or its **verdict**. None guarded its **answer**. And the
dispositions file had said the missing rule in prose since the sweep wrote it —
*"A row without one has not been asked, which is a gap and not a pass"* — for exactly as long as
that sentence had no falsifier, which was nine hours.

**`eroded_dispositions()` landed in the same minute as this erosion.** It is a good control and it
is not the wrong one; it just asks a different question. That is the part worth keeping: *an
erosion control built from one instance of erosion generalises along the axis of that instance,
and this one generalised over the SUBJECT SET while the next erosion took the ANSWERS.*

## The repair

**1. The 33 annotations are restored verbatim** from `76665df6e`, each prefixed with what happened
to it and where it came from. Nothing was re-derived and nothing in the re-audit contradicted any
of them: the re-audit's corrections all landed on the 17 rows it actually opened, which is why the
two sides compose rather than conflict. All 50 rows now carry a `loader`.

**2. `unasked_loader_rows()`** — a hit whose row has no non-empty `loader` is RED. Keyed to the
property (*a row with no answer*), not to today's answer or to a remembered count, so it fires
identically on a row that never had one and a row that lost one, and a genuinely new hit lands red
until someone opens its loader. Wired into `main() --check` with its own banner.

**7 controls, 6 mutants killed** (`tests/background/test_self_clearing_alarm_census.py`):
the rung removed entirely (4 tests fire); `str(row.get(f, ""))` instead of `or ""` before `str`,
so a JSON `null` falls open; `is None`, so a blank string falls open; the guard widened to swallow
`undispositioned()`'s partition; the rung computed but dropped from the exit code; and the banner
naming the wrong rung. The negative leg — a row WITH an answer is silent — is asserted, because a
rung that refuses everything passes every refusal test.

## What was NOT done, and why

- **No control on the merge itself.** The tempting fix is a gate that diffs a merge resolution
  against the merge base for deletions. That is a whole-tree ratchet on every merge in a
  three-lane repository, and this register is one of many files; the cheap, local, provable
  version is a register that refuses to be a register with holes in it. If a second file loses
  authored content this way, that is the second instance and the class fix is then earned.
- **The `_scope_of_benign` prose stays.** It is the definition; `unasked_loader_rows()` is its
  falsifier. Deleting the sentence because it now has a test would remove the only statement of
  what the field is FOR.

## The generalisation

**A register's rows can lose their ANSWERS while every control that guards the register stays
green, because a control built to guard a register guards its SHAPE.** Verdict present, reason
present, row present, hit present — four checks, all structural, all satisfied by a row that has
forgotten what it knew. The content-bearing field is the one nobody writes a check for, because
checking it feels like checking prose.

And the narrower one, for the next merge here: **when you resolve a conflict by adopting one side
whole, diffing your resolution against that side proves only that you adopted it.** The side you
adopted may itself have been written over a stale base — which is exactly what "adopt the other
side whole" is FOR — so the diff that can find the loss is against the merge base, in both
directions, not against either side.

## Class registration

Belongs to `controls_that_cannot_fail`.

*Declared 2026-09-05 by the delivery seat, on the director's instruction to fold findings into the class registers rather than leave them as individual documents. Classified on the MECHANISM THIS DOCUMENT DESCRIBES (its body), not on its title: the registered classifier greps titles, and the titles have outgrown its vocabulary — which is why 92 findings sat `unclassed` while the six classes held 138 instances. The body carries 4 matches for `controls_that_cannot_fail` against 1 for the runner-up, which is the threshold used; anything below it was left for a reader rather than graded from a sibling.*
