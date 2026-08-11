# [WORKER-FINDING] AO2's G6 fires on the word "nothing" anywhere in a wrapped INDEX note (2026-08-11)

**Rank:** backlog. It costs a commit round-trip, not a wedge — but it is the shape that teaches
people to write shorter, worse notes, which is the exact outcome `parse_records`' own docstring
says it was designed to avoid.
**Lane:** `H_harness` · **Class:** an unbounded field parser makes a keyword guard misfire.
**Filed from:** the OPS2 tick of 2026-08-11, per SELF-INTERRUPT DISCIPLINE — queued, not fixed
on sight. It refused a commit whose reuse record was correct.

## Observed (with evidence)

`tools/write_time_gate.py` refused:

```
• tools/sample_gate_rss_premium.py: G6 the record says the index found nothing, but "peak rss"
  and its siblings return 1 row(s): tools.sample_gate_rss_premium.
```

The record claimed no such thing. It named the returned row explicitly ("The index returns
exactly one row, tools.sample_gate_rss_premium — this module itself, self-matched because the
index reads the WORKING TREE"). What tripped the guard, located by running the predicate
directly:

```python
g._NOTHING_CLAIMED.search(record["INDEX"]).group(0)   # -> 'nothing'
# context: '... _preexec_memcap computes its limit and then `pass`es -- a memory cap that
#           caps nothing.'
```

The match is inside an aside about a *different* module, filed in passing. It has no bearing on
what the index returned.

## Why the two mechanisms combine into a false refusal

Both halves are individually reasonable, which is why this survives review:

1. `parse_records` deliberately appends every indented continuation line to *the field in
   progress*, so `INDEX:` accretes an unbounded amount of free prose. Its docstring defends this:
   *"a record refused for wrapping would just teach people to write shorter, worse notes."*
2. `_NOTHING_CLAIMED` is a bare keyword regex — `\b(none|nothing|no (existing|current|prior|
   other)|...)` — with no scoping to the clause that talks about the index.

So the guard's subject is "whatever prose happened to land in the INDEX field", not "the record's
claim about the index". Any note long enough to be useful can contain the word *nothing* about
something else. The longer and more honest the note, the likelier the misfire — the incentive
runs backwards.

**A second instance is already latent:** the same aside would trip it via `no other` or `none`
just as easily. This is a CLASS, not this one word (R10) — the repair must be to the guard's
subject, not to the alternation list.

## Suggested shape (not built — with a recommendation)

* **A. Scope the trigger to the sentence containing an index reference**, rather than the whole
  field.
* **B. Give the record an explicit field for the finding** — `FOUND: <rows>` / `FOUND: none` —
  and run G6 against *that*, leaving `INDEX:` free prose. The claim becomes structured instead
  of inferred from keywords.
* **C. Have G6 skip the check when the record names the row the live index returns** — cheap,
  and it is the case that misfired here.

**Recommendation: B.** A and C both keep a keyword regex as the arbiter of a factual claim, so
they narrow this instance without closing the class; B moves the claim out of prose entirely and
makes the guard's subject the thing it is named for. C is worth taking *as well* if B is not
drawn soon, because it is small and it closes the observed case.

## Workaround used this tick

The aside was moved out of the `INDEX:` field into the commit body, where it belonged anyway.
That is a workaround, not a fix: it depends on the author knowing the trigger word.

## Related

* `docs/design/WRITE_TIME_GATE.md` — the record format and the guard table (G1–G6).
* `feedback_unbounded_field_parser_makes_guards_misfire` — the same class, previously seen.
* `feedback_control_keyed_to_one_syntactic_form`.
