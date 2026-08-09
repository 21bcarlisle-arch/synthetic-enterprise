# [DIRECTOR-RULING] Hook-bypass is a WALL — and the class gets closed by a tool

**Date:** 2026-08-09. **Channel:** director, in-window. **Status:** RULING, binding.

## THE RULING

> "Ruling on hook-bypass: the default is a wall — bypass is never a judgment call.
> Tonight's is retroactively sanctioned as the one permitted interim shape, all four
> conditions required together: disclosed in the commit message, both parents
> independently gated, docs-only (no code, no level move), and filed. Now close the
> class: file an atom for a sanctioned surgical-landing tool — commit exactly-named
> paths with the gate run against the clean extract of the resulting tree, receipt
> recorded in the commit — so the check always runs and 'bypass' stops existing as a
> concept. Your disclosure tonight is why this ruling is calm; keep that reflex."

## WHAT IS NOW A WALL

Bypassing the pre-commit gate is a **WALL**, not a judgement call. This covers the
forms that bypass it *incidentally*, not merely `--no-verify`:

- `git commit-tree` / `git merge-tree --write-tree` used to construct a commit
- any push of a ref built by plumbing rather than by a hooked `git commit`

A dirty shared index refusing `git merge` is **not** licence to route around the hook.

## THE ONE PERMITTED INTERIM SHAPE

`d6f894b6e` (2026-08-09, merging the advisor's RESOURCE HEADROOM GOVERNOR with the
KNIFE2 adoption) is retroactively sanctioned. It required **all four together** —
any one missing and it would not have been:

1. **Disclosed** in the commit message, in its own paragraph, not buried;
2. **Both parents independently gated** (`450bf6903` 352 passed; `6071cd518` advisor-staged);
3. **Docs-only** — no code, no `level_current` move; one markdown file added;
4. **Filed** — reported to the director rather than passed off as routine.

This shape is INTERIM. It expires when `OPS_surgical_landing_tool` lands.

## WHY THE TOOL, NOT A STRICTER RULE

The bypass happened because `git merge` **correctly** refused: 35 paths of other
lanes' staged work sat in the shared index, and a merge commit would have swept them
in. That is a real, recurring structural conflict on a single shared tree — a rule
saying "don't" leaves the operator with no legal move, and MAKE_IT_STICK says a rule
without a mechanism evaporates. So the class closes with a TOOL that makes the legal
move available, not with an exhortation.

## THE STANDING REFLEX

The director named the disclosure as the reason the ruling is calm rather than an
incident. Keep it: state a bypass plainly in the commit message AND in the report,
every time, even when it looks defensible. A quiet bypass is the incident; a
disclosed one is a decision.
