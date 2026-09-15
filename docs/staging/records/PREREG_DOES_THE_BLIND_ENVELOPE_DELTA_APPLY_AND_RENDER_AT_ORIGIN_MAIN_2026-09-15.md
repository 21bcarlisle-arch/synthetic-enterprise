# PREREG — does the blind envelope delta apply, and render, at `origin/main`?

**Filed:** 2026-09-15, before any of the three measurements below was run.
**Lane:** Lane 0 delivery, claim `the-two-finished-runs-artefacts-reach-origin-and-the-envelope-renders`.
**Severity:** MEDIUM — a published surface claims a block the published producer cannot build.

---

## Why this is being measured at all, and how the drawn framing was wrong

The item drawn said: two artefacts are missing from git — one "staged, in no commit", one
"untracked, written by a finished run" — so land the two of them and the envelope will render.
Asking the three questions (HEAD, index, `.gitignore`) of each, against the right tree, that framing
does not survive:

| Path | Drawn as | Actually |
|---|---|---|
| `docs/design/blind_envelope_arms_2026-09-11.json` | staged, in no commit | correct — staged `A ` in the SHARED tree's index only |
| `docs/observability/value_cycle_ab_s1_noise_floor_20260910b.json` | untracked | **wrong — committed on local `main` in `5660e1f81`** |

And the stated cause — *"the producer reads its exact path at line 348"* — is false on the published
producer. `blind_envelope` appears in **zero** files at `origin/main`. Line 348 of
`tools/generate_value_arms_data.py` at `origin/main` is inside `CLOCK_MEANING`, unrelated prose.

The real shape is a **fork**, and it is already being worked: local `main` is **41 ahead / 35
behind** `origin/main`, and four `se-lane0-merge-*` worktrees exist. The whole envelope feature —
`_blind_envelope()` at `main`-worktree line 8697, its call site, the page block, the door test — is a
**+530-line uncommitted delta on top of local `main`**, across three files that `origin/main` also
diverges on. So the drawn path list is a strict subset of the change it describes: landing the two
JSON artefacts alone puts data on `origin/main` that nothing there can read.

## Predictions, before running anything

**P1.** The +530-line envelope delta (`main` → shared working tree, over
`tools/generate_value_arms_data.py`, `site/capabilities/index.html`,
`site/test_the_baseline_comparison_reaches_the_reader.py`) will **not** apply cleanly onto
`origin/main`'s copies of those three files. *Reason: the two bases are 35 commits apart and all
three files are edited in that span.*

**P2.** If P1 is refuted and the delta does apply, `generate_value_arms_data` run at `origin/main`
will still **fail to emit a populated `blind_envelope` block** on the first attempt, because
`_blind_envelope` is authored against `main`-only helpers.

**P3.** Landing only the two JSON artefacts — the drawn instruction, executed literally — would
leave `site/data/value_arms.json` at `origin/main` with **no `blind_envelope` key at all** (not an
empty one), because the producer that would write the key does not exist there.

**Falsifier for each:** P1 is refuted by a clean three-file apply. P2 by a populated block on the
first run. P3 by the key appearing without the producer delta.

## What "done" means for this claim

Not "the two files are in a commit". **The envelope renders from a clean `git archive origin/main`
extract** — `site/data/value_arms.json` in that extract carries a populated `blind_envelope`, and
`site/capabilities/index.html` renders a span and a position from it. If it renders empty, the
finding is which of the three reads failed, named.

## Recorded outcome

*The predictions above are not edited. Two held, one was wrong.*

**P1 — CONFIRMED.** `git apply --check` refused two of three files. A 3-way apply produced **six
conflicts**: five in `tools/generate_value_arms_data.py`, one in the door test.

**P2 — REFUTED, and I was wrong.** Once the conflicts were resolved, `generate_value_arms_data`
emitted `blind_envelope` with `available: True` and all five lines on the **first** run. Nothing in
`_blind_envelope` needed a `main`-only helper: it calls `_blind_line` (which the delta defines
itself), plus `_cited_path`, `_f` and `_read`, all three of which `origin/main` already has. The
delta's entanglement with the fork was entirely in the *surrounding* lines, not in the feature.

**P3 — CONFIRMED, by the door's own words rather than by executing the literal instruction.** The
skip message printed `why_not=None`, which is `{}.get("why_not")` — the key was **absent**, not
present-and-empty. So the drawn instruction executed literally would have published two artefacts
that nothing at `origin/main` reads, and the block would not have rendered empty: it would not have
existed. The brief's own stated failure mode ("if the extract renders an empty envelope, that is the
finding") could not have occurred.

## What every conflict turned out to be, and why "pick a side" was the wrong move

All six were **additive on both sides** — `origin/main` and `main` each appending different things
at the same place. Resolving by adopting either side wholesale would have deleted the other's work,
which is this repository's named merge shape. All six were resolved as **unions**, with one
deliberate exception:

`DEPARTURE_TERM_BASELINE_PATH` **does not exist at `origin/main`** (0 occurrences). The delta
carries a second, unrelated feature — the departure-baseline control arm and the second sign rule —
tangled into the same hunks. Landing it would have imported four controls
(`test_the_runs_own_answer_to_which_side_of_zero_reaches_the_reader` and three others) grading a
producer feature that is not there. Those four were **dropped**, not resolved: they belong to the
41/35 fork merge that the `se-lane0-merge-*` worktrees own. Evidence they do not belong here: taken
wholesale they went **red immediately** (3 failed), and they are red for the honest reason — the
producer cannot answer them.

## The second finding: how this stayed invisible for 106 hours

`_live_feed()` reads the **published** copy via `published_blob` → `git show :<path>` — the INDEX,
never the working tree, and it fails closed. The door was therefore *correct and already
load-bearing*; it reported the defect as a **skip**, once per control, seven times a run:

> `this publish carries no available blind envelope (None)`

That is the whole 106-hour gap. The [LAUNCH UNLANDED] alarm fired 107 times and the door said the
same thing seven times per run, but a skip is not a red, so nothing ever blocked. **This is the
"nothing noticed it" shape again — it was surfaced constantly, into a channel where it could not
be distinguished from an ordinary skip.**

*Consequence for anyone verifying this: the brief's proposed check — `git archive origin/main` to a
directory, then run the door — **cannot work**, and would have produced a false red. An archive
extract has no index, so every `git show :<path>` in it fails closed. Verification must use a real
checkout that has an index. That is what was used here.*
