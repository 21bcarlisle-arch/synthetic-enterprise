# WORKER FINDING — a mutation that patches both sides of the seam it tests proves nothing

**Severity:** LATENT · **Lane:** H_harness

**Filed** 2026-08-12, from the H27 Expert Hour #21 landing (atom D37, `H27_payment_belief_gap`).
**Class** control-that-cannot-fail (R15), fail-silent sub-class — a mutation whose subject is
neutralised on BOTH sides of the seam, so the control it certifies is never exercised.
**Rank requested** backlog. Nothing published rests on either instance.

## The class

A seam control asks: *does A still hand its result to B?* The mutation must break the crossing
while leaving both ends alive. Two ways to get this wrong, and this Hour hit one of each:

1. **Patch the name the observer itself uses.** If the spy and the mutation reach the seam
   through the *same* binding, the spy wraps the mutation and still records a crossing.
2. **Patch a shared upstream that both the producer and the checker read.** Both sides then move
   together, they agree, and the divergence the control looks for cannot arise.

In both shapes every assertion in the test file can be green while the control is inert.

## Instance 1 — observed-with-evidence, FIXED in the Hour #21 landing

`tests/tools/test_couple_w2_11_d5.py::test_a_composer_that_stops_crossing_the_ledger_seam_fails_the_walk`
(as first written) did:

    monkeypatch.setattr(lpt, "write_gap_entry", lambda *a, **k: None)

`write_gap_entry` is a module **global** of `background/live_payment_triad.py` (imported at line
104, called at line 803), and `tools/couple_w2_11_d5.py::_publish_one_book` spies the seam by
replacing *that same attribute* with a wrapper around whatever it currently holds. So the spy
wrapped the neutralising lambda, `captured` still received exactly one crossing, the provenance
check passed — and the run died on `FileNotFoundError` reading a ledger the no-op never wrote.
The test was green-by-raise for the wrong reason: it asserted `pytest.raises(AssertionError)` and
got one only because the *unrelated* read failed.

**Fixed on landing** by mutating the call site instead of the attribute: the composer routes the
write around the spied name (through the test module's own import-time binding to the same
function), so the ledger is still written, the seam genuinely is not crossed, and the named
refusal fires. Evidence: the test now passes on the named message
(`handed 0 result(s) to the ledger writer`), and the full atom suite is 440 passed.

## Instance 2 — observed-with-evidence, NOT fixed (this is the queued half)

`tests/tools/test_couple_w2_11_d5.py::test_a_composer_that_stops_carrying_a_renderers_string_fires`
(Hour #20, atom D36) patches `background.gap_metric.format_ageing_summary` and then asserts the
composed note diverges from the walk's renderer output.

That divergence only exists if the note was composed **before** the patch. The note comes from
`pair._PUBLISHED_BOOKS`, a module-level cache. In a full-file run an earlier test has already
populated it with notes composed by the real renderer, so the mutation moves only the walk's
side and the control fires correctly. Run **alone**, the cache is empty, the books are composed
*after* the patch, both sides use the mutated renderer, they agree, and the control reports no
divergence:

    $ pytest "tests/tools/...::test_a_composer_that_stops_carrying_a_renderers_string_fires"
    assert measured["ageing"]["renderer_in_note"] is False
    E   assert True is False
    1 failed in 3.30s

**It fails rather than passes**, so it is loud, not fail-open — the reason this is LATENT and not
BLOCKING. But when run alone its subject is not the seam it names, and a control whose subject
depends on which siblings ran before it is not a control of that seam.

**Proven pre-existing**, not an Hour #21 regression: the same single-test run fails identically
at committed HEAD (`43a456cba`) in a detached `git worktree`, where none of Hour #21's changes to
`measure_reader_render_sites` exist.

## Recommendation — not asking, this is what the next draw here should do

1. Make the control's subject independent of sibling ordering: have the test seed
   `_PUBLISHED_BOOKS` with books composed by the **real** renderer explicitly, then patch, then
   walk. The cache dependency becomes part of the fixture rather than part of the luck.
2. **Then** sweep the class rather than the instance (R10). The question for every seam control
   in this atom, and in `background/gap_metric.py`'s callers, is: *does my mutation reach the
   seam through a name the observer also uses, or through a shared upstream the producer also
   reads?* Both answers make the control inert.
3. Do not widen the mutation until (1) lands — a mutation whose reachability rests on test order
   is exactly what this finding is about, and adding more of them is the treadmill.

## What this finding is NOT

No published gap value, epsilon or declared precision depends on either control, and both D36/D37
instruments measure what they say when run as a file. The claim is narrower than either of those:
it is about two mutations' **reachability**, which is the only evidence R15 accepts that a control
can fail at all.
