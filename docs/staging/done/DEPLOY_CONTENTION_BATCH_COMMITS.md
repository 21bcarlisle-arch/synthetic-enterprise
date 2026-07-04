[PROJECT] Deploy contention: 58 failed GitHub Pages runs from over-frequent pushes. Batch the commits.

DIAGNOSIS (from Actions API): 58 recent failed "pages build and deployment" runs, all identical -- build succeeds, "Deploy to GitHub Pages" step fails. Cause: pushes every 5-10 min (auto-process + daemon-state syncs + phases) each trigger a Pages deploy; GitHub throttles/supersedes concurrent deploys (~10 builds/hr soft limit); superseded deploys report as failures and email Rich each time. Site self-heals (each success carries all commits) but creates 30-60 min staleness windows and constant alert spam.

ALSO CHECK: the Cloudflare workflow deploys per-commit too. At ~150 commits/day, a free Cloudflare Pages plan (500 builds/month) exhausts in ~3 days -- check the plan/limits and current usage NOW. If quota trips, poesys.net stops updating silently.

FIX AT SOURCE -- reduce push frequency, not alert visibility:
1. Auto-process: accumulate locally, push every 30 min (instead of ~10), or push only when content actually changed (diff check on generated files -- many commits are near-identical regenerations).
2. Daemon-state syncs (watchdog logs, agent status): fold into the next auto-process commit rather than pushing standalone. These alone add several pushes/hour of near-zero-value deploy churn.
3. Phase commits: unchanged -- push immediately as now. Real work should deploy promptly.
4. Result target: <=6 pushes/hour sustained, which sits under the Pages limit and cuts Cloudflare usage ~4x.

OPTIONAL HARDENING: replace the automatic Pages build with an explicit actions/deploy-pages workflow using a concurrency group (cancel-in-progress: true) so superseded deploys report "cancelled" not "failed" -- eliminates the failure emails for genuine races.

VERIFY: after the change, report pushes/hour before vs after, and confirm zero deploy-failure emails over a 3-hour window. Also report Cloudflare plan limits + current month usage.
