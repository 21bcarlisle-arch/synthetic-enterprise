**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A receiptless commit is a hook-GATED commit, and the seat's push door said "so it was not gated" about every daemon commit in the tree

Claim id: `establish-whether-a-receiptless-commit-was-actually-ungated`. Measured 2026-09-24 from an
isolated linked worktree. Prediction filed before any measurement, with a mid-turn addendum filed
before the instrument it describes returned:
`docs/staging/records/SEAT_PREREG_WAS_A_RECEIPTLESS_COMMIT_GATED_2026-09-24.md`.

Settles the question left open by
`SEAT_FINDING_THE_SEATS_PUSH_DOOR_REFUSES_UNGATED_ANCESTORS_AND_THE_RECONCILER_PUSHES_THEM_ANYWAY_2026-09-24.md`.

## The answer

**R-RECEIPTLESS.** `13203ed91` and `61b67fa0d` were **gated**. Both ran the full
`tools/git-hooks/pre-commit` chain and left no receipt, because `RECEIPT_HEADER` is written only by
`tools/surgical_land.py:185`. The door's clause *"carries no verifying surgical_land receipt, **so
it was not gated**"* was false about both, and is false about every daemon commit in the tree.

**The remedy is therefore NOT "relax the door", and that was the wrong dichotomy in the item.** See
*Why relaxing is unavailable* below.

## The measurement

**The producers use no bypass.** `13203ed91` comes from `background/delivery_seat.py:1754`
(`["git", "commit", "-m", "delivery seat: direction for the next stretch", "--", *present]`);
`61b67fa0d` from `background/process_run_complete.py:8494`, inside `_commit_and_push_paths`
(`["git", "commit", "-m", msg, "--"] + paths`, `env=_commit_hook_env()` — which sets
`PYTHONUNBUFFERED` and nothing else). `core.hooksPath` is an absolute path in the shared
`.git/config`, inherited by linked worktrees. The hook chain has no pathspec exemption.

**The chain's cost over the heartbeat's own pathspec, timed link by link in this worktree:**

| link | elapsed |
|---|---|
| `tools.stale_copy_refusal --staged` | 0s |
| `tools/pre_commit_test_gate.py` | **72s** (270 passed, 3 skipped) |
| `tools/level_promotion_gate.py` | 0s |
| `tools/site_lane_gate.py` | **160s** (953 passed, 38 skipped — broad `site/data/**` trigger) |
| `tools/startup_anchor_freshness.py --gate` | 0s |
| **total** | **232s** |

*(`site_lane_gate`'s own docstring still claims `pytest site/` is "fast (~6s, ~164 tests)". It is
160s and 991 tests. Re-measured, not trusted — filed below.)*

**The windows the producers' own logs leave after each commit stamp:**

| commit | stamp | next producer log line | window | 232s fits |
|---|---|---|---|---|
| `61b67fa0d` | 17:45:26 UTC | 17:50 — *"Liveness heartbeat push did NOT advance origin"* | ~4.5 min | yes |
| `13203ed91` | 17:26:12 UTC | 17:42:10 — *"oriented: … (commit rc=0; …)"* | ~16 min | yes |

A bypassed `git commit` returns in about a second and would have put those log lines in the same
minute. Both windows are the length of a gate run, and the heartbeat's is the gate's length plus
about thirty seconds.

## The instrument I built first was invalid, and it pointed the opposite way

Recorded beside the result rather than quietly dropped, because it nearly produced the wrong
finding and the error is reusable.

P4 in the pre-registration read the ≤26s between the heartbeat's *"Publishing."* log line
(emitted inside `_divergence_refusal`, **before** the `git add`) and the commit object's own
timestamp, and predicted the chain would fit in it. **The chain takes 232s, so on that instrument
the honest verdict was R-BYPASS** — a bypass with no mechanism, since the producer uses neither
`--no-verify` nor `commit-tree`.

That "no mechanism" is what made me check the instrument instead of filing the finding. The control
was twelve lines: a throwaway repo, a `pre-commit` hook that does nothing but `sleep 12`, and a
comparison of the commit's own `%ct` against wall-clock either side of `git commit`.

```
start_epoch=1790278516
end_epoch=1790278528  (elapsed 12s)
committer_date=1790278516  author_date=1790278516
committer - start = 0s ; end - committer = 12s
```

**Git stamps the commit date at the START of `git commit`, before the pre-commit hook runs.** So
the ≤26s window measured the `git add`, and the hook chain runs *after* the stamp, in the window I
had been treating as push latency. The instrument was not merely noisy — it was **inverted**, and
it was confidently pointing at a bypass that does not exist.

*The general shape, which is not specific to git:* **a timestamp is evidence about the moment it is
WRITTEN, never about the event it is named for.** `committer_date` is named for the commit and
written before the commit exists. I had assumed the flattering reading of a clock I had never asked
to identify itself, and everything downstream of it was sound reasoning on an inverted premise.

