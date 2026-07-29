<!-- SUPERVISOR_DRAW: hold -->
<!-- BLOCK_RELEASE: director_ratification -- determination = no Python loader needed (systemd EnvironmentFile already loads the key into the running verify daemon); re-open only if the director confirms a non-systemd, non-model-facing verify caller exists. See docs/staging/done/RESPONSE_DIRECTOR_RULING_SIGNING_KEY_NEVER_PROVISIONED_2026-07-29.md. -->

> **HOLD 2026-07-29 — DESIGN QUESTION LARGELY ANSWERED: no Python loader needed. DO NOT BUILD.**
> The atom's own "answer FIRST" determination: is a loader absent, or does systemd `EnvironmentFile`
> suffice for every verify caller? Disk check this tick — the running verify daemon `ntfy_responder.py`
> (PID 114246) **already has `SE_WAKE_HMAC_KEY` loaded in its live env** via
> `EnvironmentFile=-/home/rich/.config/synthetic-enterprise/.env.ntfy` (`generate_units.py:49`). No
> verify-path caller was found that runs outside systemd AND is not model-facing (a model-facing caller
> MUST NOT have the key — scrubbed by design). So the honest output is **"no code change required, the
> EnvironmentFile path suffices."** **Unblocks when:** director confirms the key-match question (see
> `docs/staging/done/RESPONSE_DIRECTOR_RULING_SIGNING_KEY_NEVER_PROVISIONED_2026-07-29.md`) — if a
> non-systemd, non-model-facing verify caller is later identified, re-open then. Escalated via NTFY.

# [PLANNER-MINTED] Key-loading code for SE_WAKE_HMAC_KEY if absent, with model-facing scrubbing preserved (2026-07-29)

**Source ruling:** `DIRECTOR_RULING_SIGNING_KEY_NEVER_PROVISIONED_2026-07-29.md`,
WORK-THIS-CREATES **#2** ("Key-loading code if absent, with scrubbing preserved."). The ruling §1
**explicitly authorises the agent to build this** ("write the loader if one is missing") — a direct
director BUILD authorisation for this deliverable; the agent never handles the secret value itself.
**Serves:** the ruling's §0 finding — five comments describe how the key is scrubbed/held out-of-tree,
**and no code loads it.** Verified this tick: `background/ntfy_utils.py:45` is
`WAKE_HMAC_KEY = os.environ.get("SE_WAKE_HMAC_KEY")` — a bare env read with **no file fallback**, unlike
`background/file_api.py:41-45` which reads `.env.file-api` into `os.environ` when the var is absent. So a
process NOT launched by systemd `EnvironmentFile=-.env.ntfy` (`generate_units.py:49`) — e.g. an ad-hoc
verify, a non-service invocation — sees no key even once the director fills the file.
**Real-world fidelity gained:** none — operational plumbing so the provisioned key is actually reachable
by the verify path. Value = the §3 handover's success test can pass without depending on which launcher
started the process.

## The design question this atom must answer FIRST (do not assume "build it")
Determine, against real code, whether a loader is genuinely **absent** or the systemd `EnvironmentFile`
path already suffices for every verify caller:
- If the daemons that VERIFY inbound rulings (`ntfy_responder.py`, `director_authority_channels.py`,
  `gate_authorization.record_director_ntfy_ruling`) are ALL launched via a systemd unit that loads
  `EnvironmentFile=-.env.ntfy`, the key reaches them once the file is filled — **no loader needed**;
  the honest output is "no code change required, the EnvironmentFile path suffices", cite the units.
- If any verify-path caller can run OUTSIDE that env (the ruling's implication), add a **file-loader**
  mirroring `file_api.py:41-45`: read `resolve_secret_file(".env.ntfy")`, set
  `os.environ["SE_WAKE_HMAC_KEY"]` only if absent, at `ntfy_utils` import.

## SCRUBBING PRESERVED — the binding constraint (this is where a naive loader breaks the wall)
`file_api.py` loads its key into `os.environ` at import unconditionally. Copying that pattern verbatim
would load `SE_WAKE_HMAC_KEY` into the env of **any** importer of `ntfy_utils` — **including
model-facing processes** — defeating `scrub_model_facing_env` / `MODEL_FACING_FORBIDDEN_SECRETS`
(`secrets_location.py:40`) and re-opening the worker-forgeability gap closed 2026-07-23 (`6d81a7b08`).
The loader MUST NOT make the key readable to a model-facing spawn. Exit requires proving both:
1. a verify-path process that lacked the key now loads it from the file, AND
2. a model-facing spawn env (`scrub_model_facing_env(os.environ.copy())`, as `director_twin.py:109` /
   `build_executor.py:209` / `worker_seat.py` do) still has `SE_WAKE_HMAC_KEY` **stripped** after the
   loader runs.

## Exit criteria
- The absent/present determination is stated with cited launchers (systemd units + non-service callers).
- IF a loader is added: it is tested against a **dummy/test key** (never the real secret) — the agent
  builds and proves the mechanism without the value ever existing in-tree.
- **R15 mutation proof (a control that can FAIL):** a test that (a) reds if the loader stops loading
  the key for a verify-path process, AND (b) reds if the loader ever leaves the key in a scrubbed
  model-facing env. Break each direction, watch the matching test go red, restore byte-identical.
- **R2:** if a loader lands, name what must be restarted for it to take (the verify daemons), and the
  check the restart carries the new code.
- Reversible: `git revert` removes the loader; no secret value handled by the agent at any point.

## Deps
- **depends_on:** none to build/test (proven against a dummy key). It is a PRE-REQUISITE for the §3
  handover atom's success test — the director's `openssl rand` value is only reachable by the verify
  path once this is resolved (or shown unnecessary). Sequence: this atom resolves → `signing_key_provision_act`.

## Coverage mapping
- SIGNING_KEY #2 → **this atom.**
- SIGNING_KEY #1 → sibling `PLANNER_MINTED_phone_signer_a1_correction_2026-07-29.md`.
- SIGNING_KEY #3 → sibling `PLANNER_MINTED_signing_key_provision_act_2026-07-29.md`.
- SIGNING_KEY #4 → ALREADY COVERED (`blocked_item_literal_act_ledger` / `BLOCKED_ITEM_LITERAL_ACTS.md`);
  readiness gated on this atom + #3.

**Propose-then-proceed window:** proceed by default (ruling §1 directly authorises building the loader;
reversible via git; tested against a dummy key, real secret never handled by the agent; scrubbing wall
held and mutation-proven both ways).

## Deliverable (verbatim)
> Key-loading code if absent, with scrubbing preserved.
