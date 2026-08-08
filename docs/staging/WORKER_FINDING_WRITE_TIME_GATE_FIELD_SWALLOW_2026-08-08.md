# [WORKER FINDING] AO2's INDEX field has no terminator, so G6 reads the whole commit message

**Found:** 2026-08-08, worker tick, while landing AO9 (`c9ec19dcd`). Found by USING the gate, not by
auditing it — AO2 refused a real commit three times and the third refusal was wrong.

**Class:** control false-positive. Not a wall; the gate is doing its job in two of three cases.

## Observed, with evidence

`tools/write_time_gate.py::parse_records` collects a field's value by running from its `_FIELD` head
until the next `_FIELD` head. `INDEX:` is normally the last head in a `CUSTOM` record (only
`CATALOGUE` adds `LIBRARY:`, only `SUBSYSTEM` adds `EVALUATED:`/`REJECTED:`), so when the REUSE block
is placed anywhere but the end of the message, **`INDEX` swallows the entire remaining body**.

Measured on the real refusal:

```
INDEX field length: 1496          # the record's own INDEX line is ~380 chars
TRIGGER MATCH: nothing
match at 1338 -> '..."We have no record of what the reviewer saw" and "the reviewer saw
                  nothing improper" are opposite states...'
```

`claims_nothing_exists()` fired on the word "nothing" **1,200 characters past the end of the record**,
in prose about blind-review transcripts that makes no claim about the index at all. G6 then compared
that phantom emptiness claim against the live index, found 20 rows, and refused.

## Why this matters more than one awkward commit

G6 is the gate's only guard with an **independent oracle** — the one place the record is checked
against reality rather than against its own shape. It is therefore the guard most worth keeping
sharp, and the one whose false positives are most expensive: the cheap way out is to stop writing
detailed commit messages, or to flip `write_time_gate.mode` to `warn`, and both silently retire the
only check that can catch a false reuse claim.

Note the shape is also **fail-OPEN in the mirror direction**, which is the more serious half: because
`INDEX` absorbs arbitrary later text, a record whose own INDEX line honestly says "no existing row
covers this" stops triggering G6 the moment enough unrelated body follows it without the trigger
words. The guard's reach depends on prose that has nothing to do with the record.

## Not fixed on sight — deliberately

Per SELF_INTERRUPT_DISCIPLINE this is QUEUED, not patched mid-draw. Editing a gate so that my own
refused commit passes is the route-around shape even when the diagnosis is right, and the fix belongs
to AO2's owner with AO2's own R15 suite around it. Worked around in `c9ec19dcd` by placing the REUSE
block last in the message, which is legitimate (`docs/design/WRITE_TIME_GATE.md` states no position)
but is a convention nobody knows about and nothing enforces.

## The fix, when drawn

Bound the field: terminate a record's value at a blank line, or at the end of the contiguous block
the `REUSE:` head started. Then add the mutation that proves it — a record followed by body prose
containing "nothing"/"none" must NOT fire G6, and an INDEX line that itself claims emptiness against
a non-empty index still MUST. Both directions, per R15; the current suite has the second and not the
first, which is why a gate with an R15 suite still shipped this.

**Suggested atom:** `AO2a_write_time_gate_field_bounding`, lane H_harness, L0->L2, depends_on AO2,
file_scope `['tools/write_time_gate.py', 'tests/tools/test_write_time_gate.py']`.

## WORK THIS CREATES

1. Bound `parse_records` field values to the record block; keep G6's independent oracle intact.
2. Mutation-test BOTH directions (false positive from trailing prose; true positive from a real
   emptiness claim).
3. Decide whether the REUSE block's position should be enforced or freed — freed is better, since a
   position rule nobody can see is the next false refusal.
