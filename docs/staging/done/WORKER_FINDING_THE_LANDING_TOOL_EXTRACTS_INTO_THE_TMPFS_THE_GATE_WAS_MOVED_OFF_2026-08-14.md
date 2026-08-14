# WORKER FINDING — the landing tool extracts into the tmpfs the publish gate was moved off, so a full /tmp refuses commits while the gate is fine

**Severity:** BLOCKING · **Lane:** H_harness
**class:** publish_gate_and_wedge
**found:** 2026-08-14, unwedging the publish gate (243 consecutive failures, ~7,056 min)
**status:** LANDED 2026-08-14 in `04880c948` (tree `85343c497`, receipt gate-rc 0). **This line
previously read "REPAIRED IN THE TOOL 2026-08-14" and was FALSE when written** — the repair and all
three controls existed only on the desk, unstaged, and `git log --all -S "SE_LAND_EXTRACT_ROOT"`
returned nothing on any ref. That falsehood is not smoothed over here: it is the subject of
`WORKER_FINDING_A_REPAIRED_IN_THE_TOOL_CLAIM_HAS_NEVER_BEEN_IN_ANY_TREE_2026-08-14.md`, which caught
it by trying to discharge this document, and it made this the FOURTH instance in three days of a
record outrunning the code. The code was ADOPTED, not rebuilt (it was read and is correct):
`EXTRACT_ROOT = Path(os.environ.get("SE_LAND_EXTRACT_ROOT", "/var/tmp"))`, used by both
`_land_once`'s `mkdtemp` (via `dir=`) and the sweeper's base. One addition the doc did not call for:
moving where extracts LAND would have orphaned the ones already leaked in `/tmp` — and that backlog
is precisely what filled the tmpfs — so the sweeper now walks BOTH roots and de-duplicates when they
are the same.
**Discharged:** `tests/tools/test_surgical_land.py::test_the_extract_root_agrees_with_the_publish_gates_checkout_root`, `tests/tools/test_surgical_land.py::test_an_extract_is_not_created_under_the_tmpfs`, `tests/tools/test_surgical_land.py::test_the_sweeper_still_reclaims_the_legacy_tmpfs_backlog`, `tools/surgical_land.py` — verified in a TREE with git ls-tree at 04880c948, never in a status line.

Three R15 controls, each mutation-proven both ways (`tests/tools/test_surgical_land.py`):
`test_the_extract_root_agrees_with_the_publish_gates_checkout_root` compares against the GATE's own
constant rather than a repeated `/var/tmp` literal, so future DIVERGENCE is what reds (a hard-coded
literal would pass through the next move — the tautology this class invites);
`test_an_extract_is_not_created_under_the_tmpfs` SKIPS rather than passes where `/tmp` is not a
tmpfs, because an inapplicable check is not a passing one; and
`test_the_sweeper_still_reclaims_the_legacy_tmpfs_backlog` reds if the legacy root is dropped.
Reverting the constant reds the first two; dropping the legacy base reds the third. Full file green
(36 passed).

**The mutations, actually run on the landing tick (2026-08-14) rather than asserted** — the earlier
draft of this paragraph claimed them while the code was on no ref, so the claim is re-established
from scratch here: reverting `EXTRACT_ROOT` to `tempfile.gettempdir()` gives *2 failed, 34 passed*,
red on `test_the_extract_root_agrees_with_the_publish_gates_checkout_root` and
`test_an_extract_is_not_created_under_the_tmpfs`; dropping the legacy base from the sweeper gives
*1 failed, 35 passed*, red on `test_the_sweeper_still_reclaims_the_legacy_tmpfs_backlog`. The file
was then restored byte-identical (md5 `3e6c24ac8b02cc3ad723b48ab56dd5a3`, `diff` clean against a
pre-mutation copy) and re-run green at 36 passed, because a mutation that silently eats the edit is
its own filed defect. Each control fails on its OWN named defect and no other's.

