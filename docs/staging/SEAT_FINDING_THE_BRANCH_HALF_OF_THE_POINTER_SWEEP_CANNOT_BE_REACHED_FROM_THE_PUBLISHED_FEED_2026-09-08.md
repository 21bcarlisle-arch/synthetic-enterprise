**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING — the branch half of the pointer sweep cannot be reached from the published feed, and three ways of trying are refuted

LATENT: no published figure is wrong today. The whole-site sweep passes, and so does the new
control on the tree it was written against. What is established is that the sweep's stated blind
spot is **structural, not incidental** — it cannot be closed by any amount of reading
`site/data/*.json`, and the three cheapest ways of trying were measured and refuted.

**Filed:** 2026-09-08, delivery seat (isolated worktree), claim
`the-branch-half-of-the-multi-home-sweep`.
**Pre-registration:** `SEAT_PREREGISTRATION_THE_BRANCH_HALF_OF_THE_MULTI_HOME_SWEEP_2026-09-08.md`,
written before the probe ran. **Two of its four predictions are refuted and they are the two the
design rested on.** They are kept here beside the result rather than revised.

---

## What was predicted, and what happened

| | Prediction | Result |
|---|---|---|
| **P1** | probing FIELDS finds **> 31** multi-home subjects (value-matching finds 31 strings); est. 45–90 | **REFUTED — 25.** Fewer, not more |
| **P2** | **2–7** of the eleven zero-home here-relative strings gain ≥1 home under probe | **REFUTED — 0** |
| **P3** | at most 1 of the eleven has a field with ≥2 homes | held (0), but **vacuously**, given P2 |
| **P4** | **5–20** non-docstring here-relative producer literals; ≥1 untied | **21** (just outside), untied **13** — held |

**H2, formed after P1/P2 fell and measured immediately:** generalising the list index (judging
`open_work[].atom_name` rather than `open_work[54].atom_name`) recovers most of the eleven.
**Also refuted — 0 of 11.**

## Why P1 fell, and it is not a detail

Value-matching keys homes to the **rendered string**; probing keys them to the **field**. They
disagree because *a string with two homes and a field with two homes are different things*:

* `value_arms.json .realised.arms[].what` and `.provisioned.arms[].what` are **two fields with one
  home each**, carrying identical text. String-keyed: one subject, two homes. Field-keyed: two
  subjects, one home each.
* `composition.why_not_readable` — the parent defect — is **one field with two homes**
  (`#arms-composition`, and composed into the headline that `#arms-headline` renders).

Neither reading subsumes the other and **both are needed**. The 31 and the 25 are not a discrepancy
to reconcile; they are two different quantities, and the ratio of them would mean nothing.

## Why P2 and H2 fell — the decisive result

The eleven here-relative payload strings that render nowhere do so because **no door reads those
keys at all**, at any index, with or without a marker. `open_work`, `honest_holds`,
`how_to_read_this`, `shape_basis`, `recon_saturation_caveat` appear in **zero** deployed doors.
They are feed prose no reader ever meets. That is a different fact from the one the sweep's
docstring implies ("a producer branch … renders nowhere"), and it is worth stating separately.

And the field that actually carries the parent defect is not reachable this way either:
**`composition.why_not_readable` is not among the 3,712 payload fields the site publishes.** With
the level leg sign-stable it is absent from `value_arms.json` entirely. No probe over the published
feed can see a field that is not there. **The only instrument that reaches an absent field is the
producer that can create it** — which is what the drawn direction said, and the measurement now
establishes it rather than assuming it.

## What landed

`site/test_a_producers_here_relative_pointer_has_one_home.py` — the complement, not a replacement.
The published sweep sees every page on one branch; the value_arms rung sees every branch of one
page; this sees **every producer's prose against every field's homes**. Three rules:

1. **Field-keyed:** no feed field reaching two regions may carry a here-relative sentence. Homes
   derived by marking each field and re-driving the door's own boot path — one extra render per
   door, not one per field, and the marker is a prefix so doors that branch on content still take
   their real branch.
2. **Producer-keyed:** every non-docstring here-relative string literal in `tools/generate_*.py`
   is a sentence some branch can publish; tied to a published field, it is judged against that
   field's homes.
3. **Fail closed:** an untied literal — one on a branch today's data does not drive — is refused
   when its producer writes a feed that has any multi-home field. Scoped that way deliberately:
   refusing all thirteen today would be refusing the site for not being measurable.

## Evidence it can fail — every poison run against the real tree and reverted

* untied here-relative literal added to `generate_delivery_page.py` (writes the 2-home
  `delivery.json`) → **rule 3 reds**, naming producer, line, phrase and feed.
* **the same poison, run against `site/test_a_here_relative_pointer_has_one_home.py` → 5 passed,
  GREEN.** This is the complementarity claim measured rather than argued: the published sweep is
  structurally blind to a sentence that never reaches the feed.
* landmark wording, same site → **green**. The rule does not refuse the repair.
* here-relative sentence into `delivery.json .what_it_decided.focus[0].why` (probed 2-home field)
  → **rule 1 reds**; landmark wording there → **green**.
* probe blinded (no homes derived) → witness + both mutation legs red.
* render dropped after planting (drift) → fidelity leg reds first, before any rule passes on
  silence.

## Also found, not fixed — filed rather than carried silently

`site/_live_harness.mjs` reflects `appendChild` into a `children` array **nothing reads**, and
elements from `createElement` never enter the output map at all. A door rendering by DOM-building
would report **zero homes for everything**, and every rule in both files would pass. Measured:
**no deployed door uses either**, so this is latent — but it is a fail-open under both controls and
under `live_pixel_verify` itself, which is a wider blast radius than this lane. Second: the harness
accepts a `#hash` argv[3] that `live_pixel_verify.run_harness` **never passes**, so every door is
rendered on its default branch only. Only `/explore/` reads `location.hash` today, so the cost is
small now and the plumbing is one argument away.

## What is next

* **The thirteen untied literals** (twelve in `generate_value_arms_data.py`, one in
  `generate_proof_data.py`) are recorded and not refused. Closing them needs per-page rungs that
  RUN the producer's branches, as `_every_pointer_this_page_can_publish` does for value_arms.
  That is the remaining work of this claim, and it is per-page by necessity.
* **The harness `appendChild`/`createElement` gap** should be closed at the harness, where it fixes
  both controls and the live verifier at once.
* **The eleven unrendered here-relative sentences** are feed prose no door reads. Either a door
  should render them or the producers should stop writing them; today they cost payload bytes and
  carry pointers nobody can meet.
