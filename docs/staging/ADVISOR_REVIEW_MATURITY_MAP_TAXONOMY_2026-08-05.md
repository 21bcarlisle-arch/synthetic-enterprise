# [ADVISOR-REVIEW] — Maturity map taxonomy audit (2026-08-05)

**Type:** [FINDINGS]. Full parse of `docs/design/maturity_map.yaml` (185 atoms, 1.7MB) against the charter estate, run while the machine is offline. Cells and levels are the director's — nothing here edits an atom. Findings only; shapes, not mechanisms. Refute with evidence.

## F1 — The spine has become a database (89% one field)
Of the map's 1.7MB, **1.5MB (89%) is the `simplifications` field**. The registry itself — ids, lanes, levels, scopes, dependencies — is ~200KB. The simplifications *discipline* is right (canon requires every simplification registered); its *storage* inside the spine is the same disease found three times today (done/ drawer, repo-as-database, ledger duplication): the readable governance surface has been eaten by its own evidence. Largest single atoms: H23 (44KB), SITE1 (39KB), W1_11 (37KB). Shape: simplifications live in a sibling store keyed by atom id; the map keeps one-line pointers. The map should be readable by the director on a phone.

## F2 — file_scope no longer arbitrates (the lane wall's input is degraded)
48 files are claimed by more than one atom, and — worse — **whole directories are claimed as scope**: `docs/design` by 31 atoms, `tools` by 16, `background` by 13. A directory claim makes collision detection vacuous there. Sharpest real collisions: `company/compliance/domain_invariants.py` claimed by **8 atoms across three lanes** (F, W1, W2) and `background/supervisor.py` by 6 (H, A, OPS). The lane wall hook can only be as good as this field; today the field cannot answer "who owns this file."

## F3 — Charter debt, by the map's own rule
The W2 charter records the rule: *"a lane earns its charter when its dial reaches 3+."* Applying it: **H — 35 atoms, 13 at level 3+, no charter.** The largest lane in the project has no wall definition. Also past the threshold with no charter: F (3 at 3+, plus Fa/Fb/Fc satellite prefixes), OPS (3 at 3+), CA (3 at 3+). Separately: the charter estate is split between `docs/design/charters/` and top-level `docs/design/` files, and `CHARTER_W2_AFFORDABILITY.md` reads as a lane charter but is a cluster-concretisation doc *within* W2 — authority is clear on reading, naming is not.

## F4 — Prefix sprawl: 22 lane prefixes, no registry of valid lanes
Stripping digits from ids yields 22 distinct prefixes: the 11 chartered lanes plus ARCH, BRAND, CA, DD, GAP, HX, OPS, SITE, SP, SPINE, Fa, Fb, Fc. 25 ids (13.5%) break the `LETTER+NUMBER_name` grammar entirely (e.g. `A_scope_of_need_scoring_frame`, `DD_seasonal_cashflow_physics`, `H_GAP_fabric_belief_truth_gap`), so any tooling that parses lane-by-prefix mis-sorts them. Nothing in the repo declares which prefixes are legitimate lanes. Shape: a lane registry (one small file), and the grammar enforced at mint time — the write-time gate from the ARCHITECTED-OUT programme is the natural place.

## F5 — Registry integrity details
(a) Dependency edges hold prose: 4 `blocked_on`/`depends_on` values are sentences (`director_systemd_deploy`, `closed_zonal_rejected_2026-07-21_watching_brief…`), not atom ids — the graph is uncomputable while edges are free text; a `blocked_reason` field is the shape. (b) The same fields are sometimes string, sometimes list — type inconsistency that crashes naive walkers. (c) **Provenance carries zero dates**: the map cannot answer "when was this atom minted" — the governance layer has no temporal provenance while the company layer is built bitemporal. (d) One atom has `epoch: None`.

## Clean bill (stated because it's evidence too)
All 185 ids unique. **Zero cross-lane near-duplicate names — the B9=E5 duplication class was fully cleared.** 119/185 atoms at target level. Level spread healthy (40 at L0, 65 at L3). Epoch forward-load: 59 atoms (32%) belong to epochs 3–5 — legitimate parking IF the draw predicate excludes future epochs; worth one confirmation, not a defect.

## Not done here
No atom edits, no charter drafts, no lane mergers — cells are the director's. F1–F5 are registered for sequencing; F3's missing-charter work (H first) needs the director's view on whether H is one lane or several.

— Advisor review, 2026-08-05.
