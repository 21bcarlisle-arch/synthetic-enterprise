**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-commons-artefact-cannot-tell-when-its-source-was-revised

# The switching-rate artefact's URL was a 404, its derivation cited a price table, and the publisher's own release refutes 8 of its 10 years

**Measured:** 2026-09-07, delivery seat. Predictions fixed before any figure was read, in
`SEAT_PREREGISTRATION_CAN_THE_SWITCHING_RATE_BANDS_BE_READ_FROM_THE_PUBLISHERS_OWN_RELEASE_2026-09-07.md`.
**Class:** `figures_on_a_superseded_clock`.
Discharges the last `cannot_tell` named in
`SEAT_FINDING_TWO_COMMONS_ARTEFACTS_CITE_A_PUBLICATION_THAT_HAS_MOVED_AND_FOUR_OF_NINE_COULD_NOT_BE_ASKED_2026-09-07.md`.

> **TWO LANES FOUND THIS INDEPENDENTLY AND CONCURRENTLY, AND THE OTHER ONE LANDED FIRST.**
> `f706dbf3d` (21:05) settled the artefact from a separate seat while this work was in its gate run;
> its finding is
> `SEAT_FINDING_THE_SWITCHING_BANDS_OWN_PUBLISHER_DISAGREES_WITH_IT_IN_EIGHT_OF_TEN_YEARS_2026-09-07.md`.
> Same publication, same 8 of 10, same root cause, same judgement not to repair the band without a
> re-capture. **That lane's artefact text is kept and this one's was discarded** — this document is
> rebased to be additive rather than a second account of the same discovery, because two narrations
> of one finding is how a reader ends up unable to tell which is current.
>
> **It did one thing this pass did not, and it is the better check:** before claiming the verdict it
> tested both obvious rescues — against the file's own flat 28.0m denominator it is still 8 of 10
> outside on the same years, and read as *both fuels* it is 8 of 10 outside on *different* years. So
> the band is not a mislabelled fuel scope or a divisor error; it is a different series. That is a
> stronger statement than anything measured here and it is theirs.
>
> **What this document and its landing add**, and the reason it is not withdrawn entirely:
> - the **control** — `tests/architecture/test_a_refuted_commons_artefact_cannot_quietly_become_current.py`
>   and the machine-readable `values_refuted_by_the_publisher` block it reads. The other landing
>   states the refutation in prose in a `note`; nothing held it to the bands it measures, so
>   *widening one band until it swallows the publisher's figure* would have erased the finding
>   without moving a single value. Five mutations run against the live artefact, all firing.
> - the **root cause corrected at its source** — `churn_price_elasticity.md` §1 now carries the
>   refutation banner. Both lanes diagnosed the Table 2.1/2.7.1 slip; neither had corrected the file
>   that contains it, which is the file the next reader will copy from.
> - the **knowledge map** — its "Switching rates" row still read **SETTLED** on the refuted band.
> - **P3's refutation**, below, which is a pre-registered prediction and belongs to whoever registered
>   it before looking.
> - the **ElectraLink fuel scope**, resolved to electricity.

## The one-sentence finding

`gb_domestic_switching_rate` said of itself *"THIS ARTEFACT CITES A DERIVATION, NOT AN EDITION, and
that is the thing to fix rather than to check around"* — and when the edition was finally fetched it
did not merely date the file, **it refuted it: 8 of the 10 published bands do not contain the
publisher's own figure for that year.**

## The verdict moves `cannot_tell` → `superseded`

| | |
|---|---|
| cited (v1) | an in-repo derivation, `churn_price_elasticity.md` §1; URL `/government/collections/domestic-energy-switching-statistics` |
| that URL, fetched 2026-09-07 | **HTTP 404.** The page does not exist. |
| actual publication | DESNZ *Quarterly domestic energy switching statistics*, QEP table 2.7.1, `/government/statistical-data-sets/quarterly-domestic-energy-switching-statistics` |
| edition marker it "lacked" | `public_updated_at` = **2026-06-30T09:30:10+01:00**, with a quarterly `change_history` and a stated next release of 2026-09-29 |

