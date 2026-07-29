<!-- SUPERVISOR_DRAW: self-drawable -->

# [PLANNER-MINTED] Standing draw default: reversible work proceeds with a recorded undo, it does not queue for permission (mechanism + R15) (2026-07-29)

**Source ruling:** `DIRECTOR_RULING_WORK_AT_RISK_DEFAULT_2026-07-29.md`, WORK-THIS-CREATES **#4**
("A standing default in the draw: reversible work proceeds with a recorded undo; it does not queue for
permission.").

**Serves:** the durable half of the ruling — #1/#2/#3 clear the *current* backlog once; #4 stops it
re-accreting. Per MAKE_IT_STICK: *"convert policy to mechanism, or accept it will evaporate."* The
ratchet the ruling names (§11) was built one reasonable ratification clause at a time; a prose default
would decay the same way. This atom makes the §2 reversibility test the **draw default in code**.
**Real-world fidelity gained:** none — harness/operational mechanism. Value = a new reversible atom
NEVER re-enters the blocked set by category; only a PROVABLE one-way door queues for the director.

**Lane:** FRAME → BUILD (real mechanism change in the self-refill draw / gate-authorization /
`background/one_way_door.py` — the burden-of-proof-is-on-"it's-a-door" default already exists
[`ONE_WAY_DOOR_DEFAULTS_TO_ACT.md`]; this extends it so a category block [level move, ratified
BUILD_OPEN] is NOT sufficient to wall — only a proven §2 failure is). Draw ORDER/gating is a DIAL,
git-reversible; no wall, no safety-control, no authority-trust change. Self-drawable now.
**Target level:** harness mechanism + **R15 mutation proof** (this is the "stick" requirement — a
prose-only version does not count as done). No maturity-map level claimed.
**Deps:** none directly (parallel to #1/#2). The §2 test it encodes is the same logic the
reclassification applies by hand; landing the mechanism makes future reclassifications automatic.

## NOT a re-mint of `director_act_rung_zero_draw`
`PLANNER_MINTED_director_act_rung_zero_draw_2026-07-29.md` is about **director acts** drawing at
rung-zero (latency of the director's authority). THIS atom is about the **agent's own reversible work**
not queuing for the director at all (removing false blocks). Different actor, different mechanism.

## Exit criteria
- The draw/gate applies §2 as the default: an atom is walled ONLY if a released control proves it is a
  §2 one-way door (real money/customer/market, external comms, safety/authority-trust, evidence
  destruction, unpublishable, R13 curriculum). A category alone (level move, BUILD_OPEN on a ratified
  decision) does NOT wall.
- Reversible releases auto-record their undo (`background/decision_log.py`) — recording, not asking, is
  the reversibility guarantee (§15).
- **R15 both ways:** a mutation proves (a) a reversible doc/level atom is NOT walled (fail = false block
  regressed) AND (b) a genuine one-way door (e.g. secrets/safety-control change) IS still walled
  (fail = the release went too wide). Fixture-isolate any new register path (memory
  `new_draw_rung_needs_fixture_isolation`).
- §4 binding wired: a staged clause claiming "returns for ratification" that cannot name its
  irreversibility is rejected by the mechanism, not silently obeyed.

## Reverse / undo
git revert the supervisor/one_way_door change; the pre-existing category-block behaviour returns. No
external state touched.
