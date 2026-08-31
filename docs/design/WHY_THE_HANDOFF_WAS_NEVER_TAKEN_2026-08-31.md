# Why the handoff was never taken — and it was not a usage limit

**Director, 2026-08-31:** *"your runner's 'Usage limit active — skipping autonomous turn' is false.
I've just checked — 8% of the session used, 15% of the week, weekly counter reset at 04:00 today.
Nothing is limited. So autonomous turns have been suppressed on a wrong signal and nothing has run
since 13:36. Find what that check reads, how long it has been returning true, and how many turns it
has skipped."*

He was right that the signal was false. It was false in a way I had not considered, and it was not
what stopped the work.

---

## 1. What the check reads, and the answer to "how many turns has it skipped"

`background/autonomous_runner._usage_limit_active` reads **`tmux capture-pane -p`** on the `claude`
session and matches three phrases anywhere in the visible pane.

**It has skipped ZERO turns, because the module has not run since 2026-07-08.**

| | |
|---|---|
| `"Autonomous runner started"` events, ever | **27**, the last on 2026-07-07 |
| launches with a real pid | 426, the last on **2026-07-08** |
| launches whose pid is a mock object | **2,976**, on every day since |
| `"Usage limit active"` lines | **3,443** across 52 days |

Every line in that ledger since 8 July was written by
`tests/background/test_autonomous_runner.py`, which called the real `log()` at the real path.
**6,421 of the file's 27,675 lines — 23% — are pytest output**, and the seventeen dated today are
seventeen unit tests. `ps` confirms nothing launches the module; its own docstring said so, in a
parenthesis ninety lines down.

**So I read test output as production telemetry and reported a usage limit to the director that had
never existed.** That is the error, and it is mine rather than the check's.

## 2. The check was still wrong, and is fixed as asked

Three defects, and only the third is obvious:

1. **A pane is scrollback, not a status line.** A limit message from three hours ago is still on
   screen. The check had no notion of recency, so once a limit had ever been shown it read as
   active until the text scrolled off.
2. **An unreadable pane and a clean pane gave the same answer.** They still do — but now that is
   deliberate and stated: no evidence means RUN.
3. **The claim was logged without the evidence for it**, which is how 3,443 lines became unreadable.

`usage_limit_verdict()` returns a verdict that must carry its own evidence, and **skips only on a
matched line that also names a reset time still in the future.** A phrase with no reset time cannot
be dated. A reset time in the past has expired. Both run, and both say why.

Fail-open here is the correct direction and worth being explicit about, because this repo's usual
instinct is the opposite: *a wrongly-launched turn costs one API call the real limit refuses in a
second; a wrongly-skipped turn costs every turn until someone notices, and nobody noticed for 54
days.*

## 3. A test could write the record, which is why the record could not be trusted

The sink that should have stopped it **already existed** and had a hole shaped exactly like this.
`tests/production_surface_guard.py` protects `docs/staging` and `docs/status` as whole SURFACES —
and protected `docs/observability` by **nine hand-listed dotfiles**, every one of them runtime
control state, every one added after a test had already written it. The narrative `*.md` ledgers,
the record of what the machine actually did, were not protected at all.

The module's own docstring makes the argument against its own tuple three times — *"a guard list
only protects the paths somebody thought of"* — and then maintains it exactly like the call sites it
replaced.

`docs/observability` is now a protected surface. **The blast radius was measured rather than
assumed: 102 tests across 11 modules**, every one of them a genuine test writing the production
record, and every one repaired — mostly by redirecting a path constant, twice by
`@pytest.mark.real_state_write` where the test legitimately rebuilds a deterministic store from
committed blobs. The three contaminated ledgers were cleaned (6,421 + 825 + 150 lines), and
`tests/test_isolation_guards.py` now scans every ledger for the fingerprints of a test process,
with a population floor so an empty scan cannot pass.

## 4. What ACTUALLY stopped the work, and it is a better finding

The handoff was never taken because **LANE 0 claimed sixty-eight items and delivered none.**

    "LANE 0 DELIVERY:"    the line the DRAW writes when it takes an item   ->  68 occurrences
    "LANE 0 DELIVERY --"  the DOORBELL text that reaches a worker          ->   0 occurrences

Zero, across every ledger in the repository, since the lane was built on 2026-08-25.

`supervisor.find_work()` has two callers with different powers. The **supervisor** polls it every
~2 minutes as an independent escalation watchdog — its own `grant_turn` docstring says it *"performs
ZERO pane writes"*, so it draws for the alarm signal and throws the reason away. The **pull-loop
Stop hook** calls the same draw at a turn boundary and is the only thing that feeds work to a
session.

`delivery_lane.draw()` claimed on the way past. Two-minute polling against a turn boundary is not a
race, it is a walkover: the watchdog took every item first, discarded the doorbell, and held the
claim for its full 100-minute deadline — during which `next_item` correctly skipped it as `held`, so
every draw that COULD have delivered saw an empty lane. The sweeper then released it as abandoned
and the cycle repeated.

**It failed by succeeding.** The claim worked. The log line was written. The ledger recorded a draw.
Nothing was red — and two sessions, including the one that had just built a handoff mechanism ON TOP
of this lane and reported it *"armed and untested"*, read the log line as delivery.

Fixed with `draw(claim=False)`: the claim belongs to the caller that can deliver.
`tests/background/test_a_draw_is_not_a_delivery.py` holds it, including the regression in the shape
it actually took — fifty watchdog polls must leave the item drawable.

## 5. The second consumer, armed

