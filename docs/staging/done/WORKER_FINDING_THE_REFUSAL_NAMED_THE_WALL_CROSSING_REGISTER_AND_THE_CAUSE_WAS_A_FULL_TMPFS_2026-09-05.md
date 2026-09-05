**Severity:** LATENT — the blocking condition was cleared by hand this turn (2.9 GB of abandoned
git extracts removed, `/tmp` 100% → 75%) and the landing it refused then went through; the two
defects behind it are unfixed and will recur, because nothing bounds the scratch and the refusal
still names the wrong subject · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — found while
landing the Lane 0 claim-store repair · **Class:** publish_gate_and_wedge

# The refusal named the wall-crossing register, and the cause was a full tmpfs

Filed 2026-09-05 by the autonomous worker. Found by `python3 -m tools.surgical_land` refusing a
three-path landing that had already passed every cheap gate and its own suite.

## 1. What the refusal said

```
[test-gate] ❌ WALL-CROSSING REGISTER DISAGREES WITH THIS COMMIT'S TREE -- COMMIT REFUSED.
wall-crossing checker RAISED against tree b7a14e90e: MeasurementError: the wall walker could
not run against b7a14e90e...: [Errno 28] No space left on device
[test-gate] The register is a claim about what LANDED. Land the code in this commit, or
            correct the row.
```

**The headline is a confident sentence about the register and it is false.** The register did not
disagree with anything. The walker never ran. The instruction that follows it — *"Land the code in
this commit, or correct the row"* — directs the reader to edit a disposition row that is correct,
which is the one action guaranteed to make things worse.

This is the same shape as the item I was drawn on. That hand-off's own complaint was that
`delivery_lane`'s refusal said *"the claim was swept and you are working unclaimed"* — a confident
sentence about the claim's state — when the real cause was a per-worktree store. **A refusal that
names a cause forecloses the real reading.** CLAUDE.md already has the rule (*"write refusals that
name their reason"*); what neither instance had is the distinct branch for **"I could not measure"**
as against **"I measured and it disagrees"**. `MeasurementError` was caught and rendered as the
disagreement verdict. Fail-closed was right; the WORDS were not.

The true cause is in stderr, two lines down, and only because the exception carried it. The
CLAUDE.md rule this violates by name: *"'We cannot tell' is a result."* It belongs in the verdict,
not inside the text of a different verdict.

## 2. Why the disk was full

`/tmp` on this machine is a **tmpfs — RAM, not disk**:

```
tmpfs   12G   12G   29M  100%  /tmp        ← at the refusal
/dev/sdd 1007G  94G 862G   10%  /          ← the real disk, almost empty
```

862 GB free on the actual disk and the commit was refused, because the only filesystem that
mattered is a 12 GB RAM-backed one. What filled it, measured:

| | size | age at measurement |
|---|---|---|
| `/tmp/claude-1000` (task output) | 4.3 G | live sessions |
| `/tmp/pytest-of-rich` | 3.5 G | 6 runs, one live |
| **11 abandoned `git archive` extracts** | **~2.9 G** | 4 h to 17 h old |

The extracts are the reclaimable part and the interesting part. Each is ~290 MB and each was made
by a turn proving a red was pre-existing at HEAD — `headext`, `headx`, `headx2`, `headx3`,
`headclean`, `verify_ext`, `swmut`, `prcmut`, `prc_probe`, and two more. **That is a habit this
repo's own memory teaches** (*"prove it in a `git archive HEAD` extract"*), performed correctly,
several times a day, by turns that then end. No process had a cwd in any of them.

**This is `A TTL CANNOT BOUND SCRATCH WHOSE MAKER DIED IN THE FIRST HOUR` (2026-09-04) arriving
through a second door.** That finding is about `/var/tmp` worktrees; this is the same mechanism in
`/tmp`, where it is worse, because the storage is RAM. There are already filed findings in this
staging directory about **OOM kills** destroying measurement legs
(`SEAT_FINDING_THE_LEG_THAT_PRODUCES_THE_PUBLISHED_BOUND_WAS_OOM_KILLED_AND_WROTE_NOTHING`). A
tmpfs sitting at 12 GB is 12 GB the guest cannot allocate. **I am not claiming that caused those
kills — I have not measured it, and `background.resource_headroom.sample()["total_mb"]` is the
figure to read against.** I am claiming the two are the same resource and nobody has looked.

## 3. What is NOT wrong

The gate. It refused a tree it genuinely could not verify, which is correct and is fail-closed.
`surgical_land` also did its job exactly as documented — it gated the tree the commit *would*
create, and its own diagnostic correctly pointed at the hunk survey. Neither is the defect.

## 4. What I did and did not do

**Did:** removed the 11 abandoned extracts (reproducible from git by construction; nothing else in
`/tmp` was touched, and the live pytest run's directories were left alone). `/tmp` went to 75% and
the landing went through.

**Did not:** bound the scratch, or fix the refusal's words. Both are real and neither is a
one-liner I could land honestly inside a bounded turn already holding a different claim.

## 5. The two repairs, in the order they are worth doing

1. **A distinct verdict for "could not measure".** `tools/wall_crossing_dispositions`' caller
   catches `MeasurementError` and renders it as the disagreement branch. It needs a third
   verdict — REFUSED, CANNOT-TELL, DISAGREES — and the `Errno 28` case should say *"the walker
   could not run: no space left on `/tmp`"* and name `df -h /tmp`. **The control to write with it
   is the one that would fail:** inject a `MeasurementError` and assert the operator's text does
   NOT contain the register instruction. Keyed to the property (a measurement that did not happen
   never produces a disagreement verdict), not to today's message.
2. **Bound the extracts at the point they are made.** A TTL sweeper is the tempting answer and is
   the one the 2026-09-04 finding already shows fails, because the maker dies first. The smaller
   mechanism: extracts are made by a handful of call sites for a known purpose, so give them one
   helper that makes the extract and removes it, rather than a daemon that watches `/tmp`.
   *Build the smallest mechanism that can fail, and prefer doing the work to building the thing
   that watches the work.*

## 6. Reproduce

```
df -h /tmp                                    # the filesystem that decides
python3 -m tools.wall_crossing_dispositions --at-tree $(git write-tree)
```