**The artefact was never missing an edition marker. It was pointed at a page that does not exist.**
This is the second commons recipe in two days that could not terminate — after the cap composition,
whose page resolved 200 and served nothing on the subject. That one failed by serving the wrong
thing; this one by not being there at all. Both read, from inside, exactly like a check that had
been run. **A recipe nobody has run to completion is not a check**, and neither of these had ever
been run to completion.

## What was PREDICTED and what happened

| # | prediction | outcome |
|---|---|---|
| P1 | the data set carries a domestic **electricity** switch count 2016–2025 that annualises | **CONFIRMED**, and better than registered — it publishes the **denominator beside the numerator**, so the rate needs no second source |
| P2 | at least one of 2022–2025 falls outside its band | **CONFIRMED** — three of the four do |
| P3 | 2016–2021 sit inside their bands | **REFUTED — five of the six are outside** |
| P4 | the verdict leaves `cannot_tell` | **CONFIRMED** — `superseded` |

**P3 is the one I was most confident about and it is the one that broke.** The six early years
carried precise stated counts and two had been separately live-adjudicated against Energy UK, which
is exactly why they read as the trustworthy half. The precision was real and the numbers were still
wrong: *a figure quoted to three significant figures is evidence of how it was written down, never
of where it came from.*

## The comparison

| year | this file (m) | publisher (m) | in band? | file rate % | publisher rate % |
|---|---|---|---|---|---|
| 2016 | 4.76–4.93 | 4.420 | **OUT** | 17.0–17.6 | 15.82 |
| 2017 | 3.78–3.92 | **5.118** | **OUT** | 13.5–14.0 | 18.20 |
| 2018 | 5.46–5.60 | 5.402 | **OUT** | 19.5–20.0 | 19.06 |
| 2019 | 5.80–5.96 | 5.946 | in | 20.7–21.3 | 20.82 |
| 2020 | 6.30–6.44 | 5.811 | **OUT** | 22.5–23.0 | 20.21 |
| 2021 | 5.01–5.15 | 4.502 | **OUT** | 17.9–18.4 | 15.57 |
| 2022 | 0.80–1.20 | 0.893 | in | 2.9–4.3 | 3.06 |
| 2023 | 2.50–3.50 | 1.867 | **OUT** | 8.9–12.5 | 6.33 |
| 2024 | 3.50–4.50 | 2.681 | **OUT** | 12.5–16.1 | 9.03 |
| 2025 | 4.00–5.00 | 3.146 | **OUT** | 14.3–17.9 | 10.40 |

**The two that hold are not confirmations.** 2022's band is 1.4pp wide on a 3.1% level. Eight bands
are refuted and two are *not refuted*, which is a different thing — and a band wide enough that it
cannot be wrong is not doing the work a band is for.

Three things the table says that the row-by-row reading does not:

- **The peak is in the wrong year.** The file calls 2020 the high-water mark at 6.39m. The record
  says 2019 (5.946m) beat 2020 (5.811m). The 2020 row's own note *already recorded* Energy UK
  corroborating ~5.9m — and kept 6.39m anyway. The disagreement was written down at the time and
  nothing acted on it.
- **2017 is the only optimistic error and the largest.** The file calls it a consolidation trough at
  3.84m; the publisher says 5.118m, **up** on 2016. There is no 2017 trough in the published record.
  Every other error runs high.
- **The denominator is wrong too.** `basis` says accounts "sat between 27.5m and 28.3m" and that a
  flat 28.0m costs "less than 0.4pp". The publisher's own column runs 27.947m → **30.249m**, outside
  that range in five of ten years, and the true worst error is **0.835pp** at 2025.

## The root cause, and it is one wrong digit in a citation

`churn_price_elasticity.md` §1 names its source as **"DESNZ Quarterly Energy Prices Table 2.1"**.
Table 2.1 is a domestic **price** table. The switching series is table **2.7.1**. On the evidence of
the numbers, the series was never read from the switching table at all — which is consistent with
every symptom above, including a 2017 trough that exists in no published source.

