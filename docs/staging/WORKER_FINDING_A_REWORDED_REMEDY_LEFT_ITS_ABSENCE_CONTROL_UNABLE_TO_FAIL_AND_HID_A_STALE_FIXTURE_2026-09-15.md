# A reworded remedy clause left its absence-control unable to fail, and that hid a stale fixture

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — H_harness control repair

**DISCHARGED 2026-09-15** by the commit carrying this line, which lands both halves of the repair
together exactly as §"The repair, and its evidence" requires. Nothing below is revised: the
finding was right, including the warning not to land the assertion without the fixture. What the
discharge adds is the measurement the finding predicted but had not run, and one deliberate
departure from its wording — see the closing section.

**Found:** 2026-09-15, while closing the 2026-09-11 origin fork (`0191f92f5`, and the merge that
follows it). Not fixed in that landing on purpose — it is a different defect and the fork's
commits should be readable as the fork's.

## What is wrong

`tools/generate_value_arms_data.MORE_SEEDS_WOULD_NOT` was reworded on this side of the fork. It
used to read:

> More seeds would not resolve it: re-drawing the dice measures this spread again, it does not
> shrink it.

It now reads:

> More seeds do not shrink this SPREAD: re-drawing the dice measures the same width again. What
> they do buy is how well those draws pin their own MEAN, which is the quantity this page states a
> side from — the error bar below prices how many the family on disk would need.

That rewording is a real improvement: it separates what more seeds do to a spread from what they
do to that spread's mean, which is the quantity the page actually states a side from.

`tests/tools/test_generate_value_arms_data.py::test_a_resolved_contrast_names_no_remedy_at_all`
still asserts:

```python
assert "More seeds would not resolve it" not in headline, headline
```

**That literal is a string this producer can no longer emit.** The assertion is satisfied by every
possible composer, including one that prints the remedy clause unconditionally — which is exactly
the failure the test's own docstring says it exists to prevent ("it would make the control above
satisfiable by a composer that prints the clause unconditionally").

## The second defect, which the first was hiding

Key the assertion to the constant instead of the literal — `gva.MORE_SEEDS_WOULD_NOT not in
headline` — and it fires immediately. What it catches is not the producer. It is the fixture:

```python
headline = gva.build(art, _floor_with_spread(100.0),
                     _decomposition(0.85, resolvable=True))["headline"]
```

`_floor_with_spread`'s `selection_mean` defaults to `0.0`, so the selection family is centred on
zero: the leg sits 0.0 standard errors from zero, the page withholds it, and the remedy clause the
test forbids is **correctly** printed. The test is named for a state — every contrast resolved —
that its own fixture does not reach. Both legs are set to £50,000 in the artefact, but only one of
them is put outside its floor.

This is the exact mirror of the defect `_withheld_headline` fixed on 2026-09-04, recorded in that
helper's own docstring: *"BOTH LEGS ARE PUT INSIDE THE FLOOR, AND UNTIL 2026-09-04 ONLY ONE WAS."*
Here both legs must be OUTSIDE, and only one is.

## Why nothing noticed

The two defects protected each other. The stale fixture could not be caught while the assertion
was pinned to a string the producer had stopped emitting, and the dead assertion looked alive
because it sat in a test whose name and docstring describe a control that does work. A green
beside a red from the same cause is a suspect; here there was no red at all.

## The repair, and its evidence

One line, plus the fixture:

```python
headline = gva.build(art, _floor_with_spread(100.0, 50_000.0),
                     _decomposition(0.85, resolvable=True))["headline"]
assert "larger SETTLED BOOK" not in headline, headline
assert gva.MORE_SEEDS_WOULD_NOT not in headline, ...
```

`_floor_with_spread` already takes `selection_mean` — the parameter exists for precisely this, and
`_withheld_headline` already uses it. **Do not land the assertion change without the fixture
change**: keyed to the constant against today's fixture the control is red, and it is red for the
fixture's reason and not the producer's.

