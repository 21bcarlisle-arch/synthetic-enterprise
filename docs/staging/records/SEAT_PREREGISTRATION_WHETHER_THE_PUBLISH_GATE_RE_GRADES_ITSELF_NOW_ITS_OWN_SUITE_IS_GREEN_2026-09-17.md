# PREREGISTRATION — does the publish gate re-grade itself now that its own suite is green?

**Kind:** preregistration
**Author:** delivery seat (lane 0), 2026-09-17
**Written at:** 2026-09-17T04:35Z, BEFORE running any of the three measurements below.
**Subject:** `docs/observability/.publish_gate_state.json` on the shared tree
(`/home/rich/synthetic-enterprise`), and the 12 node ids it names in `blocking_tests`.

---

## Why this is written before the answer

The drawn item asserts two things about the tree, and both are predictions until measured:

1. that the 14 ledger-guard failures are fixed and landed at `159a2d4fc`, so the 12 named
   `blocking_tests` are now green;
2. that the *remaining* wedge, if any, is the publisher losing the HEAD ref lock — the item
   quotes `fatal: cannot lock ref HEAD: is at aff4b153f but expected 56d746816` from the last
   `liveness_surface_refusal`.

Claim 2 is **already refuted by reading the file** — no measurement needed, so it is recorded here
as an observation, not a prediction. The live `liveness_surface_refusal` at 2026-09-17T04:03:02Z
reads `cause: push_never_landed`, evidence `push rc=1, origin=6e02d6442, head=93e3cf396`. The
ref-lock refusal the item quotes is no longer the latest one. What follows is therefore a
*different* attribution question from the one the item posed, and that difference is the point.

## Facts already established by reading (not predictions)

- `origin/main` = `eb5ee25a8`. The shared tree's `HEAD` = `93e3cf396`, and
  `git merge-base --is-ancestor 93e3cf396 origin/main` is **false**: the shared tree is on a
  genuine fork whose merge base with origin is `d316e039b`.
- `last_clean_publish = null`, `wedge_since = 1789011039.74` = **2026-09-10T03:30:39Z**,
  `episode_clean_publishes = 0`, `episode_failures = 52`, `total_red = 23`,
  `red_census = complete`, `red_at_head = not_established`.
- So the gate has **not** re-graded: `wedge_since` has not moved in seven days, and it is
  `None`-on-clean-publish by construction (`process_run_complete._read_publish_gate_state`).
- All three commits the item cites (`159a2d4fc`, `aff4b153f`, `56d746816`) are ancestors of
  `origin/main`, so the premise that the fix landed is intact.

## The predictions

**P1 — the named reds.** Running the 12 `blocking_tests` node ids at `origin/main` (`eb5ee25a8`)
in this isolated worktree, **all 12 pass**. Confidence: moderate. The failure mode I expect if I
am wrong is not "the ledger-guard fix didn't work" but "one or more of these node ids no longer
exists", because four of the five named test files have been rewritten since `wedge_since`.

**P2 — why the state is stale.** `blocking_tests`, `total_red` and `suspects` are cleared only by
`_clear_blocking_tests()` on a **rc=0 publish cycle**, and `last_clean_publish` is only stamped by
one. So the stale 12 will persist however green the suite is, until a publisher cycle completes
end-to-end. I predict the state file is **not** self-correcting on any other path, and that no
test asserts it is.

**P3 — the actual remaining cause.** The publisher now fails *after* the hook chain, at the push:
it commits onto the shared tree's local branch, `git ls-remote` shows origin never took it, and
the refusal is recorded as `push_never_landed`. My prediction is that this is **not** a transient
lost race but a standing consequence of the fork: origin advanced to `eb5ee25a8` by another lane
while the shared tree built `cd6f06c5d` → `93e3cf396` on top of `d316e039b`, so a plain push can
only ever be rejected as non-fast-forward, and **every** subsequent publisher cycle will record
`push_never_landed` until the fork is reconciled. If that is right, the wedge is neither the reds
(fixed) nor the ref lock (superseded) but the fork — a third cause.

**What would refute P3:** a push failure whose evidence shows origin *at or behind* the shared
head (a genuine race), or a shared head that is an ancestor of origin/main. Either would mean the
refusal is transient and the next cycle clears it.

## P4 — added 2026-09-17T04:52Z, after P1–P3 resolved and BEFORE the run it describes

Added honestly out of order, because reading `docs/observability/.last_gate_blocking_tests.json`
refuted the framing P1/P2 were written under. That record is **not** stale: `ts = 1789617470.34` =
2026-09-17T03:57:50Z, `git_hash = 882ef8aad`, `census = complete`, `total_red = 23`. So the 12 node
ids were re-measured 35 minutes before I read them — at `882ef8aad`, which is a commit on the
**fork**, not on `origin/main`.

That makes P2 half wrong in a way worth recording: the state is not stale in the sense of "written
before the fix landed". It is *current* and it is measured *on a different tree*.

**P4:** running the same 12 node ids at `882ef8aad` — the commit the gate actually graded — they
are **red**, or at least some of them are, because a complete census at 03:57Z found 23 reds there
while `origin/main` at `eb5ee25a8` runs all 12 green (P1, measured). If instead they run **green**
at `882ef8aad` too, then the gate's red is not attributable to the tree it names either, and the
census is measuring something other than the checked-out commit — a strictly worse finding, and one
I would not expect.

## Done means

The attribution above is measured and written into a finding in `docs/staging/`, and landed. I am
explicitly **not** re-fixing the 12 reds, and **not** reconciling the fork inside this turn
without first establishing that the fork is what it looks like — pushing or merging the shared
tree's divergent commits is another lane's uncommitted-adjacent work and the seat does not do it
blind.

---

*Related:* `docs/staging/records/SEAT_PREREGISTRATION_THE_PUBLISH_GATES_OWN_SUITE_IS_RED_ON_ONE_INCIDENTAL_LIVE_WRITE_2026-09-17.md`,
`docs/staging/reference/CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md`.
