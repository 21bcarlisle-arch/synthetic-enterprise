# WEBSITE_FRESHNESS_AND_DEDUP — surface quality pass (P1)

**Staged:** 2026-07-08 by advisor, on Rich's direction.
**Tier:** 2 — this is surface-quality work under the 70/30 visibility rule, and the
website has now been raised by the director repeatedly, which auto-escalates to P1
(director-repeat rule). Proceed without waiting, but do not pre-empt Phase RY if it
is already in flight — sequence this immediately after, or in parallel if safely
non-conflicting (different files).

## Why (director observation, 2026-07-08 morning)
Rich reviewed the site and reports: some sections look stale or don't make sense,
there is still repetition, and there are one or two gaps. The advisor independently
verified concrete instances from the repo (below). Treat the listed items as
*examples found remotely*, not the full defect list — the primary deliverable is a
sweep of **every** page (live and shadow) against three tests: (a) is this stamp or
figure current? (b) does this section say something no other section already says?
(c) does this section still make sense to a first-time reader?

## Verified defects (fix these, then keep sweeping)
1. **Stale stamps, wrong at source.** `site/shadow/index.html` regenerated today but
   its header reads "Phase RE | 15740 tests" — the project is at Phase RX with a
   materially different test count. `site/project/index.html` last meaningfully
   updated 2026-07-03 and still references Phase OL. Root-cause fix required, not a
   hand-edit: **one generator-owned stamp** (phase, test count, date, commit) that
   every page consumes. No page may carry its own literal phase/test/date values.
2. **Cross-surface number inconsistency.** Test counts differ across surfaces
   (15,740 / 15,872 / 15,959 seen simultaneously today). Add phase stamp + test
   count + headline financials to the consistency gate, **including shadow-vs-live
   divergence** — the shadow copy is a surface too and must not silently drift.
3. **Repetition.** `site/supplier/index.html` carries three adjacent reputation
   blocks ("Reputation & Customer Feedback", "Global Reputation Index — Portfolio
   Trend", "Reputation Events"). Collapse into one coherent section with a single
   narrative: what the public sees → what the company infers → what it did about it.
   Then sweep all pages for the same pattern (multiple sections restating one fact).
4. **Encoding bug.** A supplier-page heading renders the literal text `\u2014`
   instead of an em-dash ("Nudge Discovery \u2014 Offer Framing"). Fix at the
   generator (escaping path), not by editing the output HTML, and grep all
   generated output for other escaped-literal leaks (`\u`, `&amp;amp;`, `&#`).
5. **RX evidence gap (rule 0b).** Phase RX closed this morning; its shadow-live
   predicted-vs-realised scorecard is not yet visible on any business surface.
   Land it where a reader would look for it (Sim or Supplier tab), stamped by the
   shared generator stamp from item 1.

## Definition of done (R1 — consumer-verified)
- The advisor or director fetching the **deployed** pages (not the repo copy) sees:
  a single consistent phase/test/date stamp on every page; no duplicated reputation
  sections; no escaped-literal text; RX scorecard present; shadow and live agree or
  the divergence is deliberate and labelled.
- Remember R2: committed ≠ deployed. Verify after the publish step actually runs.
- Report via NTFY with the list of *additional* defects found in the sweep beyond
  the five above — that list is the evidence the sweep happened.

## Out of scope
No new board sections, panels, or metrics (rule 0a/R6). This phase removes and
corrects; it adds nothing except the RX evidence already owed under 0b.
