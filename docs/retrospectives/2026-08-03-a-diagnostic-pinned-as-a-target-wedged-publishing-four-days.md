# A diagnostic pinned as a target: four days of blocked publishing from one literal (2026-08-03)

**Prompted by:** the RUNG-1 publish-gate-wedge self-refill tick (director rulings
`UNWEDGE_PUBLISH_PRIORITY_ZERO` 2026-07-23, `WEDGE3_AND_RUNG1_MECHANISE` 2026-07-24). The gate had
been red for ~5,900 minutes with no pass at HEAD `952454e2c`.

**Claim discipline (R9):** every claim below is `observed-with-evidence` (quoted gate output, a
cited commit, a file:line checked against current code) or `inferred` (my reasoning from that
evidence, marked as such).

## What happened

`observed-with-evidence` — `docs/observability/sim-runner-log.md`, 2026-08-03 02:54 UTC, the gate's
own output:

```
_____________ test_closed_account_notice_real_churned_customer_c1 ______________
tests/tools/test_billing_tab_fix.py:116: in test_closed_account_notice_real_churned_customer_c1
    assert notice.startswith("Account closed 2020-12-30")
E   AssertionError: assert False
E    +  where False = 'Account closed 2021-12-30 — final bill C1-INV72. Account settled to zero
                       (net of £111 written off).'.startswith
1 failed, 18503 passed, 1 skipped, 983 deselected, 9 xfailed ... in 419.23s
```

One assertion. It pinned customer C1's churn date — **an RNG draw** — as the literal `2020-12-30`.
The recent world builds (`W2_12` change-of-tenancy debt physics, `W2_13` occupancy→consumption,
`W2_14` continuous engagement) legitimately perturbed the life-event draws and moved it to
`2021-12-30`. The control went red. `process_run_complete` returned rc=1 on every cycle from
2026-07-30 01:28Z (last successful publish, `02247e7fe`) to 2026-08-03.

`observed-with-evidence` — cost: **401 `run_complete_*.md` markers queued** in `docs/staging/`,
zero commits to origin for ~4 days (origin sat at `952454e2c`, dated 2026-07-30 05:59), and the
live site frozen — while the simulation itself was **completely healthy**, producing a valid run
every ~9 minutes the entire time.

`observed-with-evidence` — C1's live record is internally coherent, not corrupt: last billed period
ends `2021-12-29`, churn `2021-12-30`, final bill `C1-INV72`. The world was right. The control was
wrong.

## The shape

**R12 says a generated value is a DIAGNOSTIC, never a target.** That rule is normally read as being
about *margin* — don't tune the company toward a benchmark. This incident is the same law one level
down, in a place nobody was looking: **a control that asserts a diagnostic's exact value has made it
a target.** The sim is then forbidden from changing, and the punishment for changing anyway is that
publishing stops.

The most damning detail: `observed-with-evidence`, the test's own comment had **already diagnosed
this, in writing, and filed it as debt**:

> `NOTE (queued debt): pinning an exact RNG-derived date makes this test brittle enough to WEDGE
> the publish pipeline on any legitimate life-event change -- the real fix is to assert C1's own
> generated churned-date structurally, not a literal.`

The comment even records the date oscillating `2020-12-30 → 2021-12-30 → 2020-12-30` across three
prior builds. Someone saw the exact failure mode, wrote down the exact fix, and re-stamped the
literal anyway. **A queued finding with the fix already written is not "queued" — it is a known live
fault with a countdown on it.** This is SELF_INTERRUPT_DISCIPLINE's edge: QUEUE-by-default is right
for the infinite supply of harness findings, but not for a finding whose own text says *this will
wedge the pipeline*. The discriminator is not severity-in-the-abstract, it is **"does this finding
name a blast radius outside its own file?"**

## Why nothing caught it for four days

`inferred`, from the evidence above: every alarm fired correctly and none of them shortened the
outage.

- The wedge detector worked — it recorded 6 consecutive failures and armed the alert.
- The worker logged `Failed to process ... (rc=1) — will retry next cycle`, every ~11 minutes, ~500
  times.
- The retry was the problem, not the safety net. Each cycle re-ran a **7-minute** full suite to
  rediscover the identical deterministic failure. A red gate is not a flake; retrying it is pure
  cost. `inferred`: the loop had no notion of "this exact failure at this exact HEAD already
  failed", so it burned four days re-proving one assertion false.

## What changed

1. **Instance** (`1325f2bb9`) — the date is asserted structurally against the account's own churn
   event, cross-checked by an **independent** part of the record (the invoice stream: churn ≥ last
   billed period end; no invoice period starts after churn). Strictly stronger than the literal,
   which could not distinguish a real date from a fabricated or defaulted one.
2. **Class** (`88d9f3546`) — `tests/tools/test_no_live_data_literal_pins.py` refuses any bare
   run-derived literal (ISO date, generated `C*-INV<n>` id) asserted inside a test function that
   reads live generated data, across **both** `tests/` and `site/`. R10: the class fails
   automatically now, not the instance.
3. **The sibling lane, found by writing (2)** — extending the guard to `site/` immediately surfaced
   the same class in `site/company/test_company_door.py`: a pinned live-derived held-credit floor
   (`== 2975.67`). The site-lane pre-commit gate refused the guard's own commit over it. Fixed
   structurally in the same change. `observed-with-evidence`: this confirms
   `[[feedback_audit_sibling_half_for_hardened_class]]` — the sibling half had it too, and only
   looking found it.

R15 both ways on the guard: it fires on a replay of the actual 2026-07-30 assertion and on the
sibling shape (pinned invoice id); it stays silent on the structural pattern and on inline-fixture
literals. Notably the mutant that proves leg 1 **hardcodes the currently-correct date** — so the old
literal assertion would have passed it. The replacement is not just less brittle, it catches a
defect the original could not see.

## The lesson worth keeping

**A control asserting an exact generated value is not a strong control — it is a scheduled outage.**
It cannot tell "the world legitimately changed" from "the code broke", so it reports both as the
same red, and the machine's only options are to stop publishing or to re-stamp the literal. Both are
wrong. Assert the *relationship* (this rendered value IS the record's own, and the record is
internally consistent), never the *value*.

## Still open

`observed-with-evidence`, not fixed here, deliberately out of this tick's scope — **the retry loop
has no deterministic-failure memory.** It re-ran a 7-minute suite ~500 times against an unchanged
HEAD to rediscover one deterministic assertion failure. The wedge detector counts the failures but
does not suppress the futile retry. A same-HEAD-same-failure short-circuit (fail fast, keep the
alert, stop burning the cycle) would have made this outage visible in its diagnostic cost rather
than hidden in a log that looked busy. Filed as a harness finding rather than fixed on sight
(SELF_INTERRUPT_DISCIPLINE) — but per the discriminator above, it names a blast radius outside its
own file, so it should be drawn soon rather than queued indefinitely.
