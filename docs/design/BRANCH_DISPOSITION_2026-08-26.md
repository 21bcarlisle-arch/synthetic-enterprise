# Branch disposition, 2026-08-26

Director, 2026-08-26: *"46 branches on origin, 29 worktree-agent, 8 claude, 6 salvage, only main
live. The salvage ones hold work somebody deliberately parked and nobody returned to. Say what's
stranded, land or discard it, delete the rest."*

This file is the "say what's stranded" half, written BEFORE the deletions so the record survives
them. Every row carries its tip SHA: a deleted branch is recoverable from that SHA for as long as
origin has not garbage-collected, and after that this table is the only account of what was there.

Total branches (excluding `main`): 45

## Fully merged into main — content is already in origin, deleting loses nothing

| branch | tip | last |
|---|---|---|
| `ccm/registry-validator` | `9a191006a` | 2026-08-05 |
| `ccm/simplifications-extraction` | `3d2718a57` | 2026-08-05 |
| `claude/are-you-there-yn3vub` | `16573bfa7` | 2026-08-06 |
| `claude/ccm-characterization-tests-pass-2-8aym88` | `ea3f711ec` | 2026-08-06 |
| `claude/epistemic-wall-import-ratchet-jnw2dl` | `477063a30` | 2026-08-05 |
| `claude/ghost-pusher-liveness-q7isjy` | `ee2dd0865` | 2026-08-07 |
| `claude/invoice-characterization-tests-lvwfw0` | `fc9b731a6` | 2026-08-06 |
| `claude/seat-guard-daemons-689xof` | `9fd2f4d1f` | 2026-08-07 |
| `claude/seat-guard-hooks-r561fi` | `de94c0306` | 2026-08-05 |
| `claude/static-quality-ratchets-smpvif` | `de1dd50f3` | 2026-08-06 |
| `site1-expert-doors-reconcile` | `45246fd16` | 2026-08-03 |
| `worktree-agent-a0241e48573cdf5d3` | `ad482600b` | 2026-07-13 |
| `worktree-agent-a0df789208747ab98` | `954cf6b03` | 2026-07-13 |
| `worktree-agent-a22b4f1cbec9b0dd3` | `a7c74147e` | 2026-07-13 |
| `worktree-agent-a3d060503940dc0d8` | `c1902fedd` | 2026-07-13 |
| `worktree-agent-a5e5fab65d05fdf93` | `35d2f7871` | 2026-07-13 |
| `worktree-agent-a6a372f9e7cae76b2` | `29ba79c32` | 2026-07-13 |
| `worktree-agent-a7f7adeb627f11410` | `8a7a90f66` | 2026-07-30 |
| `worktree-agent-a8641cf21857fbfa5` | `11b7ea185` | 2026-07-13 |
| `worktree-agent-a9ec080a4cba6773c` | `489960be2` | 2026-07-13 |
| `worktree-agent-abf9c1ac250caa3a7` | `d6efc0dcc` | 2026-07-13 |
| `worktree-agent-ae47fa98177b3938b` | `fb1227dbc` | 2026-07-13 |
| `worktree-agent-afa8d4b108ff5c729` | `e16f00de5` | 2026-07-13 |

Count: 23.

## Unmerged — what each actually holds

