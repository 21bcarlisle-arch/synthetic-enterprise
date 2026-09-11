**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-commons-artefact-cannot-tell-when-its-source-was-revised

# The cap composition cites a model twelve editions stale, its re-check recipe named the wrong page, and every settled period it published is right to the digit

**Measured:** 2026-09-07, delivery seat. Predictions fixed before the version was read, in
`SEAT_PREREGISTRATION_IS_THE_CAP_LEVEL_MODEL_BEHIND_THE_LANDING_PAGE_NEWER_THAN_V1_19_2026-09-07.md`.
**Class:** `figures_on_a_superseded_clock`.
Discharges item 3 of `SEAT_FINDING_TWO_COMMONS_ARTEFACTS_CITE_A_PUBLICATION_THAT_HAS_MOVED_AND_FOUR_OF_NINE_COULD_NOT_BE_ASKED_2026-09-07.md`.

## The one-sentence finding

`ofgem_cap_unit_rate_composition` was derived from `Default_tariff_cap_level_v1.19.xlsx` (2023-08)
and the current edition is **v1.31** (2026-08) — twelve version numbers on, **ten published editions
the page still carries** — and the reason nobody could
tell is that the artefact's `how_to_recheck` told the reader to look for the model on a page that has
never linked it.

## The verdict moves `cannot_tell` -> `superseded`

| | |
|---|---|
| cited | `Default_tariff_cap_level_v1.19.xlsx`, `/sites/default/files/2023-08/` |
| current | `Default-tariff-cap-level-v1.31.xlsx`, `/sites/default/files/2026-08/` |
| editions the page carries after v1.19 | v1.20, v1.21, v1.22, v1.23, v1.24, v1.25, v1.28, v1.29, v1.30, v1.31 — ten. The series skips numbers, and v1.30 is published under a different NAME (`Energy-price-cap-levels-pre-levelised-rates-model-v1.30`), so a check keyed to the filename stem rather than the version would have missed it. |
| cap periods we are short | **twelve**, January 2024 through October–December 2026 |

## Why it stood at `cannot_tell` for a day, and it was not the publisher's fault

The artefact's stored URL is `/energy-policy-and-regulation/policy-and-regulatory-programmes/default-tariff-cap`.
Fetched 2026-09-07: HTTP 200, 221,775 bytes, and it carries **exactly one** `.xlsx` link — the Annex 9
levelisation workbook, v1.11. It does not link the cap level model and, on the evidence of the page
itself, never did. The recipe said "open it, find the cap level model link, and read the version out
of the FILENAME". There is no such link, so the recipe terminates in `cannot_tell` every time it is
run, forever, and the artefact would have sat at `cannot_tell` indefinitely while reading as though
the question had been asked.

**The model lives on a different page**: `/energy-regulation/domestic-and-non-domestic/energy-pricing-rules/energy-price-cap/energy-price-cap-default-tariff-levels`,
which carries the full versioned history from v1.2 (2019-02) to v1.31 (2026-08). One fetch, and the
answer is unambiguous.

This is the `in_filename_only` failure being *worse* than the module's own docstring says. The
docstring's fear is that the landing page keeps resolving while serving a newer edition. The reality
here is that the landing page keeps resolving while serving **nothing at all** on this subject — and
a 200 with the wrong content reads exactly like a working check.

## What was PREDICTED and what happened

| # | prediction | outcome |
|---|---|---|
| P1 | the current model is strictly newer than v1.19 | **CONFIRMED** — v1.31 |
| P2 | no settled period's share moves | **CONFIRMED** — all 21 identical, see below |
| P3 | `min_share` 0.4077 / `max_share` 0.8077 unchanged | **CONFIRMED**, follows from P2 |
| P4 | the verdict leaves `cannot_tell` | **CONFIRMED** — `superseded` |

P1 was registered as the cheap prediction and it was. **P2 is the one that mattered and it was
registered at moderate confidence with its failure mode named** — a levelisation restatement of
settled periods. It did not happen.

## The measurement behind P2, and why it is not the flattering read

All 21 periods the artefact publishes were re-derived from v1.31 and compared to the stored values,
per period, for direct debit:

- **21 of 21 commodity shares identical to four decimal places.**
- **21 of 21 annual £ allowances (benchmark minus nil) identical**, ratio 1.0000 to four decimals in
  every period, so this is not shares agreeing by cancellation — the numerator and denominator are
  each unmoved.

**The share is invariant to the benchmark divisor by construction** (it is a ratio of two quantities
divided by the same kWh), so this comparison is valid regardless of the basis question below, and it
was chosen for that reason rather than because it was the available one.

So: **the artefact's VALUES are right and its CITATION is stale.** Those are different defects and
only one of them is present. The `cross_check_against_published_cap_levels` block inside the artefact
— worst relative error 1.34% across 13 periods — is evidence the *derivation* was right. It is not
and never was evidence that v1.19 was *current*, and conflating the two is the exact failure that
opened this whole line of work.

## THE TRAP ANY RE-DERIVATION WALKS INTO, and it is not visible from the sheet name

