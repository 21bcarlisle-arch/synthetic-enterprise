# [DIRECTOR-RULING] — The site breathes: publish freshness decoupled from HEAD perfection (2026-08-10)

**Type:** [DECISION — ratified in conversation ~11:00 BST. Modifies DIRECTOR_PRIORITY_PUBLISH_FIRST_2026-08-10: its three ordered draws STAND at first priority; its "no feature draws" clause is LIFTED and replaced by this design.]

**The defect this names:** the publish gate currently conflates two questions — "is the entire repo green at HEAD?" and "may the site update?" — so any red anywhere (a stale ledger, an allowlist row) freezes the public surface entirely and silently. 22 hours of frozen site over bookkeeping is the measured cost.

**Ruling — three properties, mechanisms the worker's:**
1. **Newest-verified always flows.** The site serves the most recent snapshot that passed its scoped verification, stamped with run id, verifying commit, and verification time — visible on the page, not in a log.
2. **The gate is scoped to what it protects.** Publishing requires the publish-path's own suite green (the code that produced and renders the numbers); reds elsewhere ANNOTATE the page ("published with N open findings — see health") rather than block it. Honest transparency of repo health replaces hostage-taking by it.
3. **Behind, never frozen, never silent.** If even the scoped gate is red, the site keeps serving the last verified snapshot under a dated banner ("verification paused since T; showing run R"). A visitor can always tell WHAT they are seeing and HOW current it is. Freshness claims are provenance claims; fake-fresh (re-stamping stale runs) remains the cardinal sin — this weekend's four-times-republished figure is the named counterexample.

**Director's principle, verbatim intent:** newer-verified beats older-verified; transparent recency beats frozen perfection; the public surface's integrity is its honesty about itself, not its silence.

## WORK THIS CREATES (canonical, in-document)
1. The scoped publish-path suite defined and gated. 2. Provenance/recency stamps rendered on the live pages. 3. Last-known-good serving with the staleness banner. 4. The freeze clause retired from the standing priority; the three cure draws unchanged at first priority.

— Ruled 2026-08-10; staged by the advisor; see-and-correct applies throughout.
