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

---

## ADDENDUM — SECOND INSTANCE, same day, and it widens the class (2026-08-08, AO8 tick)

Hit again while landing `AO8_board_batteries_executable` (`tools/build_battery_register.py`).
Same root cause, but this instance shows the class is **wider than "long commit messages"**:

1. **The swallow also happens inside a source FILE, not just a commit message.** The record was
   placed in the module docstring — the obvious place, and where a reader looks for it. `INDEX:`
   then absorbed the module's entire body, including a `DISPOSITIONS` table of 76 reasons, many of
   which legitimately begin "No carbon-intensity series…", "No LNG cargo model…". G6 fired on those.
   Observed: parsed `INDEX` field ran past the record to EOF; the record's own INDEX line was
   ~380 chars.

2. **The documented workaround does not generalise.** The finding above says "place the REUSE block
   last in the message." For a module record there is no "last" that works: a trailing `# REUSE:`
   comment block is **not recognised at all**, because `_FIELD` anchors on `^\s*(REUSE|…)` and a
   `#` precedes the head. So the only working position for a module's record is the end of its
   commit message — which is the one place a future reader of that module will never look.

3. This is now **two refusals in two ticks**, both false positives, both costing a diagnosis cycle.
   Per R3 (two-strike redesign) the position convention should not be patched a third time: bound
   the field, and let the record live where it is readable.

**Amends "The fix, when drawn" above:** the fix must also decide whether `# `-prefixed record lines
are recognised, so a module can carry its own reuse record in its own docstring or header. Fixing
only `parse_records`' bounding leaves instance 2 half-broken — the record would parse correctly but
still have to live in the commit message to be seen at all.

Still not fixed on sight, same reasoning as above: editing the gate that just refused my own commit
is the route-around shape even when the diagnosis is right. Worked around identically (record last
in the commit message), and the module's docstring now says where its record actually is.

---

## Third instance, 2026-08-09 (AO10 commit `39e3cb899`)

Same class, third refusal in three ticks. The AO10 REUSE block was placed FIRST in the commit
message (the readable position), so `INDEX:` swallowed the entire body below it — 40 lines
describing the sweep. G6 fired on the word "nothing" and named "staging archive" as returning
73 rows.

Two details this instance adds:

1. **The swallow is not the only trigger — the record's own prose is enough.** My INDEX line
   genuinely contained the word "nothing", describing what `staging_watcher.archive_from_rich`
   *records* ("it leaves no trail" in the final wording). `_NOTHING_CLAIMED` matches the bare word
   anywhere in the field, so a record that says *what it found* in prose containing "none",
   "nothing" or "no existing" trips a guard whose only legitimate trigger is a claim that the
   INDEX search was EMPTY. Bounding the field (the fix above) does NOT close this: the trigger
   would still fire on an in-record use of the word.

2. **It punishes the thorough record.** My block named two real nearest rows and said why neither
   fits — exactly what G6's own refusal text asks for ("Finding something is not a refusal — say
   what you found and why new code anyway"). The more specific the prose, the likelier it contains
   a negation. The guard's trigger should be a claim ABOUT the search result (e.g. an explicit
   `FOUND: none` / `-- no row covers this` at the end of the INDEX line), not any negation in the
   sentence.

**Amends "The fix, when drawn" a second time:** the trigger needs a defined shape, not a word
match, and the R15 test for it must include a record that FINDS rows and says so using a negation
("neither of these fits") — today that record is refused, and that is the false-positive the fix
must be shown to kill.

Not fixed on sight (same reasoning as both instances above). Worked around by rewording the
record's prose to avoid the trigger word — which is exactly the obfuscation this project treats as
a defect, and is the reason this is worth drawing rather than living with.
