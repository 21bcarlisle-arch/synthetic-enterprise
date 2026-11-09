**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Measure what committed generated data costs us (2026-11-09)

**Type:** STEER, through the advisor channel. The director's words, from chat on Mon 9 Nov:

- 21:30 GMT, sharing a post on OpenAI's Pando and Anthropic's Scion (source control rebuilt for agent-scale merge volume)
- 21:33 GMT, on the advisor's recommendation to measure the cost of repository size before changing anything: "Measure it"

**When:** behind the correctness exit test. Rank it yourself.

## What the advisor found (at `c3809256b`, 9 Nov; check it)

- **Our commit volume is small:** about 289 commits in the last 7 days, against Scion's 30,000 merges a day. Volume is not our problem.
- **Our contention problem is already solved Scion's way.** `tools/surgical_land` and `tools/isolate_hunks.py` build and gate the tree a commit would create, without touching the shared working copy.
- **The repository is heavy with generated data:**
  - the HEAD tree is about 692 MB, of which `site/data/` is about 187 MB;
  - `docs/state/billing_ledger.json` is 91 MB;
  - `sim/weather_world/daily.csv.gz` is 36 MB;
  - `docs/observability/naive_organ_log.jsonl` is 32 MB, mostly the 26,580 repeat declines from before the 2 Nov repair;
  - `docs/reports/bill_validation_comparison.json` is 28 MB;
  - `docs/direction/decisions.jsonl` is 23 MB;
  - `site/data/` was rewritten in about 280 commits since 9 Oct.
- GitHub reports the repository at about 618 MB. The advisor's fetches took several minutes this week.

## The question

**What does committed generated data cost us, and what could live outside the main history without breaking the site or its door tests?**

1. **Measure:**
   - clone and fetch time, for a fresh session and for CI;
   - commit-gate time attributable to repository size, as against the gates' own work;
   - how fast history grows per week, and which paths drive it.

   Say what each number counts.
2. **Classify every large file:**
   - **source** (must be in Git);
   - **generated and needed to serve or test the site** (published from somewhere);
   - **generated and only a record** (logs and ledgers that could rotate, compact or move).
3. **Recommend only what the numbers justify.** Options include a separate publish branch or storage for site data, rotating or compacting append-only logs (the organ's repeats), or nothing. Keep "done means the rendered value changed" and the evidence trail intact: a record that is evidence is never destroyed (G5). Moving it is fine, deleting it is not. Rewriting published history is a one-way door: propose it, do not do it.

If size is not where the time goes, say so and stop.

## Risk

Touches: a read of repository metrics only, until a recommendation is approved.
Blast radius: none now. A later move of site data touches the publish path and every door test.
Probable failure mode: a recommendation that moves a file the door tests or `generate_dashboard_data` read by path, which would break publishing silently. List every reader of each file before proposing a move.
Proportionality: reversible and narrow — just do it (measurement only).

— Director steer, 9 Nov 2026, his words above; the census and drafting are the advisor's.
