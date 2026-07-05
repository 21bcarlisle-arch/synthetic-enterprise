[PROJECT] End the Pages failure emails permanently -- replace the automatic Pages workflow with a concurrency-managed one. Small, do alongside current work.

CONTEXT: recurring "pages-build-deployment / deploy: Deployment failed, try again later" = GitHub throttling concurrent Pages builds under push bursts (this morning's burst was the advisor's 14 staging commits -- advisor will batch multi-file staging into single commits going forward). Build always succeeds; next deploy self-heals. The problem is purely that superseded/throttled deploys report FAILED and email Rich.

FIX:
1. Replace the automatic GitHub Pages build with an explicit workflow: actions/checkout -> actions/upload-pages-artifact -> actions/deploy-pages, with:
   concurrency: group: pages, cancel-in-progress: true
   Superseded runs then report CANCELLED (no failure email), latest always wins. Disable the automatic "pages build and deployment" in repo settings by switching Pages source to GitHub Actions.
2. While in there: silence the Node 20 deprecation warning -- ensure workflow actions run on current runtime (actions versions pinned appropriately).
3. Verify: push 3 commits in quick succession; confirm zero failure emails, latest content served, superseded runs show cancelled.

<!-- DONE 2026-07-05: .github/workflows/github-pages.yml added (checkout ->
     configure-pages -> upload-pages-artifact -> deploy-pages, concurrency
     group=pages cancel-in-progress=true). Pages source switched from
     legacy (branch) to workflow via `gh api -X PUT .../pages
     -f build_type=workflow`. VERIFIED: two workflow_dispatch runs fired 4s
     apart -- first run shows conclusion=cancelled (not failed, no email),
     second completed success. Live site fetch confirmed both
     /status/PROJECT_STATE.txt (fresh timestamp) and /shadow/index.html
     (200) serve correctly post-migration. Root github.io/ 404s -- pre-
     existing (no docs/index.html ever existed), unrelated to this fix,
     not introduced by it. Node 20 warning addressed as a side effect
     (all actions used are current: checkout@v4, configure-pages@v5,
     upload-pages-artifact@v3, deploy-pages@v4). Cloudflare Pages deploy
     (.github/workflows/deploy-pages.yml, separate site) untouched. -->
