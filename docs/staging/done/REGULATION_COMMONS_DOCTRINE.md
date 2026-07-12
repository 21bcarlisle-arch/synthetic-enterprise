# REGULATION_COMMONS_DOCTRINE — one text, three owned derivatives (Tier 2, doctrine)

**Staged:** 2026-07-12 by advisor; director-raised ("should the oracle be SIM
or supplier discovery, or generally available?"), advisor-answered, director
direction. Small; record in CLAUDE.md + artefact library doctrine; wire into
the three-lane profiles being consumed today.

## Doctrine
1. **The TEXT is a commons.** Regulatory rule digests (the fidelity oracle
   and successors) live in the domain artefact library, provenance-tagged,
   readable by ALL lanes/profiles — mirroring reality: law is published.
   Under the wall-split hook profiles, the library is explicitly on the
   shared-readable list while sim/** and company/** stay mutually blind.
2. **Implementations are OWNED, three times, independently:**
   - WORLD (W3/W2): enforcement physics — regulator behaviour, ombudsman
     per-case fees as events, GSOP payments, customers whose behaviour
     reflects rights they hold.
   - COMPANY (D/F): its OWN reading of the law — compliance logic,
     obligations register, billing constraints (e.g. the 12-month cap).
   - HARNESS: validator invariants derived from the text, independent of
     both implementations, jurisdiction-tagged.
   **No implementation code crosses the wall.** Independence is fidelity:
   a company importing the world's enforcement can never MISREAD the law —
   and real suppliers misread law and are fined for it. Interpretation risk
   must remain structurally possible.
3. **Law is time-indexed — the blindfold covers regulation itself.** Every
   rule entry carries effective/repeal dates (21BA from 2018-05; PPM warrant
   restrictions post-2023; etc.). A decision at sim-time T may only see law
   effective at T. Regulatory CHANGES arrive to the company as publication
   events on the timeline (the existing cap-publication pattern generalised)
   — never by reading future statute. The library schema gains
   effective_from/effective_to; the as-of interface serves law like any
   other revealed truth.

## DoD
Doctrine in CLAUDE.md + DOMAIN_ARTEFACT_LIBRARY usage rules; library path on
the shared-readable list in the lane hook profiles; effective-date fields in
the library schema (backfill the oracle's UK rows); one digest line.
