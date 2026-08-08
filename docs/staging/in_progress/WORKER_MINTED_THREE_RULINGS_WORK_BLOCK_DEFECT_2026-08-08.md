<!-- SUPERVISOR_DRAW: available -->
<!-- draw-visibility marker (2026-08-08): MINTED, NOT BUILT. Deliverables below are identified from each
     ruling's BODY by the worker, because all three arrived WITHOUT a 'WORK THIS CREATES' block (§4 defect).
     The authors' own blocks are still OWED and have been requested by NTFY. These mints are the worker's
     reading, explicitly NOT a substitute for the authors' enumeration -- reconcile on arrival. -->

# [WORKER-MINTED] Work identified from three block-less rulings (2026-08-08)

## Why this doc exists

Three staged rulings carry no **WORK THIS CREATES** block:

- `DIRECTOR_RULING_H_LANE_CUT_AND_PLAIN_NAMING_2026-08-05.md`
- `DIRECTOR_RULING_INFRASTRUCTURE_POSTURE_2026-08-07.md`
- `DIRECTOR_RULING_TRAFFIC_FORECAST_AND_DEEPENING_REGISTER_2026-08-07.md`

Per §4 of `DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27`, a ruling arriving without one is a
**defect in the ruling**: mint what work is identifiable from the body **and request the block from the
author** — never silently absorb it. Both halves are done here. The block request went out by NTFY on
2026-08-08; until the authors' blocks land, everything below is *the worker's reading of the body*, which
is a weaker artefact than the authors' own enumeration and is marked as such.

**Verified with the parser, not by eye:** `supervisor.work_this_creates_deliverables()` returns `[]` for all
three files, and `supervisor.ruling_steer_missing_work_block()` lists exactly these three. The defect is
real, not a scanner artefact.

---

## Ruling A — H-lane cut + plain-words naming (2026-08-05)

**A1. Distribute H atoms to their subject lanes.** Verification-of-X belongs to X's maturity; a method is
not a lane. Named in the ruling: payment belief-gap → D, fabric belief-gap → W1, control mutation-tests →
the lanes owning those controls, judge validation → the lane owning each judged organ.
*Started this tick:* `H27_payment_belief_gap` now carries `pending_lane_move: D` rather than a half-done
rename — see the sequencing note under A2.

**A2. Land a number/id registry at the mint gate, so collisions become impossible.**
**This is the prerequisite for A1 and for minting any new atom, and should go first.** The ruling cites
three collisions; the map actually has more. Measured against `docs/design/maturity_map.yaml` (186 atoms):

- **11 genuine number collisions, 26 atoms:** `B3`×2, `B4`×2, `B5`×2, `F5`×2, `G1`×2, `G2`×2, `G3`×2,
  `H23`×2, `H24`×2, `H27`×2, **`OPS1`×6**.
- **6 numberless prefix groups, 21 atoms** — a second sub-class the ruling does not name, where the id
  carries no number at all so the grammar has nothing to enforce: `C`×2, `D`×5, `H`×4, `OPS`×2,
  `SITE`×5, `W2`×3.

47 of 186 atoms (a quarter of the map) sit in one of these two classes. Any rename or new mint attempted
before the registry exists risks adding to them, which is why A1 was deliberately not executed wholesale
this tick.

**A3. Split residual H into two lanes** — **H: The Build Engine** (draw, supervisor, worktrees, git
locking, gate hygiene, H's own exit criterion; ~14 atoms) and **OPS: Running the Machine** (daemon
lifecycle, launcher cutover, housekeeping, publish pipeline, stall handling, director escalation, plus the
posture shelf: security profiles, DR, NFR registers; ~14 atoms).

**A4. Dissolve the satellite prefixes** (`HX`, `GAP`, `H_GAP`, `OPS1`, bare `H_`) into proper ids inside
the two new lanes. Depends on A2.

**A5. Draft and adopt charters for H and OPS.** Both are past the map's dial-3 charter threshold. CC drafts
and adopts; charters take effect on adoption, no approval loop. Each receiving lane's charter gains the
standing audit-independence clause (independence lives in execution context — amnesiac organs, cold-eyes,
restricted context — not in a wall on the map).

**A6. Plain-English title + one-line gain statement on every lane and every atom.** Subject not mechanism;
mechanism vocabulary (draw, worktree, mutation, marker, hook) stays in description fields. Field mechanics
(repurpose `name` vs add `title`) are CC's choice.

**A7. Ids become machine keys** — grammar-enforced, registry-checked at mint (A2), and never rendered on
any human surface: chat, site, reports, NTFYs all show titles.

**A8. Map's site view renders titles**, lanes as named shelves, level as the visual dial; ids debug-hover
at most. The didactic rule already governing site graphs applies to the map picture.

**A9. Wire the falsifiable acceptance test:** the director, reading a lane's atom titles cold on his phone,
can spot a misfiled atom; a misfiling invisible in titles is a naming failure. Runs at each epoch close
alongside consolidation. *This is the R15 control for A6 — without it A6 is unfalsifiable prose.*

