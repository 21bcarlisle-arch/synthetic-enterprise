# Phase 0c Findings — "Delegate all code to Qwen, review and fix only"

Phase 0c's brief was explicit: every line of code in this increment goes
through `qwen2.5-coder:14b` (local, via `tools/delegate_ollama.py`); the
frontier orchestrator's job is to spec, review, test, hand-patch defects, and
commit — not to write code from scratch. This document is the process-level
verdict that approach earned, alongside the Process observability figures
CLAUDE.md asks every phase to produce.

## What shipped

Three deliverables, three commits, all built from five delegation rounds:

1. `simulation/run_phase0c.py` — widened the Phase 0b settlement run from a
   Q4-2016-only window to the full 2016 calendar year, reusing the existing
   pipeline unchanged. Result: portfolio margin **−£78.28** over the year —
   every customer ran at a loss for all of 2016, not just Q4.
2. `saas/customer_reaction.py` — `score_dissatisfaction()`, a per-customer
   running counter that increments whenever a settlement period's actual cost
   of supply exceeds the fixed-tariff bill for that period by more than 20%.
3. `saas/clv_seed.py` — `build_clv_seed()`, a per-customer chronological
   running total of (contract value billed − actual cost of supply): the
   first building block toward real CLV modelling.

Each of (2) and (3) was wired into `run_phase0c.py` with a second, smaller
delegation round ("here is the current file verbatim, add this one section").

## What worked

- **"Transform this data shape per these rules" held up again.** Every one of
  the five generations was *structurally* correct on the first attempt — right
  signatures, right control flow, right aggregation logic. This confirms Phase
  0b's headline finding rather than just repeating it: well-scoped,
  shape-transform tasks are squarely in this model's competence band when the
  prompt states exact upstream signatures.
- **The "edit this file" pattern beat "write this file from scratch."**
  Rounds 3 and 5 (wire `score_dissatisfaction`/`build_clv_seed` into the
  orchestration script) handed the model the *entire current file* verbatim
  and asked for a minimal, scoped change. Both came back as clean,
  surgical diffs — new import, one new print block, one new return key,
  nothing else touched. `diff`-ing the result against the pre-edit file showed
  zero incidental changes. This is a noticeably more reliable mode than
  generating a module from a spec, and worth defaulting to for incremental
  work going forward.
- **A sibling file as a style reference reliably transfers house style.**
  Pasting `run_phase0b.py` (round 1) and `tariff_pricing.py`'s docstring
  (rounds 2 and 4) into the prompt produced output that matched naming,
  print-formatting, and docstring conventions closely enough that no
  style-related hand-patches were needed.
- **Cheap.** Five local calls, ~9,858 Ollama-reported tokens combined,
  produced ~194 net lines of reviewed, working, committed code at zero
  marginal cost (local inference). See the token breakdown below.

## What didn't — three repeatable failure modes worth naming

1. **Markdown code-fence wrapping, every single time.** All five generations
   wrapped their output in ```` ```python ... ``` ````, despite the prompt
   explicitly saying "output ONLY the raw Python source... no markdown
   fences" — repeated, in caps, in every prompt. 5/5 is not noise; this is a
   reliable quirk of this model (or this prompt template) that should be
   *automated around* rather than re-prompted against — `tools/delegate_ollama.py`
   or its callers should strip a leading/trailing ` ```python `/` ``` ` fence
   unconditionally rather than trusting the instruction to land.
2. **Echoing placeholder text verbatim from the prompt.** Round 2's prompt
   showed a real docstring from `tariff_pricing.py` as a style example, but
   elided its middle with a literal `...` for brevity. The model copied that
   literal `...` into the generated docstring as if it were real prose — a
   textbook garbage-in-garbage-out result. Lesson: never put placeholder
   ellipses or `[...]`-style elisions in few-shot reference text; either paste
   the whole real example or none of it.
