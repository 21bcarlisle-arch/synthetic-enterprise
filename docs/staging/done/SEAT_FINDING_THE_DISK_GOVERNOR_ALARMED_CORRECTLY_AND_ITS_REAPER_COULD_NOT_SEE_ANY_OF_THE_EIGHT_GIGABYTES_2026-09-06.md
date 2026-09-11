**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** no_caller_and_never_runs

# The disk governor alarmed exactly as designed and its reaper could not see a single byte of the 8.4 GB that caused the alarm

**Found 2026-09-06 by the delivery seat, when `/tmp` hit 100% mid-turn and killed a commit's own
`pwd`. Not looked for.**

---

## What happened

`/tmp` is a 12 GB tmpfs. It filled during a `surgical_land`; the commit itself landed and the
shell's next builtin died with `write error: No space left on device`.

`background/disk_headroom.py` did its first two jobs correctly. `observe()` had the band right and
the alarm text is exactly what it should be:

> DISK PRESSURE: 1203 MB free on /tmp (90.0% used). Floor is 2048 MB. This alarms BEFORE exhaustion
> by design — on 2026-08-19 the machine stopped at 152 MB with no warning at all. Expired scratch
> was ALREADY reaped before this alarm fired (**nothing reapable (all scratch in use or within
> TTL)**); this band is what remains after that, so it needs a person.

The bolded clause is the defect. `reap --dry-run` says **"would free 0 MB from 0 expired scratch
dir(s)"**, and the alarm hands that phrasing to the reader as *the scratch has already been dealt
with, what is left is real*. It had dealt with nothing, because none of the pressure was in a
directory it looks at.

## Where the 8.4 GB actually was

| Directory | Size | Reaped? |
|---|---|---|
| `/tmp/claude-1000/**` — harness session scratch, one live session holding eight ~294 MB HEAD extracts | 6.4 GB | no |
| `/tmp/pytest-of-rich/**` — pytest `tmp_path` trees from finished runs | 2.0 GB | no |
| repo-copy scratch under `REAP_ROOTS` | — | 0 MB found |

Deleting `/tmp/pytest-of-rich` alone took the box from 90% to 74% and cleared the alarm. Nothing
was live: the only `pgrep -f pytest` hit was this session's own command line, which contains the
word (the self-match trap, already on the record).

## The two things worth separating, because they want different repairs

**(1) The reaper's population is `REAP_ROOTS`, and the machine's scratch has outgrown it.** The
module's own docstring is proud of the right thing — *"a reaper that deletes on uncertainty is a
worse failure than a full disk"* — and that principle is not in question. But `pytest-of-rich` is
not uncertain: it is pytest's own documented temp root, pytest garbage-collects it itself, and a
numbered run directory with no live pytest is scratch by construction. It is identifiable, and the
reaper does not look at it.

The harness session scratch is the harder half and I am **not** proposing the reaper touch it: a
live session's `scratchpad` held eight repo extracts and was written 20 minutes before I looked.
Deleting that would be exactly the failure the docstring refuses.

**(2) The alarm asserts more than the reaper knows, and that is the load-bearing half.** *"Expired
scratch was ALREADY reaped before this alarm fired"* is true of `REAP_ROOTS` and false of the disk.
A person reading it — this seat did — concludes the easy space is gone and the remaining pressure
is structural. It was the opposite: two thirds of it was pytest garbage a one-line `rm` cleared.

**This is the cheaper fix and it is the one to do first.** The alarm should name the largest
consumers it can see and say plainly that they are outside the reaper's population, rather than
reporting `0 MB` in a phrasing that reads as *nothing to find*. A governor that cannot see a
directory must not describe that directory as handled — the same fail-open shape as an orphan check
with no entrypoints certifying a whole tree as unreachable, which this repo already refuses one
module over in `tools/orphan_ratchet.py`.

## What is NOT proposed

A new register, a new daemon, or a TTL sweep over `/tmp/claude-1000`. The first would be paperwork
about a backlog; the last would eventually shoot a live lane's uncommitted extracts in the back.

## Evidence

- `python3 -m background.disk_headroom --reap --dry-run` → `would free 0 MB from 0 expired scratch
  dir(s)`, taken while `/tmp` was at 90%.
- `du -sh /tmp/*` at the same moment: `6.4G /tmp/claude-1000`, `2.0G /tmp/pytest-of-rich`, then six
  ~294 MB HEAD extracts belonging to other live lanes.
- After `rm -rf /tmp/pytest-of-rich`: `free_mb 3157`, `used_pct 73.7`, `alarm: None`.
