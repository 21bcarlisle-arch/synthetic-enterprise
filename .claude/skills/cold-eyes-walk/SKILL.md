---
name: cold-eyes-walk
description: Manufacture an outside vantage for reviewing a deployed artefact (a page, a door, a headline figure) — fresh instance, hard blindfold, priors-before-pixels, persona priming, same-page reconciliation. Use before closing any public-facing surface, at every Door/page close, and as the technique underlying HARDEN-stage Expert Hour reviews on maturity-map atoms.
when_to_use: Invoke when a business-surface change (site page, customer-facing artefact, headline figure) is about to be marked done, or when asked to "review this like a skeptic" or "run a cold-eyes pass".
context: fork
---

# COLD_EYES_PROTOCOL — manufacture the outside vantage

**Origin (2026-07-11, staged, director's insight):** the advisor catching real thesis-chart defects
was not superior capability — same model — it was VANTAGE (cold context, audience-primed,
artefact-only). This skill institutionalises that vantage as a repeatable role, upgrading the
existing Expert-Hour simulation and fresh-context evaluator with a stricter blindfold.

## The protocol (for every Expert-Hour walk and every Door/page close)

1. **Fresh instance, hard blindfold:** the reviewer sees ONLY the deployed rendered artefact
   (URL/screenshot), never the build context, diffs, or intentions. Epistemic wall applied to
   review itself: the grader must not see inside the build. (This is why `context: fork` is set on
   this skill — run it in a forked subagent that only receives the artefact, not this session's
   own conversation history.)
2. **Priors before pixels:** before viewing, the reviewer states expected sane ranges for the figure
   classes it's about to see (e.g. "incumbent opex per household: £X-Y") — THEN it looks. Any
   displayed figure outside its own stated prior is a finding. This forces the plausibility
   knowledge already in the weights to actually fire, rather than being bypassed by pattern-matching
   on the page's own framing.
3. **Persona priming:** run as a named veteran (energy CEO / CTO / VC / payments ops), with the
   persona's first question: "what would you doubt first on this page?" Doubts are findings even
   when the underlying number is internally correct — reads-as matters as much as is-correct.
4. **Same-page reconciliation:** explicitly cross-check every figure appearing more than once, or in
   tension, on one page — independent of any automated data-layer consistency gate.
5. Findings land in the adjudication ledger (`docs/observability/sanity_adjudication_ledger.json`)
   like any other; builder context is only consulted AFTER findings are filed, never before.

## Plausibility anchors (standing, complements the protocol)

Every headline figure class on public surfaces should have an independently-sourced sane-range
anchor in the invariants library. Independence rule applied to PRESENTATION, not just data: the
anchor must not derive from our own pipeline. Out-of-range display is a sanity-daemon flag even when
internally correct — "correct but implausible-looking" is its own finding class, resolved by either
fixing the basis or explaining the divergence directly on the surface.

## Relationship to Expert Hour (maturity-map HARDEN stage)

This is the SAME technique the map's own Expert Hour bar uses at HARDEN stage
(`docs/design/MATURITY_MAP.md` §1-2) — a level-3+ claim requires a veteran persona finding "no major
gaps or flaws" via exactly this walk. Don't build a separate "expert-hour-walk" skill; invoke this
one and frame the persona/artefact for the atom in question.
