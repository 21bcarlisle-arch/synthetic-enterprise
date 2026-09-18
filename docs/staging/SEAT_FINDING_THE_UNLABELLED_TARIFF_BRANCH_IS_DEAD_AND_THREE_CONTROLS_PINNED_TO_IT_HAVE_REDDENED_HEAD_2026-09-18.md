**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The unlabelled-tariff branch is dead, and three controls pinned to it have reddened HEAD

**Filed:** 2026-09-18 · **Claim id:**
`the-two-arms-have-never-priced-the-same-population-and-the-page-says-they-have`
**Corrects:** `92230b699`'s commit message and
`docs/staging/SEAT_RESULT_THE_ARMS_NOW_PRICE_ONE_BOOK_SIX_CONTROLS_REFUSE_THE_REPUBLISH_AND_THREE_WERE_ALREADY_RED_2026-09-18.md`

---

## The correction, first

`92230b699` says of the three red `test_the_renewal_funnel.py` legs:

> *"There is no commodity left to move them to, so the fixture has to CONSTRUCT an unlabelled
> record rather than find one."*

**That remedy is wrong and would not work.** I established the cause correctly — the gas call site
was repaired on 2026-09-16 and `resolved_tariff_type` has had one answer since — and then wrote a
remedy that assumes an unlabelled record is still constructible through it. It is not. Read the
whole function body rather than its docstring:

```python
def resolved_tariff_type(record: dict, *, successor: bool = False) -> str | None:
    if successor:
        return "fixed"
    return record.get("tariff_type") or "fixed"
```

**Neither branch can return `None`.** `record.get("tariff_type")` returning `None` is precisely the
case `or "fixed"` absorbs. No record — constructed, drawn, won or hand-authored — resolves to
anything but `"fixed"`. The fixture cannot build a subject that does not exist in the codomain.

The correction is filed here beside the claim rather than applied silently to the commit, because
the commit is in the record and a remedy that reads as established is exactly the failure this
project prices.

## What this actually is

The return annotation is still `str | None`. The `None` arm of it is **dead code**, and with it
every downstream "unlabelled" path that reads this function — including
`run_value_cycle_ab.product_label_by_account_class`'s `the_guard_admits_it: False` leg and the
`a_found_account_can_reach_the_product_gate` boolean the live page's sentence turns on.

Three controls in `tests/tools/test_the_renewal_funnel.py` assert over that dead arm:

* `test_the_census_counts_what_the_guard_reads_not_whether_the_key_is_there` — asserts key-presence
  and resolved value **come apart**; they no longer can;
* `test_MUTATION_a_labelled_won_record_makes_the_gate_reachable` — asserts the unlabelled leg gives
  `False`; it gives `True`;
* `test_a_founder_account_passing_the_gate_is_not_a_found_account_reaching_it` — same field, same
  flip.

**The irony is the finding.** The second one's own docstring says it exists because *"a boolean only
ever observed one way cannot be told from one that is structurally unable to leave it — R15's
unreachable-branch shape"*. It is now itself asserting a structurally unreachable value. The control
written to prevent the shape has become an instance of it.

**And this is the third time these controls have lost their subject to a repair.** The docstring
records being moved from electricity to gas on 2026-09-07 for exactly this reason. Moving is what
has failed twice; the answer is not a third move.

## Why nothing noticed for two days

They have been red since 2026-09-16 and HEAD is red now — proven in a clean `git archive` extract of
`92230b699`'s parent with no local changes: `3 failed, 21 passed`. Every lane whose test selection
reaches that file is refused, and every lane whose selection does not reach it commits happily. That
is the selection-by-subject-stem property working as designed and hiding a red tree as a side
effect. **I found it only because my republish happened to select that file** — not because anything
was watching.

## The remedy, and it is a judgement not a repair

Three options, and the choice is not mine to make silently:

1. **Delete the `| None` from the signature and the dead downstream branches**, and re-key the three
   controls to the property that now holds — every leg is labelled, so the gate is reachable for
   found accounts and the page should say "book size", not "a gate". Honest, and it removes a
   diagnostic the page currently leans on.
2. **Restore a reachable unlabelled state** if one is FIDELITY-correct — i.e. if a real supplier
   genuinely cannot resolve a product for some account. That is a question for the domain, not the
   code, and `or "fixed"` may have over-reached when it closed the gas leg.
3. **Monkeypatch `resolved_tariff_type` in the fixture** to keep the controls alive over a state the
   world cannot reach. This is the cheap option and it is the wrong one: a control over an
   impossible input is furniture.

**My recommendation is (2) asked first, then (1).** Whether an unresolvable product is a real thing
a supplier sees is a knowledge question with a published answer, and `or "fixed"` was landed to fix
a *spelling* disagreement between two builders — not to rule that unlabelled accounts do not exist.
If the domain says they do, the repair is in the world and the controls come back for free. If it
says they do not, (1) is right and the dead branch should go.

## What would refute this

A second definition of `resolved_tariff_type` shadowing this one, or a caller passing something
other than a `dict`. **I checked the first and it does not hold**: `grep` over every `.py` in the
tree returns exactly one definition, `simulation/run_phase2b.py:579`, and the one production caller
(`tools/run_value_cycle_ab.py:3522`) imports it rather than respelling it — deliberately, per its
own comment, because a restated spelling is what caused the 2026-09-16 defect.

I did **not** exhaustively check the second. A caller passing a non-`dict` would raise rather than
return `None`, so it would not restore the branch either, but I have not enumerated the call sites
to prove it.