v1.31 renames the sheets: `ElecSingle_Other_3100kWh` -> `ElecSingle_Other_Benchmark`. The reader
resolves that sheet by an f-string built from `BENCHMARK_KWH`, so it **fails closed** on v1.31 rather
than reading it wrongly. Good. But the obvious repair — resolve the sheet by pattern and read the
benchmark out of the header cell, which is what the constant's own docstring already claims happens —
**is wrong, and wrong by 24%.** Row 7 of that sheet says:

> Benchmark Annual Consumption Level: **2,500 kWh**. *"Following the review of benchmark consumption
> in the energy price cap decision on 21 November 2025, from Jan 2026 - March 2026 (cap P15b) onwards
> outputs in this tab are based on the revised typical consumption. All previous cap periods up to
> P15b are ba[s]ed on the old typical consumption (3,100 kWh) in this tab."*

**One header cell, two bases, in one column block.** A reader that takes the header at its word
divides every pre-2026 column by 2,500 instead of 3,100 and inflates every historical unit rate by
24% (29 of the 33 periods, in all three payment methods) — while every *share* stays correct,
because the divisor cancels. The headline would look
untouched and the published p/kWh series would be silently wrong. That is the same shape as the RO
buy-out indexation change landed this morning: **the basis changes inside one column and the file
must say so beside the figures.**

The divisor rule is confirmed against published data, not inferred. Deriving with 3,100 for
January 2024 – October 2025 and cross-checking against `ofgem_default_tariff_cap_windows.json`:

| period | derived ×1.05 £/MWh | published | error |
|---|---|---|---|
| Jan–Mar 2024 | 284.8 | 286.2 | 0.5% |
| Apr–Jun 2024 | 245.2 | 245.0 | 0.1% |
| Jul–Sep 2024 | 223.7 | 223.6 | 0.0% |
| Oct–Dec 2024 | 245.0 | 245.0 | 0.0% |
| Jan–Mar 2025 | 248.6 | 248.6 | 0.0% |
| Apr–Jun 2025 | 270.3 | 270.3 | 0.0% |
| Jul–Sep 2025 | 257.9 | 257.3 | 0.2% |
| Oct–Dec 2025 | 264.8 | 263.5 | 0.5% |

At 2,500 the same rows land 24% high in every case. So the sheet's own note is corroborated for its
pre-2026 half by published cap levels. **Its post-2026 half is NOT corroborated here**, because
`ofgem_default_tariff_cap_windows.json` stops at 2025-12-31 and has nothing to check the four 2026
periods against. That is stated rather than assumed: the four 2026 periods rest on the publisher's
note alone.

## The second defect, found on the way, and it is why the block would have rotted again

`tools/ofgem_cap_unit_rate_composition.py::main` writes `measure()` straight over the artefact.
`measure()` does not emit `source_check`. **Re-running the derivation therefore DELETES the
supersession block**, which takes the artefact from `superseded` to un-askable and wedges every
lane's commit on the ASKABLE leg — the failure arriving through the one action a diligent session
would take. Repaired here: `main()` carries the existing block forward and stamps the model name it
actually read, so a re-run cannot silently claim a fetch it did not perform.

## The mechanism this generalises to, built beside it in this commit

Nothing in the tree could ask whether a citation SUPPORTS the provenance level claimed beside it —
the defect the RO repair found one row over this morning.
`tools/commons_citation_supports_provenance.py` puts that question, offline, from the artefact's own
bytes. Its NOT_AFTER leg refuses the real pre-repair RO entry read out of commit 5a2778d06, and its
DEFINED leg refused a live artefact on its first run over the tree: **`gb_domestic_switching_rate`
stamped ten rows `primary` while its own `how_to_recheck` says "THIS ARTEFACT CITES A DERIVATION, NOT
AN EDITION"**. The file contradicted itself, in two fields, and had done since it was written. All
ten are now `secondary` against a legend that says what the two levels mean here; `primary` is
defined in that file and deliberately reached by nothing, because reaching it is the artefact's own
open job.

## What is next

1. **Extend the composition to the twelve missing cap periods** (Jan 2024 – Dec 2026) off v1.31. This
   needs three changes to `tools/ofgem_cap_unit_rate_composition.py`, and it is a separate landing
   because it moves a published figure: resolve the benchmark sheet by pattern; carry a PER-PERIOD
   benchmark (3,100 up to P15a, 2,500 from P15b) rather than one constant; and state that basis
   change in the artefact's `basis` beside the figures.
2. **Expect the headline claim to move and do not defend it.** The reading "ABOVE 0.40 in every
   period the cap has actually been in force" is stated over periods ending 2023-12. The unpublished
   2024–2026 shares run 0.4710–0.5773, so it survives on today's evidence — but it is a claim keyed
   to a window, and the window is what changed.
3. **Extend `ofgem_default_tariff_cap_windows.json` past 2025-12**, without which the four 2026
   periods cannot be cross-checked and the fail-closed corroboration silently covers less of the
   series each quarter. That artefact is itself `cannot_tell` for want of an edition marker.
4. **Re-point the other `in_filename_only` artefacts' recipes at a page that carries the file.** This
   one named a page that 200s and serves nothing on the subject; that is not a property of this
   artefact, it is a property of recipes nobody has ever run to completion.
