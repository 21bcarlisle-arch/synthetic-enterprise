**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 3 · **Atom:** C32_one_obligation_one_vulnerability_scorer
· **Class:** no_caller_and_never_runs

# The four vocabularies are two — and the live one held a term invented from a boolean

**Result document, 2026-09-06, delivery seat.** Third turn on atom C32, and the one that finishes
the convergence. It continues
`SEAT_RESULT_THE_TWO_REGULATORY_OUTCOMES_NOW_HAVE_ONE_DECIDER_AND_THE_BENCHMARK_THAT_WAS_NEVER_A_RATE_IS_GONE_2026-09-06.md`,
whose closing section said "still four vocabularies — what converged is the two DECISIONS, not the
enums", and named the two that remained. Both are done here.

---

## 1. What the free-text column actually cost, measured rather than argued

`crm/service_log.VulnerabilityFlag.flag_type` was `str`. A column that enumerates nothing
constrains nothing, and the live store is what that bought:

| the register, `company/data/service_log.db` | |
|---|---|
| active `vulnerability_flags` rows | **4,557** |
| distinct `flag_type` values | **1** |
| that value | **`financial_difficulty`** |
| vocabularies it is a member of | **none of the four** |

It got there as a hardcoded literal in `record_contact`, written whenever
`ServiceEvent.vulnerability_flag` was true. **That field is a boolean.** A boolean carries no term,
so the literal was a term invented at the point one was needed and none existed — the same shape as
the £150 CAC and the 31% "UK benchmark" this atom deleted yesterday, in a SQLite column instead of a
constant.

**It was not inert.** `warm_home_discount.whd_eligible_customers` is the distinct customer ids of
any active flag of any `flag_type`, so Warm Home Discount candidacy runs off it, feeding the
portal's per-account `whd_eligible` badge and `whd_summary`. And the admin register rendered
`flag_type.replace("_", " ").title()` — 4,557 rows presented to an operator as **"Financial
Difficulty"**, a confident English label for a term nobody ever chose.

## 2. The fix, and the mapping row I did not write

`flag_type` is now `company.crm.vulnerability_register.VulnerabilityFlag | None`. The import is the
point: a second spelling cannot drift from a source it does not have.

**`None` is a first-class answer, not a null.** It means "flagged, term not recorded", which is what
the boolean always said. `term_display` prints `Not recorded (stored as 'financial_difficulty')`
rather than an English label, so the absence reaches the surface instead of being dressed as a
category. A caller that knows the term passes it — `record_contact(event, vulnerability_term=...)`,
keyword-only, so no existing caller changes.

**The back-compat read path coerces nothing, and that was the tempting mistake.** One dict row —
`financial_difficulty → PAYMENT_DIFFICULTY` — would have made 4,557 rows readable and would have
been wrong: the string was written from a boolean, so it never named a state, and `fuel_poverty`,
`payment_difficulty` and `job_loss` are three different operational terms it could equally have
stood for, carrying three different required actions. Mapping it would have moved the guess out of
the column, where it was visibly a guess, and into a table, where it would read as established.
The raw value is kept in `recorded_as` so nothing is lost and the decision stays reversible.

## 3. The fourth vocabulary, and the two of its eight terms that did not survive translation

`regulatory/consumer_vulnerability_register.VulnerabilityCategory` was eight near-synonyms of the
twelve operational flags with no production caller. Records now key on the operational vocabulary.
Six mapped term-for-term. Two did not, and **both refusals are the finding, not a loss**:

- **`FINANCIAL_HARDSHIP` had no single counterpart.** The operational vocabulary keeps
  `FUEL_POVERTY`, `PAYMENT_DIFFICULTY` and `JOB_LOSS` apart because they carry different required
  actions and are different states. One word let a caller avoid saying which; a caller must now say.
  Same shape as the free-text column next door, and the same shape as *bill shock*.
