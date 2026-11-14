**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] One writer per shared file: measure where the lanes collide first (2026-11-14)

**Type:** STEER, through the advisor channel. The director's words, from chat on Sat 14 Nov:

- 11:13 GMT, sharing https://claude.com/resources/articles/building-always-on-agents with no comment.
- 12:10 GMT: "Per lane? Or per code base? Eg SIM Vs supplier?"
- 12:11 GMT, on the advisor's recommendation below: "Yes"

## What the advisor found (check it)

- **The source.** Anthropic, "Building always-on agents" (William Hu, 13 Nov 2026). Its five primitives are a durable inbox, timers, memory outside the worker, permissions, and an outbox. We match most of them: staging is the inbox, systemd timers are the scheduler, memory works by pointer, `for_the_director` defers without blocking, and NTFY is mothballed ("start quiet"). One rule we run the opposite way: **"An inbox should only have one active worker at a time."** The article names the cost of breaking it: competing runs and lost events.
- **Our contention is visible.** From 31 Oct to 14 Nov, 158 of 748 commit subjects (about 21%) match merge, reconcile, surgical, held-behind-origin, sweep, fork, unlanded or stranded. That is a crude keyword count: mechanical merges inflate it, and quiet contention is missed. Example: 14 Nov, "The shared tree is held behind origin by the seat's unlanded orientation record alone".
- **The heat is in shared state, not code.** File touches over the same window, merges excluded: `site/data` 2,778; `archive` 728; `docs/staging` 577; `tests` 396; `site/knowledge` 185; `simulation` 73; `company` 69. The top single files are `DIRECTION.yaml` 58, `SEAT_STRETCH_LOG.md` 46, `publish_provenance.json` 35, `decisions.jsonl` 35, `delivery.json` 34, and two staging findings at about 30 each. So a split by codebase (sim against supplier) would barely help; that split already exists as the wall and the engineers' file scopes.

## The question

**Which shared files account for most of the collisions between seats, and would giving each one a single writer remove them?**

## The outcome wanted

1. **Measure collisions, not touches.** Over two weeks of history and transcripts, for each file:
   - how often it was written by more than one seat or daemon within the same hour;
   - how many merge, reconcile, sweep, stranded or held-behind-origin events trace back to it;
   - an estimate of the session time those events cost.

   Name the seats involved. Pre-register the prediction first. The advisor's guess is that `site/data` and `DIRECTION.yaml` lead, and that `company/` and `simulation/` are small.
2. **If two or three files account for most of it,** propose a one-writer trial on the top one only. The pattern by file type:
   - **Generated feeds:** one publisher builds them from what has landed; lanes stop committing them. This overlaps the held 9 Nov generated-data steer; say whether this releases it.
   - **Ruled state** (`DIRECTION.yaml`, `decisions.jsonl`): lanes post a change request; one owner writes.
   - **Logs:** append-only, one file per seat, merged on read.
3. **If not,** say plainly that the shared tree's cost is paid and known, and stop. No redesign without the number.
4. Fold in the existing `isolate_hunks`, `surgical_land`, tree-lock and fork-alarm evidence. Say which of them a one-writer file would make unnecessary. A guard that can be deleted is the win, not one more.

## Reading-log entries to append

| Date | Source | Shared by | What we took | Verdict |
|---|---|---|---|---|
| 2026-11-14 | Anthropic, "Building always-on agents" (claude.com/resources/articles/building-always-on-agents, 13 Nov) | Director | We match the inbox, timers, memory-by-pointer, deferred approval and start-quiet; we break "one active worker per inbox". Measure collisions by file; trial one writer per hot shared file. | MEASURE |
| 2026-11-14 | AgriciDaniel/claude-obsidian (MIT, ~16k stars): Claude Code plus an Obsidian vault as a self-organising cited wiki | Director | Already have: source to linked cited notes, orphan rulings, conflict-safe writes (`isolate_hunks`, `surgical_land`). Its one idea, notes hung on what they're about, is the 14 Nov concept-link measurement. | ALREADY HAVE |
| 2026-11-14 | Samsung Research, LittleBit (NeurIPS 2025) and LittleBit-2 (ICML 2026): sub-1-bit LLM compression | Director | Shrinks memory but not the quality gap: Llama-2-7B perplexity 15.9 at 0.1 bits per weight against 5.5 FP16. It needs quantization-aware training a 3060 cannot do, and speed is shown only on an A100. Qwen was retired for quality and memory; this fixes only memory. The 12 GB card also cannot hold seat-sized context. | NOT FOR US |

## Rules

- **Measure before build**, and key the result to the property: collisions and their cost, not touch counts.
- **One variable at a time.** One file, one trial.
- **HOOK-BYPASS IS A WALL.** A single writer must still land through the gates.

## Risk

Touches: read-only over git history and transcripts; one report.
Blast radius: none until a trial is proposed.
Probable failure modes:
- **Counting churn as contention.** A daemon rewriting its own file 30 times a day costs nothing. Mitigated by the more-than-one-seat-per-hour rule.
- **A single writer becomes a new bottleneck** or a single point of failure. Any trial names its liveness check and how to reverse it.

Proportionality: doc-and-measurement only. Implement directly.

— Director steer, 14 Nov 2026, his words above; the reading and drafting are the advisor's.
