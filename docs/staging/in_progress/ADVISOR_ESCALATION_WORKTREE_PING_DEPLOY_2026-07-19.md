# ADVISOR ESCALATION — Worktree transient pings STILL reaching the director; deploy the ratified fix and prove quiet (2026-07-19)

**Type:** [STEER] — escalation per the advisor's stated morning deadline. Absorb; do not interrupt the SSP recal fork.

**The director, this morning, on the 06:21/06:26 pings:** *"I don't see how these help me if I don't do anything with them. Are they real? No problem? Don't know."* That sentence is the defect in full: an alarm whose only correct response is "ignore it" — and which the director cannot even classify without the advisor — is not observability, it is noise that trains him to ignore the channel that must work when something genuinely breaks.

**The facts:** WORKTREE UNDECLARED has fired ~10 more times since the H24_worktree ping-hygiene fix was BUILT and DIRECTOR-RATIFIED (L2, 18 Jul 14:16). Every instance since has been a healthy transient — (MERGED), fresh IDs, oscillating counts, reaped moments later. The ratified fix is evidently NOT in the running reconciler: the **committed-not-deployed class, now its fourth instance** (H23 publish gate, [ACT]-paging, treadmill-quiet daemon-side, and this). That class was already named for a mechanical check in the R3 escalation of 18 Jul — this is further evidence it needs one.

**The asks, all narrow:**
1. **Deploy** the ratified H24_worktree hygiene into the running reconciler (restart whatever daemon holds the stale code), and **prove one quiet cycle with transients present** — forks churning, zero transient pings, log-only.
2. **Route:** per the ratified NTFY taxonomy, this class is mirror-only even when it legitimately fires — it must never page the director. Genuine anomalies (worktree persisting beyond fork lifecycle, unmerged, count growing) still page LOUDLY — signal quality, not deafness.
3. **Class fix for committed-not-deployed:** a ratified fix's definition-of-done includes reaching the RUNNING system (deploy + verify), mechanically checked — propose the mechanism. Four instances in two days is R3 territory; do not let a fifth accumulate.

**Risk & proportionality:** a daemon restart (own commit, revert-clean) + an alert-routing change + one proposed mechanism. Blast radius: reconciler alerting only; the reap SAFETY guard (locked-refusal) must remain untouched and verified post-deploy. Tag: narrow/reversible — just do it.

— Advisor, honoring its stated escalation deadline, 2026-07-19.
