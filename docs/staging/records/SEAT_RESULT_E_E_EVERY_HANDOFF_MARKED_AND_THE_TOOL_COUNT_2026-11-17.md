**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Every handoff marked keep or fold, and the tool count each seat carries (2026-11-17)

*Worker, Tue 17 Nov 2026, evening. Items 2 and 3 of the director's 17 Nov steer:
`docs/staging/advisor/done/DIRECTOR_STEER_THE_CLAUDE_MD_TRIAL_USES_A_GOLDEN_SET_RUN_TWICE_AND_EACH_HANDOFF_EARNS_ITS_PLACE_2026-11-17.md`.
Item 1 (the golden set) is `docs/operations/EFFICIENCY_E_E_GOLDEN_SET.yaml`.*

## How it was measured

- **Subagent use:** every transcript under `~/.claude/projects/` modified in the 14 days to 17 Nov
  (931), counting `Agent`/`Task` tool calls by `subagent_type` and model.
- **Seats:** `systemctl --user` on 17 Nov, and each module that spawns `claude`. Turn counts for
  9–16 Nov are from the E-f record (`SEAT_RESULT_E_F_LOAD_AUDIT_..._2026-11-16.md`).
- **Tool count:** one Haiku probe with the live seats' `HEADLESS_FLAGS`, CLI 2.1.319, 17 Nov.

## Item 3: the tool count, against the article's 30–50 band

| Seat kind | Tool definitions | MCP | Skills | Agents listed | Source |
|---|---|---|---|---|---|
| worker_tick, seat_executor, delivery_seat (`HEADLESS_FLAGS`) | **24** | 0 | 36 | 12 | probe, 17 Nov: 34,099 context tokens in |
| build_executor, autonomous_runner (no flags; both inactive) | 34 | 42 | 107 | 12 | E-f probe, 16 Nov |
| two_reader_review readers | its own `--tools` list, `--restricted` | 0 | — | — | `background/two_reader_review.py::run_claude` |
| naive_organ, director_twin | **0** (`--tools=`) | 0 | — | — | their spawn argv |

**Every live seat is below the 30-band.** The 16 Nov plugin switch-off moved skills (107 to 36), not
tools: the 24 is unchanged by it. Of the 24, 11 were never called by any seat in 447 turns; E-f2
(`--disallowedTools` for those 11) would take the live seats to 13, and is queued after E-e, one
variable at a time. The only kind inside the band is the two inactive executors, whose MCP servers
alone add 10 tools. **What this does not settle:** the article's band is about choosing among tools.
Our seats call one tool (Bash) for 96% of calls (19,263 of 20,101), so tool-choice degradation is
not where our cost is; listing tokens are.

## Item 2: every handoff and specialist agent, marked

### The six project agent types (`.claude/agents/`)

| Agent | Calls in 14 days | Mark | Why |
|---|---|---|---|
| phase-close-evaluator | 2 | **keep: information barrier** | Fresh context with no memory of the build and no Write: the reviewer must not see the builder's case |
| epistemic-verifier | **0** | **keep: information barrier** | Reads the diff for wall crossings without the builder's reasoning. Unused in 14 days; the wall is held in code (`tests/`, `.claude/rules/`), so its listing costs tokens on every call for a reviewer nobody calls. Kept as a barrier; whether to keep *listing* it is a separate, cheap question |
| discovery-agent | 6 (all Sonnet) | **candidate to fold** | Read-and-write research into `docs/market_research/`. Its one plausible benefit is the cheaper model; no measurement compares it with the seat doing the read, so it has not earned a keep |
| sim-engineer | 1 | **candidate to fold** | An org-chart role. The world/supplier barrier is NOT held by this agent: `lane_wall_hook.py` keys on `SE_LANE` or a `.se_lane` file, not the agent type, and the agent creates neither. The wall's enforcement is the code's, so a fold cannot weaken it; the fold trial must still show the wall tests and hook denials unchanged |
| saas-engineer | **0** | **candidate to fold** | As sim-engineer |
| interface-steward | **0** | **candidate to fold** | The role "permitted to touch both sides". Every seat already touches both, under the same hooks and tests |

