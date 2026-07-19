# Deploy-reality check + worktree-ping mirror routing — proposal

**Provenance:** advisor escalation `docs/staging/ADVISOR_ESCALATION_WORKTREE_PING_DEPLOY_2026-07-19.md`
(asks 2 and 3). Ask 1 (the transient-suppression fix + deploy + quiet cycle) is DONE — see below.

## Ask 1 — DONE, with an R9 correction to the framing

**Fixed + deployed:** `classify_worktree` now returns `PENDING_REAP` (benign transient) for a MERGED
worktree awaiting the H24 dir-reaper, instead of `UNDECLARED` (accretion). Only detached / no-branch /
ORPHAN worktrees are undeclared now. R15-proven both directions (`test_merged_worktree_pending_reap_does_NOT_alarm_but_orphan_DOES`):
the merged transient no longer pages, a genuine orphan still alarms. Deadman restarted to deploy; quiet
cycle proven (see the commit + the restart evidence).

**R9 correction (evidence, not the assumed narrative):** this was NOT actually a committed-not-deployed
instance. The services restarted at **05:45 BST today** — *after* the H24_worktree fix landed (18 Jul
15:55) — yet pings still fired at 06:21/06:26. The running code WAS current. The pings persisted because
the **ping-hygiene was never in the code**: the H24 work delivered the dir-*reaper* but `classify_worktree`
never graced MERGED worktrees (its own docstring even admitted "merged: the worktree should have been
pruned" while still returning UNDECLARED). So the true class here is **(A) ratified-in-design,
never-mechanised** — distinct from **(B) committed-not-deployed** (code exists, running daemon stale).
Both are "a fix's DoD didn't reach reality," and both deserve the mechanism in ask 3 — but naming the
right one matters (R9): the remedy for (A) is "prove the mechanism exists + fires" (a mutation test),
not "restart the daemon."

## Ask 2 — mirror-only routing (propose; small taxonomy change, not built here)

After the ask-1 grace, the worktree-undeclared alarm fires only on GENUINE accretion (detached /
no-branch / unmerged-old orphan) — which is rare and real, and arguably *should* page. But the advisor
wants even a legitimate worktree-undeclared to be **mirror-only unless the count is GROWING** (a single
stable orphan = surface quietly; a growing accretion = page loud).

The `notify()` contract (`background/notify.py`) has a CLOSED kinds set —
`real_alarm | digest | director_echo | test_fixture` — with no mirror/log-only kind. Proposal:
1. **Add a `mirror` kind** to `KINDS` (structural tag the director sees; routed to the mirror/log surface,
   never the phone topic). This is a designed-contract change, so it lands as its own commit with a test
   that a `mirror`-kind send never reaches the paging path (mutation: a `mirror` send that reaches
   `send_ntfy`'s director topic must fail the test).
2. **Route worktree-undeclared as `mirror` by default**, escalating to `real_alarm` ONLY when the
   undeclared count exceeds the previously-seen max (genuine growth) — implementable in the deadman by
   tracking a high-water mark in the transition state, no new file. Genuine growing accretion pages;
   a stable/shrinking count is mirror-only. This directly satisfies "mirror unless growing."

Not built this turn (a closed-contract taxonomy change deserves its own isolated commit + the mutation
proof above); the ask-1 grace already removes the observed transient noise, so this is the belt to the braces.

## Ask 3 — the committed-not-deployed class fix (propose the mechanism)

Four "DoD didn't reach reality" instances in two days (H23 publish-gate, [ACT]-paging, treadmill-quiet
daemon-side, this worktree hygiene). Propose a **deploy-reality reconciler** — a deadman check
(mirror-by-default, page on a genuine stale-critical):

- For each `enabled` service in `process_manifest.yaml`, resolve its entrypoint module(s) and compute the
  git commit time of the LAST change touching them on `main`. Compare against the running process's start
  time (`ps -o lstart` / systemd `ActiveEnterTimestamp`). If a commit touching the module POSTDATES the
  process start → **STALE DEPLOY: service X is running code older than change Y** (this catches class B).
- For a fix TAGGED ratified (a `LEVEL_UP`/BUILD_OPEN with an atom id), assert two DoD facts mechanically:
  (a) a mutation test exists that names the fix's own defect and is currently GREEN (the mechanism exists
  and fires — catches class A: ratified-but-never-coded, because no such test can be green if the code
  isn't there); (b) the running service embedding it is not stale per the check above. A ratified fix
  failing either is flagged.
- **R15:** the reconciler must itself be failable — a synthetic "service started before its module's last
  commit" fixture must make it fire; a synthetic ratified-fix-with-no-mutation-test must fire. Fail-closed:
  an unresolvable module→service mapping is flagged, never silently passed (a check that can't run is a
  failed check — R15 fail-silent doctrine).

This makes "reaching the running system + a proof it fires" part of a ratified fix's DoD, mechanically,
so a fifth instance is caught by the machine rather than by the advisor's eye.

**Status:** asks 2 and 3 are proposals (their own isolated commits later); ask 1 is landed + deployed.
Batched for the daily [ACT] with the other proposals.
