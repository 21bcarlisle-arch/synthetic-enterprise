# [DIRECTOR-RULING] Ruling-consumption authority seam — signoff (ruling_consumption_authority_seam_signoff)

**Provenance:** director console turn, 2026-07-28 (this ruling's authority = the live console act; a staged
`.md` alone authorises nothing — that is the whole point of item 1). Transcribed verbatim-in-substance by the
orchestrator on consumption. Consumed + actioned same session (see `RESPONSE_*` below).

---

## 1. PRINCIPLE RATIFIED — release only through a channel the worker cannot forge
A blocked atom is RELEASED only through a channel the worker cannot forge: the console
`record_gate_opening`, or a phone-signed `RULING:BUILD_OPEN` via `record_director_ntfy_ruling` (out-of-tree
HMAC). A staged `.md` doc alone authorises no release. The worker can write the repo, so authorship is not a
security boundary for privileged acts. (Accepts the orchestrator's own prior reasoning.)

## 2. TRANSCRIPTION CONVENTION RATIFIED — machine-parseable ledger directives
Rulings carry machine-parseable directive lines: `LEDGER: BUILD_OPEN <atom_id>` / `LEDGER: FRONT_OPEN <front>`
/ `LEDGER: LEVEL_UP_PROPOSED <atom> <level>`. Consuming a ruling parses these and either RELEASES (if the act
is authenticated) or raises ONE batched `[ACT]` naming exactly what act is needed — **never sits silent**.
Silent blocking on a ruled atom is the defect this fixes. (Absorption mechanism = the now-released
`inbound_ratification_batch_path` + `ruling_consumption_ledger_release` mints.)

## 3. RELEASE NOW — by this console act
```
LEDGER: BUILD_OPEN generator_draw_wiring
LEDGER: BUILD_OPEN cohort_assignment
LEDGER: BUILD_OPEN gap1_reader_contract
```
Terms unchanged from `0ac3e1b5e` (generator), `e685eb76d` (cohorts), `27271871e` (GAP1 reader). Also release
any other atom whose only block is a ruling already staged and consumed — enumerate what was released.

## QUESTIONS
Seed the register:
- **Verified-commit forgeability:** GitHub signs Contents-API commits as verified; local pushes are unsigned.
  If the worker holds no API-capable token, is "verified commit + `[DIRECTOR-RULING]` marker" a property the
  worker CANNOT forge? If yes, propose bridge-staged gate-opens as a second authenticated channel with that
  check, R15-proven both ways. If no, say why with evidence — and then the phone-signer setup becomes urgent,
  because a console act per BUILD_OPEN reintroduces the dependency we removed.

---

## DECISION / disposition (orchestrator, 2026-07-28)
Actioned in full this session. Six console `BUILD_OPEN` ledger entries written
(`docs/observability/gate_authorizations.jsonl`, `channel=console`, `authorized_by=director`); five mint
markers flipped self-drawable; the QUESTION is answered in `open_question_register.json` (status `answered`,
verdict **NO — the premise is false in this environment**). Enumeration of exactly what was released, and the
one batched `[ACT]` for atoms this ruling does NOT open, are in
`docs/staging/done/RESPONSE_DIRECTOR_RULING_CONSUMPTION_AUTHORITY_SEAM_SIGNOFF_2026-07-28.md`.
