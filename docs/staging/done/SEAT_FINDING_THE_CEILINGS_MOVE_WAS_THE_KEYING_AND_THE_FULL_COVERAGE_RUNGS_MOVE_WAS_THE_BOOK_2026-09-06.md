**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# The ceiling's move was the keying and the full-coverage rung's move was the book — the published attribution had them the wrong way round

**Found:** 2026-09-06, delivery seat, claim
`the-r1-ceiling-is-a-selected-maximum-published-as-a-bound`.
Pre-registration: `records/SEAT_PREREGISTRATION_THE_ONE_VARIABLE_RERUN_SAME_BOOK_NEW_KEYING_2026-09-06.md`
— written before the run. **Three of its five predictions are refuted**, and two of those three
refute a causal story this project landed yesterday at `f92232d53`.

No instrument was changed here. This is the one-variable re-run that `f92232d53` handed on:

```
python3 -m tools.r1_inference_ceiling --run <shared tree>/docs/reports/run_output_23cbe058b_20260906T141424Z.json
```

---

## The design, and why it can attribute where the last run could not

`f92232d53` compared the HEAD instrument on a **later** book against the pre-keying instrument on
the **published** one. Two variables, so it refused to attribute anything and handed this on. Three
cells of the 2×2 now exist and the fourth is not needed:

| | book `23cbe058b` (14:14Z) | book `3851553ec` (17:59Z) |
|---|---|---|
| **pre-keying instrument** | artefact at `613f9bd17` | *not run — not needed* |
| **HEAD instrument** | **this run** | artefact at `c244b93a0`, now `origin/main` |

Reading down the first column isolates the **instrument**. Reading across the bottom row isolates
the **book**. `613f9bd17`'s artefact names `run_output_23cbe058b_20260906T141424Z.json` in its own
`run_output` field, checked before the run, so the first column really is one book.

**And the two books are the same population, verified directly rather than assumed** — both hold
**264 supply points → 177 households, 87 legs folded**, at base seed `20260724`. So the bottom row
is not "a bigger book". It is the *same 177 households, logged more*.

## The decomposition

### Column: the keying alone, on the published book

| | `613f9bd17` | this run | |
|---|---|---|---|
| ids graded | 213 supply points | **149 households** | folded |
| `mean_recent_margin_rate` | n=213, −0.0422 | **n=149, +0.0537** | moved |
| `portfolio_premium_pct` | n=213, −0.0509 | **n=149, −0.0401** | moved |
| `unit_rate_gbp_per_mwh` | n=100, refused | n=100, refused | **identical** |
| `svt_rate_gbp_per_mwh` | n=69, −0.1263 | n=69, −0.1263 | **identical** |
| `rate_vs_svt_pct` | n=69, −0.3530 | n=69, −0.3530 | **identical** |
| `company_eac_kwh` | n=69, −0.0645 | n=69, −0.0645 | **identical** |
| `company_churn_estimate` | n=69, +0.2362 | n=69, +0.2362 | **identical** |
| `resentment_score` | n=69, refused | n=69, refused | **identical** |
| `perceived_bill_saving_gbp` | n=69, +0.4799 | n=69, +0.4799 | **identical** |
| `expected_term_margin_gbp` | n=56, −0.0061 | n=56, −0.0061 | **identical** |
| **ceiling (best of 45)** | **+0.6127** | **+0.6308** | **moved** |
| in-sample on the winner | +0.1674 | +0.2288 | moved |
| corrected bound p95 | +0.5529 | +0.5779 | moved |
| **p** | **0.0249** | **0.0249** | **identical (4/200 both)** |
| **full-coverage rung p** | **0.8507** | **0.8657** | **did not fall** |

### Row: the book alone, on the HEAD instrument

| | this run (`23cbe058b`) | `origin/main` (`3851553ec`) | |
|---|---|---|---|
| population | 264 pts / 177 hh / 87 legs | 264 pts / 177 hh / 87 legs | **identical** |
| households carrying an observable | 149 | **164** | grew |
| `unit_rate_gbp_per_mwh` | n=100, refused | **n=164, −0.1192** | coverage |
| `svt_rate_gbp_per_mwh` | n=69, −0.1263 | **n=146, −0.1286** | coverage |
| `rate_vs_svt_pct` | n=69, −0.3530 | **n=146, +0.0898** | coverage |
| `company_eac_kwh` | n=69, −0.0645 | **n=164, −0.0880** | coverage |
| the other six fields | — | — | **n and held-out identical** |
| **ceiling** | +0.6308 / in-sample +0.2288 / n=69 | +0.6308 / +0.2288 / n=69 | **byte-identical** |
| p | 0.0249 (4/200) | 0.0299 (5/200) | one draw |
| **full-coverage rung** | observed +0.0537, **p=0.8657** | observed +0.1192, **p=0.4328** | **moved** |

Every move in the book column sits against a coverage change and nowhere else. Where coverage held,
the number is identical to four decimal places.

## What this refutes

**1. The ceiling's `+0.0181` is entirely the keying, and the published account said it was not
attributable.** `f92232d53` reported the move and correctly declined to credit it; it is now
credited. The winner moves on the *same* book with the *same* 69 households.

