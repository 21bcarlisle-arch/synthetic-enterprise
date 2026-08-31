**Severity:** LATENT · **Lane:** H_harness

# [FORK ORPHANS] 1 orphaned fork branch(es) never merged home [ENFORCE (salvage+reap)]: c3-shown-price-measure; reaped 0/1. Fork branches that built work and never merged home -- the

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **0.2h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[FORK ORPHANS] 1 orphaned fork branch(es) never merged home [ENFORCE (salvage+reap)]: c3-shown-price-measure; reaped 0/1. Fork branches that built work and never merged home -- the fragmentation disease. Reap-only: each is salvage-tagged then reaped (enforce-mode) or flagged (report-first); a good orphan is recoverable from its salvage tag and re-runnable, never auto-landed unreviewed. Triage: docs/observability/ + salvage/* tags.
```

## What is known without diagnosing anything

- Signature: `deadman_fork_orphan` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-31T01:11:05+00:00
- Repeats before escalation: 3 (threshold `ESCALATE_AFTER_REPEATS`)
- Paging for this signature is now SUPPRESSED. It resumes automatically the moment the
  underlying state changes — including when it clears.

## What this document is asking for

The repetition is the finding. Something is failing the same way on a loop and nothing is
converging on it, which is the shape the director named as "a symptom, not an event". Draw
this, diagnose the condition named above, and either fix it or record why the alarm is wrong.

Archive to `docs/staging/done/` when the condition is resolved. While this document is live
-- here or in `in_progress/` -- a continuing condition APPENDS a dated line below rather than
filing a second document (2026-08-24). A condition that returns AFTER this has been archived
files a fresh document, because that is a new episode and an R3 two-strike signal.

## Still live

---

## DIAGNOSED 2026-08-31 (Lane 0, delivery seat) — one root cause under TWO repeating alarms

**The alarm is right, and `reaped 0/1` is not a failure — it is the reaper refusing correctly.**
`background/fork_reconciler.py` will not `branch -D` a branch that is checked out somewhere; its own
message says so: *"branch is checked out in worktree X; reap that DIRECTORY first
(`evaluate_worktree_reap`, its own `.worktree_reap_enabled` flag)"*. `c3-shown-price-measure` is
checked out at `/tmp/.../scratchpad/c3wt`. So the branch cannot be reaped until the worktree goes.

**That is also the whole content of the second repeating alarm**, `[UNDECLARED WORKTREE]` /
`c_wt_orphan_worktrees`, filed the same day. Two signatures, two escalated documents, one condition
one layer down. Neither can converge while the other stands, which is why both repeat.

**Why the branch is unmerged, which is the part no counter can see.** It is not lost work. It is
the C3 shown-price arm, and it is unmerged **by decision** — see
`docs/staging/WORKER_PREREGISTRATION_WHAT_THE_SHOWN_PRICE_MUST_SHOW_2026-08-30.md`, which measured
it, refuted its own prediction twice, and concluded C3 stays out of `main` until the value-arms A/B
run, because C3's sign turns out to be a property of the company's own price position rather than of
the world change. An orphan-counter cannot distinguish "abandoned" from "deliberately parked", and
here it is the second.

**Verified before touching anything, not remembered:**

- `salvage/c3-shown-price-measure` → `f93fd1ea9`, byte-identical to the branch tip (`git diff` empty)
- the tag's tree contains `simulation/shown_price.py` and the `simulation/customer_events.py` seam
- the worktree is **clean** (`git status --porcelain` empty) and **idle** (no process holds it)

**The one thing that was actually missing, now fixed.** The C3 write-up named its next step but
never said where the arm's code lived — so a reader drawing the A/B run would have rebuilt it from
prose. The salvage tag is now cited on that artefact, in a new section, *before* the branch name is
allowed to disappear. That ordering is the point: the pointer had to outlive the branch.

**Disposition: the worktree is removed, which unpins the branch and lets the existing enforce-mode
reaper do its job.** Nothing is lost — the salvage tag holds the work, and
`test_salvage_precedes_reap_and_refuses_when_salvage_cannot_be_confirmed` is the landed control that
guarantees the reap cannot outrun the salvage. Reversible: `git worktree add` from the tag.

Not archived by me in the same breath as the fix — the condition clears when the reaper next runs
and finds nothing to report, and that is the acceptance test rather than my say-so.
