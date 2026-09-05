**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** measurements_that_mirror

# FINDING — the per-line claim was false on the one carrier whose reader also writes

**RECORDED, not BLOCKING: both defects were repaired in the commit that files this, with
mutation-proven controls, and all five disposition rows were corrected in the same commit. What
was found was HIGH — one torn line in `site/state/live_decisions_log.jsonl` permanently stopped the
public track record from ever growing again, and separately blanked the published scorecard built
from it. Both are fixed. The class matters more than the instance: five census rows asserted a
property from one sibling's behaviour, and the assertion was wrong on the only carrier where a
reader is also on the write path.

**Filed 2026-09-05. Pre-registration:**
`SEAT_PREREGISTRATION_THE_FOUR_JSONL_READERS_GRADED_FROM_A_SIBLING_2026-09-05.md`, written before
any reader was opened.

---

## What was claimed

`docs/design/self_clearing_alarm_dispositions.json` carried, on five JSONL carriers, a `loader`
field saying the whole-file corruption partition does not apply **because the readers parse per
line** — "a corrupt line costs one entry, never the file". Verified for one reader,
`notification_digest._read_queue`. The other four rows said *same as above*.

## What is actually there

Every reader of all five paths, opened and classified. **T** = per-line tolerant, **L** = one bad
line raises out of the reader, **O** = open not guarded by `except OSError`.

| Carrier | Reader | Class | Note |
|---|---|---|---|
| `ntfy_digest_queue.jsonl` | `notification_digest._read_queue` | T | the one that was verified |
| `publish_gate_duration.jsonl` | `suite_duration_watch.read_series` | T | also `isinstance(rec, dict)` — the strongest here |
| | `settlement_ceiling_probe` (`:305`) | T + **O** | operator-run probe; raise is visible |
| `gate_authorizations.jsonl` | `gate_authorization.read_ledger` | T | |
| | `level_promotion_gate` | T | via `read_ledger` |
| | `delivery_seat` (inline walk) | T | |
| | `discovery_pass_ceiling._level_moves` | T, open fails **closed** | OSError → `CeilingUnavailable` |
| | `harness_exit_criterion._read_ledger_strict` | **L, by design** | raises on any unparseable line, with a docstring saying an empty read would be the fail-open |
| | `map_assertion_provenance._verified_at` | T + **O** | publish-time generator |
| | `generate_evidence_data.ledger_by_atom` | T + **O** | via `_require` |
| `live_decisions_log.jsonl` | `generate_track_record_scorecard._load_log` | **L** + O | **defect** |
| | `run_live_decisions.append_decision_log` | **L** + O | **defect, on the write path** |
| `decisions.jsonl` | `direction.read_decisions` | T | the only carrier with genuinely one reader |

## The defect

`append_decision_log` builds its once-per-day idempotency set with an unguarded
`json.loads(line)["decision_run_at"][:10]`. Run against a log with one half-written row:

```
--- append_decision_log with one torn line:
RAISED JSONDecodeError Unterminated string starting at: line 1 column 21 (char 20)
lines after: 2          <- the new decision never reached the file
--- _load_log with one torn line:
RAISED JSONDecodeError
--- _load_log with a bare-scalar line:
RAISED AttributeError 'str' object has no attribute 'get'
```

The bad line **stays on disk**, so every later call raises too. A corrupt line did not cost one
entry; it cost every entry the log would ever have received, on the *write* path — the precise
inverse of the claim. The file is appended to from the publish cycle, which is killed on a
deadline, so a torn write is the realistic corruption, not a hypothetical one.

The second reader is what publishes the record: `_load_log` feeds
`site/state/track_record_scorecard.json`, folded onto the public Method page. Its raise is
swallowed by `process_run_complete`'s `except Exception` and logged as *"Track record scorecard
generation failed"* — so the entire predicted-vs-realised record leaves the site, from one byte,
with no reader able to tell that from having nothing to show.

## The fix

**CORRECTED 2026-09-05, beside the claim it got wrong.** This section originally read *"Both readers
skip a bad line and keep going. Skipping is right here and is not fail-open"*, and argued that a
dropped line "at worst permits a second row for one day". That argument was wrong about the
appender, and a concurrent lane repairing the same defect reached the opposite answer independently
— which is how it was caught, at the merge. **The two readers need OPPOSITE repairs.**

The scorecard is a pure READER and skips: a bad line costs one entry. Because it is a published
surface the skip is **stated, not silent** — an `unreadable_log_lines` field rides on the artefact.
Zero is the normal answer, and it must be a real zero rather than an absent field, so a reader can
tell a clean log from an unasked question.

The appender is a WRITER and **refuses**, naming its reason on stderr. The "at worst one duplicate"
concession was the whole defect: a torn line is a write killed mid-flight, so the likeliest torn
line is *today's own row*. Skipping it drops today out of `existing_dates`, the guard reports "not
logged yet", and a re-run appends a second row for the same day — the exact duplicate the
one-entry-per-day rule exists to forbid, and `generate_track_record_scorecard` grades both. So the
bad case is the LIKELY one, not the tail. Nothing is lost by refusing: `live_decisions_<date>.json`
and `live_decisions_latest.json` are already on disk before the append is attempted. The integrity
of a published track record beats its continuity — a record that stopped growing behind a named,
greppable refusal is honest; one that quietly gained a second row for a day is not.

`tests/tools/test_the_jsonl_carriers_torn_line_partition.py` — 9 controls, all mutation-proven
(7 mutants killed, including *guard too wide*, *guard only the parse and not the subscript*, and
*publish the count but always as 0*).

## What did NOT change, and why

- **The `benign` verdict on all five rows.** The episode question is answered by the writer, and
  every writer here opens `'a'`. The `loader` field was the wrong thing, not the verdict.
- **`harness_exit_criterion._read_ledger_strict` stays line-fatal.** It is right: an empty read
  there would present as "no advances, no problem".
- **The three `O` readers** (`settlement_ceiling_probe`, `map_assertion_provenance`,
  `generate_evidence_data`) are named and left. All three are generators or operator-run tools
  whose callers already treat a raise as an unavailable source; the raise is loud, not silent.
  Guarding them by reflex is what the dispositions file's own `_scope_of_benign` forbids.
- **`_read_queue`'s one hole** — a line that is valid JSON but not an object reaches
  `defer()`'s `entries[-1].get("seq", ...)` and raises AttributeError — is named in its row and
  deliberately not guarded: no writer in that module can produce such a line, and the realistic
  corruption yields an *incomplete* line, which the existing `JSONDecodeError` arm already handles.

## The predictions, kept beside the answers

1. *The reader set is larger than one per carrier* — **held for three of four** (7, 2, 2), and
   **refuted for `decisions.jsonl`**, which genuinely has one reader. The disposition rows said
   "the reader" about a path with seven of them.
2. *At least one reader is line-fatal or whole-file* — **held**, and worse than predicted: two
   unintentional ones on the same carrier, plus one deliberate.
3. *More readers are `O` than are `L`* — **held**, 5 to 2.
4. *None of this moves the `benign` verdict* — **held**.

## The generalisation

A row graded from a sibling is a row nobody opened. The sweep's own rule was that a row with no
answer is a gap and not a pass; a row with an **inherited** answer is worse, because it reads as
asked-and-answered and nothing will ever ask it again. The four rows had been wrong for as long as
they had existed, and the census that produced them was green throughout.

The discriminating question, had anyone asked it: **does any reader of this path also write to
it?** That is the one place where "a corrupt line costs one entry" stops being a statement about a
lost entry and becomes a statement about a dead file — and it was true of exactly one of the five.
