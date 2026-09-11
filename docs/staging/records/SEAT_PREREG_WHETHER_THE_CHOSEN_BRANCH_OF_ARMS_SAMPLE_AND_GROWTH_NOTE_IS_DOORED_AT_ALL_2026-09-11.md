# PREREG — is the chosen-sample branch of `#arms-sample` and `#growth-note` doored at all?

**Severity:** LATENT · **Lane:** H_harness

**Written:** 2026-09-11, BEFORE running the mutation below.
**Claim:** `the-chosen-books-margin-is-unmeasured-and-the-page-branch-is-inert-until-the-feed-is-regenerated`

---

## Why this is being asked

`480f2cf75` landed a door over the chosen sample and it is a good one — but its subject is
**`#growth-headline` alone**, the sentence `tools/generate_book_growth_data.py` builds SERVER SIDE.
The drawn item names two *other* anchors, and both are built by the door's **own JavaScript**:

* `#arms-sample` — `site/capabilities/index.html:1127`, the chosen branch.
* `#growth-note` — `site/capabilities/index.html:421`, the chosen branch.

Both carry the same damage the landed door exists to keep off the page. `#arms-sample`'s uniform
branch closes with *"divide it by 0.183 to read the supplier instead"* — the arithmetic a reader
can carry out that returns a wrong number in silence.

## The suspicion, stated as a property

`#arms-sample` **does** have door legs (`site/test_the_baseline_comparison_reaches_the_reader.py`,
`test_the_book_on_this_page_is_named_as_a_sample_of_the_business` and
`test_the_sample_bound_carries_the_producers_own_numbers_and_not_its_own`). They render through the
live harness against the PUBLISHED growth feed, which since `480f2cf75` says `chosen_weighted`. So
they *execute* the chosen branch.

But executing a branch is not dooring it. Every assertion those legs make is satisfied by the
**uniform** branch too:

| assertion | uniform branch | chosen branch |
|---|---|---|
| `"sample" in rendered.lower()` | "are a uniform 18.3% **sample** of" ✓ | "are a CHOSEN 18.3% **sample** of" ✓ |
| `"{:.1f}%".format(rate*100) in rendered` | ✓ | ✓ |
| win count rendered | ✓ | ✓ |
| `"{:.3f}".format(rate) in rendered` | "divide it by **0.183**" ✓ | "dividing by **0.183** would be wrong" ✓ |

