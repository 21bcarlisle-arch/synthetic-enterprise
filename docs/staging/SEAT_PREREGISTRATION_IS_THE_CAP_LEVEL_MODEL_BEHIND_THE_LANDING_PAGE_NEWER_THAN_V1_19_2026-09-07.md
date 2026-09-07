**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-commons-artefact-cannot-tell-when-its-source-was-revised

# PRE-REGISTRATION — is the cap level model behind the landing page newer than v1.19, and does it move the shares?

*A pre-registration asserts nothing; it fixes the predictions before the answer is read. The finding
it feeds carries its own severity, and is
`SEAT_FINDING_THE_CAP_COMPOSITION_CITES_A_MODEL_TWELVE_EDITIONS_STALE_AND_ITS_RECHECK_RECIPE_NAMED_THE_WRONG_PAGE_2026-09-07.md`.*

**Filed 2026-09-07, BEFORE the version was read.** Written after the first two fetches and before the
third, and the state of knowledge at the moment of writing is stated exactly so the reader can judge
whether the predictions were cheap.

## What is being measured

`docs/domain_artefact_library/regulatory/ofgem_cap_unit_rate_composition.json` cites
`Default_tariff_cap_level_v1.19.xlsx` behind an unversioned Ofgem landing page — the `in_filename_only`
shape, which `tools/commons_source_supersession.py` names as the most dangerous of the five because
the URL keeps resolving whatever edition it now serves. Its verdict has stood at `cannot_tell` since
2026-09-07 because the earlier read of that landing page surfaced only the Annex 9 levelisation
workbook (v1.11), which is a different publication.

## What was already known when this was written

1. The stored landing page (`/energy-policy-and-regulation/.../default-tariff-cap`) was fetched at
   2026-09-07, HTTP 200, 221,775 bytes, and carries exactly ONE `.xlsx` link:
   `Annex-9-Levelisation-allowance-methodology-and-levelised-cap-levels-v1.11.xlsx`. It does not link
   the cap level model at all. That reproduces the earlier `cannot_tell` and explains it: the recorded
   `how_to_recheck` ("open it, find the cap level model link") describes a link that is not there.
2. A DIFFERENT Ofgem page —
   `/energy-regulation/domestic-and-non-domestic/energy-pricing-rules/energy-price-cap/energy-price-cap-default-tariff-levels`
   — was fetched, HTTP 200, 381,032 bytes, and carries a version history of
   `Default_tariff_cap_level_v*.xlsx` workbooks. Versions seen in the first 40 lines of that listing:
   v1.9 (2021-08), v1.10 (2022-02), v1.13 (2022-08), v1.14 (2022-11), v1.15 (2023-02), v1.18 (2023-05).
   The listing was truncated at 40 rows and continues past 2023-08; **the highest version present has
   not been read.**

## The predictions

**P1 — the current cap level model is strictly newer than v1.19.** The linked history reaches v1.18 by
2023-05 while the page itself carries 2026-08 material, and the cap has been re-set quarterly
throughout. Anything else would mean Ofgem stopped versioning this workbook in 2023.
*Confidence: high. This is the cheap prediction and is registered as such.*

**P2 — the artefact's per-period shares do NOT move.** Every period in the artefact ends at
October–December 2023. Those are cap levels Ofgem has already published and charged against, and a
later edition of the model extends the table forward rather than restating settled periods. If P2
holds, the artefact is stale in its CITATION and correct in its VALUES, and the repair is a re-point
plus a coverage gap (2024-01 onward missing), not a re-derivation.
*Confidence: moderate. The named way P2 fails is a methodology restatement — levelisation (Annex 9,
the very workbook the landing page does serve) changed the allowance construction, and if the newer
model restates historical nil-consumption or benchmark allowances on the levelised basis then the
component split, and therefore the share, moves for settled periods too.*

**P3 — `headline.min_share` 0.4077 and `max_share` 0.8077 are unchanged.** This follows from P2 and is
registered separately because it is the figure a reader quotes.

**P4 — this will change the verdict off `cannot_tell`.** Either to `superseded` (P1 true) or to
`current` (P1 false). A third `cannot_tell` would mean the newer model could not be located or read,
and that outcome is recorded here in advance as a real possibility so that reporting it is not a
retreat: openpyxl must open a workbook Ofgem may publish with a structure the v1.19 derivation code
does not match.

## What would refute each

- P1 is refuted by the highest `Default_tariff_cap_level_v*` on the page being v1.19 or lower.
- P2/P3 are refuted by re-deriving any settled period's share from the newest workbook and getting a
  different number. The comparison is against the artefact's own stored `commodity_share_of_unit_rate`
  per period, per payment method, not against the headline — a headline can be unmoved while periods
  underneath it move in offsetting directions.
- P4 is refuted by the read failing.

## The thing this must not become

The artefact's `cross_check_against_published_cap_levels` block already agrees with published cap
levels to 1.34% worst case. That block is evidence the v1.19 derivation was RIGHT; it is not evidence
that v1.19 is CURRENT, and the two must not be confused when the answer comes back. A correct reading
of a superseded publication is exactly the failure that opened this whole line of work.