**The repair proved itself on its own landing.** The earlier draft noted that the tick's landings
"still used the `TMPDIR=/var/tmp` workaround, since the repair could not be in the tool that was
landing it." That is no longer true and is the neatest available evidence: `tools/surgical_land`
ran from the working tree carrying this repair, with no `TMPDIR` override, and extracted to
`EXTRACT_ROOT` — so the commit that landed the fix is the first one the fix itself served.

## What was observed (observed-with-evidence)

`python3 -m tools.surgical_land` — the ONLY sanctioned way to land a commit on a dirty shared tree
(`docs/design/SURGICAL_LANDING.md`, hook-bypass is a wall) — refused:

```
[surgical-land] REFUSED: REFUSED on DISK, not on code: 352MB free where the extract needs ~500MB,
so the gate could not be materialised. Swept 0 stale surgical-land extract(s) first, reclaiming 0MB
```

`df` at that moment: `/tmp` is a **tmpfs**, 7.8G, **96% full, 355MB free**. `tools/surgical_land.py:582`
extracts with `tempfile.mkdtemp(prefix="surgical-land-")` and its sweeper roots at
`tempfile.gettempdir()` (line 227) — both `/tmp`.

The identical defect was diagnosed and fixed for the publish gate on **2026-08-11**, and the fix is
still there in `background/process_run_complete.py`, comment and all:

> THE GATE'S CHECKOUTS LIVE ON DISK, NOT IN RAM (2026-08-11). `tempfile.gettempdir()` is `/tmp`, and
> on this box `/tmp` is **tmpfs** — 7.8G, backed by the same 15.9G of RAM the suites need. …
> `HEAD_CHECKOUT_ROOT = Path(os.environ.get("SE_GATE_CHECKOUT_ROOT", "/var/tmp"))`

So the gate materialises on ext4 (888G free) and the tool that lands the gate's own repairs
materialises in RAM. Re-running with `TMPDIR=/var/tmp` succeeded immediately, same tree, same paths.

## Why this is a finding and not a chore

It is the **sibling half** of an already-hardened class (`feedback_audit_sibling_half_for_hardened_class`):
one call site of `gettempdir()` was moved to disk and its sibling was not, and nothing exists that
would have found the second one. Its cost is worse than the first, because it lands on the recovery
path: a full tmpfs blocks *every commit on a dirty tree*, including the commit that would unwedge
publishing — with a message that correctly says DISK and correctly says nothing failed, at exactly
the moment a tick is hunting a red test.

The same tmpfs also decided a publish-gate test's verdict this tick (see
`test_a_full_filesystem_under_the_sandbox_cannot_red_the_verdict`), which is the third consumer of
`/tmp` found coupling a verdict to free RAM in one hour.

## The repair (not applied here — SELF_INTERRUPT_DISCIPLINE)

Mirror `HEAD_CHECKOUT_ROOT` exactly: a module constant
`EXTRACT_ROOT = Path(os.environ.get("SE_LAND_EXTRACT_ROOT", "/var/tmp"))`, used by both `_land_once`'s
`mkdtemp` and the sweeper's base, so the tool and the gate agree about where a checkout lives. The
class-level version is a control asserting that no repo tool materialises a repo-sized checkout under
`gettempdir()` on a box where that is tmpfs — which is the only form that would have caught this one.

## What is NOT claimed

- No claim that the tmpfs was full *because of* any particular process: `/tmp/pytest-of-rich` is 1.5G
  and ~2G more is prior wedge-diagnosis debris (`/tmp/gatecand*`, `/tmp/wedgediag_*`, `/tmp/wouldbe`,
  `/tmp/cand2`, `/tmp/gate_head_tree`), but `fuser -m` on a tmpfs path matches the whole MOUNT, so
  nothing here establishes which of those are abandoned. None were deleted.
- No claim that publishing was wedged BY this: the wedge's cause was the uncommitted `name` drain
  (landed this tick). This blocked the *repair*, for one attempt.

**Evidence:** `tools/surgical_land.py:227,582` · `background/process_run_complete.py` `HEAD_CHECKOUT_ROOT`
· `df -h /tmp` at 2026-08-14 13:10 BST (96%, 355MB) · the refusal line above · the same command
succeeding under `TMPDIR=/var/tmp`.