That last row is the sharp one: the control demands the divisor be **present**, and both branches
print it — one as an instruction to use, one as an instruction to refuse. The control cannot tell
those two apart, and its own remedy prose ("*the page tells a reader the count is a sample without
giving them the divisor that turns it back into the supplier*") is **false of a chosen book**,
where no such divisor exists. Maths right, remedy prose wrong.

`#growth-note` is the simpler case: `tests/tools/test_capabilities_growth_section_renders.py` covers
only the *absent* and *capital* branches. Nothing names the selection at all.

## THE PREDICTIONS — recorded before the run

**P1.** Deleting the chosen branch of `#arms-sample` (`if (g && g.settlement_selection ===
"chosen_weighted") {...}` at `index.html:1127`), so the render falls through to the uniform prose,
leaves **every existing test in `site/test_the_baseline_comparison_reaches_the_reader.py` GREEN**,
and leaves the landed chosen-sample door **GREEN**, while the published page tells a reader of a
chosen book to divide by 0.183.

**P2.** Deleting the chosen branch of `#growth-note` (`index.html:421`) likewise leaves
`tests/tools/test_capabilities_growth_section_renders.py` and the landed door **GREEN**.

**P3.** The landed door (`test_the_chosen_sample_reaches_the_reader_without_a_divide_instruction.py`)
stays green under **both** mutations, because its only subject is `#growth-headline`, which is built
server-side and is untouched by either edit.

**If P1–P3 hold, the gap is real and the door I write is the remedy.** If any of them is refuted,
the branch is already doored somewhere I did not find, and the honest outcome of this turn is to say
so and release the claim rather than to add a duplicate control.

## What "done" means for this turn

A door whose legs **discriminate the two branches** — each one red when the chosen branch is
deleted and the uniform prose renders in its place — over both anchors, driven through the real
`_live_harness.mjs` against the real producer's output. Keyed to the selection the feed declares,
never to today's 18.3%, so it cannot rot when the budget lifts and the rate goes to 1.0.

---

# RESULT — 2026-09-11, written after the run

**P1, P2 and P3 all HOLD. The gap is real and the door is landed:
`site/test_the_chosen_book_is_not_called_uniform_on_the_two_JS_built_anchors.py`.**

## First, a correction beside the claim: my first measurement was taken against the wrong subject

I applied both mutations to `site/capabilities/index.html` **in the working tree**, ran the three
suites, got `145 passed`, and was ready to call P1–P3 confirmed. That measurement was worthless.

`site/test_the_published_bytes_reader.py` resolves a door through `git show :<path>` — **the
INDEX** — precisely so that a repair sitting unlanded in a tree cannot be mistaken for one a reader
can see. So a working-tree edit is invisible to every one of those controls: they were green
because the mutation **never reached their subject**, not because they failed to notice it.

The number was right and the reason was wrong, which is the more dangerous half. Both readings say
`145 passed`, and nothing in that output distinguishes "the controls are blind to this defect" from
"the defect was never applied". Had I stopped there I would have filed a true conclusion supported
by no evidence.

The honest run poisons the index — `git hash-object -w` then `git update-index --cacheinfo` — and
restores the original blob (`6e76207d`) after each arm. Re-measured that way:

| mutation | the three existing suites | the new door |
|---|---|---|
| M1 `#arms-sample` chosen branch deleted | **145 passed, 1 skipped** | differ[arms-sample] + uniformity + instruction + lift RED |
| M2 `#growth-note` chosen branch deleted | **145 passed, 1 skipped** | differ[growth-note] + same-rate + lift RED |
| M3 `#arms-sample` chosen branch unconditional | **145 passed, 1 skipped** | differ[arms-sample] + **both cull legs** RED |
| M4 `#growth-note` chosen branch unconditional | **145 passed, 1 skipped** | differ[growth-note] + cull-note RED |

M1/M2 are P1 and P2. The landed headline door stayed green throughout, which is P3 — its subject is
`#growth-headline`, built server-side and untouched by either edit.

## What the reader actually saw under M1

Rendered against the real published feed, which declares `chosen_weighted`:

> The 164 settled accounts above are a **uniform** 18.3% sample of the 500 accounts the company
> won … **divide it by 0.183 to read the supplier instead.**

The exact arithmetic-a-reader-can-carry-out the landed door exists to keep off this page, one
section below it, with 145 controls green over it.

## M3 and M4 were not in the pre-registration and are the more interesting half

I pre-registered only the *deletion* mutations. Deletion proves the chosen legs can fail; it does
**not** prove the cull legs can. A page that lost its **cull** branch instead — rendering "CHOSEN"
unconditionally — is exactly as wrong, and would pass every chosen-branch assertion in the file.
That is R15's unreachable-PASS-branch shape, which this project has entered three times in one
afternoon through three different doors, so I added the other end of the partition and mutated it
too. M3 and M4 are what make the cull legs evidence rather than decoration.

## One defect found in my own control, and the narrowing it needed

The first draft keyed uniformity to the bare substring `"uniform"` and went **red on a correct
page**: the chosen branch's whole point is to say *"It is deliberately **NOT** uniform"*. A denial
of uniformity is not a claim of it.

A narrowing added to fix a false positive is asymmetric and is a place for the defect to hide, so
the denial is stripped in a shared `_claims_uniformity` helper applied to **both** ends — not
special-cased inside the one leg that was inconvenient. The cull's own *"are a uniform 18.3%
sample"* survives the normalisation untouched, which is what keeps `test_a_real_uniform_cull_IS_
still_called_uniform` able to fail. M3 confirms it still can.

## The finding this leaves behind, which is not mine to fix here

`test_the_sample_bound_carries_the_producers_own_numbers_and_not_its_own` asserts the divisor is
**present** and explains itself as *"the page tells a reader the count is a sample without giving
them the divisor that turns it back into the supplier"*. Over a chosen book **there is no such
divisor**. The assertion still passes — both branches print the number — so the arithmetic is
right while the sentence explaining it is false. Filed separately rather than repaired here,
because changing a control's prose in the same commit that adds its replacement is how a correct
fix becomes unattributable.