## Why the values are NOT corrected in this landing, and it was measured rather than assumed

Correcting `rates` in place turns **20 controls** red in
`tests/architecture/test_switching_rate_commons.py`, and they are not all containment.
`tools/fit_year_level_anchor.py --internal-return` **refuses outright** against the corrected record
— *"1313 of 1313 SVT rows are reproduced by NEITHER composition"* — because **the committed world
capture's SVT hazards were produced by a world running on these rates.** Six committed verdict
blocks derive from that capture (`--composition`, `--emergent-verdict`, `--internal-return`,
`--route-attribution`, `--svt-shortfall`, `tools/published_route_split --write`).

So the repair is: correct the record → re-capture the world → regenerate all six, **in one landing**,
because the same tree cannot hold half of it. That is a world-behaviour change and it is not this
turn's. The refutation therefore lands as a block *beside* the wrong values, with the publisher's
figures tabulated in it, and `tests/architecture/test_a_refuted_commons_artefact_cannot_quietly_become_current.py`
holds the two apart.

## What the repair will do, stated now so it cannot be claimed as a win later

The world reads `rate_pct_hi` live, so its target level moves the moment `rates` moves: the mean high
endpoint falls **16.5% → 13.9%**, with the recent years hardest — 2023 **−49.3%**, 2024 **−43.9%**,
2025 **−41.9%**.

`departure_level_anchor` records six of seven fitted years sitting **BELOW** their band by 3.3pp to
9.0pp. A band that falls 3–7pp in the recent years moves the record **toward** the world. **Part of
that standing gap is this file being wrong, not the world being wrong.**

**What must not be concluded is that the world is therefore fine.** The gap shrinking because the
target moved is not the mechanism improving, and `departure_level_anchor` already says the repair
belongs *downward* into the individual model's hazards, not sideways into a different scalar. How
much of the gap was the record is **not established here and must not be guessed** — it is exactly
what the re-capture is for. Written down before the re-capture runs, so it cannot be filed as a
prediction afterwards.

## Settled on the way

The `unreconciled_cross_check` against ElectraLink is **partly resolved**. v1 could not tell whether
its count was electricity or both fuels and said the readings "differ by a factor of 1.8". The
publisher's per-fuel columns settle it: read as both fuels, ElectraLink's 2019 peak of 6.34m would
have to match the record's 10.768m — 41% low, which no counting convention explains. Read as
electricity it is 6.34m vs 5.946m (2019) and 3.21m vs 2.681m (2024): **consistently 7–20% above the
Ofgem/DESNZ count, in the same direction every year.** It is an electricity series. *Why* it runs
high is still open and is not guessed at.

## A dial the director should know has been emptied

`reserved` says where inside the band the world is aimed is a curriculum value, tie-broken to the
high end. With v1's bands up to 3.6pp wide that choice was worth 1.8pp in 2024. Once the record is
the publisher's own count the band is a **0.1pp** declared rounding tolerance and the tie-break moves
the world by 0.05pp. **The rule is unchanged and nothing here decides anything** — but the evidence
becoming precise has emptied the dial, and that is a thing to be told rather than to discover.

## What is next

1. **The re-capture landing**: correct `rates` to the publisher, re-capture, regenerate the six
   verdict blocks, re-fit `YEAR_LEVEL_ANCHOR`, and report how much of the 3.3–9.0pp gap was the
   record. The corrected table is already tabulated in the artefact, so no re-fetch is needed.
2. **`company/market/market_report.py::_UK_DOMESTIC_ACCOUNTS_M`** is wrong against the same table
   (27.5–28.3 claimed, 27.947–30.249 published) and is a separate constant with its own callers.
   Filed, not fixed.
3. **Audit the remaining commons recipes by RUNNING them**, not by reading them. Two of two examined
   this week named a page that could not answer the question. That is not a property of these two
   artefacts; it is a property of recipes nobody has ever run to completion.
