# The ledger reads what an item ASKED for each path now, and the first draft of the reading was fail-open on its own vocabulary

**Severity:** RECORDED
**Lane:** A_strategy_governance
**Claim:** `the-ledger-credits-a-path-an-item-only-asked-you-to-read`
**Date:** 2026-09-22

---

## The premise, re-measured before starting

The drawn item cited `edc1b14df` and warned it was already an ancestor of `origin/main`. It is —
but the premise of this item is not that commit landing. It is that `_landed_by_sibling` reads
**every** path an item's prose names as a path the item is about. That reading was still live at
`090a5d260` (tree level with origin, 0 commits behind at draw time). Nothing in
`background/delivery_lane.py` had a concept of a path's ROLE. **Premise stands.**

The duplicate-work check named `the-ceilings-downstream-still-fits-a-value-that-never-shipped`,
which holds `simulation/net_new_acquisition.py`. That is the *subject* of the over-credited item,
not this work: this item's subject is the ledger's reading. Genuinely different work on an
overlapping file. Carried on.

## What was wrong

`_claim_paths` returns every repo path an item's prose names, whatever it names it for, and both
credit readings matched on it. So a commit touching a path an item named only *to read a constant
out of* — or named only inside an explicit `DO NOT TOUCH` clause — retired the item.

Measured on the live ledger, at the instance the item names:

| path in `the-settlement-ceiling-...`'s set | what the prose asked for it |
|---|---|
| `simulation/net_new_acquisition.py` | **the subject** — "Move `SETTLEMENT_CUSTOMER_YEAR_BUDGET` in …" |
| `docs/observability/settlement_ceiling_slope_20260921.json` | read — "DERIVING the new one **from** …" |
| `background/publish_freshness.py` | read — the weekly interval constant |
| `simulation/premise_population.py` | **forbidden** — "DO NOT TOUCH … or …" |
| `tools/generate_value_arms_data.py` | **forbidden** — same clause |

`edc1b14df` touched `background/publish_freshness.py` and its own message says
`NOT TOUCHED: simulation/net_new_acquisition.py` in capitals. The item was retired
`landed_elsewhere` on it, and the evidence string published was `touched
simulation/net_new_acquisition.py, …` — `", ".join(paths[:3])`, the item's own first three paths
in sorted order, naming the question as if it were the answer.

**A commit to a file the item FORBADE would have credited it just as well.** The direction file is
an input to this mechanism: words written to protect a path made it creditable.

## What shipped

- `_path_roles(text, known=None)` — each confirmed path occurrence is governed by the **nearest**
  governing verb before it inside its own clause. A read/forbid governor makes that occurrence a
  mention; a change governor, or none at all, makes it a subject. A path is dropped only when
  **every** occurrence is a mention.
