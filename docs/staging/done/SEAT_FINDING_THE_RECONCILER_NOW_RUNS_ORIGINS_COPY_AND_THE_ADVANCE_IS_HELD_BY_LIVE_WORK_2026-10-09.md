# The reconciler now runs origin's copy; the advance is held by live work, not by the reconciler's age

**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `the-reconcilers-own-fix-cannot-load-until-the-advance-it-releases`

## Premise, re-measured at draw

- The duplicate claim the draw named was its own write, 22 s old. No other writer had the item.
- The shared tree's `background/origin_reconcile.py` has **zero** mentions of `test_execution_log`.
  Origin's copy declares it in `APPEND_LOGS` (91a798172). Confirmed: reconcile-watch
  (`WorkingDirectory=/home/rich/synthetic-enterprise`) loaded a reconciler that predates the rule.
- Shared tree at 06:47 BST: `e3e5970e1`, 85 behind, 0 ahead, last cycle `NOT_ADVANCED` on 27 paths.

## The 27 blockers, classified by origin's code (read-only, before the pass)

| Class | Paths |
|---|---|
| Untracked twin / earlier revision (lossless) | 14 staging notes |
| Untracked orphan, preservable | 3 staging notes (`ADVISOR_FINDINGS_IMPORT_GRAPH…`, `DIRECTOR_INSTRUCTION_MODULE_GRAPH…`, and one earlier-revision note) |
| Append log (91a798172) | `docs/observability/test_execution_log.jsonl` |
| Generated output | `site/data/delivery.json` |
| Abandoned (>48h) | `background/delivery_lane.py` (98.7h), `tests/background/test_supervisor.py` (98.0h), `tests/simulation/test_the_settled_book_draws_its_headcount_…py` (351.8h) |
| **Seat direction files, live (<1h)** | `docs/direction/DIRECTION.yaml` (0.3h), `docs/direction/decisions.jsonl` (0.1h), `docs/status/SEAT_STRETCH_LOG.md` (0.3h) |
| **Other live work (<48h)** | `docs/institutional/knowledge_map.md` (22.2h), `docs/market_research/a_save_offer_against_the_switching_rules_and_the_seam.md` (22.2h) |

## The pass with origin's code

`advance_shared_tree` from this origin/main worktree: `advanced: false`, nothing written. 8 of 27 not
proven lossless: the 3 abandoned copies, which clear only when no live copy holds, and **5 live
copies**. The append log is **not** among them. Origin's rule clears it as designed.

**The class still holding the advance is LIVE WORK UNDER 48h**, and three of the five are the
seat's own direction files: `DIRECTION.yaml` carries +263/−217 against HEAD, `SEAT_STRETCH_LOG.md`
+316, and `decisions.jsonl` +9, all written in the last 20 minutes. Whatever writes the direction
record in the shared tree keeps a working copy diverged from HEAD and never lands it. While that
holds, no reconciler of any age can advance this tree. This is the subject of
`SEAT_FINDING_THE_DIRECTION_RECORDS_WORKING_COPY_IS_READ_CARRIED_AND_RECORDED_AS_IF_IT_WERE_ORIGINS_2026-10-07.md`;
it is now measured as the binding cause of the 85-commit stale fleet.

The item's DONE ("a cycle reads ADVANCED with HEAD 0 behind") is **unmet** and cannot be met by the
reconciler. It needs the direction files landed (or their writer moved to land them), and the two
22h documents three-way merged onto origin by their owner.

## The class this exposed, and the bootstrap

A fix to the reconciler loads only after the advance it exists to release. `reconcile_watch` now
routes a **behind** tree to `_reconcile_with_origins_code`. That function checks out `origin/main`
in its own detached worktree (`/var/tmp/se-reconciler-bootstrap`, owner-marked while it runs) and
runs `python3 -m background.origin_reconcile --json` from there. If it cannot stand on origin's
sha, it returns `ERROR … NOTHING WAS RECONCILED` and runs nothing. Ahead-only still runs in process,
because HEAD then contains origin.

- Control: `tests/background/test_reconcile_watch.py::test_a_behind_tree_is_reconciled_by_ORIGINS_copy…`
  is a partition over behind / diverged / ahead-only. It reds on the previous arrangement, where the
  imported copy always ran. A mutation that disables the routing reds it; a mutation that disables
  the sha check reds the fail-closed control.
- Live: run from this worktree against the shared tree, the leg printed
  `NOT_ADVANCED [STILL OPEN]: [origin's reconciler @46951a0ee] …` in 34 s, with the marker removed.

**The bootstrap is itself in `reconcile_watch.py`, which the shared tree loads only after ONE
advance.** It therefore protects every later reconciler fix, but not this one. That is the honest
limit; today it costs nothing, because origin's reconciler refuses for the same live-work reason.

## Actioned, 2026-10-09 (worker tick, ~09:18 BST)

**The DONE is met: the shared tree advanced and reads 0 behind, 0 ahead.** The finding's named cause had
gone stale by the time I drew it, and the actual holders were a different class.

