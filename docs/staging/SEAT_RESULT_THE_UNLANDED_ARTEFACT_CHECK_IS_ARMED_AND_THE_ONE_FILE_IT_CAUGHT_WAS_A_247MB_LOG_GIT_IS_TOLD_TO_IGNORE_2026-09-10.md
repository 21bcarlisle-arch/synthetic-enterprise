**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — a completed long job's named artefact must reach git or say it did not) · **Class:** uncommitted_and_orphaned_work

# RESULT — the unlanded-artefact check is armed, and the one file it caught was a 247MB log git is under standing orders to ignore

---

## The answer, in one paragraph

**The check is built, wired to the deadman, and proven able to fire by an eight-mutation poison
round — and it is GREEN on today's tree, which the drawn item predicted would be red.** The premise
had expired before the item was drawn: of the two stranded pieces of work it names, the
machine-hours run landed at `dd9dc9451` (2026-09-10 00:45) and the other is a staging document that
is not in the launch register at all, so the check structurally cannot name it. What the check DID
find on its first real run was a third thing nobody had counted: `arms-rerun-20260909b` recorded an
in-repo `log` path, `docs/observability/arms_rerun_20260909b.log`, present on disk and in no commit.
That was **a false positive in my own first draft** — the file is 247MB and `.gitignore` holds
`docs/observability/*.log`. "Not in git" and "must not be in git" are identical from the index and
opposite in meaning, and the first draft could not tell them apart.

---

## What was built

One check over the register that already exists. No new register, no new module: it is
`landing_verdict()` / `landed_check()` inside `background/launch_liveness.py`, beside the `reask()`
that already re-asks the same records, and a CLI flag `--landed`.

**The two halves of one register.** `check()` settles a claim about a **process**. This settles the
reader's actual question, which is about a **file**: `finished` and `in git` are different facts and
nothing joined them. The register already names both the job and the path, so the join is one leg.

| Verdict | Refuses? | Means |
|---|---|---|
| `LANDED` | no | the path is in HEAD |
| `STAGED` | no | in the shared index and in no commit — a lane mid-landing looks exactly like this |
| `UNTRACKED` | **yes** | a finished job wrote it into this repo and nothing holds it |
| `IGNORED` | no | `.gitignore` covers it — a standing decision, not a stranding |
| `ABSENT` | no | nothing was written; that is the liveness re-ask's question |
| `OUTSIDE` | no | not under the repo root (`/var/tmp/...`) — ungradeable by construction |
| `RUNNING` | no | the unit is still going; refusing would say "land your half-written file" |
| `UNREADABLE` | **yes** | git could not be asked. Fail closed |

Four decisions worth keeping, each learned by running it rather than by thinking about it:

1. **HEAD and the index are asked separately.** `git ls-files` reads the index. A path that is only
   staged has reached no commit, no clone has seen it, and `reset --mixed` loses it — and this repo
   has already had one control read green for exactly that reason. `STAGED` is named, not refused:
   refusing would wedge every other lane for the duration of somebody else's commit.
2. **`.gitignore` is the third question**, added after the first real run produced the false
   positive above.
3. **The skip for a running job is keyed to the systemd probe, not to the record's `claim`.** A
   record whose unit was collected sits at `live` for ever, and keying to the claim would let
   exactly the stranded case escape by never being settled.
4. **Every field the record names is graded — `artefact`, `log`, `rc_path` — not just `artefact`.**
   The only path this check has ever flagged on real data was a `log`. An artefact-only reading, the
   literal wording of the drawn item, called that record clean.

**Wired, because a check with no caller never runs.** `deadmans_switch._check_launch_artefacts_landed`,
called from `run_cycle` beside its sibling. It gets its **own alarm key** on purpose: a settled
liveness claim is an *event* and pages once, correctly; an unlanded file is a **standing condition**
that is still true tomorrow, and sharing the key would announce it once and then read as resolved.
It notifies as `drift`, not `real_alarm` — nothing is dying, and paging the director because a file
needs committing is how this channel has buried its own signal before.

---

## The poison round

The check is green on the live register, so *green* proves nothing on its own. Eight mutations, run
against the 25-leg suite; every one produced a red, and the tree was restored green afterwards.

| # | Mutation | Reds |
|---|---|---|
| 1 | grader always returns `LANDED` | reachability, running-job, log/rc |
| 2 | refusals never counted | broken-probe, log/rc |
| 3 | `head` answered from `ls-files` (the index) | reachability, index-alone |
| 4 | only the `artefact` field graded | log/rc |
| 5 | relative path read literally, not joined to the repo | reachability, instance, index-alone, absolute-spelling |
| 6 | a broken git probe reads as clean | reachability, fail-closed |
| 7 | running-skip keyed to `claim == live` | reachability, collected-unit |
| 8 | `OUTSIDE` lines suppressed for the artefact too | names-what-it-cannot-see |

The partition leg (`test_every_landing_verdict_is_reachable`) is asserted **first**, over a real
temporary git repository, because a grader whose every branch says `LANDED` passes every per-branch
leg below it and a grader whose every branch refuses passes every refusal leg.

---

## Where the drawn item was wrong, stated plainly

**"Done when the check is red on today's tree."** It is not, and it should not be. One of the two
named items landed at `dd9dc9451` two commits before the draw — the premise expired between the
doorbell being composed and the work being done. Predicting that a correctly-specified fail-closed
control will change bytes on a clean feed is predicting a defect; the poison round is what stands in
for it.

**"Settle the canon as the first thing the check names."** The check cannot name it.
`docs/staging/DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07.md` is a staging document, not a launch
artefact, and it appears in no launch record. The two stranded items are the same *shape* but only
one of them is in this register's domain. **The canon move is settled in this commit anyway** — the
root deletion and the `done/` copy land together, ending 23.1 hours of a half-completed move — but
it is settled by hand, and nothing in this check would have caught it.

---

## What is next, and what this does NOT cover

- **Three of seven records write only to `/var/tmp`.** The check says `OUTSIDE` and prints it rather
  than staying silent, so the gap is visible — but a run whose only output is outside the repository
  has *no landable evidence it ran at all*, which is a real hazard and a different one.
- **The 247MB log is the same hazard wearing the other hat.** `arms-rerun-20260909b` is a
  six-hour run whose only surviving local trace is a file git is told never to hold. `IGNORED` names
  that on the page; nothing yet acts on it.
- **The register is only as good as what records into it.** A job launched without
  `launch_long_job` has no record, so this check is blind to it by construction. That is the
  seventh-throwaway-launch class, already filed separately.
