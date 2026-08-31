# [DIRECTOR-CANON] — End-to-end is how we design and test; a concept has one home (2026-08-31)

**Type:** [CANON — a standing standard, with a deliberately evidence-first first step. Sits alongside the world validation ladder rather than inside it: the ladder governs whether the world is right, this governs whether the parts of it agree with each other.]

---

## 1. The pattern this closes

Every lane, atom, control and page in this project is locally coherent and locally defended. **Nothing owns the joins.** A defect that lives *between* two things has no owner and no test, so it is rediscovered from whichever end someone happens to approach, and the same shape is found again and again in different clothes.

The evidence is a fortnight old and it is all the same defect:

- One legal VAT rule with **seven declarations**, and a repair landed in one module on 8 July still live as the identical defect in another on 31 August.
- `MAX_CHURN_PROBABILITY` at 1.0 on one side of the seam and 0.95 on the other — one name, two ceilings, and the 0.95 is what made charging the cap look free.
- `DISCOUNT_RATE` defined independently in three files.
- "Net margin" meaning two different quantities, which is the whole of the £4.9M reconciliation confusion.
- A researched acquisition model in `opex_ledger` called by nothing while an invented £150 was spent.
- A guard still pointing at a module that no longer held its subject.
- A standing charge that is the sum of two fuels used as one.

None of these is a broken component. Each is a **join** failing, and a join with no owner has no test.

**The deeper consequence:** fragmentation is why the same fix keeps being made instead of the class being closed. The no-caller pattern only became visible when findings were consolidated and someone counted *across* instances. Nothing does that routinely.

---

## 2. The standard

**Three properties, and they are the point of this document.**

**End-to-end is how we design, not only how we test.** Every piece of design says where it sits on the customer's journey — weather, price, demand, bill, payment, settlement, judgement — and which concepts it touches. That is a habit asked *before* building, and it is the cheapest of everything here. It is the question "what else assumes this?" moved earlier.

**A concept has one home.** A domain concept — a rate, a rule, a quantity, a ceiling — is defined once, with its meaning, its unit, its owner and its source. Everything else *reads* that definition. Two implementations that happen to agree is not agreement; it is a coincidence waiting to end.

**The joins are tested, not assumed.** Where two parts meet, something asserts they mean the same thing by the same name. A seam with no test is a seam that will disagree quietly.

---

## 3. The first step, and why only one

**Do the end-to-end journey walk first. Do not build a concept registry yet.**

Walk one household from weather through price, demand, bill, payment and settlement, asserting the joins along the way. Every defect listed in §1 sits somewhere on that path.

The reason for this order rather than naming concepts first: a walk **exercises** the concepts where a census only **inventories** them. It will show where meanings genuinely disagree — and, just as usefully, where the same word is honestly doing two different jobs and should stay two things. A registry built before that evidence would be a naming exercise, and would enshrine distinctions that do not matter while missing the ones that do.

**Then, and only then, decide the shape of the concept work** — what a definition looks like here, which concepts earn one, and how the code reads it. That decision is deliberately not made in this document, because the walk should inform it.

---

## 4. The constraint that matters most

**This is exactly the kind of work that becomes bureaucracy, and bureaucracy here would be worse than the disease.**

A registry nothing reads is a fourth artefact that can lie. A model of the domain maintained separately from the code drifts from it, and then we have added to the class of defects we are trying to close rather than closing it.

So the test of success is mechanical, not documentary: **the code reads the definition.** If a concept is defined and a module still carries its own copy, nothing has been achieved. Prefer the smallest mechanism that can fail. Do not build the thing that watches the work instead of doing the work.

The same applies to the journey walk: one walk that genuinely asserts joins is worth more than a suite of walks that assert nothing.

---

## 5. What this does not decide

The shape of the concept work, the form of a definition, which concepts qualify, the mechanism of the join tests, and the sequencing beyond "walk first". All the delivery seat's, informed by what the walk finds.

## WORK THIS CREATES (canonical, in-document)
1. The end-to-end journey walk: one household, weather to judgement, joins asserted.
2. A statement of what the walk found — where concepts disagree, and where a shared word is honestly two things.
3. On that evidence, the shape of the concept work decided and begun, with the code reading definitions rather than mirroring them.
4. Join tests where the walk showed a seam that nothing was holding.
5. The design habit adopted immediately and independently of all the above: every new piece of design says where it sits on the journey and which concepts it touches.

— Director canon, 2026-08-31. Local correctness has been achieved and the joins have not. This closes that, evidence first, and refuses to buy it with bureaucracy.
