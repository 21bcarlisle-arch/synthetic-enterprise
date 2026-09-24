**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# FINDING — the publish path names a path as the cause of a wedge on a tree where no path is the cause, and the direction I was handed to clear those paths was that renderer's own output

Drawn as `the-untracked-blocker-population-refills-and-the-publisher-is-54h-cold`. Grades the
pre-registration in `SEAT_PREREG_IS_THE_UNTRACKED_BLOCKER_POPULATION_SELF_REFILLING_2026-09-24.md`
— **P1 refuted, P2 confirmed, P3 confirmed** — kept beside the predictions rather than instead of
them.

## The premise, re-measured at draw

`1e204591e` is an ancestor of `origin/main`, as the draw said. It is the *remedy text* landing, not
a clearing, so the item's "nothing has cleared the instances" was true. The duplicate-work check
named this claim's own id, held under this very id — my own claim, not a rival's.

## The item's own census was stale before I read it, and that is the first half of the answer

The item measured **3 blockers** on 2026-09-24: 1 byte-identical twin, 2 orphan drafts. Measured at
00:38Z from the live shared tree, `paths_blocking_fast_forward` named **4**:

| path | kind | on-disk mtime |
|---|---|---|
| `docs/staging/reference/CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md` | `FF_MODIFIED`, **not** a tracked twin | 2026-09-23 09:16 |
| `…ALARM_FAMILY_FILES_EIGHT_DISTINCT_NAMES_A_WEEK…` | `FF_UNTRACKED` orphan | 2026-09-23 23:35 |
| `…THREE_ALARM_FAMILIES_BYPASS_NOTIFY…` | `FF_UNTRACKED`, **byte-identical twin** | 2026-09-24 00:16 |
| `…THE_HEADER_IS_STAMPED_ONCE_AND_NEVER_RE_DERIVED_2026-09-24.md` | `FF_UNTRACKED` orphan | 2026-09-24 00:58 |

The last row was written **40 minutes before I measured**, i.e. *after* the item was drafted. The
third row has changed class since the item read it. **The population refills, and it refilled
inside the turn that was commissioned to clear it** — which is the condition the item itself named
as the finding: *"If the untracked population refills after a clear, THAT is the finding and the
instances are not the work."*

## But it refills at a trickle, and P1 was wrong about why the pile looks small

**P1 predicted ≥ 10 untracked `docs/staging/` paths that `origin/main` already carries. The answer
is 3 — exactly the blocking set. REFUTED.** My reasoning was that a cleared-window orphan lingers on
disk forever and the pile therefore grows monotonically. It does not linger, because the drain
genuinely fires: `refs/preserved/origin-reconcile-orphan/` holds **3 commits, one path each**
(2026-09-18, 2026-09-22, 2026-09-23), so since the orphan door was built on 2026-09-17 it has
cleared ~0.4 paths/day against a standing population of 2–3. The pile is small because it is
*drained*, not because it is finite. (43 other files are untracked under `docs/staging/`, but at
paths `origin/main` carries nothing at — never-landed drafts, a different pile and not this one.)

**P2 predicted ≥ 1 candidate mint/day. 267 distinct root-level `docs/staging/*.md` paths were added
on `origin/main` over 2026-09-17 → 09-24, ≈38/day. CONFIRMED**, by a factor of 38.

So the honest statement of the population — and it is neither of the two the item offered — is:
**self-refilling, at a rate the existing drain roughly keeps up with, and therefore not the wedge.**

## The second half, which inverts the item: no path is the cause of this wedge

The shared tree is **10 ahead / 9 behind** `origin/main`. `advance_shared_tree` asks `commits_ahead`
*before* it judges any path, and on a diverged tree returns, verbatim:

> git refused the fast-forward because this tree has **DIVERGED** — 10 local commit(s) that
> origin/main does not have. **No working-tree path is the cause** and clearing twins would delete
> files and still not advance, so nothing was touched.

**P3 CONFIRMED**, empirically and not only from source: called with an injected canned `ff` failure
and with `remover`/`restorer`/`locker` replaced by functions that raise on contact, it returned
`advanced=False, cleared=[]` with that reason and **reached none of the three**. Clearing the
orphans by the door the item named would have deleted three files and advanced nothing — the exact
"deletion bought for no advance" that `advance_shared_tree`'s all-or-nothing rule exists to prevent.

## Where the item's wrong instruction came from — and it is a live instrument, not a slip

`background/process_run_complete._refused_advance_cause` is the publish path's reader-facing
diagnosis. It asks `paths_blocking_fast_forward` and **never asks `commits_ahead`.** Run against the
live shared tree at `ahead = 10`, it answered:

> **VERDICT:** this is NOT merely the guard working: a tracked file this tree has edited is
> **holding the shared tree behind origin**. It belongs to whichever lane is holding it, and
> `python3 -m tools.isolate_hunks --survey` is how that lane lands its hunks without waiting
>
> **CLAUSE:** Refused by 4 path(s): … **THE STEP IS TO LAND OR REVERT THOSE PATHS**, NOT TO RE-RUN
> THIS MODULE … the 3 UNTRACKED path(s) clear by landing them or by removing them

Every operative sentence there is false on this tree. No path is holding anything. Landing or
reverting all four advances nothing. And *that instruction is, near enough word for word, the
direction I was commissioned to carry out.*

`_blocking_clause` — the single renderer both the reconciler's legs and the publish path share —
has the same blind spot: it attaches `_landing_clause`'s remedy to any non-empty path list, without
ever asking whether a fast-forward was possible at all.

**This is the VAT shape CLAUDE.md names.** One rule — *divergence is not a collision, and on a
diverged tree no path is the cause* — learned and paid for in `advance_shared_tree` on **2026-09-05**
(`behind 32, ahead 5`, 18 paths named, none of them the cause). Nineteen days later the two
reader-facing renderers beside it, in the same file and in its closest sibling, still do not know
it. A bounded tick cannot see this; it is only visible from the seat, which is where the item's own
instruction and the instrument that produced it can be held in one view.

## What is being built

`_blocking_clause` asks divergence for itself and, when the tree is diverged, leads with that and
withholds the landing remedy — so a path list cannot be read as a cause. `_refused_advance_cause`
derives its verdict with divergence checked first, so "a tracked file … is holding the shared tree
behind origin" cannot be said of a fork. The control keys to the **property** — *on a diverged tree,
no renderer names a path as the cause* — over the whole partition (diverged / dirty / clean), not to
today's four paths.

## What is NOT being done, and why

The three orphans are **not** cleared this turn. Clearing them is a deletion bought for no advance
while `ahead = 10`, and the fork closes by the gated merge door (`origin_reconcile`'s own merge leg
/ `surgical_land --merge origin/main`), which is a judgement and not a daemon's to make unattended.
The orphan drain is working at the rate the mint rate needs; it is not the problem and the instances
were never the work.