- **`TEMPORARY` ("post-surgery, new baby") was a temporality wearing a category's clothes.**
  Post-surgery is `SERIOUS_ILLNESS` that ends; a new baby is `CHILD_DEPENDENT` that does not.
  Whether a state ends is already carried per record by `follow_up_date`, which is where it belongs
  — it is a property of this household's episode, not of the term.

## 4. Two is the finished state, and the ratchet had to be told so

`KNOWN_VOCABULARIES` is now `{PSRCategory, VulnerabilityFlag}` and would read as a job half done
without this said out loud: **the obligation has two layers and they are not synonyms.**
`PSRCategory` is the published needs codes, the regulator's own words. `VulnerabilityFlag` is what
our agents actually record, seven terms of which confer nothing under the licence. What was ever
wrong was not that there were two layers — it was four spellings of them with no stated relation.
The relation is one function, `needs_code_for`, which grades an operational term against a published
one in three answers and refuses to invent the middle.

**The detector was sharpened, which is also how a detector gets blinded.** Its free-text leg used to
fire on the mere presence of an annotated `flag_type`; it now fires only when the annotation admits
every string. That is the honest property — a class holding a term drawn from a shared enum is a
*user* of a vocabulary, not a rendering of one — and it is exactly the edit you would make to turn a
ratchet green dishonestly. So both sides are asserted in **one** control
(`test_a_term_field_is_a_vocabulary_until_it_is_typed`): free text caught, `str | None` caught, a
bare literal caught, a renamed field caught, and the typed field not caught. A leg that only checked
the last of those would pass just as well against a scan that had been made to see nothing at all.

## 5. The mutation round, targets proved present first

Seven mutations, each asserting its target was in the file before patching, so a survival could not
have been a patch that never applied. Seven killed, none survived:

| mutation | verdict |
|---|---|
| unknown stored term coerced to `PAYMENT_DIFFICULTY` | KILLED |
| the invented literal `financial_difficulty` comes back | KILLED |
| the surface titles the off-vocabulary string again | KILLED |
| the detector blinded — nothing counts as unconstrained | KILLED |
| the detector widened — a typed field counts too | KILLED |
| the term-field list narrowed, so a rename escapes again | KILLED |
| `is_medical` points at the wrong term | KILLED |

The two detector mutations are opposite directions of the same knob, and both must die or the
sharpening in §4 is unproved in one direction.

## 6. The ruff baseline, and the number that was not mine

`RUFF_BASELINE["I001"]`: 1323 → **1321**, total 2302 → 2300. **The shared tree reads 1320 and that
is not this commit's number.** The third fix belongs to another lane, uncommitted, in
`tests/tools/test_generate_maturity_map_data.py`; freezing 1320 would have red the live control the
moment this landed alone. Measured in a `git archive HEAD` extract overlaid with exactly this
commit's files — the same trap the previous turn hit and left the method for, one entry down in the
same file.

## 7. What is left, and why the level did not move

**The level stays 2 and the build is not why.** The convergence is complete. L3 is "passed the full
loop incl. HARDEN; Expert Hour: *this is real*", and `expert_hour` on the atom still reads
`not_attempted`. Recording 3 would be a level claimed on a stage nobody ran. `loop_stage` moves
`build → harden`; one cold-eyes pass is the whole of what remains.

**One gap stays open from the previous turn and is not closed here:** the *current* UK PSR
registered rate is still unsourced. The 2016 figure carries its date and a staleness flag; nothing
in `company/` may quote a present-day rate until the 2025 Consumer Vulnerability Strategy PDF yields
one.

**One thing is now visible that this atom does not own.** `whd_eligible_customers` treats *any*
active flag as a Warm Home Discount Broader Group candidate, on a register whose terms it never
reads. That was invisible while every row said the same off-vocabulary word; with the term typed, it
is a question with an answer. Queued, not fixed — outside this atom's scope, and the seat's own
interrupt discipline applies to its own findings.
