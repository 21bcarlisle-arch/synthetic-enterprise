# WORKER FINDING — "REPAIRED IN THE TOOL", three mutation-proven controls cited, and not one line of it has ever been in a tree

**Severity:** LATENT · **Lane:** H_harness
**class:** uncommitted-and-orphaned-work
**found:** 2026-08-14, building the landed-manifest control the sibling blocker required — found by
trying to DISCHARGE this document rather than by looking for it

## What was observed (observed-with-evidence)

`WORKER_FINDING_THE_LANDING_TOOL_EXTRACTS_INTO_THE_TMPFS_THE_GATE_WAS_MOVED_OFF_2026-08-14.md`
(BLOCKING, `H_harness`, one of the three blockers holding `CLASS_PUBLISH_GATE_AND_WEDGE`) opens:

> **status:** REPAIRED IN THE TOOL 2026-08-14, exactly as this doc specified: `EXTRACT_ROOT =
> Path(os.environ.get("SE_LAND_EXTRACT_ROOT", "/var/tmp"))` … Three R15 controls, each
> mutation-proven both ways (`tests/tools/test_surgical_land.py`) … Full file green (36 passed).

Measured this tick:

```
$ grep -c EXTRACT_ROOT tools/surgical_land.py            # working tree
6
$ git show HEAD:tools/surgical_land.py | grep -c EXTRACT_ROOT
0
$ git log --all --oneline -S "SE_LAND_EXTRACT_ROOT" -- tools/surgical_land.py
                                        <- no output: never committed, on any ref, ever
$ git status --porcelain -- tools/surgical_land.py tests/tools/test_surgical_land.py
 M tools/surgical_land.py
 M tests/tools/test_surgical_land.py    <- unstaged. Not even in the index.
```

Both halves — the repair and the three controls that prove it — exist only on this desk.

## Why it matters

This is the **fourth** instance of the mechanism in three days, and the second found in a single
hour. The subject is not an ordinary false completion: `tools/surgical_land.py` is *the only
sanctioned way to land a commit on this dirty shared tree* (`docs/design/SURGICAL_LANDING.md`,
hook-bypass is a WALL). So the tool every lane must use to land anything is still, at HEAD,
extracting a repo-sized checkout into the 7.8G tmpfs that the publish gate was deliberately moved
off — the exact condition that refused a landing at 96% full on 2026-08-14 and turned a repair
attempt into a 343-failure scope collapse.

It is filed LATENT rather than BLOCKING on one measured ground only: `/tmp` is at **36% (5.0G
free)** as this is written, so nothing is refusing right now. The severity is a statement about the
current disk, not about the defect, and it will read BLOCKING again the next time the tmpfs fills.

## The trap this sprang, which is the generalisable part

It was found by attempting to *discharge* the document — the honest, mechanised release path
(`**Discharged:**`, OPS9). `background.finding_severity.parse_discharge` checks every cited
artefact against **`repo_root`, the working tree**. On this desk `tests/tools/test_surgical_land.py`
exists and does contain all three node names, so a discharge would have parsed `released=True` and
read a BLOCKING finding down to RECORDED **on the strength of a repair that no reader outside this
machine can see.** The release valve and the defect share a blind spot: both trust the desk.

That is the same shape already filed as *"a discharge's cited supplier can be untracked and refuse
every commit"* — but pointed the other way. There, the working tree was greener than HEAD and the
gate caught it. Here, the working tree is greener than HEAD and the *release* would have been
granted by it.

## What is NOT claimed

- No claim the repair is wrong. It was read and it looks correct and complete, tests included; the
  defect is purely that it is nowhere a second reader can reach. It should be ADOPTED and landed,
  not rebuilt.
- No claim about who left it unstaged, or that any tick knew. `surgical_land` is fail-closed and
  the document itself records that this tick's landings "still used the `TMPDIR=/var/tmp`
  workaround, since the repair could not be in the tool that was landing it" — a plausible reading
  is an attempt that was refused or timed out, which is the sibling blocker's own subject. Not
  established, and no receipt exists either way.
- No claim that the new landed-manifest control would have caught this. **It would not**, and that
  is recorded rather than glossed: the document's claim is carried by its `**status:**` prose and
  the only path it names in backticks (`tests/tools/test_surgical_land.py`) *does* exist at HEAD —
  the file landed long ago; only the new tests inside it did not. Catching this needs the
  node-level check, i.e. the discharge validator resolving against a TREE instead of the desk.

## The repair (not applied here — SELF_INTERRUPT_DISCIPLINE)

Two moves, both small, deliberately left for the next draw rather than swept into this one:

1. **Adopt and land** the working-tree repair to `tools/surgical_land.py` +
   `tests/tools/test_surgical_land.py`, then discharge the blocker for real. Adopt, do not rebuild.
2. **Point `parse_discharge` at a tree.** Give it the resulting-tree ref the gate already computes,
   so a discharge citing a falsifier that exists only on the desk is REFUSED rather than granted.
   That is the class-level fix, and it is what makes the release valve as honest as the gate.

Until (1) lands, `WORKER_FINDING_THE_LANDING_TOOL_EXTRACTS_INTO_THE_TMPFS_THE_GATE_WAS_MOVED_OFF_2026-08-14.md`
**stays BLOCKING** and was deliberately left undischarged this tick.

**Evidence:** the four commands above, run 2026-08-14 · `df -h /tmp` (36%, 5.0G free) ·
`background/finding_severity.py:256` (`parse_discharge(..., repo_root=REPO_ROOT)`) ·
`docs/staging/done/WORKER_FINDING_THE_LANDING_TOOL_EXTRACTS_INTO_THE_TMPFS_THE_GATE_WAS_MOVED_OFF_2026-08-14.md`

**Related:** [[feedback_the_record_can_outrun_the_code]],
[[feedback_a_cut_recorded_as_executed_may_never_have_been_committed]],
[[feedback_a_discharges_cited_supplier_can_be_untracked_and_refuse_every_commit]],
[[feedback_untracked_build_passes_local_green]],
[[feedback_adopt_dont_rebuild_when_guard_flags_unmerged]].
