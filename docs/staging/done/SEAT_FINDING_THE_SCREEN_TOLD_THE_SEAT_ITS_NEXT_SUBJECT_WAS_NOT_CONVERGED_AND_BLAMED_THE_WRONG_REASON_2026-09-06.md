**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# FINDING: the screen told the seat its next subject was not converged, and blamed the wrong reason

**Measured 2026-09-06, delivery seat, isolated worktree at `69f0a59a1`, claim id
`converged-battery-next-subject`. Found while opening the sweep's second subject for this turn.
Repaired in the same commit.**

---

## What happened

The drawn direction names `tools/generate_company_data.py` as the subject after `ops_repo`. Asking
the instrument that ranked it for its row:

```
$ python3 -m tools.converged_contract_screen --module tools/generate_company_data.py
'tools/generate_company_data.py' is not a converged module
(<3 first-party callers, or not a repo module)      # exit 0
```

Both stated reasons are false. It is a repo module and it has three first-party callers — the
screen's own `--all --json` output says so in the same tree, in the same run of the same function.
**The true reason is a third one the message does not offer: `--module` matches
`r["module"]`, which is a DOTTED name, and it had been handed a path.**

That is not a spelling quibble. The screen's ranked table prints dotted names; every finding,
commit message and staged direction in this repository spells the same module as a path, including
the direction that named this subject. The two halves of the instrument disagree about how a
subject is written, and the disagreement surfaces as a confident false statement about the subject.

## Why the message is worse than no message

It sent me looking for a caller that had never disappeared. The screen had reported four callers on
2026-09-05 and three today, so "a caller was removed and it dropped below the threshold" was the
obvious reading of a message that explicitly proposed it — and it was wrong: three is *at* the
threshold, and the row exists.

`CLAUDE.md`'s rule is *write refusals that name their reason*, and the argument for it is that a
refusal that says why is how you discover the refusal itself was wrong. **A refusal that names two
plausible reasons neither of which is the true one inverts that: it is a wrong answer with a
rationale attached, and the rationale is what makes it survive scrutiny.** This one survived long
enough to be believed.

It also **exited 0**, so nothing calling the screen from a script could tell "not converged" from
"you spelled it the way the rest of the repo spells it".

## The repair

`--module` now accepts a path, a slash-form and a dotted name as one subject, and the refusal
computes the actual reason rather than reciting candidates:

* not a module in this repo → says so, prints how it read the argument, offers same-stem
  candidates, **exit 2** — a failed lookup is not an answer;
* a real module below the threshold → reports its measured caller count, direct importers and
  reaching suites, **exit 0** — that is an answer.

`tests/tools/test_the_screens_refusal_names_the_reason_it_actually_refused.py` proves it and proves
it can fail: reverting the one line to `wanted = args.module` reds the path-lookup leg and the
below-threshold leg while the other four stay green. Every leg is keyed to the property — the
subject under test is whatever the screen ranks first, and the below-threshold module is discovered
at run time — so nothing here is pinned to today's census.

## The substantive result underneath, which the false refusal was hiding

Asked properly, `tools/generate_company_data.py` is **3 callers, 1 direct test importer, 132
reaching suites** — and that one direct importer, `tests/tools/test_generate_company_data.py`,
counts as a DEDICATED suite. **It is no longer a zero-test-importer module.** It gained one at
`cbd5f6298`, the commit that moved 42 tests to where a runner looks.

So the sweep's ranked queue has moved under it again, in the same direction as last time:

| screen output | 2026-09-05 | 2026-09-06 |
|---|---|---|
| converged modules (≥3 callers) | 166 | **168** |
| of those, no dedicated suite | 14 | **13** |
| of those, **no test importer at all** | 2 | **1** |

The one remaining is `simulation/run_phase3b_recalibration.py` — 6 callers, 0 direct, 4 reaching.
**`tools/generate_company_data.py` has left the category the direction drew it for**, which does not
make it a bad subject (194 → 132 reaching suites and one dedicated file is still the shape) but does
mean the queue's stated reason for it no longer holds and a fresh pre-registration must say so.

This is the third time in two days that a screen row has been repaired by the sweep between being
ranked and being worked. That is the instrument behaving correctly and the QUEUE going stale
silently: the ranking is a snapshot, the direction quotes the snapshot, and nothing re-reads it.
Filed, not repaired — whether a drawn item should carry a re-screen at draw time is a decision
about the delivery lane, not a drive-by here.