---

## Ruling B — Infrastructure posture: seat, standby, scale (2026-08-07)

**B1. Retire Qwen as a dependency.** Re-point dispatcher/classification traffic to a Haiku-class API call;
run adversarial/verification organs as restricted-context Claude (context isolation, not model
foreignness, is the independence mechanism this project already trusts); demote GPU workloads (clustering,
curve-fitting, batch summarisation) to opportunistic garnish when Skynet happens to be on. Effect: the seat
becomes hardware-agnostic. The naive-organ output-budget work applies unchanged.
*Note the CLAUDE.md consequence:* the model-routing section still names qwen3:14b as "all code generation
and mechanical execution" and the risk committee as "local Ollama only". Landing B1 makes those lines
false, so B1 must carry the CLAUDE.md edit with it — flagged for the decay audit already in staging.

**B2. Build the seat's new home (top OPS project per the evening revision).** In order: the bootstrap
script; the **automated Oracle A1 acquisition loop** — retry the free-shape launch until capacity lands,
*the machine is the retry mechanism, not the director*; then a graceful **Class-A cut-over** per the staged
proposal, marker moves, PC's marker deleted, one seat on Earth.

**B3. Keep Hetzner as the interim-or-fallback seat path.** An 8 GB-class box (~€7–13/mo post-June-reset) by
the same ceremony if Oracle's queue outlasts patience or the director prefers certainty; 4 GB
(€5.49–5.99) noted as workable-but-tight for full-suite runs.

**B4. Invert DR once the seat is cloud-resident.** Standby becomes a snapshot of the cloud seat (pennies);
the PC becomes the warm second fallback. Cut-over becomes bidirectional by construction.

**B5. Run the R5 timed dead-box drill as the arbiter** of Ruling 2's provider — if the drill exposes
capacity pain at rebirth, fall back to the Hetzner-snapshot pattern **on evidence, not preference**.

**B6. Hold the AWS account closed until Epoch-5 mobilisation.** This is a *standing constraint to enforce*,
not a task to do: the modern free tier self-closes at 6 months or credit exhaustion (90-day grace, then
resources erased), so opening it now burns the clock years early. At mobilisation, open it and spend the
~$200 deliberately standing up the product skeleton. Until then "proper scale" is exactly two things:
the traffic-forecast seams (Ruling C) and the 10k probe.

> **Reserved-class note:** B2/B3 reach real money and real external accounts. Under the four reserved
> classes, *provisioning a paid box or spending* is the director's; the bootstrap script, the acquisition
> loop against a free shape, the drill and the cut-over ceremony are all buildable now without spend.
> Decompose that way rather than holding the whole of B2.

---

## Ruling C — Traffic forecast + deepening register (2026-08-07)

**C1. TARGET_DESIGN.md consumes Tables A and B as its load section** (ARCHITECTED-OUT §2). This is the
system-level "bound" the Birth-Certificate law was missing per the retro's hardening 1.

**C2. Add the scale question to the write-time gate:** for any load-bearing choice, *"does this die at
10⁵?"* Posture: preclude nothing at 10⁶, engineer for 10⁵, probe at 10⁴ — seams must survive the design
ceiling, internals need only the current rung.

**C3. Give the 10k probe its expected values from Table A**, so the probe can confirm or refute rather than
merely measure. Go-live book ≈10³; smart penetration ≥90% at scale.

**C4. Register the Table B deepening rows in the map under the naming law** (so this depends on A2/A6).
Eight rows — tariff engine, payments, metering ingest, settlement, customer model, hedging/forward,
collections, switching CoT/CoS — each as an **interface commitment, not an implementation**. Building any
row's internals ahead of need is the ghost-suburb failure, explicitly *not* compliance.

**C5. Wire KNIFE's tie-breaker to the forecast** — *the graph proposes, the forecast disposes* — which now
has a forecast to dispose with.

---

## Sequencing the worker recommends (acting on it, not asking)

**A2 (id/number registry) first** — it gates A1, A4, A6, A7 and C4, and a quarter of the map is already in
the collision classes it prevents. **Then A3/A5** (the lane cut and its charters), **then A6–A9** (naming
law plus its acceptance test), **then C1–C3** (cheap, self-contained, unblocks the probe), **then C4** once
the naming law exists. **B1 runs in parallel** — it touches organs, not the map. **B2–B5** is the OPS
project, decomposed so the buildable parts (bootstrap, acquisition loop, drill, cut-over ceremony) proceed
without waiting on the reserved spend. **B6 is a standing constraint**, enforced not built.

## Still open — owed by the authors, requested not assumed

The **WORK THIS CREATES** block for each of the three rulings. Requested by NTFY 2026-08-08. When they
arrive, diff them against A1–A9 / B1–B6 / C1–C5 above: **anything in the authors' blocks and not here is a
gap in the worker's reading**, and anything here and not in theirs is a mint to withdraw or defend. That
diff is the point of the §4 rule and is why these deliverables were not quietly written into the rulings
themselves as if authored there.
