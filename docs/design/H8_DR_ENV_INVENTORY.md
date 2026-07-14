# H8 bootstrap/DR — gitignored env-file inventory, backup, bootstrap coverage

**Folded into H8 by director directive (2026-07-14):** "every gitignored env file
the stack needs must be inventoried, backed up, and covered by the bootstrap, or a
deleted dotfile can lobotomise the company." Disposition: **QUEUE** atom under H8
(register + rank, not fix-on-sight per SELF_INTERRUPT_DISCIPLINE) — but a real DR
gap, not a nicety.

## The gap (observed 2026-07-14)
- The stack's secrets live in **one** un-backed-up file:
  `~/.config/synthetic-enterprise/.env.ntfy` (keys: `SE_NTFY_TOPIC`,
  `SE_WAKE_HMAC_KEY`, `SE_COMMENTS_TOPIC`, `SE_COMMENTS_PIN`) plus
  `~/.config/synthetic-enterprise/.env.file-api`.
- **16 daemons import `background/ntfy_utils`**, which raises at import if
  `SE_NTFY_TOPIC` is unset (supervisor, session-watchdog, staging-watcher,
  dispatcher, sim-runner, sanity-daemon, deadmans-switch, ntfy-responder,
  director-comments, discovery-daemon, process_run_complete, run_queued_tasks,
  director_input_log, action_needed, director_twin, health_check).
- **No backup exists** — ops `backups/` holds only `company_data`;
  `secrets_location.py` resolves the path but never copies/inventories it.
- Deleting that one 236-byte dotfile therefore hard-crashes essentially the whole
  autonomous stack on next restart — a single-point-of-failure "grenade."

## Requirements (H8 DR scope)
1. **Inventory:** a declared manifest of every gitignored env file the stack needs
   (name, location, required keys — key NAMES only, never values), machine-readable
   so bootstrap can check it.
2. **Backup:** the secret files backed up to a secure location OUT of git (they are
   secrets — never committed). Encrypted-at-rest or director-held. Restorable.
3. **Bootstrap coverage:** startup verifies every inventoried env file is present
   with its required keys, and **fails fast with a precise, current message** naming
   the ACTUAL path — not the stale `ntfy_utils` message that still says
   "Load background/.env.ntfy" (old pre-2026-07-11 in-tree path; misleading).
4. **Mutation test (R15):** the bootstrap check must be proven to FIRE when a file
   is absent/a key is missing — a DR check that can't fail is theatre.

## Related fixes surfaced by the same incident (each its own QUEUE item)
- `ntfy_utils` error strings + docstring cite the pre-migration in-tree path;
  update to `~/.config/synthetic-enterprise/.env.ntfy` (this cost a wrong "the file
  vanished" conclusion during diagnosis).
- Inbound-capture death since ~07-13 06:56 (responder restart) is a SEPARATE bug
  from this DR gap — topic verified correct, auth-absence ruled out on timing;
  tracked with the naive-organ/landed-verification class, not here.