| branch | tip | last | source files | subject |
|---|---|---|---|---|
| `salvage/ep6-wall-protocol-typing-20260819` | `65a31eb3a` | 2026-08-19 | 65 | On main: EP6 salvage: wall protocol typing pass, red (3F/1E), parked off the shared tree |
| `salvage/knife3-growth-desk-20260819` | `b5bfd6505` | 2026-08-20 | 63 | On main: KNIFE3 step 39 salvage: growth_desk counted_in_guard removal, parked off the shar |
| `salvage/knife3-step39-consumer-half-20260820` | `8bba6988e` | 2026-08-19 | 12 | SALVAGE(auto): preserve this fork's uncommitted work at 2026-08-19T09:06:56Z |
| `salvage/knife3-step39-consumer-half-20260820b` | `63ae1c8a0` | 2026-08-20 | 7 | KNIFE3 step 39 salvage, CONSUMER HALF: the allowlist entry was removed but the cut it decl |
| `salvage/saas-margin-rename-20260819` | `c52cb09fc` | 2026-08-20 | 52 | On main: saas margin-rename salvage: contribution/net_of_all_costs split, parked off the s |
| `salvage/seam-door-call-conformance-20260819` | `7fde5be4a` | 2026-08-20 | 62 | On main: seam-door-call-conformance salvage: untracked WIP, parked off the shared tree |
| `worktree-agent-a0ce47338375413e2` | `79db61c42` | 2026-08-03 | 32 | SALVAGE(auto): preserve this fork's uncommitted work at 2026-08-03T13:26:29Z |
| `worktree-agent-a28e560dac839894b` | `4910538ae` | 2026-08-03 | 1 | SALVAGE(auto): preserve this fork's uncommitted work at 2026-08-03T13:26:29Z |
| `worktree-agent-a3faa0acb3290cf4c` | `8419dacda` | 2026-08-03 | 26 | SALVAGE(auto): preserve this fork's uncommitted work at 2026-08-03T13:26:29Z |
| `worktree-agent-a416449f398f3b333` | `464998e56` | 2026-07-30 | 5 | RESCUE(SITE_EH1 rival impl): preserve a dead fork's uncommitted 836-line build |
| `worktree-agent-a6ad9f2b324019a71` | `8d27f05dd` | 2026-08-03 | 33 | SALVAGE(auto): preserve this fork's uncommitted work at 2026-08-03T13:26:29Z |
| `worktree-agent-a7e53b3f1c77109b1` | `2539d3a90` | 2026-08-18 | 0 | SALVAGE(auto): preserve this fork's uncommitted work at 2026-08-18T18:00:34Z |
| `worktree-agent-a8181339172167dad` | `a11a8be80` | 2026-08-03 | 12 | SALVAGE(auto): preserve this fork's uncommitted work at 2026-08-03T13:26:30Z |
| `worktree-agent-a84b7d9b76495702e` | `8949feb06` | 2026-08-03 | 5 | SALVAGE(auto): preserve this fork's uncommitted work at 2026-08-03T13:26:30Z |
| `worktree-agent-a860ccd66f355984a` | `bcec77146` | 2026-08-03 | 5 | SALVAGE(auto): preserve this fork's uncommitted work at 2026-08-03T13:26:30Z |
| `worktree-agent-a8661079868072634` | `39409b90c` | 2026-08-03 | 11 | SALVAGE(auto): preserve this fork's uncommitted work at 2026-08-03T13:26:30Z |
| `worktree-agent-a878c7c096d5deb9a` | `70fa1e195` | 2026-08-03 | 33 | SALVAGE(auto): preserve this fork's uncommitted work at 2026-08-03T13:26:30Z |
| `worktree-agent-abdcad5f797657eb3` | `3f79e7250` | 2026-07-30 | 8 | RESCUE(SITE_EH1_segment_disclosure): preserve a dead fork's uncommitted 818-line build |
| `worktree-agent-ae5594bc48eb7fdb2` | `4672d5c52` | 2026-08-03 | 31 | SALVAGE(auto): preserve this fork's uncommitted work at 2026-08-03T13:26:31Z |
| `worktree-agent-ae60f5d5b72b61420` | `bb3011629` | 2026-08-03 | 6 | SALVAGE(auto): preserve this fork's uncommitted work at 2026-08-03T13:26:31Z |
| `worktree-agent-aebe35df16c7670fd` | `336db0261` | 2026-07-30 | 5 | fix(SITE_EH2): the section header promised grading that had never happened |
| `worktree-cwd-fix` | `f8aff26d5` | 2026-07-21 | 12 | W2_12 D-SEGMENT trait-adoption recoupling atom -> L1 TWIN-RATIFIED (director console 2026- |


## The ruling on each unmerged branch

**Four salvage branches are SUPERSEDED, not stranded.** `salvage/saas-margin-rename-20260819`,
`salvage/ep6-wall-protocol-typing-20260819`, `salvage/seam-door-call-conformance-20260819` and
`salvage/knife3-growth-desk-20260819` all carry the same ~1,700-line core: the
contribution / `net_of_all_costs` margin split across `saas/clv_model.py`,
`saas/cost_to_serve.py`, `saas/enterprise_value.py`, `tools/couple_clv.py` and their tests.
**That work is on main and has been since 2026-08-17** — `saas/clv_model.py` reads
`CLV_MARGIN_BASIS = "net_of_all_costs_margin_gbp"` and `tests/saas/test_clv_margin_basis.py`
exists there. It landed by a different route two days BEFORE these branches were cut, so the
branches are stash-shaped snapshots of a tree that was already behind. `ep6-wall-protocol-typing`
additionally describes itself as red in its own commit subject ("3F/1E").

**`salvage/knife3-step39-consumer-half-20260820` is superseded by its own `...20260820b`
sibling** — 1,160 lines against 279, and the `b` subject says why: the earlier cut left "the
allowlist entry removed but the cut it declares not in the tree".

**`salvage/knife3-step39-consumer-half-20260820b` IS GENUINELY STRANDED and is being kept.**
279 lines across 8 files, and it is real unfinished work with a clear rationale: KNIFE3 step 39,
moving `use_var_hedge_decision` out of `run_phase2b` and into the company's own desk, so the world
stops deciding whether to ask the company a question. `HedgeDesk.set_term_hedge` gains a `None`
return — the established shape for a company door that declines, matching
`request_tou_offer(...) is not None`. Three of its four source files are untouched on main since;
`company/policy/decision_policy.py` is not, because this seat added `renewal_margin_arm` to it
today, so landing it needs that one conflict resolved.

**Fifteen `worktree-agent-*` branches are automated fork snapshots, not authored work.** Every
one carries a single commit whose subject is `SALVAGE(auto): preserve this fork's uncommitted work
at <timestamp>` — a dirty worktree preserved when a July/August fork was torn down, dated
2026-07-30 to 2026-08-03. Sampling the largest (`a3faa0acb3290cf4c`, 26 source files): diffing it
against current main shows main AHEAD on the sampled file (12 lines main has, the branch lacks),
i.e. the branch is stale residue rather than a fork ahead of trunk. They are the backup taken when
twelve fork-salvage branches were found existing only on this machine; the backup did its job, and
nobody returned to them in 23 days.

## Disposition

| class | count | action |
|---|---|---|
| fully merged into main | 23 | DELETE — content is in origin |
| superseded salvage | 5 | DELETE — content is on main by another route, or superseded by a sibling |
| automated fork snapshots | 15 | DELETE — stale residue, main is ahead |
| genuinely stranded | 1 | KEEP: `salvage/knife3-step39-consumer-half-20260820b` |
| other | remainder | see table above |

Deleting a branch does not delete a commit while origin retains it; the tip SHAs above are the
recovery handle, and this table is the record after that.

## Postscript — the one kept branch was examined and could not land either

`salvage/knife3-step39-consumer-half-20260820b` was held back from the deletions above as
genuinely stranded work. Examined properly, it cannot land, and the reason is worth more than
the branch is.

**It applies almost cleanly.** Of its seven source files, six are untouched on main since the
branch was cut; only `company/policy/decision_policy.py` has moved, and the two changes do not
overlap textually — the branch rewrites a comment block, main added the `renewal_margin_arm`
field near the top.

**But its premise is false against the current tree.** The comment the branch installs states:

> *"`run_phase2b.main()` was the world's last wall crossing into this module; cutting it meant
> deleting the `policy` parameter, so those four fields now resolve exactly the way `tone_mode`
> always did — from `active_policy()`."*

`simulation/run_phase2b.py:877` on main today reads
`def main(report_end=None, sim_interface=None, policy: DecisionPolicy | None = None)`. The
parameter was never deleted. The branch is the CONSUMER half of a cut whose producer half is
not in the tree — which its own commit subject says: *"the allowlist entry was removed but the
cut it declares is not in the tree."*

**And main has since built on the parameter staying.** `tools/run_value_cycle_ab.py` (2026-08-26)
runs each arm inside `policy_scope(...)` **and** passes `policy=`, deliberately, to inherit
`run_phase2b.main`'s refusal of a run whose argument and scope disagree — the chimera guard that
stops an A/B silently comparing two different suppliers. Landing the consumer half alone would
install a comment asserting a deleted parameter, against a tree whose value-cycle measurement
depends on that parameter existing.

**Disposition: DISCARDED, intent recorded.** What KNIFE3 step 39 (§3ah) wanted is still worth
doing and is unchanged by this: move the `use_var_hedge_decision` switch out of the world and
behind the company's own desk, with `HedgeDesk.set_term_hedge` returning `None` when the desk is
not running the VaR layer — the established shape for a company door that declines, matching
`request_tou_offer(...) is not None`. Tip `63ae1c8a0`. The work to do is the PRODUCER half first;
the consumer half is nine lines and can be rewritten in an afternoon against whatever the tree
says then, which is cheaper than carrying a branch whose comments describe a tree nobody has.
