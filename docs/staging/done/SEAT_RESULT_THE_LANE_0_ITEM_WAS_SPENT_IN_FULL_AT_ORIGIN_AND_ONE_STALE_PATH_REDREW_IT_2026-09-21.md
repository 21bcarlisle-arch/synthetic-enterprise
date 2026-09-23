**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, claim `rerun-the-arrivals-on-value-arm-leg-now-the-crash-is-fixed`

# The Lane 0 item was spent in full at origin, and one stale path in the local tree redrew it

*All four of the drawn item's asks were done and landed before this tick fired. The item was drawn
anyway, with its BLOCKING finding announced as live, because the draw asks **two different oracles**:
the premise check asks git (and got the right answer), while the staging census asks the
**filesystem** — `STAGING_DIR.iterdir()`, `background/supervisor.py:554` — of a shared tree that is
**13 commits behind `origin/main`**. **I predicted that staleness would inflate the unprocessed list
broadly; it does not — 1 of 48.** That one is the BLOCKING finding, and under RUNG 1c one is enough
to set an entire lane's draw order.*

---

## 1. The premise, re-measured — spent in full, not in part

| the item's ask | state at draw time | evidence |
|---|---|---|
| re-run the arrivals-ON value-arm leg | **DONE** 2026-09-19 18:28 | `arrival_decision_population.json`, `pass_seconds` 1491.4 |
| answer the pre-registration, prediction left uncorrected | **DONE** | landed `db00d334c` |
| §6 Owed — survey the `advance`-like class | **DONE** 2026-09-21 11:04 | landed `357b0e11b` |
| the finding dispositioned | **DONE** | `docs/staging/done/` on `origin/main` |

The tick fired at 12:00; `357b0e11b` landed at 11:04. **The last outstanding bullet was closed 56
minutes before this invocation was woken to close it.**

`3a8d15185` — the commit the doorbell's premise check flagged — was never the spend. It is the crash
fix the item cites as the *enabling* condition, correctly an ancestor. The premise checker reported
it accurately and the accurate report was not the useful one: **the question was never "did the
enabling commit land" but "did the enabled work land", and nothing asks that.**

The ON leg's answer, for the record and re-derived by nothing here: `decisions_that_existed`
**107 → 114**, scored **104 → 107**, 95% null half-width **0.11280 → 0.11164** (1.0% narrower — the
rank leg got the same, not cheaper). P2 confirmed, my P3a (point 95, band 85–107) **refuted**.

## 2. Why it was redrawn, and my own hypothesis is refuted

The draw's two oracles disagree because they read two different things:

* **premise check** → `git`, which resolves against `origin/main`;
* **staging census** → `STAGING_DIR.iterdir()`, a plain filesystem read of the working tree.

`HEAD...origin/main` reads **0 ahead / 13 behind**. Six of those 13 commits move staging documents
into `done/` or `reference/`, so the filesystem read cannot see those archivals.

**P5 (mine, written before the count): the stale tree inflates the unprocessed list substantially —
I expected on the order of six.** Measured over all 48 root-level `.md` files, comparing each
against its path on `origin/main`:

| | count |
|---|---:|
| already archived at origin, still at root here | **1** |
| still at root at origin — genuinely unprocessed | 31 |
| not at origin at all (untracked alarm drafts, local) | 16 |

**P5 is refuted.** The other five archiving commits move documents this tree never had at root. The
staleness is worth exactly one path — and I would have published "the queue is six deep in ghosts"
had I not counted.

## 3. One path is enough, and that is the finding

The single stale path is
`SEAT_RESULT_THE_WORLD_THAT_MINTS_ARRIVALS_CANNOT_FINISH_A_VALUE_ARM_PASS_..._2026-09-19.md`,
severity **BLOCKING**. Under RUNG 1c / OPS12 clause 3 a live BLOCKING finding draws ahead of the
general disposition queue, latent findings and all new feature work in its lane. So the doorbell
announced:

> lane A_strategy_governance carries a live BLOCKING finding ... drawing ahead of the general
> disposition queue, latent findings, and new feature work