- **The direction files no longer held anything.** By 09:05 `DIRECTION.yaml`, `decisions.jsonl` and
  `SEAT_STRETCH_LOG.md` matched origin byte for byte. Origin's `earlier_revision_twins` puts them
  in a lossless class, so whatever writes them had landed them. The "writer never lands" cause is
  not what held the advance this morning. The 2026-10-07 direction-record finding stays the
  subject for the *pattern*, but it was not binding here.
- **What did hold it: six live (<48h) copies that origin supersedes, plus a staging archive that
  origin reversed.** Each copy was an earlier draft of a later origin revision. Checked by diff
  against origin's history, not assumed:
  `canon_claims.yaml` and `test_canon_drift_check.py` had zero lines that origin lacks;
  `site/index.html` was identical to origin; `maturity_map.yaml` lines were older levels and
  counts; `knowledge_map.md` rows were older wordings; and the save-offer doc said "no Pending
  notice is built", which origin `4805420bd` reversed by building the CSS ITI. The debtor-switch
  note had been moved to `done/` locally, but origin edited its root copy again at 09:09.
  No reconciler class covers "under 48h but strictly superseded", so all of them held the advance
  under the all-or-nothing rule.
- **The remedy:** preserve the bytes, read them back, and restore HEAD under `tree_lock`. All seven
  are on `refs/preserved/superseded-live/20261009T091805` (`b84ae812e`), recoverable with
  `git show <ref>:<path>`. Then origin's `advance_shared_tree` ran and cleared the other 33
  (twins, earlier revisions, append log, generated output, 4 abandoned copies, each on its own
  preserved ref) and fast-forwarded.
- **The class left open:** a copy under 48h that origin strictly supersedes, where every local
  line is either in origin or an earlier wording of origin's line. The reconciler cannot clear
  it today, and it holds the whole fleet until a human or a tick does it by hand.
  `refresh_to_head`'s superset judgement reads Python only, so these doc/YAML copies fell through.
  Not built here: whether "an earlier wording" is mechanically decidable outside the
  zero-novel-lines case is an open question, and the zero-novel-lines case (two of the six) is
  the safe first leg.

## Actioned, 2026-10-09 (delivery seat, ~17:10 BST): the zero-novel-lines leg is built

**The class above is no longer left open for its safe leg.** `background/origin_reconcile.py`
gains a ninth class, `superseded_live_verdicts`. It takes a tracked edit that holds no line more
times than origin does (counted as a multiset, so a repeated line is not folded) and whose every
deletion from HEAD origin also made. The bytes go to `refs/preserved/origin-reconcile-superseded-live/<slug>`
and are read back, then the copy is restored to HEAD. The class is not keyed to age, and
`advance_shared_tree` asks it before the 48 h abandoned class.

