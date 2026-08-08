# [ADVISOR-FLAG] — The seat needs a pulse monitor that outlives it (2026-08-08)

**Type:** [REQUIREMENT — problem, not mechanism]. Director-prompted tonight after the day's second silent seat death.

**The instance:** worker output provably alive 19:33 UTC (AO11 pushes), seat provably dead-at-login by 20:06 UTC (director's own pane). Between those brackets: nothing announced anything. Three watchdogs built today all monitor WORK-layer health (publish gate, marker sweep, operational cadence); none monitors the SEAT itself, because a dying invocation cannot report its own death — the one alarm that structurally cannot live inside the thing it watches.

**The requirement:** a daemon-side monitor, outside every seat invocation, that alarms the phone channel when no tick-completion evidence (pushed commit, completion marker — the mechanism's choice) has appeared for N minutes while the scheduler believes work remains. It must distinguish "idle because the plate is empty" from "silent while work is drawn." Auth death is the motivating instance, not the class boundary: crash-loops, wedged clones, and dead schedulers should trip the same wire.

**Pairs with (director's list, tomorrow):** a long-lived token in the credential store, making the auth-death instance extinct; this flag covers everything else that can kill a seat quietly.

— Advisor, on the director's question "don't we need an active supervisor?"; the answer is this organ, not a window.
