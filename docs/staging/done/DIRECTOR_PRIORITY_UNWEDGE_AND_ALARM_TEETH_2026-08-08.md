> **ACTIONED 2026-08-09, both draws disposed. Archived.**
>
> **Draw 1 — unwedge: DONE.** Neither offered suspect was the live cause; the logs out-voted them,
> as this doc said they would. Pristine HEAD was GREEN on all three ratchet codes (E402 194,
> F401 279, I001 1388), and the hook paths were already anchored. The wedge had TWO causes,
> found serially: (1) an unused `typing.Callable` in an **uncommitted** edit to
> `background/fabric_gap_ledger.py` — the ratchet lints the WORKING TREE, so one concurrent
> writer's lint error wedges publishing for everyone and is invisible at HEAD (commit e21066b78,
> which also rescued the complete-but-uncommitted worst-of-N fix it was sitting in); (2) a stale
> derived `docs/design/FORWARD_ATTACHMENT_LEDGER.md` after two findings declared `**Advances:**`
> (commit bbb959cba). Verified by running the gate's own argv without `-x` to find every remaining
> red at once rather than one per ~9-minute publish cycle: **22,353 passed, 5 skipped, 14 xfailed,
> rc=0**.
>
> **Draw 2 — the class: ALREADY BUILT, verified by read, not rebuilt.** (a) episode memory —
> `wedge_since`, `episode_failures`, `cited_findings` and `markers_pending` are carried in the
> alarm (`process_run_complete.py:1866-1945`); (b) alarm→dial — `supervisor.py:2895-2925` lifts a
> cited finding into RUNG 1 priority zero, and its comment cites this doc by name.
>
> **One thing Draw 2(a) does not yet survive**, filed rather than fixed
> (`WORKER_FINDING_EPISODE_MEMORY_WIPED_MID_EPISODE_2026-08-09.md`): at 04:54 UTC a 10-failure,
> 50-minute, 5-hash episode was reset to a fresh 1-failure wedge while the cause was still red and
> 23 markers were unpublished. The memory exists; something still clears it mid-episode. The call
> site is NOT asserted (R9) — two candidates remain and the log interleaves.

# [DIRECTOR-PRIORITY] — Unwedge publish, then give alarms memory and teeth (2026-08-08)

**Type:** [PRIORITY FLAG — director-instructed after his own census question]. Two draws, in order.

**The episode truth (mirror census, advisor-run tonight):** 10 wedge alarms today, 15:41→22:47 UTC — a seven-hour live episode; LATEST stale 2h+; markers piling since 15:05 UTC. Historically: **150 wedge alarms in the mirror**, including an unbroken hourly wall across Aug 1–3 — the pre-shutdown machine spent its last three days alarming about this exact disease and never drew the cure. Every alarm truthfully described a 60-minute window and forgot the episode.

**Draw 1 — unwedge.** Your own two filed findings hold the suspects: RUFF_RATCHET_RED_AT_HEAD (E402 201 vs 194 at pristine HEAD — the prime candidate for the persistent rc=1) and RELATIVE_HOOK_PATHS_WEDGE_SESSION. Fix or re-freeze with provenance; the alarm clears itself on the next clean publish.

**Draw 2 — the class, two properties:** (a) **episode memory** — a wedge alarm carries wedged_since, consecutive failure count, and markers pending, so a seven-hour episode can never again narrate itself as a fresh hour; (b) **alarm→dial wiring** — an ACTION NEEDED alarm citing a filed finding RAISES that finding's draw priority instead of only addressing the director. A chronic red on the public proof surface must self-prioritise; tonight it lost every draw to feature work while its own cure sat filed.

Suspect-classes offered, not prescribed; the logs out-vote everything. Batch keeps; this outranks it.

— Advisor, on the director's census question; see-and-correct applies.