`background/seat_executor` is armed as `seat-executor.timer` (:05 and :35, off the tick's :00/:30
and off delivery-seat's :20), declared in `background/schedule_manifest.yaml` so a fresh machine
reproduces it.

One stand-down had to change first, and it was the same class of mistake: **it asked about presence,
not contention.** The liveness check ran before the draw and refused on a warm heartbeat alone,
which made the executor unrunnable in exactly the situation it was built for — a continuation is the
interactive seat deliberately giving a piece away, and the seat that wrote it is nearly always still
alive, because it writes the handoff and then keeps working. A re-derived focus item still stands
down; a handed-off continuation runs.

**The first tick ran at 18:12, took the handoff, and finished at 18:37 with `rc=0`.** The whole loop
closed unattended: draw → isolated worktree → `surgical_land` → `promote_worktree_landing` → pushed.
`b8e6ba32d` is on `origin/main` and the interactive seat did not touch it.

**The work is at the standard, which is the part I did not take for granted.** It filed its
pre-registration *before* measuring. It confirmed P1, P3 and P4 in the years named in advance —
2022's SVT route alone expects 12.80% against a band topping out at 4.30%, *"so no renewal anchor
≥ 0 reaches it — refused with its cause, never clamped."* It found the union is **the denominator,
not the rows**: both routes' natural denominators are wrong for the published band and wrong in
opposite directions, and the record counts ACCOUNTS. It checked three properties rather than
assuming them (departures terminal: 82 departures, 82 distinct accounts; zero unobserved interior
account-years). It declined to paste the fitted constants into the world and named two causes. And
**it left its refuted prediction standing**: *"P2 REFUTED … I predicted every reachable year would
fit lower; four did and five fitted higher"*, with the reason.

That is the discipline this seat is held to, produced by a tick with nobody watching.

## 6. What the first live run found in four minutes

Two BLOCKING findings, both filed, both fixed:

* **A daemon committed into the unattended writer's worktree.** `fork_salvage` committed
  `SALVAGE(auto)` inside `/var/tmp/se-seat-executor` four minutes in — a worktree is isolated from
  other WRITERS, not from other DAEMONS on the same box.
* **`promote_worktree_landing` verified the tip, not the range** — my own defect from this morning,
  **and the first live run walked through it while I was writing the fix.** The executor landed on
  top of the salvage commit and pushed, so `139332d90 SALVAGE(auto)` is on `origin/main` beneath
  `b8e6ba32d`: an ungated commit reached `main` through the route whose entire purpose is to prevent
  that, on its first unattended use. The content is two observability files and nothing needs
  reverting. **A push moves a ref**, so the subject is `origin/main..HEAD`, and it is now.
* **`fork_reconciler`'s worktree reaper is ARMED** and had spared the executor only by luck — it
  refuses a DIRTY tree, and `ensure_worktree` cleans at the start of every turn, leaving a
  clean-detached-MERGED window that is reap-eligible. `git worktree remove` on a live writer is the
  whole turn gone. Both reap doors now refuse a live writer, and
  `seat_executor.worktree_is_live` is the one home both daemons ask.

And one more of the same class, found by a control written to check something else: **the lane wall
enforced denials only while it could write its diary.** An unwritable log turned every denial into
an allow, because `_log_denial` sat un-wrapped above every `return 2`. Its sibling —
`record_publish_gate_success` — had the identical shape: a failed write to a diagnostic hit-rate
file abandoned the wedge clear, so on a full disk the publish gate would have stayed wedged for
ever.

**That is a class this project has never named.** We audit controls that *refuse on input they could
not read* — found three times in one day in August, with a rule written for it. Nobody had asked the
mirror question: **which controls stop enforcing when a WRITE fails?**

The census was run rather than filed: an AST pass over the hooks, the daemons, the tools and the
compliance layer for refusing functions containing an unguarded file write found **32**, of which
**0 in hooks** and 4 in gates — all four false positives. So the shallow form of the class closes at
two instances. What it cannot see is a write hidden behind a helper the refusing function calls, and
`_log_denial` itself was exactly that, so this bounds the class rather than closing it.

**And the condition is not hypothetical: `/tmp` on this machine filled the same evening**, and for
several minutes every process that tried to write a file got ENOSPC. That is precisely the state in
which these controls stop refusing.

## 7. Two more things the arming taught, both about the writer's own tree

**The narrow fix failed on its second instance in ninety minutes.** `fork_salvage` committed into the
executor's worktree; I exempted it by comparing the path against `seat_executor.WORKTREE`; the same
daemon then committed into the landing worktree *this work was being prepared in*, because that one
was not the executor's. The subject should have been *a live writer*, not *this module's path* — and
I wrote the narrow version while looking at the module that had been hit. Any writer now declares a
worktree in use with a pid marker, and a leg drives it from a path that is not the executor's so the
narrow version cannot come back green.

**The suite was not runnable in a worktree, which is where the new writer lives.** 31 errors across
nine modules on an unmodified `origin/main` checkout, all from one line: the anti-commit tripwire's
`_real_repo_head` shelled out to `git rev-parse HEAD` when `.git` was a file, and every test that
stubs `subprocess.run` answered that call — so HEAD read as `"unreadable"`, appeared to move, and the
tripwire failed closed as a GHOST PUSHER. The identical trap is fixed four lines above it, with a
comment explaining why. In the main tree `.git` is a directory and nobody could see it.

Thirty-one ghost failures would send an unattended writer chasing nothing, or teach it that reds in
its own tree are normal. **The second is the one that would actually cost something**, and it is the
opposite of what a writer with nobody watching has to believe.
