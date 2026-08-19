**Severity:** BLOCKING · **Lane:** H_harness
**Discharged:** `tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py::test_no_declared_honest_store_also_claims_the_same_citation`,
`tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py::test_MUTATION_the_word_only_predicate_fires_this_contradiction_on_the_real_corpus` — 2026-08-19: the lexicon miss is repaired by NOTATION (a symbol disclaim pattern; claims 231 to 229 against a floor of 90) and the CLASS is held by a control keyed on a register the verdict never consults, proven to fire by re-running the real 354-store corpus under the pre-fix predicate. §6 records the full discharge.

# A record says the same true thing four times; the lexicon reads it as honest when spelled `UNTRACKED` and as an over-claim when abbreviated to `` `??` `` — and the control has been red at HEAD since 2026-08-18

**Found:** 2026-08-19, worker tick, H27 Expert Hour #39, while running the three sibling controls
after landing this atom's own uncommitted code.
**Class:** `controls_that_cannot_fail` (the born-red direction).
**Measured at:** HEAD `459d41aea`, reading the index. §1 and §2 are `observed-with-evidence` (R9);
§4 is inferred and labelled.
**Intended rank (P-1):** top of the H_harness BLOCKING band — a control red at HEAD for a record
that is telling the truth is the shape that gets a control switched off.
**QUEUED, not fixed on sight** (SELF-INTERRUPT DISCIPLINE): the tick that found it was landing a
different repair in a different atom, and EP1 is not this tick's lane.

---

## 1. The red, and it is not mine

`tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py::test_no_committed_store_credits_a_falsifier_the_repository_does_not_have`
fails at HEAD:

    tests/saas/test_clv_margin_basis.py           (on disk here only)
        credited as BUILT by: docs/design/simplifications/EP1_clv_three_horizon.yaml
    tests/tools/test_derived_basis_parentage_gate.py  (on disk here only)
        credited as BUILT by: docs/design/simplifications/EP1_clv_three_horizon.yaml

Both files are on disk and `git log --all` is empty on each — so the *absence* is real. What is
false is the verdict's premise that EP1 is **claiming** them.

## 2. The mechanism: one sentence, two spellings, opposite verdicts

Read through the control's own `_clauses` / `_DISCLAIMS`, EP1's committed store says the same fact
eight times. Four are silenced and four are judged, and the only difference is vocabulary:

| clause, verbatim | verdict |
|---|---|
| ``` `tests/saas/test_clv_margin_basis.py` and `tests/tools/test_derived_basis_parentage_gate.py` are UNTRACKED (`??`). ``` | DISCLAIMED |
| ``` ... test_clv_margin_basis.py  UNTRACKED (`??`)  ... test_derived_basis_parentage_gate.py  UNTRACKED (`??`)  The finding is still live in the staging root, undischarged. ``` | DISCLAIMED |
| ``` `tests/saas/test_clv_margin_basis.py` and `tests/tools/test_derived_basis_parentage_gate.py` still `??`. ``` | **AFFIRMATIVE** |

`_DISCLAIMS` carries `untracked`, `uncommitted`, `on disk`, `no commit` — a **word** list. It has
no entry for `??`, the git porcelain code for the identical statement. EP1's later passes
abbreviated, and the record's honesty is now a function of how verbosely its author restated a fact
they had already stated correctly three times.

## 3. When it went red, and why nobody saw it

`git log -S 'still `??`'` names **`b6148d907`** ("EP1 DISCOVER/FRAME pass 8", 2026-08-18). The
store half of this control landed the same day, with EP1's two paths declared in
`_DECLARED_HONEST_ABSENCE` — correctly, because at that moment the clause still said `UNTRACKED`.
Pass 8 then rewrote the clause into the abbreviated form, which moved the tokens from `silenced`
to `claims`, and the declaration in `_DECLARED_HONEST_ABSENCE` no longer covers them (it is only
consulted for *silenced* mentions). The atom never touched the control; it re-worded a note.

## 4. Why this is BLOCKING and not LATENT (inferred)

The sibling control's own docstring states the design premise it is now violating: *"A control born
red is a control someone disables."* It has been red for ~24h against a record that is accurate,
and the pressure that creates is to widen `_DECLARED_HONEST_ABSENCE` — which would silence a real
mention by name and leave the mechanism broken for the next abbreviation. The population is
unmeasured: I did not count how many other stores spell an absence in porcelain rather than prose,
and the count is not asserted here precisely because it has not been.

## 5. Recommendation, recorded not asked (`NEVER_ASK_WITHOUT_RECOMMENDING`)

1. **Do not add these two to `_DECLARED_HONEST_ABSENCE`.** That register exists for mentions the
   lexicon *did* silence; using it to paper over a lexicon miss inverts what it means, and the
   entry would be indistinguishable from a genuine declaration.
