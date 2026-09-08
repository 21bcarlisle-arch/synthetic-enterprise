**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `prune-comment-only-path-edges-and-freeze-the-33-in-one-commit`)

# A path in a comment is no longer an edge, and the floor now says so

Pre-registration: `docs/staging/SEAT_PREREG_COMMENT_LINE_PATH_EDGES_ARE_NOT_EDGES_2026-09-08.md`,
written before the change and before any census in this tree. Input finding:
`records/SEAT_FINDING_THIRTY_FOUR_MODULES_ARE_HELD_OUT_OF_THE_ORPHAN_SET_BY_A_COMMENT_AND_THIRTY_THREE_HAVE_NO_GRANDFATHER_2026-09-08.md`.

## Premise: NOT spent

The draw flagged both cited commits (`46b51ba8a`, `9a280c876`) as already ancestors of
`origin/main`. They are — but they are the commits that *measured* the defect, not ones that fixed
it. `tools/capability_index._path_references` at `cc7452013` still regexed raw source text with no
comment awareness. Re-measured here before starting: **372 orphans against a 374 floor**, with the
comment-only edges intact. The work was outstanding.

## What changed

`_path_references` now skips any path token lying inside a `#` comment, via `tokenize` rather than a
`#`-hunting regex — the two disagree exactly where it matters, because
`PATH = "tools/x.py"  # not tools/y.py` carries a real edge and a comment on one line, and a `#`
inside a string literal is not a comment at all.

## Predictions, and how each came out

| # | Prediction | Result |
|---|---|---|
| 1 | `tokenize` prunes a strict SUPERSET of the line-starts-with-`#` rule | **Held.** Superset, +1 module |
| 2 | Newly orphaned: 34–70 | **Held, at the bottom of the range: 35** |
| 3 | All 33 named in the input finding still orphaned here | **Held, 33 of 33** |
| 4 | The floor grows, never shrinks | **Refuted in one row — see below** |
| 5 | Frozen `module_count` equals this tree's; provenance note falls silent | **Held** (1124, silent) |

Prediction 1's single extra module is `company.billing.cot`, held reachable by two **trailing**
comments citing where a constant came from (`_FINAL_BILL_PAYMENT_WINDOW_DAYS = 28  # matches
company/billing/cot.py::_OVERDUE_DAYS`). One instance is the whole argument for `tokenize` over the
census's regex: had the census been the specification, this module would have kept a false edge and
nothing would ever have named it.

## Prediction 4 was wrong, and the correction is in the floor

`freeze()` recomputes from scratch, so it dropped `company.regulatory.epg_reconciliation_register` —
frozen as an orphan, and now "wired". Its two references are in **docstrings**, in
`simulation/svt_rates.py` and `simulation/price_cap_enforcement.py`, and both of those docstrings say
in so many words that the register *has no production caller*. The prose wiring it is the prose
denying it.

Taking that shrink would have left an editorial reword of a docstring able to refuse every lane —
the identical defect, one class over. So the row is **held in the floor past its own computed
reachability**, with the reason written into the baseline's `_doc` and a delete-me condition naming
the commit that should remove it. The ratchet prints an honest note about it on every `--report` and
does not refuse. That note is the correct surface: a disagreement is evidence, not a verdict.

## The refutation test the pre-registration promised

Every one of the 35 modules' pruned edges was read. **Not one is a real invocation.** They are
provenance citations without exception — *"superseded by"*, *"matches"*, *"found by"*, *"the
historical replay lives in"*. The two nearest to wiring are a documented manual reproduction step
(`# Reproduce with python3 tools/need_stock_joint.py --lifts`) and a comment describing a human
re-run (`# ... re-runs tools/render_site_nav.py --write`); neither is executed by any code. The
floor is not recording anything untrue.

## What this cost elsewhere, and what it did not

Six company-side modules lost their last *caller* (the index's stricter notion) and so needed
rulings in `docs/design/ORPHAN_DISPOSITION_REGISTER.md`. All six are real, tested capabilities with
no importer — `unhooked`, consumer nominated by package, with the provenance on each row so the next
reader knows why six rulings arrived on one day. `--render-dispositions` confirms the derived column
matches the tree.

## The pre-existing red, and why clearing it was this seat's job

`test_the_live_register_rules_on_every_live_orphan` was **already red at clean HEAD** on a single
item — `epg_reconciliation_register`, STALE DISPOSITION — proven in a `git archive HEAD` extract
before this work touched anything. I first intended to leave it: it is not mine, and its proper fix
is the docstring atom.

`surgical_land` refused on it, and that is the useful part. *A red commit is structurally
impossible*, so this red was not merely sitting there — **it was wedging every lane in the tree**,
and had been since before this turn started. Nothing was going to land through it. That makes
clearing it the seat's job rather than scope creep.

The row is deleted, which is what §0 of the register demands of a ruling whose subject the index no
longer calls an orphan, and §6 of the register now records why it went, that it is *not* wired, and
the exact commit that must give it a fresh ruling. Silence about a module is not a false claim; a
ruling the checker reads as stale is. The claim itself — a real, tested capability with no consumer —
survives in §6 and in the held baseline row.

## The docstring half, measured and deliberately NOT done

The input finding called its 34 a FLOOR because a path in a docstring is still an edge. Measured
here: pruning docstring paths as well takes the orphan set from 407 to **535 — a further 128
modules**, against 34 for the comment half. That is a different size of blast radius and it is its
own atom with its own both-doors proof; shipping it inside this one would move the floor for two
reasons at once and make neither attributable. The scope in the pre-registration stands, now with a
number behind it rather than an intuition.

## What is next

1. **The docstring half: 128 modules.** Same edge model, same freeze-in-the-same-commit discipline.
   It is what releases `epg_reconciliation_register` from the floor, and that row is the standing
   marker for it.
2. `company.market.portfolio_position` and `company.pricing.cost_to_serve` reached the register as
   `unhooked` here. Both are tested and have real consumers available; wiring either is an ordinary
   shrink, and now an honest one.
