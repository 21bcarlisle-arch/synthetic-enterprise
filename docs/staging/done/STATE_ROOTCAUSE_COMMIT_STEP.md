[PROJECT] PROJECT_STATE.txt root cause ISOLATED -- it is the commit step, not the generator, not the deploy. Stop fixing the wrong layers.

EVIDENCE (from GitHub Actions run history + live fetch):
- "Deploy to Cloudflare Pages" runs are SUCCEEDING (20:29:17, 20:13:16 UTC). Cloudflare serves poesys.net and it deploys fine every cycle.
- "pages build and deployment" (GitHub Pages' own workflow) is failing -- but that is NOISE. poesys.net is served by Cloudflare, not GitHub Pages. The failing GH Pages workflow is a separate, redundant deploy that can be ignored or disabled.
- Live fetch of https://poesys.net/state/PROJECT_STATE.txt STILL returns Generated 2026-06-30T20:06:26Z, Phase HY, 9,290 tests.

THEREFORE: Cloudflare successfully deploys every cycle, but keeps serving the June 30 file. That means the file is NOT being regenerated-and-committed into the path Cloudflare publishes. The generator has been "fixed" 4x with no effect because the generator was never the problem. The deploy was never the problem. The problem is between "auto-process run completes" and "new bytes committed to the served path."

DIAGNOSE EXACTLY THIS, nothing else:
1. Does the auto-process run actually call the PROJECT_STATE.txt regeneration on each run? (The auto-process commits report+LATEST.md+site/ every ~30min -- is PROJECT_STATE.txt generation in that hook at all, or orphaned in a separate script that never runs?)
2. When it regenerates, does it write to the path Cloudflare serves /state/ from? Confirm the exact source path Cloudflare maps /state/PROJECT_STATE.txt to, and confirm the generator writes THERE.
3. Does the regenerated file get git-committed and pushed? An uncommitted regenerated file never deploys. Check whether it's gitignored or written outside the committed tree.

MOST LIKELY: PROJECT_STATE.txt generation is not wired into the 30-min auto-process commit hook (which IS committing LATEST.md and site/ successfully -- note LATEST.md vs PROJECT_STATE.txt: is only one of them in the hook?). Wire PROJECT_STATE.txt regeneration into the same hook that already successfully commits LATEST.md and site/data/, since that path demonstrably deploys.

VERIFY: after the fix, wait one auto-process cycle, then curl https://poesys.net/state/PROJECT_STATE.txt and confirm timestamp is fresh + phase is current. Quote the fetched timestamp in the NTFY. Not done until that fetch shows current data.

DISABLE THE NOISE: the failing GitHub Pages workflow serves no purpose if Cloudflare is the host -- disable it so it stops generating false failure notifications.
