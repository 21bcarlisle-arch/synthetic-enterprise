# RESPONSE — ruling_consumption_authority_seam_signoff (2026-07-28)

Actioned in full, same session, via the console channel (this director turn = the authenticating act).

## Item 1 (principle) & Item 2 (transcription convention) — RATIFIED, absorption armed
Recorded in `docs/staging/done/DIRECTOR_RULING_CONSUMPTION_AUTHORITY_SEAM_SIGNOFF_2026-07-28.md`. The two
mints that MECHANISE item 2 (so it is *absorbed*, not merely *consumed*) were themselves blocked on exactly
this signoff — both now released and self-drawable:
- `ruling_consumption_ledger_release` — ruling-consumption writes/parses the ledger entry that releases a block.
- `inbound_ratification_batch_path` — parses `LEDGER: BUILD_OPEN/FRONT_OPEN/LEVEL_UP_PROPOSED` → release-or-raise-ONE-`[ACT]`.

## Item 3 — RELEASED NOW. Enumeration of exactly what was released
All releases are console `BUILD_OPEN` records in `docs/observability/gate_authorizations.jsonl`
(`authorized_by=director`, `channel=console`, provenance = this console turn). Mints additionally flipped
`SUPERVISOR_DRAW: self-drawable`. **No LEVEL move was granted** (you wrote BUILD_OPEN, not LEVEL_UP_PROPOSED) —
every level stays `director_level_up` (R16); build forks re-apply it on completion.

| Atom | Basis | Mechanism | Terms |
|---|---|---|---|
| `generator_draw_wiring` | item 3 (named) | BUILD_OPEN + marker self-drawable | `0ac3e1b5e` |
| `cohort_assignment` (`CA1_cohort_assignment_live`) | item 3 (named) | BUILD_OPEN (map atom; blocked_on:director_level_up stays — its build is done, live effect rides SE_DRAW_POPULATION) | `e685eb76d` |
| `gap1_reader_contract` | item 3 (named) | BUILD_OPEN; reader BUILD marker = `gap1_reader_contract_failopen_fix` (folds the corrected contract) | `27271871e` |
| `gap1_reader_contract_failopen_fix` | item 3 catch-all | BUILD_OPEN + marker self-drawable | same GAP_TRIAGE ruling `27271871e` |
| `ruling_consumption_ledger_release` | released by items 1+2 (this ruling IS its named blocker) | BUILD_OPEN + marker self-drawable | this ruling |
| `inbound_ratification_batch_path` | released by item 2 (implements the ratified convention) | BUILD_OPEN + marker self-drawable | this ruling |

**Coupling note:** `cohort_assignment` (CA1) and `generator_draw_wiring` are one live act — CA1's `assign_cohorts=True`
seam is built default-off behind the director-reserved `SE_DRAW_POPULATION`; the generator activation flips that
flag on, which un-latents cohort assignment in the same run. The activation changes which world every run faces
(R13 curriculum act) — now director-authored. This is a substantial BUILD (flag flip + ~19 `run_phase*` entrypoints
hardened to the SYN-* dict shape + R15 both-ways + epistemic-verifier on the diff); it is now authorised and
drawable and should run as a dedicated build (not a supervisor micro-turn).

## NOT released — one batched `[ACT]` (item-2: never sit silent)
Registered in `action_needed_register.json` as `ruling-consumption-buildopen-residual-2026-07-28`:
- `gap_registers_as_mint_sources` — generic `director_build_open`, no consumed ruling names it; needs an explicit `BUILD_OPEN <atom>`.
- `stop_control_gap_characterisation` — `director_build_open` **and** ONE-WAY-DOOR #5 (safety-control), console-only/never-self-authored; I will not release it under the catch-all. Needs its own explicit console BUILD_OPEN or phone-signed ruling.

## Item 4 (QUESTION) — ANSWERED in the register: **NO**, premise false here
`open_question_register.json` key `0d7f5e74b25b`, status `answered`. Short form: the worker DOES hold an
API-capable token (`gh` OAuth `gho_…`, `repo`+`admin`+`push`, reaches the Contents API, stored under the same OS
user autonomous_runner spawns worker turns as), so it can mint GitHub-"verified" commits bearing any
`[DIRECTOR-RULING]` marker. A bridge keyed on "verified commit + marker" is therefore **forgeable** — under R15 a
control that can't fire on its own defect, worse than none — **so it was NOT built**. The genuinely non-forgeable
channel is the phone-signer HMAC (`SE_WAKE_HMAC_KEY` verified absent from the worker env, only referenced never
valued in-tree, in `MODEL_FACING_FORBIDDEN_SECRETS`). **Your contingency stands: the phone-signer setup is urgent**
— a console act per BUILD_OPEN reintroduces exactly the human dependency it removes, and the verified-commit trick
cannot substitute.
