# [ADVISOR-NOTE] — CCM provenance + the seat-guard finding (2026-08-05)

**Type:** [PROVENANCE + FINDING + one small work item]. Director-ratified for staging 2026-08-05 evening. Explains two `[CCM]` merges the resident worker will find on main, and registers a structural defect they exposed.

## Who CCM is
"CCM" = director-launched Claude Code cloud sessions (Anthropic-managed sandboxes, GitHub-proxied, push restricted to their own branch), briefed by the advisor with fenced, self-contained task orders. CCM is NOT the worker seat: its fences forbid touching `docs/staging/`, CLAUDE.md worker duties, NTFY, and daemons. It exists to do bounded, repo-complete, cache-free work while the machine is offline. Do not re-mint what it shipped.

## What landed (both advisor-verified before merge; proofs in the PR bodies)
- **PR #4 — governance registry validator** (retro instantiation 2): `tests/design/test_maturity_map_contract.py`, 17 tests; dated ratchet allowlists (shrink-only, stale-entry enforced); R15 mutation tests; the 4 prose dependency edges moved to `blocked_reason`.
- **PR #5 — simplifications store extraction** (retro FM-1): `docs/design/simplifications/` (~181 per-atom files + README carrying the project's first Birth Certificate), loader `tools/simplifications_store.py`, SINGLE-USE migration script, six consumers ported with per-consumer proofs (incl. `supervisor._atom_fingerprint`, a one-line count read, fingerprints byte-identical), map 1,716,747 → ~248,7xx bytes under a 400KB spine-ratchet test. Round-trip SHA-256 identical pre/post. Advisor additionally ran the PR4-test × PR5-map combination and a full local double-merge simulation: clean, 48/48 across contract + store + facets.
- Loose thread deliberately left: `block_reason` prose exists on 27 atoms alongside the new 4 `blocked_reason` tokens — reconcile during the ruled map rework, not before.

## THE FINDING — hooks don't know whose hands they're in
`.claude/hooks/` is committed, so **every Claude Code session on this repo, anywhere, executes the worker seat's hooks.** Observed live in both CCM sandboxes: `stamp_human_presence` dirtied `.human_last_input`, auto-process machinery ran, the stop-hook issued seat-inappropriate guidance. `pull_next_work.py` is the dangerous one — a foreign session could consume the instruction channel. It did not happen, but only because the brief's fence and the agent's judgment held: behavioural protection where structural is required.

## The fix (ordinary work, worker sequences; see-and-correct applies)
A **seat-guard**: each hook derives seat identity from a marker that exists only on Skynet (environment variable or a file OUTSIDE the repo — anything in-repo clones everywhere) and silently no-ops when absent. `pull_next_work.py` first, then the stamp/log hooks; the guard itself gets an R15 mutation test both ways (marker present → hook acts; absent → provably inert). Register in the map under the naming law — plain title: "Hooks know whose hands they're in." Future CCM tasks then rest on structure, not luck.

— Advisor note, staged 2026-08-05 evening; machine offline throughout both CCM sessions.

## Amendment (2026-08-05, ~21:45) — all four PRs merged; seat-guard SHIPPED; one observation

The director merged PRs #4, #5, #6, #7 at 21:31. Updates to the above:
- **The seat-guard is BUILT and on main** (PR #7) — do not re-mint. Seven hooks guarded, `block_sudo` universal, structural-lock test prevents unguarded future hooks, R15 both ways (advisor replicated the mutation digit-for-digit). Marker: `~/.config/synthetic-enterprise/.env.ntfy`; `SE_SEAT` overrides. Fail-closed: marker missing/unreadable → hooks silently inert. Resident-side integration self-proves at first wake: if the tick draws work, the guard passed through.
- **The epistemic wall is under test** (PR #6, merged WITH its perimeter-widening amendment): static import ratchet over {company, saas} ↔ {sim, simulation}, seam = company.interfaces. Class (a) company-side→SIM holds 2 named legacy edges (saas→simulation) — the wall's highest-priority shrink targets. Class (b) freezes the ~107-edge reverse mass. Shrink-only allowlists, stale-entry enforced. Advisor ran the full suite on merged main: 114 green across design+hooks+architecture tiers; map 248,736 bytes; store 181 files.
- **Observation to reconcile at wake:** commit `4483b34` ("chore(liveness): publish heartbeat", 17:38 2026-08-05) was pushed DIRECTly to main while the machine was nominally offline and no workflows exist. The liveness publisher appears to have run at least once mid-week. Check the boot/journal record for 2026-08-05 ~17:38 and reconcile; no other unexplained pushes observed.
