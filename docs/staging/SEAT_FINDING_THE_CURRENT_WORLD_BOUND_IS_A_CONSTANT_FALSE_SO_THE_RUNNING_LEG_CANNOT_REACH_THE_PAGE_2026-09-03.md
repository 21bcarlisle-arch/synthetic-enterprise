**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The current-world bound is a constant `False`, so the leg running to produce it cannot reach the page

*Delivery seat, 2026-09-03, lane-0, claim `the-baseline-was-beaten-in-a-world-that-no-longer-exists`.
Established by reading `_current_world_contrast` and its caller against the `--out` path of the
running unit, not by measurement, so this is a finding and not a prediction.*

---

## What is wrong

`tools/generate_value_arms_data.py::_current_world_contrast` returns, on its admitting branch:

```python
"bound_available": False,
"why_no_bound": ("NO BOUND ON THIS PAGE WAS MEASURED IN THIS WORLD. ...")
```

Both are **literals on the only branch that can reach them**. There is no input to this function —
none — that makes `bound_available` true or `resolved` anything but `None`. The `floor` argument is
read for `world_identity.digest` to compose the refusal's prose and *for nothing else*; its docstring
says so approvingly (*"`floor` is read for its date and its world ONLY — never for a number"*), which
is correct about the OLD floor and became the whole defect once a live-world floor was commissioned.

This is the constant-verdict shape this project has recorded before: **a control whose pass branch
is unreachable reports a constant verdict.** Here it is a *publication* whose resolved branch is
unreachable, which is the same failure pointed at a reader.

## Why it is not merely pending

`se-noise-floor-all-20260903b.service` has been running since 11:53:25Z with

```
--redraw-mode all --out docs/observability/value_cycle_ab_s1_noise_floor_20260903.json
```

and the module reads exactly two floor paths:

| constant | file | world |
|---|---|---|
| `NOISE_FLOOR_PATH` | `value_cycle_ab_s1_noise_floor.json` | **unstamped** — 2026-08-31, superseded |
| *(none)* | `value_cycle_ab_s1_noise_floor_20260903.json` | the live world — **nothing reads it** |

`CURRENT_WORLD_THREE_ARM_PATH` was moved to the `_20260903` artefact when the arms were re-run. The
floor path beside it was not. **So the leg now running will land, and the page will not move** — and
it will not move *silently*, because the refusal prose it keeps printing ("the floor legs are still
running") will still be there and still read as true.

That is the same defect as `9eec4cac3` — *"the arms were re-run … and the generator did not read
it"* — one artefact along, and it was reintroduced by the commit that fixed it, because that commit
wired the contrast's path and left the bound's.

## What makes it invisible

The generator's own control asserts the defect as the expected state:

```python
# tests/tools/test_generate_value_arms_data.py:2225
assert admitted["bound_available"] is False
```

That call passes `floor=None`, so the assertion is *correct for its subject* — but nothing anywhere
supplies a live-world floor, so no subject distinguishes "no bound was supplied" from "a bound can
never be formed". The door rung is the one control keyed to the property
(`if cw.get("bound_available"): assert resolved is not None`), and its true branch has never been
reachable either: it has been dead code guarding a constant since it was written.

## The repair

A `CURRENT_WORLD_NOISE_FLOOR_PATH`, read and admitted on **two independent guards**, both of which
have a sole witness already on disk:

1. **world digest == live** — sole witness `value_cycle_ab_s1_noise_floor.json` (mode `all`, names
   no world at all).
2. **`redraw_scope.mode == "all"`** — sole witness `value_cycle_ab_s1_noise_floor_only_20260903.json`
   (live world, wrong leg). This is the leg-swap guard, and it is the one that matters: the `only`
   leg is live-world, finished, and on disk *now*, so the cheap wrong repair — point the new
   constant at the floor that exists — passes guard 1 and publishes the wrong bound.

Neither guard alone is a control: a single subject satisfying both alternations makes each an
equivalence. The two artefacts above are the sole witnesses that keep them separable.

**Discharged:** `tests/tools/test_generate_value_arms_data.py::test_the_current_world_bound_takes_only_the_undecomposed_leg_of_this_world`,
`tests/tools/test_generate_value_arms_data.py::test_the_generator_reads_the_current_world_floor_from_its_own_constant`,
`tests/tools/test_generate_value_arms_data.py::test_MUTATION_the_leg_guard_and_the_world_guard_each_fail_alone`.

Repaired in the same commit that files this: the module gains the path constant, the two guards and
a reachable bound; the generator suite gains the sole-witness controls and a control on the DEFAULT
read, which is the branch the site runs; the door suite closes the rendered-verdict fail-open. Four
mutations were run and reverted under python3 -B. The verdict the bound will produce is predicted,
before the leg returned, in the sibling pre-registration on what the live-world bound makes the page
say.
