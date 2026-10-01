**Severity:** INFO · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# Pre-registration: the year-on-year change in one dwelling's metered electricity, from NEED 2026

Claim `size-the-registry-eac-read-error-from-the-published-record`. Written 2026-10-01, before the
measurement was run.

**What is being measured.** For each NEED 2026 dwelling with valid (`V`) electricity in two
consecutive years, the ratio r = E(t+1)/E(t). Pairs are pooled over 2016/17 to 2023/24. A
settled EAC that equals last year's use exactly (a perfect read history) is still wrong about next
year by this ratio. So this is a **floor** on the registry EAC's error against the next year's use,
not the error itself. It is reported by `MAIN_HEAT_FUEL` because NEED carries no meter type.

**Predictions (median of |r−1|, p90 of |r−1|, share with |r−1| > 0.25):**
- P1. Gas-heated: median 0.08–0.14; p90 0.30–0.45; share > 0.25 is 0.12–0.25.
- P2. Gas not the main heating fuel: median and p90 both above gas-heated (heating-weighted use
  moves with the winter and with occupancy).
- P3. The 2021/22 → 2022/23 pair (the price shock) has a median r below 1 for both classes.

## Results (added after the run; the predictions above are unedited)

- **P1 FAILS on all three legs, and in one direction: the distribution is wider than predicted.**
  Gas-heated median |r−1| is 0.143 (predicted 0.08–0.14), p90 is 0.550 (predicted 0.30–0.45), and
  the share above 0.25 is 0.290 (predicted 0.12–0.25). I had pictured household change alone. The
  NEED figure is the industry's own AA or EAC (80/20, per DESNZ), so it also carries changes of
  occupier and estimate-to-actual corrections.
- **P2 HOLDS.** Gas not main heating fuel: median 0.179, p90 0.714.
- **P3 HOLDS.** 2021→2022 median r is 0.923 for gas-heated and 0.932 for not-gas-main.

Full table: `docs/market_research/how_far_a_settled_eac_sits_from_next_years_use.md`.