2. **Widen `_DISCLAIMS` by SYMBOL, then measure.** Add the porcelain codes a record actually uses
   for "not in the index" — `` `??` ``, `` `!!` `` — and re-run the census. The store half's own
   floors (`_MIN_CLAIMS = 90`) are the guard against that widening going too far: if adding two
   two-character tokens collapses the affirmative-claim count, the lexicon has swallowed the corpus
   and the change is wrong.
3. **Then ask the R10 question, because an instance fix is not a closure here.** This is the second
   time this class has turned on a *restatement* rather than a fact (the first was the store half's
   own `tests/**/test_*.py` glob). The invariant worth extending is that a record's verdict must
   not depend on which of several equivalent spellings of the same true statement its author chose
   — which points at keying the disclaim test on the git STATE of the cited path (does any ref
   carry it) as a cross-check on the prose, rather than on prose alone.

---

## 6. DISCHARGED 2026-08-19, worker tick

All three recommendations actioned in
`tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py`. Control was
**1 failed / 17 passed** at `459d41aea`; it is **21 passed** now.

**§1 honoured — `_DECLARED_HONEST_ABSENCE` was NOT widened.** The two EP1 entries that were
already there (from 2026-08-18, when the clause still said `UNTRACKED`) are untouched and remain
live; nothing was added to any register to make the red go away.

**§2 built, and the widening is bounded by measurement, not by assertion.** `_DISCLAIMS` is a
`\b`-anchored WORD list, so `` `??` `` could never have been added to it — the porcelain code was
unreadable to that lexicon *by construction*. New `_DISCLAIMS_SYMBOL` + a `_disclaims()` predicate
that every call site now goes through. Backtick-quoted only: measured over the 354 committed
stores, `` `??` `` occurs in 4 token-bearing clauses (all EP1's) and `` `!!` `` in none; `!!` is
carried anyway as the same statement in the same notation. Effect on the corpus, measured:

    claims   231 -> 229    (floor _MIN_CLAIMS = 90)
    silenced  95 ->  95    (the tokens were already silenced by the verbose clauses)

The §2 prediction — that the fail-open floor is the guard against over-widening — held: the
lexicon moved exactly the two tokens it was aimed at and nothing else.

**§3 answered, but NOT as recommended, and the difference matters.** §3 proposed cross-checking
prose against the git STATE of the cited path. Rejected: that inverts the control's deliberate
burden of proof (docstring, "silence is a claim") and would make it born ~90% red on a
DISCOVER-heavy register — the exact shape §4 warns gets a control switched off.

A same-store/same-token *split verdict* keyed on absent paths was also rejected as **tautological**
with the verdict: any affirmative claim of an absent path already fires it, so the split adds no
independent question. Measured anyway — 44 split pairs corpus-wide, only 2 with the file absent,
both EP1's.

Built instead: `test_no_declared_honest_store_also_claims_the_same_citation`, keyed on
`_DECLARED_HONEST_ABSENCE` — a register **the verdict never consults** (it filters on
`_KNOWN_UNLANDED | _STALE_CITATION`), so it is a second differently-keyed question, not a
restatement. If a store is certified honest about a path and also claims it, either the
certification is wrong or the predicate missed a spelling. Its failure message explicitly refuses
the `_KNOWN_UNLANDED` escape and names the lexicon as the repair — so the §4 pressure now trips a
loud red instead of finding a quiet paper-over.

**R15, on the real corpus rather than a fixture.** `_read()` takes the disclaim predicate as a
PARAMETER, so `test_MUTATION_the_word_only_predicate_fires_this_contradiction_on_the_real_corpus`
re-runs the 354 committed stores under the exact pre-fix word-only predicate — the repository's
state at `b6148d907` — and asserts the class control fires, naming the EP1 clause. Paired with
`test_MUTATION_the_symbol_lexicon_does_not_silence_a_bare_credit` (three clauses that quote a path
in backticks and must stay affirmative), the widening is proven to fire in one direction and stay
quiet in the other.

**§4's population question, answered.** It was declared unmeasured and is now measured: 4 clauses,
one atom. The corpus does not otherwise spell an absence in porcelain.

Sibling halves re-run green (13 passed): `test_no_committed_discharge_cites_an_unlanded_falsifier.py`,
`site/test_the_site_lane_runs_no_untracked_control.py`.

**Not closed by this tick:** the EP1 falsifiers `tests/saas/test_clv_margin_basis.py` and
`tests/tools/test_derived_basis_parentage_gate.py` are still untracked and still owed by the
B_commercial lane. That debt is unchanged — this finding was about the control misreading an
honest record of it, not about the debt itself.