**2. The mechanism `f92232d53` published for that is wrong, and the way it is wrong is worth having.**
It read a per-field table in which every decision-time field was byte-identical, and concluded the
pair rung was untouched because "the pair rung is built from the intersection of those fields — which
is why its n is 69 before and after, and why the winner barely moved." The n is indeed 69 before and
after. **But the winner is a PAIR, and its second axis is `portfolio_premium_pct` — an account-state
field.** Folding does not change how many of the 69 carry it; it changes the **value** each of them
carries, because a dual-fuel household's portfolio premium becomes the mean over both legs' priced
terms instead of the electricity leg's alone. Different cell edges, different assignment, a different
maximum. *Coverage identity is not value identity, and an n column cannot see the difference.*

**3. The full-coverage rung's `0.8507 → 0.4328` was the book, not the fabricated target column.**
This is the headline of `f92232d53` and it is refuted. That finding says:

> The rung that was compromised is the one that has read `cannot tell` all along, and its p has
> moved from **0.8507 to 0.4328** now the fabricated share of its target column is gone.

Removing the fabricated share, alone, on the same book, moves that p from **0.8507 to 0.8657** — the
wrong way, and by less than one draw of the null. The entire fall to 0.4328 arrives with the later
book's logging. The contamination was real and the leg guard is right to exist; it simply is not what
made that rung's p fall.

**So the published attribution is inverted on both halves.** The move `f92232d53` could not attribute
is the keying; the move it attributed to the keying is the book.

## What it decides about the prescription

`f92232d53` and A49 both carry "what closes it is COVERAGE, not a re-run." That survives, and this
run is the first thing to *measure* it rather than assert it, because it holds the population
byte-identical while coverage grows:

- 177 households, 264 supply points, one seed, two draws three hours apart;
- households carrying an observable: **149 → 164**; the four account-state fields: **100→164,
  69→146, 69→146, 69→164**;
- the full-coverage rung, which is the only rung big enough to carry an honest verdict:
  observed **+0.0537 → +0.1192**, p **0.8657 → 0.4328**.

Nothing in the instrument produced that. **The subject of the prescription is now named: the world's
LOGGING of account state — not more households, and not a better reading of the ones we have.**

### And the counterweight, which belongs on the same page

The full-coverage **magnitude** rung is the only place in this instrument that has ever returned an
estimate clearing its own noise floor. It did so on the **published** book: **+0.1860** against a
floor of **+0.1601**, p=0.0498. One book-step later, on the identical population, it is **−0.1136**
against **+0.1487**, p=0.1741 — *it changed sign and stopped clearing.*

A point estimate that flips sign between two consecutive draws of one population is not measuring
anything stable yet, and this is direct evidence for A49's `magnitude: None` gate rather than an
argument for it. It is also the reason the p-fall above must not be read as R1 closing: **the rung
got a better verdict and a worse estimate from the same book-step.**

## Grading the pre-registration, beside the result

| | prediction | outcome |
|---|---|---|
| P1 | no per-field count rises; the increases are the book | **confirmed** — not one count rose; the only counts that moved are 213→149 on the two full-coverage fields. The deduction (`|image| ≤ |domain|`) held |
| P2 | households falls to 149 | **confirmed** — 149 |
| P3 | the pair rung is unmoved to the last digit | **REFUTED** — +0.6127 → +0.6308, and the refutation is §2 above |
| P4 | p moves off 0.0249, into 0.02–0.05 | **REFUTED** — p is 0.0249 either way, 4/200 both. Observed and bound rose together (+0.0181 / +0.0250) |
| P5 | the full-coverage rung's p falls below 0.70 | **REFUTED** — 0.8507 → 0.8657, and the refutation is §3 above |

P1 and P2 were declared deductions rather than guesses and I claim no credit for them. P3, P4 and P5
were the three that could embarrass the record and all three did.

## What was deliberately NOT done

**No regenerated `docs/observability/r1_inference_ceiling.json` is landed.** The run writes that path
as a side effect and its contents describe a **superseded** book; the artefact at `origin/main`
correctly describes the current one. It was restored byte-for-byte after the run — md5
`d0127e6d08225ad5a12e4c192cf77bae`, checked — and the numbers live in the tables above instead.
Landing a *worse* artefact to carry evidence would be the same defect this claim has already hit
twice.

The exposure `f92232d53` left open — the page publishing `+0.6127` on 213 supply points — **closed by
the other lane's own hand at `c244b93a0`**, before this run. No page change is needed or made here.

## What is still open

- The book column is **one step**. Two consecutive draws of one population at one seed are not
  independent books, so "coverage moves the rung" is one observation of a difference, not a rate, and
  nothing here says coverage keeps rising or that it would carry the rung to `clears`.
- The `verdict_stability` rung was not run (`the_verdict_is_the_same_on_every_draw_measured: null`).
  A linked worktree holds no gitignored run outputs and `--stability` needs the siblings; that is
  reachable with `--run` pointed at the shared tree and is the obvious next measurement.
- Unchanged: `+0.6308` is a selected maximum, its magnitude has no unbiased estimate, and **A49 must
  keep reading the magnitude field, which is `None`.**
