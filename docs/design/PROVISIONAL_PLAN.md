# Provisional Plan — computed, not guessed

**Staged:** RERANK_AND_PROVISIONAL_PLAN.md Part 2 (director-decided, 2026-07-12): *"We now have the
ingredients, so derive rather than estimate."* Every figure below is recomputed fresh from git
history and `docs/design/maturity_map.yaml` by `tools/generate_provisional_plan_data.py` →
`site/data/provisional_plan.json`, published on the Journey door (`site/project/`). Nothing here is
hand-typed as a plan figure; re-run the generator to refresh.

## LAW A GUARDRAIL (non-negotiable — also in CLAUDE.md)

**The plan is a diagnostic and a tie-breaker, NEVER a target.** Dates are forecasts; exit tests
remain the ONLY gate. No atom may be promoted, and no verification shortened, to hit a forecast. If
a date and a test conflict, the date is wrong. Deviation from the plan is ALLOWED and expected — the
map re-ranks on evidence — but must be logged with a reason.

## 1. Empirical cycle times (mined from `maturity_map.yaml`'s own git history)

29 real level transitions observed across the map's ~2.5-day life so far (first committed
2026-07-10). Median cycle time per level-step: **~0.07 days (~1.6 hours)**. This is *not* a claim
that real capability-building takes 1.6 hours per level — it reflects this project's dense
agent-turn cadence (many turns land per day), so the git-commit clock compresses relative to a
human-paced dev cycle. The signal that *does* generalise: the slow tail is driven by **review
iterations, not raw elapsed time** — the two slowest transitions observed
(`W5_1_banking_payment_rails` L2→L3 at 0.92 days, `W3_1_price_cap_binding` L1→L2 at 0.63 days) both
correspond to atoms that needed multiple Expert Hour passes before a clean PASS, not atoms that were
simply "harder to code." This matters directly for the director-hours model below: **the review loop,
not the build loop, is where duration variance actually lives.**

## 2. Critical path (dependency graph → each epoch's real blocking chain)

Computed by walking `depends_on` to find the longest chain of atoms that still have a real gap
(`level_current < level_target`), per epoch — mirrors `background/supervisor.py`'s own
dependency-walk convention.

| Epoch | Open atoms | Critical chain | Length |
|---|---|---|---|
| 1 | 3 | independent singletons (E2, W4_2, A1 each block only themselves) | 1 |
| 2 | 10 | `W1_reveal_over_time → D2_three_clocks → {B1_margin_bridge, W3_2_settlement_timetable}` | 3 |
| 3 | 8 | `W2_2_population_draw → W2_4_household_budget → {W2_7/8/9/10}` | 3 |
| 4 | 7 | `A2_decision_rights_register → A3_approval_interface → A4_sim_approver → A5_tournament_fitness_mortality` | 4 |
| 5 | 3 | independent singletons (H4, F4, F5 each block only themselves) | 1 |

**The single longest true dependency chain in the entire map is 4 atoms deep** (the A-lane
governance chain culminating in `A5_tournament_fitness_mortality`) — shallower than intuition might
suggest for a 52-atom map. The Epoch-2 spine (`W1_reveal_over_time → D2_three_clocks`) is confirmed,
by this computation, as the real bottleneck feeding *four* separate downstream atoms
(`B1_margin_bridge`, `W3_2_settlement_timetable`, and transitively `E2_revenue_reconciliation`), not
merely a repeatedly-asserted claim in the atoms' own prose — this is the first purely structural
(not narrative) confirmation of that spine's centrality.

## 3. Concurrency: max useful width, computed via file_scope disjointness

