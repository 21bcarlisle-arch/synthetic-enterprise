<!-- SUPERVISOR_DRAW: done -->
> **CLOSED 2026-07-29 (worker tick). All six items actioned; the Sweep report is below.**
>
> | # | Item | Disposition |
> |---|---|---|
> | 1 | `director_build_open` abolished as a block type | **DONE** `2b095998f` — all instances cleared; **mechanised** `69bbf00b7` |
> | 2 | `director_level_up` abolished; levels recorded not gated | **DONE** `2b095998f` — `record_level_up_self_certified` is the replacement authority |
> | 3 | BUILD_OPEN / LEVEL_UP_PROPOSED / ledger-release convention deleted | **DONE** `69bbf00b7` — see Sweep |
> | 4 | PIN + min-length/format check on inbound messages deleted | **DONE** `ae0f67079` |
> | 5 | One-way-door tags re-scoped to reality | **DONE** `dbb16e8ab` — reserved set is now exactly the four real-world consequences |
> | 6 | `gap_registers_as_mint_sources`: build it | **DONE** — build had landed `2454e70`; only the level cell remained, held by the block type item 2 abolishes. Registered as map atom `GAP1_gap_registers_as_mint_sources`, L3 self-certified |
>
> **SWEEP — what was removed (the ruling asked for this report):**
> * **13 atoms released.** Every `blocked_on: director_build_open` / `director_level_up` in
>   `docs/design/maturity_map.yaml` → `null`. Zero permission blocks survive.
> * **The stage-advance / BUILD-open alarm** in `fronts_reconciler.py` (§10.2) → `BUILD_UNGATED`,
>   informational only. That path existed *solely* to decide whether the director had permitted a BUILD.
> * **`docs/observability/.fronts_enforcement_enabled` deleted** and must stay deleted — the draw-filter
>   prevention layer is retired to its pre-2026-07-18 dormant default.
> * **The abolition is now a MECHANISM, not a data edit** (`_is_externally_blocked`): a `blocked_on`
>   naming any deleted permission convention no longer suppresses a draw, no matter who writes it or
>   when, and each ignored block is logged loudly. Clearing the 13 values was a one-time edit, and an
>   edit is an exhortation — this exact block type is what made 31 atoms yield zero drawable work.
>
> **WHAT I KEPT, each named with the real-world consequence it prevents (per your instruction):**
> * **The four reserved consequences** — real money, real people, a public claim in Poesys's name, a
>   real person's safety. A `blocked_on` describing one of these still blocks even if it also cites a
>   permission token; the judgement is delegated to `one_way_door.classify_action`, not forked.
> * **The level *record*** (R16 ledger-backed) — now self-certifiable, so it informs an auditable trail
>   and no longer waits on a human. Consequence prevented: a level move with no trace at all.
> * **Genuine non-permission blocks** — upstream dependencies, coupled-triad walls, named R10 data gaps.
>   One survives on the live map: `H27_payment_belief_gap` (`blocked_on: coupled_triad_measured`).
>   Consequence prevented: drawing an atom whose work genuinely does not exist yet.
>
> **DEFECT IN THIS RULING (§4, `DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27`):** it carries
> no **WORK THIS CREATES** block. I minted from the body rather than absorb it silently, and have asked
> the advisor bridge for the block. Flagged, not held — the work is done.

# [DIRECTOR-RULING] — Rip out the permission machinery. Tonight. (2026-07-29)

**Type:** [DIRECTOR-RULING] via advisor bridge. Do this now, before more work; it is cheap and it is blocking everything else.

## The problem

`THE_STANDARD` and `NTFY_IS_THE_DIRECTOR` removed approvals, signatures and gates **in writing**. The code still has them. **Code beats canon**, so you keep obeying machinery that no longer has a rule behind it.

Evidence from the last hour alone: a PIN invented for a status-report merge; an [ACT] asking permission to run one reversible command; a publish-gate alarm forwarded instead of fixed; three questions raised with no recommendation, two of which were yours to decide; and an [ACT] enumerating "BUILD_OPEN residue" against a signoff convention that was **withdrawn this afternoon**.

Every one of those is the old apparatus still wired in. This morning's mothballing removed the *busywork* machinery and left the *permission* machinery intact.

## Do now — remove, do not gate

1. **`director_build_open` is abolished** as a block type. Every atom currently held by it is released. There is no such thing as needing a build opened.
2. **`director_level_up` is abolished** as a block. Levels are proposed and recorded, never gated. R16's real requirement was *ledger-backed, not self-certified* — recording satisfies it.
3. **The BUILD_OPEN / LEVEL_UP_PROPOSED / ledger-release convention is deleted**, along with the signoff residue, the catch-all logic, and every path that enumerates what a director must authorise. If a code path exists solely to decide whether the director has permitted something, delete it.
4. **The PIN mechanism is deleted.** Any minimum-length or format check on inbound director messages is deleted — "yes", "go" and "PIN 07C3 PROCEED" must all work.
5. **One-way-door tags are re-scoped to reality.** A "safety control" that stops a *simulation* is not a safety control. **Only these are reserved:** spending real money, contacting real people, publishing a claim under Poesys's name, and anything touching a real person's safety. **Re-tag everything else and release it**, including `stop_control_gap_characterisation`.
6. **`gap_registers_as_mint_sources`: build it.** No further asking.

## The replacement, in one line

**Where you would previously have blocked: act, record how to reverse it, and say what you did.** Where you would previously have asked: **recommend, act on your own recommendation, and say what you decided.** The director reverses what he dislikes; that costs one message and is the whole safety model.

## Sweep

Search the codebase for anything that waits on, checks for, or reports the absence of director authorisation. **If it exists to gate rather than to inform, remove it.** Report what you removed. Anything you believe must stay, name it with the real-world consequence it prevents — and if the consequence is internal to a simulation, that is not a reason.

## Test

**After this, the only sentences you can send the director that require a reply are about real money, real people, or a public claim.** Everything else is "here is what I did" or "here is what I am doing unless you object."

— Advisor bridge. The advisor wrote most of what is being removed. 2026-07-29.