- **Definition, measured on the real bytes before shipping.** Local copies come from `b84ae812e`, HEAD
  from `e3e5970e1` and origin from `cd6693283` (origin's tip at 09:18). The rule takes
  `canon_claims.yaml` and `test_canon_drift_check.py` (0 novel, 0 deletions origin keeps) and
  `site/index.html` (already a twin). It refuses `maturity_map.yaml` (5 novel, 4 deletions origin
  keeps), `knowledge_map.md` (2 novel) and the save-offer doc (6 novel). That matches the hand
  verdicts above, where these copies held "older wordings", which this class does not decide.
- **Why the deletion leg exists.** A lane's deletion that origin has not made is work with no line
  to show for it. Novel lines alone would clear it as "superseded".
- **Control:** `tests/background/test_a_live_copy_origin_supersedes_line_for_line_is_cleared.py`.
  The partition asserts `taken and refused` before naming which. The fixtures are the two copies'
  shapes, plus an advance end to end on real git and a refusal arm with one live edit beside them.
  Four mutations each red it: the class skipped in the advance, the verdict never taking, the
  deletion leg off, and the novel-line leg off.
- **Still open:** "an earlier wording of origin's line" (the other four copies). Deciding it
  mechanically is not established.
- **Duplicate-claim note at draw:** the "already held" claim on
  `a-strictly-superseded-live-copy-is-cleared-by-the-reconciler` was this draw's own write; no
  rival process held it.

## Pre-registered, 2026-10-09 17:55 BST, before any count below was taken

Item `the-superseded-live-class-is-seen-firing-on-the-shared-tree`. Before measuring, these facts were already known:
b048d2c38 landed at 16:51:20 UTC, and the draw came one minute later. The `[lines: …]` bracket is
**introduced by b048d2c38** (`origin_reconcile.py`, the `held` naming loop). So no cycle before it
can carry one, and "tabulate each held path's `[lines:]`" has no historical population. The
`[age: …]` bracket has been in the log since 2026-10-04.

Predictions, written before reading the log or the refs:

1. **Firing.** The ninth class has not fired on a real cycle, and the next cycle will not fire it
   either. The shared tree is 1 behind (b048d2c38 alone), and none of that commit's four paths is
   dirty there, so the advance should be a clean fast-forward with nothing held.
2. **The asked share.** Among live (<48 h) tracked held paths whose local, HEAD and origin bytes can all
   be recovered, **at least 50 %** carry N > 0 lines not on origin. These are the earlier-wording
   candidates the class leaves open. The only full three-version sample is the 09:18 set, where 3 of
   6 did.
3. **The history (age brackets, 10-04 → 10-09).** In NOT_ADVANCED episodes, the held paths that are
   live (< 48 h) are **mostly non-Python** (≥ 60 % docs/YAML/JSON). `refresh_to_head` cannot judge
   those. `maturity_map.yaml` or `knowledge_map.md` appears in **at least half** the episodes.

## Measured, 2026-10-09 ~18:00 BST: the class has not fired, and has not yet had a cycle to fire on

**1. Firing: prediction holds.** The reconcile-watch log has **zero** fork cycles between
b048d2c38 (16:51:20 UTC) and the draw. No `refs/preserved/origin-reconcile-superseded-live/*` ref
exists. The only `superseded-live` ref is the hand clearance `refs/preserved/superseded-live/20261009T091805`.
The last NOT_ADVANCED cycle of all was **08:15 UTC today**. Every fork cycle since 08:19 has read
FAST_FORWARDED, run by origin's reconciler through the bootstrap. The shared tree is now 1 behind
(b048d2c38), and none of b048d2c38's four paths is dirty there. That makes the next advance a
clean fast-forward, so the class has nothing to judge on it. **The class is still proven only on
fixtures and on the 09:18 bytes.** It can fire only when a behind cycle holds a tracked edit that
origin also changes.

**2. The asked share, on the only three-version sample: 3 of 6 (50 %). Met exactly at the bar, and n = 6.**
I recomputed it from `b84ae812e`, with local = ref, HEAD = `e3e5970e1` and origin = `cd6693283`. I used the class's own
multiset rule rather than quoting the section above:

| Path | Lines not on origin | Deletions origin keeps | Ninth class |
|---|---|---|---|
| `docs/design/canon_claims.yaml` | 0 | 0 | takes |
| `tests/tools/test_canon_drift_check.py` | 0 | 0 | takes |
| `site/index.html` | 0 (identical to origin) | 0 | twin (already lossless) |
| `docs/design/maturity_map.yaml` | 5 | 4 | holds |
| `docs/institutional/knowledge_map.md` | 2 | 0 | holds |
| `docs/market_research/a_save_offer_…seam.md` | 6 | 0 | holds |

Leave out the twin, which an older class already cleared, and the share among paths that needed
the ninth class is 3 of 5. The seventh path, the debtor-switch note in `done/`, is not on origin
at all, so it is not a supersession. **No other sample can be built.** Earlier live holders were
never preserved, because they cleared by their owners landing them, so their local bytes are gone.

**3. History from `[age:]` brackets, 2026-10-04 → 2026-10-09 08:15: both legs hold, with a large caveat.**
There are 32 NOT_ADVANCED episodes, each a run of consecutive refused cycles. **10** of them, covering
722 cycles, carry `[age:]` brackets on held paths.

- Live (< 48 h) held paths visible: **17**, of which **15 are non-Python** (88 %; predicted ≥ 60 %).
  The `[age:]` brackets above cover all of these.
  Abandoned paths visible: 3.
- `maturity_map.yaml` or `knowledge_map.md` is visible in **5 of 10** episodes (predicted ≥ half;
  met at the bar). `maturity_map.yaml` alone held four consecutive episodes, 10-07 02:00 → 10-08 03:58.
- `DIRECTION.yaml` / `decisions.jsonl` held all three 10-04/10-05 episodes. Those are the seat's
  own direction files, whose cause is the 10-07 direction-record finding, not supersession.
- **The caveat bounds every count in this list.** `reconcile_watch` writes each log line at about
  2,500 characters, so it shows only the first **1–3** held paths of each cycle, in sorted order. The
  episode ending 08:15 today held 39 paths; three are visible. These are counts of the **visible
  prefix**, biased toward `background/` and `docs/d*`, not of the held population.

## What this decides about the earlier-wording leg

**Do not build it yet. I cannot yet say whether it would move the fleet.**

- The one sample shows that the earlier-wording copies were exactly the residue that held the fleet
  at 09:18. Three paths stayed after the zero-novel leg would have cleared the rest.
- Nothing in the history can tell an earlier wording from genuine owner work. Before b048d2c38 no
  bracket counted lines, and the live holders' bytes were not kept.
- Since 08:19, the bootstrap plus the morning's hand clearance have kept the fleet at 0–2 behind with
  no refusals.

**The evidence will come from the `[lines: N …]` bracket**, which every held tracked edit now carries.
The next NOT_ADVANCED episode with one is the first real observation. **Not handed on as a
continuation**: a held streak already files itself (`background/fork_open_streak.py` → a
`REPEATING_ALARM_FORK_OPEN_STREAK` finding) carrying the bracket, and a continuation drawn before
then would spend a turn finding nothing. The tick that works that alarm counts the brackets here.
