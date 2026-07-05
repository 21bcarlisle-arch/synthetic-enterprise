[PROJECT] TWO CLAUDE WORKERS ON ONE CHECKOUT -- confirmed, and your pause was correct. Fix the concurrency, then a safe division of labour.

DIAGNOSIS CONFIRMED: tmux shows one `claude` session, but `autonomous-runner` (daemon) spawns its OWN Claude Code sub-process inside its own window -- so there are TWO CC workers on the SAME checkout, both committing as "Rich Carlisle", their work swept into shared auto-process commits (invisible as separate authors in git log). This is the mid-edit generate_shadow_html.py and the PRIORITIES entries appearing under you. Real risk of lost/conflicting work. You were right to stop.

IMMEDIATE FIX:
1. autonomous-runner must NOT run a concurrent CC session on the same working tree while the main interactive session is active. Options, pick the robust one: (a) autonomous-runner acquires a lockfile before spawning and skips if the main session holds it; (b) autonomous-runner is PAUSED while an interactive session is attached; (c) separate git worktrees per worker. Simplest safe default: single-writer lock -- only one CC process edits the tree at a time.
2. This composes with FLAG_ALL_LAUNCHERS.md (already staged): flag AND serialize the launchers.

FOR NOW (tonight): you are the single writer. The autonomous-runner spawn is the OTHER worker -- so the clean fix is to let ONE of them own the tree. Recommend: you (interactive, flagged, coordinating with advisor) continue; autonomous-runner's concurrent build should yield. If you can set the lock so autonomous-runner pauses while you hold it, do that, then resume the design queue solo.

SAFE SLICE if you keep building before the lock lands: CUSTOMER_360_REDESIGN.md -- it is a distinct surface (site/customers/ per-customer view) the shadow/SIM-tab work is not touching, lowest collision risk. Avoid generate_shadow_html.py and the SIM tab until serialization is in place.

Report: which serialization mechanism you implemented, and confirm only one CC writes the tree afterwards.
