# [SEAT FINDING] The third drawn channel read the log from whichever tree imported it, so a worktree orientation lost it silently

**Severity:** LATENT (fixed in this commit; it was reachable but had not yet been observed biting a
live tick) · **Lane:** H_harness
**Epoch:** 3 · **Atom:** none — this is Lane 0 delivery machinery
**Found:** 2026-09-02 by the delivery seat, while VERIFYING the commit that built the channel —
not by reading it. The commit's own claim was true on the tree it was measured from.

## Class registration

`controls_that_cannot_fail`. R15's fail-silent killer, and the same one twice in one day: an
instrument reporting something other than its subject, quietly. The first was an exit code standing
in for a landing. This is a path constant standing in for a tree.

## 1. What was found, measured on both trees at the same commit

`6d18107c7` added `seat_executor.ids_run_since` as a third channel for
`delivery_seat.focus_drawn_since`, so a Lane 0 steer that IS biting cannot read as one that is not.
It works. It worked only from the shared tree.

Same commit, same code, two trees, 2026-09-02:

```
from /home/rich/synthetic-enterprise   ids_run_since(now-24h) -> 9 ids
from /var/tmp/se-seat-executor         ids_run_since(now-24h) -> []
```

`LOG_FILE` is `Path(__file__).resolve().parent.parent / "docs/observability/seat-executor-log.md"`.
Imported out of a linked worktree that resolves *inside the worktree*, where the log is not — the
log is untracked, so a worktree checkout never has one. `ids_run_since` catches the `OSError` and
returns `[]`, deliberately and correctly, so nothing raised and nothing was logged.

## 2. What that made true

`focus_drawn_since` unions three channels. A channel that answers `[]` because it could not see its
artefact is indistinguishable, inside a union, from one that answers `[]` because nothing happened.
Run from the worktree, `build_brief` reported:

```
"drawn": [], "steered": false,
"note": "the previous direction named work and NONE of it was drawn -- if this repeats,
         the steer is a no-op and the weight is not biting"
```

Run from the shared tree, the same call at the same instant:

```
"drawn": ["an-exit-code-is-not-a-landing"], "steered": true,
"note": "the previous direction named work the draw then took"
```

**That is the precise false reading the channel was built to abolish**, reintroduced by path
resolution rather than by logic — and it advises the reader that the steer is a no-op, which is the
conclusion that makes a seat re-rank around work already in hand.

**Reachable, not theoretical:** a drawn tick runs in a worktree and CLAUDE.md tells it to orient
there. The two instruments that would notice are the two that cannot: the channel reports itself
empty, and the note reports the emptiness as a finding about the steer.

## 3. The repair

`_shared_tree_log()` asks `git rev-parse --git-common-dir` — "where is the real tree" put to the
only thing that knows — and reads the log from there. `path=` still overrides, because a test wants
a fixture and a live channel wants the shared artefact, and only the explicit argument holds both.
Falls back to `LOG_FILE` when git will not answer or the shared copy is absent, so the repair can
never turn a readable log into an empty one.

## 4. Mutation record

`test_the_channel_reads_the_SHARED_trees_log_not_the_importing_trees` and
`test_a_shared_tree_with_NO_log_falls_back_to_this_trees`.

| Mutation | Result |
|---|---|
| `ids_run_since` default reverts to `LOG_FILE` | **CAUGHT** |
| `_shared_tree_log` always returns `LOG_FILE` | **CAUGHT** |
| Drop the `shared.exists()` fallback | **CAUGHT** |
| Drop the `git rev-parse` refusal guard **alone** | **SURVIVED — established equivalence** |
| Drop **both** guards together | **CAUGHT** |

The survivor was established rather than assumed: a failed `rev-parse` yields empty stdout,
`Path("")` is `Path(".")`, and the derived path then does not exist — so the `exists()` fallback
already catches it. The two guards are one control with two expressions, each making the other
unreachable, so the honest mutation moves both. Recorded in the test's own docstring. Same shape
`ids_run_since` already documents for its stand-down exclusion.

## 5. Pre-registered predictions about the ORIGINAL verdict, and how they scored

Registered before any mutation ran, to settle whether `6d18107c7`'s "mutation-proven" claim held.
Eight mutations of the two verdict legs and the refusal: **all eight CAUGHT.**

`subject_moved` failing open; the verdict reverting to `returncode`; leg 2 deleted; leg 1's
freshness clause deleted; three-dot → two-dot; an unreadable shared tree failing open; a
`LANDED NOTHING` turn discharging anyway; the refusal ceasing to name its cause.

**One prediction refuted, kept here beside the result.** I predicted three-dot → two-dot would
**SURVIVE**, reasoning that divergence attribution needs a genuinely divergent git fixture that a
dry-run suite would not build. It was **CAUGHT** — the suite does build live git fixtures. The
control was stronger than I gave it credit for, and the verdict half of the direction needed
nothing from me.

**The verification is what found this finding.** Re-running a landed claim's own measurement from a
different tree cost one command and turned a "complete" into a defect of the same class the commit
was written to remove.
