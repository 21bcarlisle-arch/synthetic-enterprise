**IN PROGRESS (2026-07-13):** Item 1 (redesign) DONE -- commit 6cdbbbff:
background/action_needed.py::escalate_if_one_way_door() built, tested, live end-to-end
NTFY-verified; hmac:invalid reconciliation confirmed already-answered-and-still-true.
One sub-item held open pending live director confirmation, not blocked on unclear
next steps: retiring the old flag_unregistered_blocking_question.py Stop hook is
itself flagged SECURITY_SAFETY_CONTROL by the very predicate this redesign built --
see docs/review_gates/FLAG_UNREGISTERED_BLOCKING_QUESTION_HOOK_RETIREMENT_TIER1.md
(open). **Item 2 (harness bootstrap/DR): QUEUE-dispositioned per STAGING_HAS_ONE_GEAR.md's
own new discipline** -- registered as docs/design/maturity_map.yaml's H8_harness_bootstrap_dr
(epoch 5, dial 1), to be drawn in its own priority order rather than actioned immediately
mid-turn. What unblocks full closure: the review gate resolving (either way) and H8
being drawn/built through to a real, measured, tested bootstrap.

# [ACTION NEEDED] two-strike REDESIGN + harness bootstrap/DR (P0 / P1)

**Staged:** 2026-07-13 by advisor, director-raised. Note: trust ledger, skills/
rules, done-is-monitored, alarm-runbook and the billing check are ALREADY staged
today (fce31c33, 2afb4196) — do not duplicate them. These two are the gaps.

## 1. [ACTION NEEDED]: redesign, don't patch (P0 — five failures)
The single least reliable mechanism in the harness. Patched repeatedly, failed
~5x including after a structural Stop-hook fix. Two-strike/R3 was exceeded long
ago.

**Advisor's diagnosis of WHY it keeps failing:** it has been guarding a FUZZY
class — "anything blocking on Rich". A fuzzy class cannot be tested, so every
fix was a guess about intent.

**That class is now CODE.** `background/one_way_door.py` (built last night)
defines precisely what requires the director: real money, real-world/legal
commitments, irretractable public claims, irrecoverable data loss, security/
safety controls, values decisions, real customers — plus the director-reserved
list (repo settings, keys, accounts, connectors, billing, security profiles).

**Redesign accordingly:**
- **[ACTION NEEDED] fires IF AND ONLY IF the one-way-door predicate returns
  true.** No judgement, no remembering, no separate heuristic. One code path.
- Everything else routes to DIRECTOR_TWIN and the agent proceeds (that is the
  whole point of PROCEED_BY_DEFAULT) — so the surface area of genuine blocks is
  now SMALL and RARE, which is exactly what makes the alarm testable at last.
- Delivery must be verified, not fire-and-forget: the ntfy is sent, the send is
  confirmed, and an unanswered [ACTION NEEDED] re-pings daily until answered.
- **Prove it end-to-end with a live test:** trigger a synthetic one-way-door
  condition, confirm the director actually receives the ntfy, confirm the
  re-ping fires. Report the evidence. Until that test passes, the mechanism is
  presumed broken.
- Retire any older blocking-question heuristics that overlap — one mechanism,
  not three (the overlap is itself a decay source).

**Also reconcile (still open):** the 2026-07-11 15:30Z input-log entry tagged
`[unknown-unverified][hmac:invalid]` against the production-readiness finding of
5 stale unauthenticated dev file-servers. Same artefact or two separate issues?
Answer it and close it.

## 2. Harness bootstrap + disaster recovery (P1 — this is DR, not just pitch)
The methodology and harness are the durable IP — but they exist in exactly ONE
place and have never been rebuilt. Part A's recoverability pass backed up the
DATA (company/data/*.db). **The MACHINE THAT RUNS THE COMPANY is not backed up
and not reproducible:** daemons, hooks, settings.json, systemd/user units, env
files, tmux topology, launcher scripts, model routing. If Skynet's disk dies
tonight, the company's history survives and the thing that operates it does not.

**Requirement:** a documented, tested bootstrap — "stand this harness up fresh
on a clean machine" — that is BOTH the IP-reproducibility proof and the real RTO
test.
- Inventory everything the harness needs that is not in the repo (env files,
  secrets locations, systemd units, tmux layout, external services). Anything
  not in the repo and not documented is a single point of failure.
- Produce a bootstrap path (script or documented sequence) that reconstructs a
  working harness from the repo + a secrets file.
- **Test it for real** — a clean directory / container / second machine, not a
  thought experiment. Report the measured time-to-working ("stand it up in an
  hour" is the target the pitch implies; measure the truth).
- Secrets never enter the repo (Option-2 floor stands). The bootstrap consumes
  a secrets file the director provides.
- Feed the measured RTO into PRODUCTION_READINESS Part B's recoverability entry.

## DoD
[ACTION NEEDED] fires solely off one_way_door.py, delivery-verified, daily
re-ping, proven with a live end-to-end test the director confirms receiving;
overlapping heuristics retired; hmac:invalid entry reconciled. Bootstrap
inventory + path produced and TESTED on a clean environment with a measured
time; result recorded in the NFR register. One digest line each.
