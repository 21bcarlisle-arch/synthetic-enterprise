**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The first orientation after the named-alarm brief named all four alarms firing that day and left them by choice (2026-11-08)

Drawn at about 01:35 GMT as `does-the-seat-act-on-a-named-firing-alarm`. The question was whether an
orientation record mentions a repeating alarm last observed on the day it ran, now that 78e94ce98 (23:55 GMT,
7 Nov) lists every live alarm above the JSON. If records still ignore an alarm the prompt names, the defect is
in the reader, and the fix is to rank or trim the list. It is not to add a detector.

## What was measured

**Only one orientation has run since 78e94ce98:** the 00:20 GMT tick on 8 Nov, session `ce66be93`. The next
is due at about 03:20.

- **The route works.** The session's prompt carries the `LIVE REPEATING ALARMS` block at character 21,899 of
  106,246, above the JSON. It names all 15 alarms. Four of them were last observed on 8 Nov: product
  machinery, dead-man worktree-undeclared, dead-man fork-orphan, and the advisor channel.
- **The reader read it.** The drafted `DIRECTION.yaml` has a `not_now` row: *"Working the fifteen live
  repeating alarms … I read them. The ones holding today are machinery alarms (dead-man worktree and fork
  orphans, product machinery, the advisor channel), and none sits between a supplier result and the exit
  test."* That is exactly the four alarms with a `last` of today. None is missing and none is extra. Each is
  left by choice, with a reason tied to the correctness stretch.
- **So the list is not furniture,** at least at 15 rows. Nothing needs ranking or trimming yet. Today's
  alarms are the top four lines because the list is sorted by `last`, newest first. That ordering may be
  what made it easy to read.

## A caveat this record has to carry

**That reasoning never reached the record.** The 00:20 draft was refused for an unrelated defect: it
rewrote the open concern `the-publish-window-is-anchored-to-monday`. `restored_previous_record` put back
the 21:21 record. So `docs/direction/decisions.jsonl` keeps no `not_now` for 00:20, and the evidence above
exists only in the session transcript
(`~/.claude/projects/-home-rich-synthetic-enterprise/ce66be93-a99f-47b5-b88e-66c7064565e4.jsonl`, which is
outside the repo). This doesn't change the answer, because the question was about the reader and the reader
did read the list. But anyone checking from the ledger alone would find nothing. It is not filed as a
defect: a refused record is meant to be discarded.

## Prediction, filed before the 03:20 record exists

The 03:20 orientation (or the first one after it that is `oriented`, not `refused`) will name in `not_now`
or `focus` every alarm whose `last` is that day's date. That is at least seat continuity, product
machinery, worktree-undeclared, fork-orphan and the advisor channel, which are all observed on 8 Nov as
of 01:40. It will not ask for a detector.

**What refutes it:** a written record that omits one of them. If that happens, the remedy is to rank or
trim the list in `background/delivery_seat.py::_render_live_alarms`, for example by printing only the
alarms observed today in full and counting the rest.

To check, run this once the record lands. It prints the latest row's outcome and each alarm keyword it mentions:
`python3 -c "import json;r=[json.loads(l) for l in open('docs/direction/decisions.jsonl')][-1];s=json.dumps(r).lower();print(r['at'],r['outcome'],[k for k in ('continuity','machinery','worktree','orphan','advisor') if k in s])"`

## Done

The claim is released. One record answers the question, and the prediction above is the second leg. It
costs a single command and needs no claimed lane. The next seat or worker to read this can grade it.
