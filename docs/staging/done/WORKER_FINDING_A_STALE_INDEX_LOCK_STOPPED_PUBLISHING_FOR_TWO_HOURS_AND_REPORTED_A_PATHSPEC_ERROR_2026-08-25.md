**Severity:** BLOCKING · **Lane:** H_harness

**Rank:** backlog — the outage is over; what is left is the diagnosis defect that made it take
two hours to find.

# A stale `.git/index.lock` stopped publishing for 1h43m, and the publisher reported it as a pathspec error about a file that was sitting right there

All claims `observed-with-evidence`.

## What the log said, and why it sent the reader the wrong way

    [process_run] Committing and pushing (net=£1,277,721)
    [process_run] Nothing to commit or commit failed (rc=1)
      git/hook output (last 40 lines):
      error: pathspec 'docs/staging/done/run_complete_20260825T141610Z.md' did not match
             any file(s) known to git

The file existed, was not ignored, and `git add` on it was perfectly legal. Nine consecutive
publish cycles failed this way and the diagnosis in the log is about the wrong thing.

## What was actually true

`.git/index.lock`, 1,274,828 bytes, mtime 6,182 seconds old, with **no git process alive** —
checked by `ps` for git, commit, pre-commit, surgical_land and process_run_complete, all absent.
A partially-written index left by a git process that was killed mid-write.

The chain: `git add` fails with *"Unable to create '.git/index.lock': File exists"* → **nothing
is staged** → `git commit -- <pathspec>` is then handed a path that really is unknown to the
index → it reports the pathspec, which is the last link and not the cause.

## The defect, and it is one line

`background/process_run_complete.py` around line 4007:

    subprocess.run(["git", "add"] + files, cwd=str(PROJECT_DIR), timeout=120,
                   stderr=subprocess.PIPE, text=True)  # H30

The return code is **not checked**. H30 was added so the commit's hook output reaches the log,
and it did its job — but only for the COMMIT. The ADD captures stderr into a variable nobody
reads, so the one message that names the real cause is discarded, and the next command's
confusing error is what survives.

`git add` is all-or-nothing: one bad path, or a lock, and NOTHING is staged. So an unchecked rc
here can only ever produce a misleading downstream error, never a truthful one.

## The fix

Check the rc. On failure, log the captured stderr verbatim and refuse the cycle with that
reason, rather than proceeding into a commit that cannot work. A stale-lock reaper is the
obvious second half and is deliberately NOT recommended here: automatically deleting a lock is
how a live `git commit` gets its index corrupted, and this repository runs pre-commit gates that
legitimately hold the lock for forty-five minutes at a stretch. Say the truth loudly; let a seat
decide.

## Cost, measured

Publishing was down 07:15Z→14:44Z with THREE causes in sequence, and the state file read
`total_red: 0` for the whole of it because the suite was green every time and only the commit
failed:

    07:15-08:05Z  a `site/**` edit landed without its test update      (mine)
    09:25-11:20Z  a level raise held in the shared INDEX, not the tree (mine)
    13:01-14:44Z  this stale lock                                      (unattributed)

Two hours of not publishing that reads as healthy is the through-line, and it is the same shape
each time: **the publish-gate state file describes the SUITE, and every one of these failures
was in the COMMIT.** A `commit_refused` with `total_red: 0` deserves its own alarm text saying
so, instead of leaving a reader to conclude the gate is fine.

## Evidence

- `ls -la .git/index.lock` — 1,274,828 bytes, mtime 6,182s before removal.
- `ps -eo pid,etimes,args | grep -iE "git|commit|surgical|process_run"` — nothing.
- `git add --dry-run docs/staging/done/run_complete_20260825T141610Z.md` — `fatal: Unable to
  create index.lock: File exists` before removal; `add '...'` after.
- The lock is preserved at `scratchpad/index.lock.stale.bak` in case anyone wants to see what a
  half-written index looks like.

---

## DISPOSITION 2026-08-25T15:0xZ — BUILT, and the incident recurred mid-fix

`background/process_run_complete.py`: new `_git_add_or_refuse()` is now the ONE place a
publish-path `git add` runs. It reads the rc, logs the captured stderr verbatim, and refuses the
cycle with `COMMIT_REFUSED` (not in `RETRYABLE_PUBLISH_OUTCOMES`, so the next cycle really
retries) instead of walking into a commit that cannot work.

**The finding named one site; there were two.** `_commit_and_push_paths` — the banner/heartbeat
path — staged just as blindly, so a lock there produced the identical misleading pathspec error.
Fixing only the caught instance is what makes a class recur (R10), so both are routed through the
helper and a source census (`test_no_publish_path_git_add_goes_unchecked`) fails on any `git add`
reintroduced outside it.

No stale-lock reaper was built, exactly as recommended.

**R15 evidence** — mutation applied to the mechanism at runtime (a gate suite was in flight, so
the shared source was not mutated), pre-fix behaviour substituted:
- pre-fix: `attempted = [git add, git add, git commit]`, log = `Committed locally, push deferred`
  — the commit IS reached and the lock message is discarded entirely. Both controls go red.
- census: flags a reintroduced `_sneaky_add` at its line. Goes red.
- null control (`rc 128 -> 0`) still reaches the commit, so refuse-always cannot green this.
- `tests/background/test_process_run_complete.py`: 77 passed (74 + 3).

**The incident repeated while this was being written, and was cleared by hand.** The 14:34Z
publish commit died leaving `.git/index.lock` (1,274,948 bytes) behind; HEAD never advanced.
Verified stale before touching it — no git process alive (`ps`), no holder (`lsof`/`fuser`),
age 659s. Preserved at `scratchpad/index.lock.stale.20260825T150238Z.bak`, then removed;
`git add` legal again immediately after.

**Still owed (not built here):** the finding's second half — a `commit_refused` cycle reporting
`total_red: 0` still reads as healthy, because the publish-gate state file describes the SUITE
while every one of these failures was in the COMMIT. That deserves its own alarm text and is
left as a separate item.