- `_claim_subject_paths` — the subset of `_claim_paths` the item asked to be **changed**.
- `_window_hits` queries git over that set, so **both** credit readings narrow together
  (`_landed_unbound` shared the defect; the docstring defence there — "what it replaces is an
  empty string" — is true of the field and false of the row, and is corrected beside the claim).
- Each hit carries the paths that actually matched; `_matched` prints those, and says so when git
  printed no filenames under a simplified merge.
- The residual's NO-PATHS branch split: "names no tracked path" vs "names N and asks for none of
  them to be CHANGED". The second is a real state now and blaming the prose for being precise is
  the fourth-voice defect one layer out.

The strand half is deliberately **left on the full set** — uncommitted bytes on a path an item was
told not to touch is a thing a reader wants shouted, not filtered.

## Two things the measurement caught that rereading the code would not

**1. The first draft was fail-open on its own vocabulary.** `READ FIRST, DO NOT REWRITE: the
shared tree holds <path>` — the commonest forbidding sentence in this repo's direction prose —
matched `rewrite` in the CHANGE list and made all three forbidden paths subjects
(`widen-the-weather-archive-beyond-c1-c4`). A negated change verb is now a read governor and is
tried first. Found by printing every live row's roles, not by rereading the regex.

**2. `reading` is a noun here.** `Rewrite the window reading in <path>` came back read-only
because the nearest governor to the subject was `reading`. Dropped from the vocabulary.

**3. The first draft broke a promise `_claim_paths` makes in writing.** It re-confirmed the prose
against `_tracked_files`, so a stamped row — answered from the ledger, "free and unraisable", and
asked of every swept row to build the orientation brief — started shelling out to `git ls-files`,
and a dead git was reported as having failed `ls-files` rather than `log`. An existing control
caught it. `known=` passes the stamp in, which also makes the confirmation stricter.

## Distribution at real inputs (live ledger, 299 rows with paths)

| | |
|---|---|
| paths named | 771 |
| kept as subjects | 695 (90.1%) |
| dropped as read-only / forbidden | 76 |
| rows left with no subject at all | 6 |

The six are readable: items whose whole instruction is to read an artefact and leave files alone
(`widen-the-weather-archive-beyond-c1-c4` is four such paths), plus rows whose draw-time stamp
holds a path today's prose only mentions (`remove-the-two-legacy-head-red-tracked-files…` stamped
only `background/head_red_register.py`, which its current prose reaches through "proving the
legacy **read**-only fallback in …"). Each of those costs a **redraw**, not a drop.

## The direction the detector is allowed to be wrong in

One-sided by construction: **no governor found leaves a path a subject**, which is what every path
was before this existed. A gap in the read vocabulary can only fail to remove an over-credit; it
can never invent one. The cost lands as an under-credit, which costs one redraw — against an
over-credit, which retires live work and publishes evidence for the retirement.

The one entry that widens rather than narrows is `to`, and it is named separately in the code:
`Move the liveness refusal from the reader to the writer in <path>` otherwise loses its only
subject to the `from` that governs the source. Measured: it recovers four paths and one of seven
zero-subject rows, and moves the instance above not at all.

## The `edc1b14df` replay, run at the landing (2026-09-22, real git, real prose, real stamp)

Asked as it stood at the instant of the false retirement — real `_item_text`, the row's real
draw-time stamp out of `.delivery_lane_claims.draws.json`, real `git log`, with the log capped at
`edc1b14df + 1s` so the item's **own** landing (`b518ddec9`, 751s later) cannot answer for it. Only
`_claim_subject_paths` is reverted for the BEFORE column; everything else is the code as it ships.

Roles the repair reads out of that item's actual prose, over its actual four stamped paths:

| path | role |
|---|---|
| `simulation/net_new_acquisition.py` | **SUBJECT** |
| `background/publish_freshness.py` | mentioned-only |
| `simulation/premise_population.py` | mentioned-only |
| `tools/generate_value_arms_data.py` | mentioned-only |

| | disposition | evidence |
|---|---|---|
| BEFORE | `landed_elsewhere` | `landed under … edc1b14df fix(cadence): … touched background/publish_freshness.py (+1 more)` |
| AFTER | `not_done` | `… none on those paths -- BUT THE WORK MAY BE SITTING THERE` |

That BEFORE line **is** the retirement this repair exists for, reproduced from the ledger rather
than quoted from the log. AFTER, neither credit reading reaches the row: the only in-window
commits touch paths it asked to read or forbade.

**The replay found a worse instance than the one this note was written about.** With nothing bound
— the state before the two siblings claimed their landings — the pre-repair reading's first credit
is not `edc1b14df` at all but `c3e2ba377`, whose matched paths are
`simulation/premise_population.py, tools/generate_value_arms_data.py`: **both** of the paths that
item's prose forbids in capitals, and the commit is the live lane's own repair that the `DO NOT
TOUCH` clause was written to stay off. The clause did not merely fail to protect the row — it
supplied the row's retirement. Same replay, `--until` capped identically.

A third reading is worth recording because it is the one the lane sees today: run against the
tree as it now stands, with no `--until` cap, the row reaches `landed_unbound` on `b518ddec9`
(`touched simulation/net_new_acquisition.py`) both before and after the repair. The afternoon's
fit is visible to the lane again and the evidence now names the path that actually moved.

## Control

`tests/background/test_the_ledger_credits_only_a_path_an_item_asked_to_be_changed.py` — one
statement over the whole partition: an item whose CHANGED path was touched must be credited and an
item whose READ-ONLY path was touched must not, from one ledger, one commit, and prose that
differs only in what it asked for the path both rows name.

Four mutations claimed. **Re-run at the landing** against the working-tree file (backed up, applied
one at a time, restored, sha256 checked), recording every leg each one reds rather than only that
something went red — because a mutation caught by a different leg than the one written for it is
the flattering reading:

| mutation | legs that RED |
|---|---|
| (a) `_claim_subject_paths` returns `_claim_paths` unfiltered — the shipped reading | `THE_PARTITION`, `THE_REFUSAL_SAYS_THE_PATHS_WERE_NAMED`, `A_NEGATED_CHANGE_VERB_FORBIDS` |
| (b) `_claim_subject_paths` returns `[]` | `THE_PARTITION`, `AN_ITEM_WHOSE_PROSE_IS_GONE`, `A_STAMPED_ROW_STILL_ASKS_GIT_ONLY_THE_COMMIT_QUESTION`, `THE_EVIDENCE_NAMES_THE_PATH_THAT_ACTUALLY_MATCHED` |
| (c) drop `_NEGATED_CHANGE` from the read governors | `A_NEGATED_CHANGE_VERB_FORBIDS` — **and nothing else** |
| (d) put `paths[:3]` back in **both** evidence strings (2 sites) | `THE_EVIDENCE_NAMES_THE_PATH_THAT_ACTUALLY_MATCHED` — **and nothing else** |

(a) and (b) are the two one-way mutations the drawn item asked for, and the partition line reds on
both — on opposite halves. Neither can be passed by a constant answer, which is the trap this
project has entered through three doors in one afternoon.

**(c) is the check the drawn item named explicitly: the mutation that breaks the verb reading is
caught by the leg written for it and by no sibling assertion.** It is a clean one-leg kill, so the
negation clause is load-bearing on its own evidence and not riding on the partition line. (d) is
the same shape. That (a) and (b) each spray across several legs is the expected direction — they
gut the shared path set every leg stands on — and the partition line is in both lists, which is
what makes it the control rather than a corollary.

## What is NOT claimed

The vocabulary's **completeness**. There is no mutation to write for it: a gap fails towards the
old reading by construction, so the honest statement of the limit lives in `_path_roles` beside
the cost direction rather than in a control that would be asserting its own filter.

## The item this was drawn against

`the-settlement-ceiling-can-move-now-that-its-curve-has-landed` reads correctly now, and the
correct answer is not the residual: `b518ddec9 fix(ceiling): the settlement ceiling is a
consequence of the landed curve` **did** touch `simulation/net_new_acquisition.py`, so
`_landed_unbound` takes the row and outranks the sibling reading. The afternoon's fit the false
retirement dropped is visible to the lane again.