Same mechanism `background/supervisor.py::_maturity_map_draw_concurrent` uses for real draws,
applied here to the full open set for planning purposes (not just what's currently drawable).

- **31 atoms currently have a real gap.** Of these, **26 have empty `file_scope`** (pure
  DISCOVER/FRAME-stage work — no code touched) and only **5 declare real file paths**
  (`W1_reveal_over_time`, `B1_margin_bridge`, `W2_4_household_budget`,
  `W4_2_verifier_timing_extension`, `A2_decision_rights_register`).
- The arithmetic max concurrent width is **31 of 31** — i.e., today's open set has *zero* file
  collisions. **Read this correctly:** this measures "no file collision," not "safe to run 31
  engineers writing code at once." It is high *because* almost everything open right now is
  read-only research/design work — the honest reading is that **file-scope contention is not
  currently the binding constraint on width at all.** Real BUILD-stage contention only reappears
  once these atoms declare non-empty `file_scope` on entering BUILD (5 already do, at the current
  snapshot).

## 4. The real bottleneck: director-hours, computed from real artefact counts

Per the director's own instruction — *"model the true bottleneck... if he is the critical path, say
so and quantify it"* — reusing the ALREADY-REGISTERED effort/elapsed rate card from
`company/governance/decision_rights.py` (`DECISION_RIGHTS_REGISTER`), applied by analogy to
project-governance touch-types rather than in-sim decisions:

- **30 `from_rich_*.md` messages** and **28 substantive non-routine staged-doc closures** landed in
  the last 3 days (2026-07-10 → 2026-07-12), excluding 343 routine daemon markers
  (`run_complete_*`/`run_pending_*`, which need no director attention per CLAUDE.md's own rule).
- **7 Tier-1 safety-control gates** closed over the project's whole life (5 of them in the last
  week) — rare, but real, and each anchored at the highest effort tier (45–60 min, matching
  `CUSTOMER_HARM_REMEDIATION`/`LEGAL_CONTRACTUAL_COMMITMENT`).
- Applying the anchored effort-per-touch (8 min for a quick steer, 25 min for a staged-doc
  review+verdict — both analogies to the existing rate card, not new invented figures): **~5.2 hours
  of real director attention per day** at the current pace.
- **Honest caveat:** this window is CLAUDE.md's own time-boxed SPIKE_WEEKEND override — an
  explicitly unusual high-throughput period, not necessarily the sustained rate once it reverts at
  the weekly reset. Re-measure after the spike ends.
- **Finding, stated plainly:** the critical *path* (section 2) is short (1–4 atoms) and mostly
  BUILD/HARDEN-stage work needing only one L3+ ratification touch per atom (~20–30 min each per the
  rate card) — so the *depth* of any single chain is not director-bound. But the *aggregate width*
  the project can usefully run in parallel (many DISCOVER/FRAME lanes at once, exactly what
  EPOCH_GATING_AND_ATOM_AUTHORSHIP.md's own fix now enables) **is** director-bound: every finding
  from every parallel lane eventually needs his eyes. **If the drawable set's width keeps growing
  faster than ~5 hours/day of review capacity, width becomes the real constraint — not file
  collisions, not compute, not agent availability.**

## 5. Confidence tiers (director-set editorial judgement, not derived)

| Epoch | Confidence | Why |
|---|---|---|
| 1 | HIGH | Closed/near-closed — 3 open atoms, all independent singletons |
| 2 | HIGH | Fully decomposed (`THE_VALUE_CYCLE_FRAMING.md` M1–M4, each with a named, specific exit test) |
| 3 | MEDIUM | Atoms named and real (W2_4–10, W1_2), dependencies real, but no named exit tests yet per movement |
| 4 | COARSE | Fewest atoms, contains the map's single deepest dependency chain, largely undecomposed |
| 5 | COARSE | Only 3 atoms, essentially unstarted (one just DISCOVER'd this session: `F5_ofgem_licence_readiness`) |

Matches `MATURITY_MAP.md` Section 8's own convention (the dial table is director-ratified data, not
computed) — these tiers are set here with that same provenance, not derived from the git-mining
above.

## Re-forecast cadence

Every epoch boundary, and after every ~10 level transitions (re-run
`tools/generate_provisional_plan_data.py`; the JSON regenerates from scratch each time, nothing
carries forward stale).

## Use

When the self-refill draw is ambiguous between candidates of similar dial weight, prefer the one on
a named critical chain (section 2) over an independent singleton — this is a tie-breaker, per LAW A,
never a reason to skip an atom's own loop stages.
