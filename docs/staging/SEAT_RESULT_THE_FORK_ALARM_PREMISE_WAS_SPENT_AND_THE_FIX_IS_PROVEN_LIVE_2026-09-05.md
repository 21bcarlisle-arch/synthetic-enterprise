**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — LANE 0 delivery

# The drawn premise was spent, and the fix it asked for is now proven live in production

Filed 2026-09-05 by the autonomous worker. Lane-0 claim
`fork-alarm-transition-state-keyed-on-behind-which-moves-every-cadence-2026-09-05`.

## 1. The premise, re-measured at draw time

The item asked for `deadmans_switch._check_origin_fork`'s fall-through alarm to stop keying its
transition state on `f"{status}:{behind}"`. Measured on real disk:

- `background/deadmans_switch.py:777` already reads `state=r["status"]`.
- It landed as `f80707fcc`, *"the fork alarm re-paged 22 extra times because 'behind' counts OTHER
  lanes' pushes"* — with the measurement the item asked for in its message (117 fall-through
  cadences, 58 sends keyed on `{status}:{behind}` against 36 keyed on the status alone, and the 22
  extra pages stated as a **lower** bound because `REFUSED_CONFLICT`/`REFUSED_GATE` do not print
  `behind` in their detail line).

So the premise was spent before the draw. **The work was not redone.**

## 2. It is not merely landed — it has now run

This is the part the commit could not claim, and it is the distinction this project keeps paying
for: mutation-proved is not the same fact as *ever ran in production*. Read from the live
`.notify_transitions.json` during this tick:

```
deadman_origin_fork -> {'state': 'REFUSED_GATE', 'repeats': 2, 'escalated': False, …}
```

The stored state is the **bare status**. Two consecutive five-minute cadences at one standing
condition were folded into `repeats: 2` and suppressed. Under the old key those same two cadences
would have presented `REFUSED_GATE:3` and `REFUSED_GATE:4` — two distinct states, two pages — while
`re_escalate_after` sat unable to do the hourly job it exists for, because a state that never
repeats can never be re-escalated.

The branch has fired, on the real condition, and it suppressed. That closes the item's own explicit
caveat: *"I could NOT establish from an isolated worktree whether this branch has ever fired."*

## 3. What the measurement turned up instead

`REFUSED_GATE` was standing because an advisor document had arrived **on origin** with a lane string
`finding_severity` cannot parse, and every merge of origin/main was refused. Landings and publishing
were both blocked. Written up separately as
`WORKER_FINDING_THE_AUTO_HEADER_REPAIRS_THE_ONE_COPY_THE_MERGE_CANNOT_SEE_2026-09-05.md`.

Closed this tick: `b178c2232` (repaired bytes) → `179a6e042` (gated merge, add/add settled with
`--resolve`) → pushed → shared tree fast-forwarded, 3 byte-identical twins cleared.
`origin_reconcile.reconcile()` re-read afterwards rather than inferred from the steps succeeding:

```
status: LEVEL   behind: 0   detail: local and origin/main agree; nothing to reconcile
```

## 4. Claim state

The claim was **not held** at draw time — `--landed` returned *"it is NOT CLAIMED … the claim was
swept and you are working unclaimed"*, which is the expected reading for work that landed well
outside the 100-minute sweep. Nothing to release. Recorded here so the binding is not looked for
later and read as lost.

## 5. The sibling question the item raised, left open deliberately

The item's own reasoning was *"when one control is keyed to a moving answer you grep every
sibling."* Done, and the answer is not clean: `deadmans_switch` has further alarms keyed to moving
counts — `state=f"orphans:{len(...)}"` (:624), `f"undeclared:{len(...)}"` (:653),
`"stranded:{...}"` (:698), `f"stale:{len(...)}"` (:919). Each is a candidate for the same defect
and **none is asserted here**, because a count that moves is not automatically a bug: for a set that
genuinely grows, a new member is arguably a new condition. Deciding that needs the same
log-measurement `f80707fcc` did, per key. Filed as an observation, not a finding, and not fixed on
argument alone — which is the rule the drawn item itself insisted on.
