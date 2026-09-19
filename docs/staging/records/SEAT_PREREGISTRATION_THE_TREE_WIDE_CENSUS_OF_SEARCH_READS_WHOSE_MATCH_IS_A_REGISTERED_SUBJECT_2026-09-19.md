**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
"search-read matches that are downstream subjects are uncensused"

# Pre-registration: what the tree-wide census of `.search()` reads will find, written before it was run

**Delivery seat, 2026-09-19, claim
`search-read-matches-that-are-downstream-subjects-are-uncensused`. Written BEFORE the instrument
was run, so it can refute me.**

---

## 1. The premise, re-measured before any work

The drawn item's premise check flagged that both commits it cites — `087e3ad58` and `c35593d24` —
are already ancestors of `origin/main`. **That does not spend the premise.** Those two commits are
the item's PRIOR ART, not its deliverable: `087e3ad58` repaired the here-relative census and
`c35593d24` repaired the two refusal-claim readers, and each of those commit messages named the
remaining instances as *known*, not as *enumerated*. The item exists precisely because the claim
"those were the last" rests on nobody having looked. Re-measured at `origin/main` `406276afc`:

```
$ git grep -c "\.search(" -- '*.py' | <sum>
397 call sites
```

397 sites, no census over them. The premise is live.

The duplicate-work check named one other live claim,
`search-read-matches-that-are-downstream-subjects-are-uncensused` — which is **this item's own
id**, held under this very draw in `docs/observability/.seat_work_in_hand.json` (`paths: []`,
nothing bound). Not a rival. The work is done, not disposed.

## 2. Why the count cannot be inferred from the tests

This is the whole reason the class needs a census rather than a test run. A `.search()` where
`.finditer()` was needed drops the second match. A dropped match is **an absent question, not a
wrong answer** — so:

- no assertion downstream fires, because nothing was ever handed the subject to judge;
- no mutation of the read fires either, as long as every real input states exactly one claim
  (measured at `087e3ad58`: reverting the widened vocabulary to `search()` left all 31 rungs
  green);
- the green therefore means "no input this week stated two", not "the read is right".

Instance count is not observable from red tests. It has to be enumerated.

## 3. The discriminator, stated before the instrument was pointed at anything

Not every `.search()` is a defect, and most are not. The split is **what the match becomes**:

- **BOOLEAN** — the match is consumed as a truth value (`if pat.search(s):`, `not`, `any(...)`,
  `bool(...)`, `is None`). A narrow read answers *"does this string contain one at all"*
  correctly, and a second match cannot change that answer. **Not the class**, however many
  matches the string holds.
- **REGISTERED** — the match, or a group of it, is bound to a name, appended, stored in a
  dict/set, returned or yielded. It travels onward as the SUBJECT of something downstream. A
  second match is dropped in silence. **Candidate.**

Registration alone is still not the defect: many registered reads are single-claim by
construction — a version line, a filename, a one-capture format where a second match is
impossible rather than unasked. The real instances are the registered reads over strings that
**can** state two.

## 4. The predictions

Written now. Whatever the instrument says, these stand beside it uncorrected.

- **P1.** Of the 397 sites, between 40% and 60% are BOOLEAN. *(The `if pat.search(x):` guard is
  the commonest shape in this tree.)*
- **P2.** REGISTERED sites number between 150 and 240.
- **P3.** Of those, the count of **real** instances — registered, over a string that can plausibly
  state two claims, feeding a downstream judgement — is **small: point prediction 5, interval
  3–10.** If it comes back above 10 I was wrong about how rare the shape is and the remedy is a
  standing control, not a set of repairs. If it comes back 0 the two hand-found instances were the
  population and the item is closed by the census rather than by a fix.
- **P4.** At least one lives under `tools/` — it has the largest cluster (44 files) and the
  generators are where prose gets parsed.
- **P5.** At least one lives in something census- or registry-shaped (a function that builds rows
  for other rungs to judge), because that is the shape both known instances had.
- **P6.** The three known instances (`site/test_a_producers_here_relative_pointer_has_one_home.py`
  vocabulary, and the two in `tests/architecture/test_switching_rate_commons.py`) will NOT appear:
  all three are already repaired to `finditer`. If any appears, a repair regressed.

## 5. What done means

No exit test is written for this item, so: **done is the enumeration existing and every real
instance it names either repaired or filed with its reason.** A census that finds nothing is a
result; a census that finds five and repairs two is a landed increment plus a named remainder. It
is NOT done by finding instances and leaving them unstated.

The instrument is AST-based, not a grep: the boolean/registered split is syntactic and a regex
over source lines cannot see it.
