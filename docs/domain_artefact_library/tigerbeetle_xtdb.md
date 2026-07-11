# TigerBeetle & XTDB — double-entry ledger + bitemporal database design patterns

**Purpose:** validate `company/interfaces/bitemporal_event_log.py` / `point_in_time_view.py`
(built 2026-07-10, Epoch-2 bounded start) against established external design patterns for
the same problem class, not to adopt either as a runtime dependency.

## Sources (R9)

- **TigerBeetle — Safety**, https://docs.tigerbeetle.com/concepts/safety/ (no version/date
  shown on page; active-development main branch).
- **TigerBeetle — Correcting Transfers recipe**,
  https://docs.tigerbeetle.com/coding/recipes/correcting-transfers/ (no version/date shown).
- **XTDB — Time in XTDB**, https://docs.xtdb.com/about/time-in-xtdb.html (current v2 docs,
  SQL:2011-based; no version/date shown on page).
- **XTDB v1 Bitemporality** (terminology history), https://v1-docs.xtdb.com/concepts/bitemporality/.

## TigerBeetle's double-entry design

Accounts and transfers, one invariant ("every debit has an equal and opposite credit").
**Transfers are immutable by design — cannot be modified after creation.** Corrections are
never a restatement of the original: always a new offsetting "correcting transfer",
conventionally tagged via `Transfer.code` (a reason code) and linked to the original via a
shared `user_data_128` id. Rationale, in the doc's own words: "adding transfers as opposed to
deleting or modifying incorrect ones adds more information to the history" — the log keeps
the original error, when it happened, and the correction, when *that* happened.

## XTDB's bitemporal model vs. this project's naming

XTDB v2 uses **"system time"** as its primary term (synonyms: transaction/processing time)
and **"valid time"** for the domain-time axis — SQL:2011 syntax: `FOR VALID_TIME AS OF <date>`
/ `FOR SYSTEM_TIME AS OF <date>`. XTDB v1 (and the wider Fowler/Snodgrass literature) used
**"transaction time"** as the primary term, matching this project's own `transaction_time`
field name exactly. `valid_time` matches XTDB verbatim on both versions.

## Direct assessment: does the built design line up?

**Yes, closely — no naming confusion for a reader familiar with the pattern.** `valid_time`
matches XTDB verbatim on both versions; `transaction_time` matches XTDB v1 / the classic
academic term precisely (XTDB v2 now prefers "system time" as a synonym, but "transaction
time" remains a recognised, cited equivalent — worth a one-line cross-reference for a reader
coming fresh from XTDB v2's own docs). `as_known_at(decision_time, ...)` is structurally
identical to `FOR SYSTEM_TIME AS OF <date>` — same query shape (bound by the recording axis,
return the domain-time view as of that point).

One real, minor gap: XTDB supports a `BETWEEN`/`ALL` range query over either axis; this
project's `BitemporalEventLog` only exposes point-in-time `as_known_at` +
`history_as_known_at`, not an explicit time-range scan. Not a correctness issue — nothing in
this project's current callers needs a range query yet.

## Adopt/adapt/skip verdicts

- **TigerBeetle's append-only correction-via-offsetting-entry pattern: ADOPT (already
  followed).** `bitemporal_event_log.py`'s own docstring ("a restatement is a NEW record with
  a later transaction_time... never an edit to the old one") is the same discipline
  TigerBeetle enforces at the database-engine level. No code change needed — cite as external
  validation. Consider adopting TigerBeetle's specific convention of a general reason-code
  field on the new record; `BitemporalRecord.superseded_by_run` already partially does this
  (names *which settlement run* superseded it, though not a general reason-code enum).
- **XTDB's terminology/query shape: ADOPT (already followed), ADAPT one gap.** Terminology
  correctly aligned; optionally add a `history_between(valid_time_start, valid_time_end,
  decision_time)` range method later if a caller ever needs one — not urgent, registered as a
  backlog nicety, not a gap.

## Provenance tag

**`validator-anchor`** — this research validates the correctness/alignment of an
already-built company-side mechanism against established external design patterns; it does
not shape SIM generation, so per the mutual-exclusivity rule it must NOT also carry
`generator-anchor`. `company-knowable` does not apply — internal engineering design
reference, not a real-world fact a UK supplier could observe.

## Licence note

Design/terminology only, no code borrowed. TigerBeetle is Apache-2.0; XTDB is MPL-2.0 (both
checked from their public repos' own licence files at time of writing — not independently
re-verified here beyond a general web-knowledge check, flag if a licence-sensitive decision
ever depends on the exact current terms).
