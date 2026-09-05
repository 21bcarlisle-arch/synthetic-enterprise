**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — LANE 0 delivery, found while re-measuring a drawn premise

# The auto-header repairs the one copy the merge cannot see, and the refusal that would have named it records only the checks that passed

Filed 2026-09-05 by the autonomous worker. Found while re-measuring the premise of the Lane-0 item
`fork-alarm-transition-state-keyed-on-behind-which-moves-every-cadence-2026-09-05`; that premise was
spent (see the companion `SEAT_RESULT_...` doc) and this is what the measurement turned up instead.

## 1. What was measured

`origin_reconcile` had been standing at `REFUSED_GATE` and nothing in the record said why. Running
the same door it runs — `surgical_land --merge origin/main` in an isolated worktree at HEAD — gave
the cause in one line:

```
[test-gate] ❌ A STAGING DOCUMENT THIS COMMIT WRITES HAS NO PARSEABLE SEVERITY HEADER
  - docs/staging/ADVISOR_REFERENCE_CLV_DRIVERS_THESIS_AND_SENSE_CHECK_2026-09-05.md:
    lane not a known lane: 'knowledge'
```

origin's copy heads `**Severity:** RECORDED · **Lane:** knowledge layer / discovery · **Type:** …`.
`finding_severity._LANE_RE` captures `[A-Za-z0-9_]+` after `**Lane:**`, so it reads `knowledge`,
which is not in `LANES`. An unclassified document refuses **every lane's commit**, so this refused
every merge of origin/main — landings and publishing both.

## 2. The mechanism built to prevent exactly this could not reach it

`staging_watcher.auto_chain` exists for this and its docstring names the director's instruction
verbatim: *"a staged document arriving should never block your landing."* It had already fired. The
shared working tree's copy carries a correct header (`**Lane:** A_strategy_governance`) and
`finding_severity --list` grades it `RECORDED A_strategy_governance`.

**But `auto_chain` writes the header in place and never commits it.** That closes the case where a
document arrives as an untracked file in the shared tree. It does not close the case where the
document arrives **on origin** — which is how every `[ADVISOR-STAGED]` document arrives, through the
remote bridge in `staging_watcher` itself.

And `origin_reconcile` merges in a **clean worktree at HEAD**, deliberately, so that the shared
index is never opened. That isolation is correct and is the whole safety argument for reconciling
unattended. Its consequence is that the shared tree's uncommitted repair is invisible to the merge
**by construction**. Two rooms: the repaired copy is the untracked one, and the tracked one — the
only one the merge sees — is the broken one.

Neither mechanism is wrong on its own. The repair cannot reach the reconciler, and the reconciler
must not reach into the shared tree.

## 3. Why it stayed invisible: the refusal records the checks that PASSED

`origin_reconcile._classify_merge_failure` renders a gate red as
`output.split("GATE RED", 1)[1].strip()[:400]`. Measured against the real refusal above:

| quantity | value |
|---|---|
| characters after `GATE RED` | 1125 |
| offset of `lane not a known lane` | **659** |
| cap applied | **400** |

So the 400 characters that get recorded are the boilerplate plus `✓ finding-class consolidation
holds` and `✓ every landing claim resolves in the tree this commit creates` — **the two checks that
passed**. The failing one is 259 characters past the cut. Every `REFUSED_GATE` line in
`deadmans-switch-log.md` reads:

> `ORIGIN FORK (REFUSED_GATE): on the resulting tree (rc=1). This is the tree the commit WOULD create…`

This is worse than truncation. A refusal that names nothing is merely unhelpful; this one records
positive evidence about unrelated checks succeeding, which reads to a scanner as *the gate was
mostly fine*. `origin_reconcile`'s own module docstring already rules against this shape — *"to
force it while reporting a verdict that names no cause a reader can act on"* — and the drawn item I
was given says its author *"could NOT establish from an isolated worktree whether this branch has
ever fired"*. This is why.

## 4. What was done

- `b178c2232` lands the repaired bytes so the merge has a side to resolve to.
- The merge then settles the resulting add/add with `--resolve` on the side carrying a known lane.
  Not one word of the advisor's text differs between the two sides; the resolution is the prepended
  header block alone.

That clears **this instance**. The class is open: the next `[ADVISOR-STAGED]` document that arrives
on origin with a header `finding_severity` cannot parse wedges every landing again, and the alarm
will again record only the checks that passed.

## 5. What was checked and did NOT hold

Stated because it was the first hypothesis and it was wrong. `auto_chain` prepending a header makes
the local copy differ from origin's blob, and the bridge writes origin's raw blob precisely so
`identical_untracked_twins` can clear it — a 2026-09-05 repair whose comment says *"one byte is the
whole defect"*. So the header looked like it must also break the fast-forward. **It does not, for
the three documents currently blocking**: all three measured byte-identical to origin's blob.
`auto_chain` had not touched them. The CLV doc was a genuine near-twin (588 bytes of prepended
header) but is now committed, so it no longer blocks. The 41 `NOT_ADVANCED` cadences logged today
are **not** attributed here — more than one thing differs between those cadences and I did not run
the one-variable version.

## 6. Recommendation

Two independent repairs, smallest first:

1. **Raise the cap and anchor it to the failing line, not the offset.** `_classify_merge_failure`
   should prefer the lines the gate marked `❌` over the first 400 characters after `GATE RED`. A
   refusal must name its reason; this one has the reason in hand and throws it away. Cheap, and it
   is the leg that would have made this finding a five-minute read instead of a probe run.
2. **Close the origin-arrival case for `auto_chain`.** The honest options are (a) the bridge applies
   `auto_chain` and lands the result through `surgical_land` when it extracts a doc from an origin
   commit, or (b) `origin_reconcile` refuses with the document named and pages that, rather than
   `rc=1`. (a) is the one that matches the director's instruction; (b) is strictly a fallback and
   still leaves landings blocked.

Recommending (1) then (2a). (1) is a one-function change with an obvious control — feed it a real
gate transcript and assert the document name survives. (2a) needs a decision about a daemon holding
a commit, which is a wider question than this finding should settle on its own.