**That finding has been closed at origin since 11:04.** A count of one, in the one severity that
orders a lane, held `A_strategy_governance`'s entire queue behind a defect that no longer exists and
spent this invocation re-deriving it. **A census whose miscount is one is not a census with a small
error; it is a census whose error is the only row that votes.**

## 4. The shared tree, measured and NOT claimed here

`WORKER_RESULT_THE_FORK_IS_CLOSED_AT_ORIGIN_..._2026-09-21.md` (claim
`close-the-fork-that-has-refused-eleven-publishes`, lane H_harness, BLOCKING) already owns this and
recorded **8 behind / 2 blocking paths** at 10:46 today. Re-read now via
`origin_reconcile.paths_blocking_fast_forward`:

| | 2026-09-21 10:46 | now (12:0x) |
|---|---:|---:|
| commits behind | 8 | **13** |
| paths blocking the fast-forward | 2 | **11** |

Eight are *modified here and origin changes them too* (`process_run_complete.py`,
`self_clearing_alarm_census.py`, `orphan_baseline.json`, `self_clearing_alarm_dispositions.json`,
`run_history.json`, `run_insights.json`, `LATEST.md`, `dashboard.json`); three are untracked drafts
origin adds at the same path. **The condition is widening, not holding.** I am not claiming the
repair — it is live under another lane's claim, and two lanes fixing one advance is how the
contested-path refusals in this tree get made.

**Corrected after the fact, beside the claim rather than over it.** The two rows above were read
**before this document landed**, on a tree that was `0 ahead / 13 behind` — purely behind, which is
the state the fast-forward path is for. Landing this document made it **`1 ahead / 13 behind`**, and
`advance_shared_tree` asks divergence FIRST and of git, not of the tree: a diverged tree refuses with
*"Diverging branches can't be fast-forwarded"* and the 11-path blocker list is no longer the binding
constraint. **The route for a diverged tree is `origin_reconcile.reconcile`'s merge-and-push, not the
advance** — the same route that gated clean and pushed at `6a9f49cf9` this morning. So the figures
stand as measured and the *reason* they are now moot is my own commit; any lane landing anything
would have done the same, and the refusal touches nothing, by construction. **Read the 13-behind as
the live number and the 11 blockers as a reading taken at `0 ahead`.**

**The recursion is worth naming.** Blocker 9 of 11 is
`docs/staging/SEAT_RESULT_THE_PAIRING_CLASS_IS_EMPTY_..._2026-09-21.md` — *untracked here, and
origin adds its own copy*. The document that discharged this claim's last owed bullet is itself one
of the paths holding this tree behind the commit that landed it. **The work arriving is what keeps
the tree from seeing that it arrived.**

## 5. What this turn did and did not do

**Did:** re-measured the premise across all four asks; counted the census error rather than
asserting it; recorded P5's refutation beside it; measured the advance blockers as a delta against
the prior finding's own figures.

**Did NOT, and does not claim:** the shared-tree advance (§4, another lane's live claim); any re-run
of either value-arm leg; any change to the survey or its tool. **Nothing in §1 was re-derived — it
was read off disk and off `origin/main`.**

## 6. Owed

- **Nothing on this claim.** It is released at the end of this turn; all four asks are spent.
- **Not claimed here, and pointed at rather than filed twice:** that the staging census reads the
  filesystem while the premise check reads git. The repair that closes it is the shared-tree
  advance already owned by `close-the-fork-that-has-refused-eleven-publishes`. **If that advance
  lands, this defect disappears without anyone writing a line against it** — which is the argument
  for not minting a second control here, and the reason this document is LATENT and not BLOCKING.
- **Left open, honestly:** whether the draw *should* cross-check the staging census against
  `origin/main` rather than depending on the tree being current. That is a real design question and
  a one-line `git ls-tree` could answer it per-file — but it is a control over a control, and
  CLAUDE.md's own rule says do the work (advance the tree) before building the thing that watches
  the work. **Recorded so the next seat can overrule me with the reasoning visible.**
