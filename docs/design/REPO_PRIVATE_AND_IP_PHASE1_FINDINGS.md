# REPO_PRIVATE_AND_IP Phase 1 pre-flight findings (2026-07-11)

**Status:** Phase 1 (agent pre-flight) run. Verdict: **NO-GO at current deploy cadence** —
one concrete blocker with a bounded fix, plus three clean checks. Phase 2 (the
actual visibility flip) remains Rich's own manual click either way, per
`docs/staging/in_progress/REPO_PRIVATE_AND_IP.md`'s own design.

## 1. Actions minutes audit — NO-GO as measured

Sampled 20 real Actions runs via `gh api repos/.../actions/runs` (07:33–11:03 UTC,
2026-07-11): **5.7 runs/hour**, extrapolating to **~4,120 runs/month**. Each run
is short (~20–25s) but GitHub Actions bills in whole-minute increments (rounds
up), so at a conservative 1 billed-minute/run floor that's **~4,120 min/month
vs the 2,000/month free-tier quota for private repos — 206% over budget.**
Public repos get unlimited free minutes, which is why this has never bitten
until now.

Root cause identified: `.github/workflows/github-pages.yml` triggers on
**every push to `main`, with no path filter** — unlike
`.github/workflows/deploy-pages.yml`, which is already scoped to
`site/**` + `docs/PROJECT_STATE.md`. Given this session alone pushed to main
roughly a dozen times in under two hours (sim-run auto-commits every ~9min
plus interactive-session commits), the unfiltered workflow is the concrete
driver of the overage.

**Recommended fix (not yet applied — flagging for your call, since it changes
site-freshness cadence):** add the same path filter to `github-pages.yml`
that `deploy-pages.yml` already uses, so a push that touches only
`docs/observability/`, `PRIORITIES.md`, etc. doesn't trigger a deploy. This
alone should bring the run count back under quota without changing what
actually gets published.

## 2. Auth continuity — clean

`gh auth status` shows the advisor identity (`21bcarlisle-arch`) already
authenticated with `repo` scope (covers private repos, not just
`public_repo`) plus `workflow`. Git push/pull with current credentials has
worked throughout this session. Low risk — should continue working
unchanged post-flip.

## 3. Link migration — bounded, mechanical

Swept for `.github.io` URLs. Historical/archival references (old snapshots,
`docs/staging/done/`, incident-log quotes) don't need touching — they're
frozen history. **Five live source files hardcode
`https://21bcarlisle-arch.github.io/synthetic-enterprise/...` URLs that will
404 once the Pages mirror dies on the flip:**
- `STATUS.md`
- `tools/generate_method_data.py` (feeds `site/data/method.json`'s
  retrospective links)
- `tools/generate_project_state.py` (3 URLs in `PROJECT_STATE.txt`'s
  canonical-links block)
- `tools/publish_report_gist.py`
- `docs/PROJECT_OVERVIEW.md`

Not fixed yet — holding until GO, since these are still valid on the current
public repo and there's no reason to break them early.

## 4. Nothing else assumes public — clean

`discovery-agent` fetches external market sources only (Elexon/NESO/ONS),
never our own site — no risk there. No `comments-box`-path or
`raw.githubusercontent.com` dependency on our own repo found beyond one
explanatory code comment (`tools/publish_report_gist.py`, not a live
reference).

## Recommendation

Hold GO until the `github-pages.yml` path-filter fix lands (small, reversible,
your call on exact filter scope) — otherwise the flip trades a real cost for
no immediate benefit. Once that's in and confirmed with a few real days of
reduced-cadence data, links (item 3) can be fixed in the same batch right
before the actual flip.
