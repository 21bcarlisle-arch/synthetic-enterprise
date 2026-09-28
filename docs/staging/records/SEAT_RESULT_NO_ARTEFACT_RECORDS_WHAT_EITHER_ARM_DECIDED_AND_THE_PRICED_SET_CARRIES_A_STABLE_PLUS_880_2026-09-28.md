**Severity:** LATENT · **Lane:** A_strategy_governance · **Atom:** `unminted` · **Class:** `measurements_that_mirror`

# No artefact records what either arm decided. The accounts the value arm priced carry a stable +£880 apart from the one churn roll

**2026-09-28.** Delivery item `does-the-value-arm-decide-anything-the-flat-arm-does-not`. Read-only:
no run was launched. I read the C1 bracket's `/var/tmp/se-c1-bracket-{a,b,c}/value_cycle_ab.json`
(seeds 11111 and 88888, three C1 states, so 6 runs but only **2 independent draws**) and the 18-seed
HEAD family `docs/observability/value_cycle_ab_s1_noise_floor_folded18_head_20260925.json`.

## Prediction, written before opening the artefacts

> The artefacts record per-arm aggregate outcomes and perhaps per-seed nets, but no per-account
> decision (renewal price offered, retention action, tariff). If so, the answer is the absence.

**Graded: half right.** No per-account decision is recorded for either arm, so the absence is the
answer to the question as asked. But I did not predict that the bracket's per-account **nets**,
together with the value arm's per-account **priced-renewal count**, would support a partial split. It
does, and the split is below.

## 1. The absence, which is the headline

| Artefact | Per-account nets, both arms | Per-account decision, value arm | Per-account decision, level arm |
|---|---|---|---|
| 18-seed HEAD family | **no** (seed-level nets only) | belief + outcome (`scored_decisions`), **no price** | **none** |
| C1 bracket (a,b,c) | yes (`{value,level}_arm_net_by_account_gbp`) | count of priced terms only, **no price** | **none** |

`priced_decision_fingerprint` is a hash of the value arm's **beliefs** (`believed_p_retain`,
`retained`). It is not its prices and it holds nothing from the level arm, so it cannot say whether
the arms chose differently. **So no artefact on disk can count the accounts the arms decide
differently on, for any seed.**

**The fields exist in memory and are dropped.** Each arm's `phase2b["value_arm_log"]` carries one row
per renewal: `customer_id`, `commodity`, `term_start`, `declined`, `chosen_margin_gbp_per_mwh`,
`offered_rate_gbp_per_mwh`, `rate_increase_pct` (`company/pricing/renewal_rate_chain.py:438`).
`tools/run_value_cycle_ab.py` already joins the two logs renewal by renewal, but only for the value
arm's *declines* (`declined_renewals`, around line 4200). **Fields `noise_floor`'s per-seed row must add
so that the next HEAD run carries them:**

1. `renewal_decisions_by_arm` — for `value_arm` and `level_arm`: `[customer_id, commodity,
   term_start, declined, chosen_margin_gbp_per_mwh, offered_rate_gbp_per_mwh]` for every log row,
   declines included.
2. `decided_differently_by_account` — the join on `(customer_id, commodity, term_start)`: per
   account, the number of renewals where the offered rate differs (or one arm declined and the other
   priced), plus the number of renewals present in one arm's log only. A renewal in one log only is a
   roster difference, and it must be counted as its own category rather than as "different".
3. **Retention actions and tariff, per account per arm: not established here.** The arms share
   `CURRENT_POLICY` in everything except `renewal_margin_arm`, so the retention and tariff *rules*
   are the same in both. Whether they can *fire* differently once the book diverges is a question I
   did not answer. The next item should grep for a per-account retention log before adding a field
   for it.

## 2. What the bracket can say without the decision fields

**The partition.** The level arm prices the same renewal population as the value arm by
construction (`decision_population.same_priced_population`, since 2026-09-18). So on any account the
value arm **never priced**, the two arms' decision rules are identical, and any net difference there
is "happened differently" and nothing else. On accounts it **did** price, the arms *may* have decided
differently. That makes the priced set an **upper bound** on "decided differently", not that set
itself.

**Checks.** On every run, value-minus-level summed over all accounts equals `selection_gbp` to within
1e-4. There are 164 accounts on every run.

| run | seed | selection £ | priced set (n=70) £ | …excluding PROS-2016-0098 £ | never-priced set (n=94) £ |
|---|---|---|---|---|---|
| a | 11111 | −3,508.25 | −3,515.57 | **+876.98** | +7.31 |
| a | 88888 | +706.67 | +703.26 | **+877.37** | +3.41 |
| b | 11111 | −3,507.32 | −3,514.60 | **+877.95** | +7.27 |
| b | 88888 | +707.60 | +704.24 | **+878.35** | +3.36 |
| c | 11111 | −3,501.47 | −3,508.54 | **+884.01** | +7.06 |
| c | 88888 | +713.40 | +710.34 | **+884.45** | +3.06 |

The same numbers, read against the three things the item asked for:

- **Accounts the arms may decide differently on: 70 of 164** on every run, 95% Clopper–Pearson
  [0.350, 0.506]. That is the proportion within this one book, not a population rate. It is an
  upper bound: **24 of the 70 show a net difference within ±£0.005**. That is consistent with
  either (a) the value arm choosing the level arm's margin, or (b) a priced term falling outside the
  settled window. The missing fields are exactly what would tell those apart.
- **Value minus level on the priced set:** −£3,516 to +£710. The ±£4.2k switch between the two seeds
  is entirely **PROS-2016-0098**: −£4,392.54 on seed 11111 and −£174.11 on 88888. It is priced (2
  renewals), but `875322e5a` already showed it is the level arm's churn roll on a household the value
  arm treats identically in both states. **Excluding it, the priced set reads +£877 to +£884, the
  same sign and nearly the same size on both seeds and all three C1 states.** The exclusion is
  **post hoc**, justified by `875322e5a` and not by anything pre-registered.
- **Value minus level on the never-priced set: +£3 to +£7**, with 59 of 94 accounts within ±£0.005.
  This is pure draw leakage, and it is **two orders of magnitude** smaller than the priced-set
  figure.

**Bounds this count earns.**

- **Across draws: we cannot tell.** There are two independent seeds, and the three C1 states barely
  move anything (±£8). Two draws that agree on +£880 is suggestive, but no dispersion can be
  estimated from n=2, so no interval is stated.
- **Across accounts, the +£880 is not broad.** On the priced set, 21 accounts favour the value arm and
  25 favour the level arm, with 24 ties. The exact two-sided sign test gives p=0.66. So the money is
  concentrated in a few accounts, not a per-customer edge spread across the book. The next measurement
  needs to find which accounts hold it.

## What this settles and what it does not

- **Settled.** The ±£4.2k selection switch does not live in decisions. The never-priced set, where
  decisions are identical by construction, moves by £3–£7. The priced set outside 0098 does not move
  between seeds.
- **Candidate, not established.** A roughly **+£880 value-arm advantage on the priced accounts**,
  stable across 2 draws, concentrated rather than broad. It is the first figure in this line of work
  that is **located where the decisions differ**, not in an aggregate outcome. It is not yet
  attributable to *inference*, for two reasons. The decision fields are absent, so a priced account
  is not yet a *differently-decided* account. And n=2.
- **Next.** Add fields 1–2 above to `noise_floor`'s row, then run the HEAD family with them. The
  question on that run is how much of the +£880 sits on renewals where the offered rate actually
  differed.
