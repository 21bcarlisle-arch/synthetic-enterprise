# PowerTAC 2020 — retail energy market simulation/tournament platform

**Purpose:** mine PowerTAC's tariff/customer model and tournament design as prior art for
this project's own tariff/contract module and (potentially, later) a curriculum/tournament
concept — design comparison only, never adopted as a runtime dependency. Explicitly flagged
as the priority artefact in the 2026-07-11 DOMAIN_ARTEFACT_LIBRARY.md amendment.

## Source (R9)

Official spec, per the PowerTAC project's own GitHub wiki: **"The 2020 Power Trading Agent
Competition"**, Wolfgang Ketter, John Collins, Mathijs de Weerdt, SSRN,
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3564107.

**Honest limitation: SSRN returned HTTP 403 to automated fetch** — the actual spec PDF could
not be pulled directly this pass. Substituted with the project's own actively-maintained
GitHub wiki (same design, same authors' project), cited per-claim below. Server version
referenced: 1.8.0-SNAPSHOT (Javadoc summary page). A follow-up pass should try downloading
the SSRN PDF via a different method (e.g. an authenticated tool, or a direct PDF mirror) if
the full spec's additional detail (exact tournament scoring formula, replay mechanism,
further customer-model detail) is needed — nothing below asserts content that wasn't
actually fetched.

## Customer/tariff model

`TariffSpecification` (broker→server value object: rates, hourly charges) wrapped
server-side in `Tariff` (rates remapped to a 2-D array by usage tier × hour);
`TariffSubscription` tracks subscriber counts and credits/debits. Rate types: tiered,
time-of-use, weekday/weekend, two-part (fixed+usage), variable (min/max, notice interval),
sign-up incentives, early-withdrawal penalties. `noticeInterval` gives customers advance
warning of price changes.
Source: https://github.com/powertac/powertac-server/wiki/Tariff-representation

## Tournament/replay design

Trial rounds (3–4, pre-finals, current-or-prior server version) → qualifying rounds →
finals; results published as machine-readable CSVs with a DOI per game. **No replay
mechanism found** in fetched content — not asserting one exists.
Source: https://powertac.org/tournament/

## Default-broker/fallback mechanism

Documented role: "Simulates holder of all customer tariffs prior to market opening." That's
the only confirmed detail — no rate-calculation mechanics found. This is a
simulation-bootstrapping device (holds customers before any broker has published a tariff),
not equivalent in mechanism to a real UK deemed/SVT fallback rate — a naming parallel only,
not a design match.
Source: https://powertac.github.io/server/master/default-broker/summary.html

## Tariff lifecycle state machine

Created (`TariffSpecification` submitted, validated) → published (wrapped in `Tariff`,
publication fee via `TariffTransaction`) → active/unexpired (broadcast via `TariffMarket` to
`NewTariffListener`s for subscription) → modified (`VariableRateUpdate` for variable-rate
tariffs) → expiring (`TariffExpire`, adjustable including immediate) → revoked
(`TariffRevoke` → immediate KILLED status; subscribers must call
`getRevokedSubscriptions()`/`handleRevokedTariff()` to transition to a superseding or default
tariff; fee applies if subscribers were active).
Source: https://github.com/powertac/powertac-server/wiki/Tariff-publication-story

## Adopt/adapt/skip verdicts

- **Tariff rate-type taxonomy** (tiered/ToU/weekday-weekend/two-part/variable-with-notice/
  sign-up-incentive/early-withdrawal-penalty): **ADAPT** — a genuinely useful checklist to
  sanity-check whether this project's own contract/tariff module (`company/billing/
  contract.py` and related) covers the same real-world rate-shape variety. Not yet checked
  against the actual module in this pass — registered as the concrete follow-up.
- **Tariff lifecycle state machine** (created→published→active→modified→expiring→
  revoked/KILLED, with revocation fees and notice-interval semantics): **ADAPT** — a clean
  external reference if this project's own contract module doesn't already model fee-bearing
  revocation and variable-rate notice explicitly. Not yet checked against the actual module
  in this pass.
- **Default-broker mechanism: SKIP** as a mechanism (bootstrapping device, not a real
  deemed/SVT equivalent) — a one-line cross-reference note is the most this earns, not
  adoption.
- **Tournament/replay design: SKIP for this pass** — too thin in what was fetchable (SSRN
  blocked) to justify any adoption decision without a deeper pass on the actual spec PDF.

## Provenance tag

**`generator-anchor`** only, if adopted at all — PowerTAC's tariff/lifecycle design would
inform this project's own SIM-side tariff/contract GENERATION patterns, not something a real
UK company "knows" (`company-knowable` doesn't fit), and per the mutual-exclusivity rule
cannot also be used as a `validator-anchor` alongside generator use.

## Follow-up registered, not started this pass

Direct comparison of the two ADAPT-verdict items (rate-type taxonomy, tariff lifecycle state
machine) against this project's actual `company/billing/contract.py` — this entry only
reports PowerTAC's own design, it does not yet assess the gap against this repo's real code.
