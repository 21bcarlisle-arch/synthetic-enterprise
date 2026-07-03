[PROJECT] Remote staging bridge -- let the strategy advisor commit instructions directly

THIS FILE WAS COMMITTED DIRECTLY BY THE STRATEGY ADVISOR VIA THE GITHUB API -- it is itself the proof-of-concept for the mechanism it describes. If you are reading this via the staging watcher, the bridge already half-works (repo -> watcher). Build the remaining piece.

WHAT TO BUILD:
Extend staging_watcher: git pull origin main every 2-5 minutes. Any new/changed file in docs/staging/ arriving via remote commit is treated identically to a /ui/stage submission -- same NTFY notification, same 4h opt-out window, same review queue.

GUARD: only act on files whose commit message carries the prefix [ADVISOR-STAGED] so random repo pushes don't trigger the queue.

CONFLICT SAFETY: the watcher's pull must be fast-forward-only (git pull --ff-only). If local uncommitted changes or divergence exist, skip the pull cycle and NTFY a warning rather than forcing.

CONFIRM: named phase entry in PROJECT_OVERVIEW.md + NTFY when live. This file arriving at all is the round-trip test.

Per HARNESS_HARDENING Rule 2: done means the phase entry exists and the NTFY names it -- not a statement.
