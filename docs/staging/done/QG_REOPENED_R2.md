[PROJECT] QG REOPENED -- advisor verification FAILED. Origin still serves the 05:31 state file one full run cycle after QG. Prime suspect: R2 violation -- the run-complete processor is a daemon running pre-QG code.

VERIFICATION EVIDENCE: advisor cache-busted fetch (?qg=1826) of github.io/synthetic-enterprise/status/PROJECT_STATE.txt at 18:28 UTC returned Generated 2026-07-04T05:31:24Z, Phase PY, gross 6,452,602, Key Files without github.io mirror URLs. The 18:21 UTC auto-process cycle completed AFTER QG (18:17) yet produced no visible regeneration. Query-string bust bypasses the Pages CDN, so this is the ORIGIN, not cache.

DIAGNOSE IN THIS ORDER:
1. R2 CHECK FIRST: is process_run_complete executed by a persistent daemon (background-worker / autonomous-runner tmux session) that loaded its code BEFORE QG? If yes, the 18:21 cycle ran pre-QG code -- no mirror, old phase-selection bug. Fix: restart the daemon(s), rerun the processing on the latest run marker, confirm docs/status/PROJECT_STATE.txt content changes in the commit.
2. If the daemon does spawn fresh subprocesses per marker (new code should have run): did the 18:21 commit actually contain a modified docs/status/PROJECT_STATE.txt? git show e4a82a87 --stat will say. If the file regenerated identically or wasn't written, the generator/mirror wiring has a path bug -- trace where mirror_github_pages.py wrote vs what Pages serves.
3. Confirm GitHub Pages deploy of the relevant commit succeeded (Actions log) -- the deploy-failure race from this morning could also swallow it.

THEN: rerun one processing cycle and report WITHOUT claiming done -- per R1 the advisor re-fetches. Expected on success: Generated timestamp post-18:30 UTC, Phase QF+ (most-recent not highest-test-count), gross 6,467,309 (the QF-corrected number), github.io shadow+state URLs in Key Files.

Pattern note for the retro ledger: this is the third committed!=running incident (PROJECT_STATE sync, watchdog script, now the run-complete processor). Consider adding a daemon-restart step to phase-close whenever a phase touches code any persistent process executes -- or better, have daemons exec processing as fresh subprocesses so code changes take effect immediately.
