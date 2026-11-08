**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] Off-box liveness yes, early publish yes, spare tokens to the site this week, and DDD first (2026-11-08)

**Type:** RULING, through the advisor channel. The director's words, from chat on Sun 8 Nov:

- 13:22 GMT, after the advisor set out the two open `for_the_director` rows (`off-box-liveness`, `the-publish-window-is-anchored-to-monday`) and a note on domain-driven design: "Not sure why machine the went off. But it's back now. I'd like to use token ls this week on site as only 66%. Yes when we research the author include or start with DDD"

## 1. `off-box-liveness`: yes

He does not know why the machine went off. So the 5–7 Nov outage was not a planned shutdown. Build the off-box check as proposed: a scheduled GitHub Actions workflow on the ops repo reads the heartbeat the sim-runner already pushes, and sends the dead-man's single push when that heartbeat is more than 6 hours old. Nothing else reaches his phone. The 15 Oct ruling (one push, only when the machine is dead) is otherwise unchanged.

Also find the cause of both stops, 3–4 Nov (about 24h) and 5–7 Nov (about 60h), if the evidence allows. That covers WSL, Windows updates, power, and the guest's memory. If the evidence does not allow it, say "we cannot tell" and say what would let you tell next time. Prove the workflow fires, for example against a stale heartbeat in a test, before calling it done.

## 2. Usage reading, and the site this week

**His reading: 66% of the weekly allowance used.** He wants the rest spent this week on the site.

- **`the-publish-window-is-anchored-to-monday`: yes.** One early publish as soon as a book passes the full gate. The Monday anchor then resumes as ruled.
- **Spend the spare allowance this week on site work.** Your choice of what, from the site items already staged:
  - the Knowledge tab taking the map's shape (world / running a supplier / building it), brought forward;
  - the control stack and its live evidence;
  - the "everything we've learned" chains;
  - the reading log's published side;
  - anything the cold reads have flagged.

  Say in the stretch log what you chose and why, and what it spent.
- **The correctness rules still hold for what the site shows.** An example or figure that fails its invariant gate is not published, however much allowance is left. The site work is added on top of the correctness stretch, not taken from it.

Pace it so the week's allowance is used without running out before the reset. P12 applies: never idle to save budget.

## 3. DDD first

When the reading rota reaches the wider-craft strand, start with domain-driven design (Evans). Its first pass checks the concept register against DDD's bounded contexts:
- each term records the area it belongs to;
- where the world's meaning and the supplier's differ, both are recorded with the translation at the seam;
- for example, "customer" as a household in the world and as an account in the supplier.

## Close

Close both rows under the 28 Oct rule (work id, done-means, due).

## Risk

Touches: the ops repo (a new scheduled workflow, its alert secret and its config), site pages, the publish window this week, and the reading rota's order.
Blast radius: the workflow can only send the one push. The site changes are reversible.
Probable failure modes:
- The workflow's alert credential: it is a live credential, so keep it in the ops repo's secrets and never in a file.
- A false alarm when the heartbeat push itself fails while the machine is fine. Say how the workflow tells those apart, or accept and state the false-alarm rate.

Proportionality: contract-touching (a live credential and a public site) — implement with the named mitigations.

— Director ruling, 8 Nov 2026, his words above; the drafting is the advisor's.

## Done

(seat executor, 8 Nov.) **The ruling is recorded and its work is carried by named commitments; the builds are not done.**
- **Close (both rows):** `off-box-liveness` and `the-publish-window-is-anchored-to-monday` are answered in
  `docs/direction/DIRECTION.yaml` with work id, done-means and due (28 Oct rule): `off-box-liveness-workflow`, due
  15 Nov (the workflow proven against a stale heartbeat, its credential only in repo secrets, both stops given a cause
  or "we cannot tell"); `early-publish-this-week`, due 10 Nov. `director_concerns --overdue` chases both.
- **Item 3, DDD first:** recorded as the head of rota (b) in `docs/institutional/reading_log.md`. The rota itself still
  queues behind the correctness exit test (5 Nov steer's own **When**).
- **Item 2, site spend:** handed on as a continuation; the choice and its spend go in the stretch log when made. The
  correctness gate still governs what the site shows.
- Not done here: the ops-repo workflow, the stop-cause investigation, the early-publish change to
  `content_publish_window`, and the site work. Each is a continuation, not a claim on this file.