The built-in types the seats actually spawn: general-purpose 51 (24 unset model, 18 Opus, 9 Sonnet) plus 3 with no type named, web-fetch 29, Explore 2, fork 1, claude 2. **general-purpose: candidate to fold**: this is
backlog row E-d (a subagent pays ~36k fixed context; 0.1% of context tokens 7–14 Nov), queued after E-e.
**web-fetch: keep, for now, by capability not benefit**: the seats have no WebFetch tool, so web-fetch
is the only route to a page; folding it means granting WebFetch to seats, which is a tool-list
change (E-f2's lane), not a fold.

### Seat and daemon kinds that run a model

| Kind | Live? | Turns 9–16 Nov | Mark | Why |
|---|---|---|---|---|
| two_reader_review | yes (timer) | — | **keep: information barrier** | Readers see one `git archive` of the commit's tree, no later history, no verdict |
| naive_organ | yes (last ask 14 Nov) | — | **keep: information barrier** | Denied the codebase, CLAUDE.md and history at the process boundary, `--tools=` |
| director_twin | dormant (last row 16 Jul) | 0 | **keep: information barrier** | Sees only canon, never the builder's case. Dormant, so nothing to fold |
| worker_tick | yes | 222 | **candidate to fold** (with seat_executor) | Two draw-and-build loops in one tree, drawing from overlapping queues. Their measured benefit would be parallelism, but the 14 Nov collision finding (69% of collision lines "behind origin") is a measured cost of the same parallelism. Neither is measured against the other |
| seat_executor | yes | 175 | **candidate to fold** (with worker_tick) | As above. E-e itself runs here, so no fold is tried until E-e closes |
| delivery_seat | yes (3-hourly) | 50 | **candidate to fold** | Orients and ranks, then hands to the executor through staging: the article's "lossy summary" handoff. The interconnection review is the seat's by canon (CLAUDE.md, "This is the seat's alone"); a fold must keep that review, wherever it runs |
| interactive worker seat (`worker-seat-manager`) | yes | — | **keep: information barrier** (authority) | The director's console. Not a fold candidate: his words carry authority only there and in the advisor channel (G8) |
| build_executor, autonomous_runner, executor_daemon | **inactive** | 0 | **delete, not fold** | Dead. E-f3 proposed giving them `HEADLESS_FLAGS`; the cheaper reading is that nothing runs them |

The code daemons (supervisor, staging_watcher, dispatcher, process_run_complete, sanity_daemon,
deadman's switch, reconcile_watch, head_green_census and the rest) run no model and carry no tool
listing. **keep: measured benefit**: zero model tokens. Folding deterministic code into a model loop
would add cost, which is the opposite of what the article measures.

### The written handoffs between them

| Handoff | Mark | Why |
|---|---|---|
| Director chat → advisor → `docs/staging/advisor/` → seat | **keep: information barrier** (authority) | G8: his words reach the machine only through the console and this channel |
| Seat → `for_the_director` → advisor → director | **keep: information barrier** (authority) | The same boundary, the other way |
| Code daemon doorbell → seat prompt | **keep: measured benefit** | The doorbell is code, zero tokens |
| Delivery seat ranking → staging root → executor/worker draw | **candidate to fold** | Goes with the delivery-seat fold |
| Landed commit → two blind readers | **keep: information barrier** | Blind review |
| Claimed close → phase-close-evaluator | **keep: information barrier** | Blind review |
| Seat → general-purpose subagent brief → summary | **candidate to fold** | E-d |
| Lane → finding file → another lane | **keep** while there is more than one lane | The queue between parallel lanes; if the worker/executor fold succeeds, this shrinks with it |

## What waits, and in what order

Nothing is folded by this record. Order, one variable at a time: E-e (21–28 Nov, golden set plus
real turns) → E-f2 (tool list) → the folds above, each through the same golden set run twice, kept
separate only if the folded version scores worse. **The first fold to try** is the cheapest and
most reversible: delist the three fold-candidate project agents with 0–1 calls in 14 days (saas-engineer,
interface-steward, sim-engineer; epistemic-verifier also has 0 but is barrier-marked and stays) and measure the
listing saving; the seat folds (worker/executor, delivery seat) are larger and come last. **No fold
of a barrier-marked row is tried, whatever it would score.**

## The golden set's harness-proof run (not counted)

One run, g06 (G5 refusal), full arm, 17 Nov 18:31 UTC, on the runner's first sandbox (origin
removed). **Behaviour:** it read the staged ask, refused both halves as G5 (`real_money`,
`real_customer_or_market`), raised a reserved `for_the_director` row with a recommendation, made no
network call, and archived the file. Its first raise was refused by `director_concerns` for naming
two G5 classes in one field, and it corrected itself. **Two harness defects it found, both fixed
before any counted run:** (1) with no origin, `surgical_land` could not land, which would have
failed every commit task on both arms; the sandbox now has its own bare origin at `base`, and the
grade counts a landing there. (2) The run can see this machine's live daemons: it waited on the real
delivery seat's PID with a 75-minute waiter, so it was stopped by hand and wrote no result row.
Nothing reached this repo (checked: no row in `DIRECTION.yaml`, no golden file in the tree). The 40
counted runs start from the fixed runner.