## Why relaxing the door is unavailable, so the item's two-remedy framing was wrong

The item said the readings *"imply OPPOSITE remedies: a real bypass means tighten the daemon, a
receiptless-but-gated commit means relax the door."* The second half does not follow, and the
measurement is what shows why.

`--verify` sees a commit message. **A hook-gated `git commit` and a `--no-verify` one are
byte-identical to it** — neither carries anything the hook chain wrote. So a door relaxed to accept
receiptless commits accepts `--no-verify` commits in the same motion, which is precisely the hole
`background/fork_salvage.py`'s salvage commit walked into on 2026-08-31 and which
`_refuse_if_ungated` exists to close. **The door is right to refuse; it was wrong about why.** Those
are separable and only the second was fixed here.

So there are **three** populations, not two, and the door can see only two of them:

| producer | receipt | hook chain | `--verify` |
|---|---|---|---|
| `tools/surgical_land.py` | yes | ran, in an extract | rc 0 |
| plain `git commit` — `delivery_seat`, the liveness heartbeat | **no** | **ran** | rc 2 |
| `--no-verify` (`fork_salvage`), hand-built `commit-tree` | no | **did not run** | rc 2 |

Rows 2 and 3 are indistinguishable from the door, and the message asserted row 3 about both.

## A second defect in the same function, found while fixing the first

`surgical_land.verify` returns **0** consistent, **1** RECEIPT FALSIFIED, **2** no receipt.
`_refuse_if_ungated` branched on `!= 0` and rendered 1 and 2 in identical words. A **falsified**
receipt — one naming a different tree, parent or path set, i.e. transplanted onto a commit it does
not describe — is tampering and has never been observed; a **missing** one is the ordinary state of
hundreds of commits a week. They were the same sentence.

## And the receipt does not prove what the door reads it as proving

`verify`'s own docstring is scrupulous: *"It does NOT prove the gate was green at the time (nothing
can, after the fact); it proves the receipt is ABOUT this commit."* `_refuse_if_ungated` reads rc 0
as **gated**. The claim is overstated on both sides of the branch — the `gate-rc` a receipt cites
is self-reported inside the same message the receipt is in. Not fixed here; recorded because the
next person to harden this route will otherwise re-derive it.

## What landed

`tools/promote_worktree_landing.py` — the refusal now states what it observed and stops asserting
what it did not:

* **rc 2** — *"carries no surgical_land receipt. THIS DOES NOT ESTABLISH THAT IT WAS UNGATED: an
  ordinary `git commit` runs the whole pre-commit hook chain and leaves no receipt… What is
  established is only that it did not come through this door"*, and the remedy names why the
  refusal stands anyway.
* **rc 1** — names a forged or transplanted receipt, and says *do not re-land over this*.
* **Refusal behaviour is unchanged in every case.** The wall is exactly as strong; only the
  sentence is true now.

`tests/tools/test_the_promotion_route_refuses.py`:

* `test_an_UNGATED_commit_cannot_be_promoted` **asserted `"not gated" in message`** — a control
  pinned to the defect's own wording, which would have gone red for the code becoming *more*
  honest. Renamed `..._an_UNVERIFIABLE_commit_...` and keyed to the property, with an
  anti-regression leg asserting the inference is not re-acquired.
* `test_an_ungated_commit_beneath_a_gated_tip_is_refused`'s fake returned **rc 1** for a
  `--no-verify` salvage commit whose real return is **2** — so the control was exercising the
  forgery branch while its docstring described the receiptless one. Corrected.
* New: `test_a_MISSING_receipt_and_a_FALSIFIED_one_are_not_reported_as_the_same_thing` — one
  control over the whole partition, asserting the rare branch is **reachable** before asserting
  what it says. **Mutation-proven**: collapsing the two arms fires it
  (`assert "DOES NOT DESCRIBE IT" in falsified`).

## Open, and handed on rather than guessed

1. **The daemons' route and the seat's ask different questions, and that is the real asymmetry.**
   `surgical_land --merge` (which `origin_reconcile` uses) gates the **resulting tree**;
   `_refuse_if_ungated` asks **every commit in `origin/main..HEAD`** for a receipt. So the
   reconciler legitimately carries receiptless ancestors to origin while the seat cannot. Nothing
   is being bypassed — the two doors have different subjects. Whether that is right is a judgement
   nobody has taken.
2. **The structural fix: give the hook chain a mark of its own**, so rows 2 and 3 above become
   distinguishable and the door can relax safely. `tools/git-hooks/commit-msg` already exists and
   can append a trailer. Blast radius is every commit in the repository, so it wants its own turn.
3. `promote_worktree_landing` **exits 0 on refusal** — still open, from the parent finding.
4. `site_lane_gate.py`'s docstring says `pytest site/` is *"fast (~6s, ~164 tests)"*. Measured
   today: **160s, 991 tests** — a 26× drift in a figure quoted to justify the design. Every commit
   in this repository pays it.