The positive twin of this control — `assert "More seeds would not resolve it" in empty`, in
`test_a_remedy_whose_OTHER_HALF_IS_EMPTY_is_refused_and_not_rounded_to_zero_percent` — had the
same literal and WAS caught, because the rewording made it go red rather than silently true. It is
keyed to `gva.MORE_SEEDS_WOULD_NOT` as part of the fork merge. That is the whole asymmetry worth
keeping: **the positive form of a word-keyed assertion announces a rewording; the negative form
swallows it.** Any `assert "<producer's words>" not in <surface>` in this repo is a candidate for
the same audit.

## What is NOT claimed

That the producer is wrong. On the run the fork publishes, the remedy clause is printed beside a
leg that genuinely was withheld, which is correct. Nothing on the live page is misleading because
of this. The cost is a control that cannot fail and a fixture that does not reach its own state —
both of which will be load-bearing the next time the composer's remedy logic is changed.

---

## The discharge (2026-09-15)

Every measurement below was taken in a clean `git archive HEAD` extract at `760637dd7`, because
the shared tree **cannot import the producer at all**: its working copy of
`tools/demand_vector_coverage.py` drops `groups=None` from `fit_weights`, so
`import tools.generate_value_arms_data` raises `TypeError: fit_weights() got an unexpected keyword
argument 'groups'` through `simulation/run_phase2b.py`'s module-level `live_population()`. That is
the sibling BLOCKING finding, and it is why this repair landed by `surgical_land --content` rather
than by pathspec.

### The four cells, which are the whole claim

|                        | HEAD's producer | MUTANT: `if withheld_contrasts else ""` dropped from the headline composer |
|---|---|---|
| **HEAD's control** (string-pinned) | pass | **pass** — this is what "unable to fail" means |
| **repaired control** | pass | **fail** |

The mutant is the exact composer this test's own docstring says it exists to catch: one that prints
the clause unconditionally. The version that stood until today passed it.

### The fixture's red is the fixture's, and it was read before it was fixed

Keyed to the constant against the *unrepaired* fixture, the assertion reds, and the message names
the fixture's reason and not the producer's — verbatim from the run:

> ... that mean sits **0.0 standard errors from zero** against the ±£58 standard error those same 3
> pin it to, short of the 4.30 this page requires before stating a side. So this book CANNOT
> RESOLVE whether the per-customer choosing is worth anything at all ...

The finding's instruction — *do not land the assertion change without the fixture change* — was
therefore not taken on trust: the intermediate state was built and its red read.

### One deliberate departure from this finding's wording

The finding proposes `gva.MORE_SEEDS_WOULD_NOT not in headline`. The landed assertion keys to
**`_ARITHMETIC_REMEDY`**, which this test file already defines as
`MORE_SEEDS_WOULD_NOT.split(":")[0]` — the leading clause — for the reason written where that name
is defined: *"The leading clause is taken because the rest of the sentence is prose that may be
rewritten again."* Keying the negative form to the whole sentence would re-arm this finding's own
trap the next time the tail moves, which is the one thing this repair must not do. The shorter
substring is also the strictly stronger absence claim.

### The rest of the file

`pytest tests/tools/test_generate_value_arms_data.py` in that extract: **200 passed, 4 failed**.
All four failures reproduce identically with HEAD's unmodified test file — one variable moved, so
none of them is this repair. They are the extract's own harness:
`test_every_input_to_the_published_supplier_claim_IS_IN_THE_PUBLISH_SURFACE` and
`test_the_published_supplier_claim_answers_THE_SAME_from_HEADs_committed_bytes` shell out to
`git ls-files` / `git show HEAD:` with `cwd=PROJECT`, and a `git archive` extract has no `.git`, so
they fail closed there. The other two read trees the extract cannot reach and report `None`.

### The audit this leaves open, and does not claim

The closing asymmetry — *the positive form of a word-keyed assertion announces a rewording, the
negative form swallows it* — is now in the repaired test's docstring where the next reader of that
control will meet it. Sweeping the repo for every other `assert "<producer's words>" not in
<surface>` is **not** done here. It is the next piece of this thread and it belongs to H_harness
with the rest.