3. **Multi-constraint ordering logic is still the soft spot.** Round 2 asked
   for two properties at once: (a) each customer's `history` chronological,
   and (b) customers appearing in the output "in first-encountered order...
   effectively by earliest settlement_date." The model satisfied (a) by
   sorting on `(customer_id, settlement_date, settlement_period)` — which also
   *happens* to satisfy (b) in this dataset, because customer IDs were
   assigned in acquisition order, but is not a faithful implementation of (b)
   in general (a customer_id-first sort produces lexicographic customer
   ordering, not chronological-first-seen ordering). This is the same flavour
   of subtle multi-step-logic slip Phase 0b saw in calendar arithmetic: each
   constraint individually is trivial, but composing two orderings correctly
   wasn't free. Caught by re-reading the spec against the generated sort key,
   not by running the code (it produced the "right" answer on this data either
   way) — another data point for "running without error is not sufficient
   review for sequencing/ordering logic," generalising Phase 0b's "...for date
   logic."

All three were hand-patched directly rather than spent on a sixth delegation
round — the same diminishing-returns call Phase 0b made on the PC1 shape
loader's last two defects, and it held up the same way: cheaper and faster
than re-prompting, and exactly the "frontier reviews and fixes" loop this
phase was scoped to exercise.

## Token efficiency

**Local model (`qwen2.5-coder:14b` via Ollama, `prompt_eval_count` + `eval_count`):**

| # | Round | prompt_eval | eval | total |
|---|-------|------------:|-----:|------:|
| 1 | `run_phase0c.py` (full-year orchestration, from spec + sibling) | 1,400 | 893 | 2,293 |
| 2 | `customer_reaction.py` (new module, from spec) | 799 | 365 | 1,164 |
| 3 | wire `score_dissatisfaction` into `run_phase0c.py` (edit, full file in) | 1,445 | 1,019 | 2,464 |
| 4 | `clv_seed.py` (new module, from spec) | 858 | 422 | 1,280 |
| 5 | wire `build_clv_seed` into `run_phase0c.py` (edit, full file in) | 1,534 | 1,123 | 2,657 |
| | **Total** | **6,036** | **3,822** | **9,858** |

**Frontier tokens (this session, computed from the transcript's `usage`
blocks — the gap Phase 0b flagged is now closed):**

- in: 154, out: 58,635, cache-create: 170,392 → **headline 229,181**
- cache-read: 4,773,678 (tracked separately — ~1/10 the cost of a fresh
  input token; not folded into the headline per the token-log convention)

**Reading the ratio:** ~23× more frontier tokens than local tokens for this
session. That's expected and not a problem — the local model only ever sees
five short, tightly-scoped generation prompts (~1,000–1,500 tokens of context
each), while the frontier orchestrator carries the whole codebase, runs and
verifies the pipeline four times end-to-end against live Elexon data, writes
every commit message, and authors this document. The local delegation
produced ~194 net lines (~51 local tokens/line) of code that needed no
re-generation — the frontier spend bought the surrounding judgment, not the
typing. That split is the thesis CLAUDE.md states outright: "deep sector
expertise combined with cheap AI execution."

## Verdict for the dev-approach question Phase 0c was scoped to test

**Delegating *all* code — including the small wiring edits, not just new
modules — to the local model, with the frontier reviewing and hand-patching
only, worked for this codebase's current size and complexity.** The "edit
this file, here's the whole current source" pattern was the standout: it
turned a model that sometimes drifts on open-ended generation into one that
makes minimal, predictable, diffable changes. Combined with automating away
the markdown-fence quirk (a one-line fix to the harness, not yet made — next
session should make it), this is a workable steady-state loop. The ordering-
logic slip is the one genuine warning sign: as the simulation grows more
temporal (multi-year runs, overlapping contracts, churn/re-acquisition), the
"composing two sequencing constraints" failure mode will recur more often and
matter more — that's where hand-written frontier code, not delegation, will
keep paying for itself, exactly as Phase 0b concluded for calendar arithmetic.
