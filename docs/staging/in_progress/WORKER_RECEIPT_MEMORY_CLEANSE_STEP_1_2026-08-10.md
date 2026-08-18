# [WORKER-RECEIPT] MEMORY_CLEANSE step 1 — 5.1GB reclaimed; the disable itself needs the operator (2026-08-10)

**Severity:** RECORDED · **Lane:** H_harness

Against `DIRECTOR_PRIORITY_MEMORY_CLEANSE_2026-08-10` step 1, granted by pane 2026-08-10 evening.
Checked the delivery record first per "ticks: verify, don't redo" — llama-server was **live**
(`ollama.service` active + enabled, `llama-server` resident 5,529 MB), so step 1 was NOT already done.

## R2-style receipt: freed memory, before and after

```
BEFORE 2026-08-10T17:26:24Z              AFTER 2026-08-10T17:27:51Z
  Mem total      15912 MB                  15912 MB
  Mem used       12329 MB                   7203 MB      -5126 MB
  Mem free        1038 MB                   5990 MB      +4952 MB
  Mem available   3582 MB                   8708 MB      +5126 MB
  Swap used       4086 / 4096 MB            3794 / 4096 MB
  llama-server    pid 3015088, RSS 5529MB   GONE
  ollama (super)  pid 2738347, RSS 42MB     pid 2738347, RSS 40MB
```

`/api/ps` before: `qwen3:14b` loaded, `size_vram` 9,646,353,939. After: `loaded: NONE`.
Unload confirmed by the daemon itself: `{"model":"qwen3:14b",...,"done_reason":"unload"}`.

## What was done, and the one part that was NOT

**`sudo` is banned in this harness** (`.claude/hooks/block_sudo.py`, HARNESS_BEST_PRACTICE_ADOPTION
item 1b) and `ollama.service` is a **system** unit running as uid 999. `systemctl stop/disable
ollama.service` is therefore not available to this seat, and hook-bypass is a WALL — so it was not
attempted twice, and no workaround was sought.

Decomposed instead, per ESCALATION_IS_NTFY_NEVER_WINDOW (do the reversible parts, escalate only the
irreducible core):

| done now | how |
|---|---|
| model evicted from memory (the 5.1GB) | `POST /api/generate {"keep_alive":0}` — no root needed |
| `discovery-daemon` PAUSED | `systemctl --user stop && disable` — a **pure** qwen organ (its only model path is `_call_qwen`, 6-hourly) |
| **STILL OPEN — operator only** | `sudo systemctl disable --now ollama.service`, so the 40MB supervisor cannot re-spawn a 5.5GB child |

## Organ disposition (the "route or pause, with a receipt" half)

Live callers of the local endpoint, established by reading each one rather than by assuming:

* **`background/discovery_agent.py`** — `_call_qwen` is the organ's whole purpose. **PAUSED**
  (stopped + disabled). Not re-pointed: routing a 6-hourly research daemon at the frontier API is
  not "trivial re-pointing", it is new recurring spend on a background loop, which CLAUDE.md
  forbids ("no frontier API spend in simulation runs").
* **`background/dispatcher.py`** — `_call_qwen` classifies inbound NTFY. **LEFT RUNNING**: the
  safety-critical direction is a keyword fast-path that never consults the model
  (`_URGENT_KEYWORDS`, "don't trust Qwen with these"), and with the endpoint empty `_call_qwen`
  returns `""`, which falls through to `normal` — i.e. it degrades toward *more* attention, not
  less. It will briefly reload the model on an ambiguous message until the service is disabled.
* **`background/background_worker.py`** — `run_ollama_task` is **defined and never called**
  (no-caller class). It does not touch ollama at all, so it keeps running; its `run_complete`
  marker sweep is load-bearing for publishing and was deliberately not disturbed.
* `naive_organ.py`, `sanity_daemon.py` — no model coupling. Untouched.

## Honest bound on this receipt

The 5.1GB is reclaimed **now**, but it is not yet *durable*: the ollama supervisor is still enabled
and will re-load qwen on the next dispatcher call or on reboot. Durability needs the one root
command above. Steps 2 (headroom governor) and 3 (tmpfs preflight + OOM classification) are
untouched and remain on their stated sequence.
