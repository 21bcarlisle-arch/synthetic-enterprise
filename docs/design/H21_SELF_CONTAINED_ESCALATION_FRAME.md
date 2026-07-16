# H21 — Self-Contained Escalation Payload (FRAME)

**Atom:** `H21_self_contained_escalation` · lane H_harness · epoch 2 · size M ·
level 0 → target 3 · provenance proposal · **BUILD-GATED (loop_stage: idle)**
**Source:** `docs/staging/done/ESCALATIONS_MUST_BE_SELF_CONTAINED.md` (P1, director-decided)
**Tightens / folds into:** `H19_escalation_ntfy_route_around` (level 2, built)
**Status of this doc:** first FRAME. DESIGN ONLY — no BUILD/runtime code (EPOCH_GATING R1).

---

## 1. The gap, precisely (WHAT vs CHANNEL)

H19 fixed the **channel**: an escalation is an async NTFY, never a window-ask, and
the loop keeps drawing other atoms while it waits (`executor_governor.run_loop` →
`_alert_wall` → `send_ntfy`, non-blocking; a blocked atom blocks only itself).

H19 did **not** fix the **content**. The live half-escalation the directive cites:

> "I hit a one-way door, decide at your cadence" → pointing at
> `docs/observability/build-executor-log.md`.

That is *half* an escalation. The director, on his phone, cannot answer it — he has
to open a terminal and read a log to even learn *what* the door is. The async design
only pays off if the notification **carries its own decision**. A link to an on-box
log is a **promissory note for an escalation, never the escalation**.

Concretely, today's `_alert_wall(kind="wall_escalated")` renders (executor_governor.py
L184-191):

- `what` = *"Headless executor hit a one-way door (WALL) — NTFY'd, loop CONTINUING…"* — **generic; no atom, no named choice.**
- `how`  = *"Decide this one-way door at your cadence … Details: the escalated item + build-executor-log.md."* — **the on-box log IS offered as the substance; no OPTIONS, no door-class, no default.**
- `why`  = interpolates `getattr(result, 'atom_reason', None)` — which IS now the
  self-contained `door_reason` (build_executor.py L669), so a *sentence* leaks
  through, but buried in the `why` field and with **no options / no class / no
  default** to act on.

So `door_reason` (the WHAT) already reaches the body; **OPTIONS, WHY-DOOR-class, and
DEFAULT do not.** H21 closes exactly that.

---

## 2. The self-contained escalation payload SCHEMA

An escalation NTFY body MUST carry, in the message itself (never behind a link):

| Field | Meaning | Source (independence matters — see §4) |
|---|---|---|
| **WHAT** | The specific decision, named: *atom id + the exact named choice.* Not "a one-way door." | Turn-supplied `door_reason` (landed, c157f862d) — one self-contained sentence. |
| **OPTIONS** | The actual choices, each **single-word-answerable** (e.g. `OPEN / DEFER / DROP`, or `yes / no`), so the reply is one word from a phone. | Turn-supplied `door_options` (**new field**). ≥2 required. |
| **CONTEXT** | The minimum needed to choose, **in the body**: current state + what each option implies at the extremes. A link is never the substance. | Turn-supplied `door_context` (**new field**), or folded into `door_reason` if short. |
| **WHY-DOOR** | Which one-way-door class (values/epoch, platform-admin, money, security, data-loss, public-claim, real-customer) — so the director knows why it reached *him* and not the twin. | **NOT turn-supplied.** Derived from `classify_action(door_reason).category` — the independent predicate. (Anti-tautology; see §4.) |
| **DEFAULT / NON-BLOCKING** | Confirm the loop continues meanwhile; state the safe default on no-reply if one exists, or say plainly there is none. | Turn-supplied `door_default` (**new field**, optional); non-blocking note is constant boilerplate. |

**On-box log demotion (hard rule):** any `build-executor-log.md` reference is rendered
as a trailing *"supplementary only"* line, never as the operative "Details:" that a
reader must open. If the five fields above are present, the director never needs the log.

### Message shape (illustrative — the render the BUILD slice would produce)

```
[ACTION NEEDED] executor-wall_escalated
What: <atom_id> — <exact named decision>.
Options (reply one word): <OPT_A> (<one-line implication>) / <OPT_B> (…) / <OPT_C> (…).
Context: <current state; what each extreme implies; blast radius>.
Why it reached you (door class): <VALUES_DECISION|PLATFORM_ADMINISTRATION|REAL_MONEY|…> — <one-line reason>.
Default / non-blocking: <safe default or "no safe autonomous default">. Loop is NOT blocked — drawing other work; acts on your one-word reply at the next boundary. build-executor-log.md is supplementary only.
```

This reuses the existing `[ACTION NEEDED] item_id / What / How / Why` envelope
(`action_needed.format_action_needed`); H21 just makes `What`/`How` **specific and
decision-bearing** and adds the OPTIONS + door-class lines, rather than inventing a
new transport.

---

## 3. Composition with the already-landed `door_reason` field (c157f862d)

The groundwork is in place; H21 is additive, not a redesign:

1. **The turn** already returns a self-contained `door_reason` — `_RETURN_KEYS`
   (build_executor.py L485) includes it, and the prompt (L536-539) instructs the turn
   to set `door_reason` to one self-contained sentence naming the decision, warning
   that a `door_reason` the predicate does not confirm is downgraded.
2. **The predicate gate** already runs: on `gate_status == "escalate"`,
   `classify_action(door_reason)` decides IFF a genuine door (build_executor.py L641-644);
   a reversible mislabel is downgraded to `idle` (no alert). H21 does **not** touch this
   gate — it inherits it. So H21 only ever renders bodies for *confirmed* doors.
3. **The class is already computed but dropped:** `cat = verdict.category.value`
   (L659) exists but is only baked into the `detail` string (L675), never surfaced to
   `_alert_wall`. **H21's BUILD slice threads `verdict.category` through
   `ExecutorCycleResult` into `_alert_wall`** so WHY-DOOR renders from the independent
   predicate, not from the turn's own say-so.
4. **New fields:** the BUILD slice extends the turn return schema with `door_options`
   (required, ≥2), `door_context` (optional), `door_default` (optional), threads them
   through `ExecutorCycleResult`, and has `_alert_wall(kind="wall_escalated")` render
   WHAT (`door_reason`) + OPTIONS + CONTEXT + WHY-DOOR (`verdict.category`) + DEFAULT
   into `what`/`how`, demoting the log link to a supplementary trailer.

Net: `door_reason` supplies WHAT; the turn adds OPTIONS/CONTEXT/DEFAULT; the predicate
supplies WHY-DOOR; `_alert_wall` composes the five into the body. No new transport, no
change to the predicate gate, no change to the H19 keep-drawing loop.

---

## 4. The mutation-style CONTROL spec (R15 — controls must be able to FAIL)

**Control:** `assert_escalation_self_contained(body) -> None` (raises
`IncompleteEscalationError` on failure). It asserts, on the *rendered* NTFY body:

- an **atom-id token** is present in the WHAT line (the named subject);
- an **OPTIONS line** with **≥2 single-word-answerable choices** is present;
- a **WHY-DOOR class** drawn from the `OneWayDoorCategory` enum names is present.

**Named defect it must fire on (the real one):** feed the render path a turn return of
the historical half-escalation — `door_reason="I hit a one-way door, decide at your
cadence"`, **no `door_options`** — and assert the render path does **not** emit a
silent generic body. The mutation test asserts `IncompleteEscalationError` is raised
(control fires). A second mutation removes only OPTIONS from an otherwise-complete
payload → must also raise. Reverting the field-presence checks (making the guard a
no-op) must make both mutation tests fail — i.e. the guard demonstrably fires on its
own named defect (R15).

**Why it is not one of the three killer patterns:**

- **Not TAUTOLOGY.** WHY-DOOR is checked against the `OneWayDoorCategory` enum names,
  produced by `classify_action()` — a *different source* from the turn's own text that
  populated WHAT/OPTIONS. The checker never derives its expected value from the same
  string it validates; it asserts *structural presence from independent producers*.
- **Not FAIL-OPEN.** Missing/empty/whitespace `door_options`, a missing atom-id token,
  or an unrecognised door-class each **raise** — the empty/absent case is precisely the
  failure case, never a pass.
- **Not FAIL-SILENT.** If the guard itself is unavailable or errors, the send path must
  **not** proceed to a plain generic body. Reconciled with H19's fail-safe (*never
  silently drop a possibly-genuine door*): the resolution is **not** to suppress the
  NTFY (that would re-introduce the silent stall H19 killed) but to emit a **DEGRADED,
  loudly-marked** body — prefixed `INCOMPLETE ESCALATION — options/decision missing,
  open build-executor-log.md` — AND record a control failure (log + a failed
  mutation assertion in test). So the director is *always* paged (fail-safe holds) and
  the incompleteness is *never* silent (R15 holds). The degraded path is itself
  mutation-tested: guard-unavailable → assert the body carries the loud marker and a
  failure is recorded, never a clean generic body.

---

## 5. Worked example — rewriting the cited half-escalation

**Before (the real defect):**

```
I hit a one-way door, decide at your cadence.
See docs/observability/build-executor-log.md.
```

(No atom, no choice, no options, no class, no default. Unanswerable from a phone.)

**After (compliant, self-contained):**

```
[ACTION NEEDED] executor-wall_escalated
What: B4 is BUILD-blocked on a one-way door — opening Epoch 4 so B4's build can start. B4 stays FRAME-saturated (design done, 0 BUILD code) until an epoch it lives in is open.
Options (reply one word): OPEN (open Epoch 4 now; B4 + W1_2 + W4_2 begin building) / DEFER (keep B4 idle; revisit at the next epoch boundary) / DROP (retire B4 from the map).
Context: Epoch 3 is the currently-open epoch; B4 is filed epoch 4. Opening Epoch 4 also unblocks W1_2 and W4_2 (3 atoms). No epoch-4 atom builds until you open it; nothing else changes on DEFER.
Why it reached you (door class): VALUES_DECISION — opening a new epoch is the director's curriculum call (R13 / LAW A), never the twin's, never autonomous.
Default / non-blocking: NO safe autonomous default (a genuine door). Loop is NOT blocked — it is drawing other idle/FRAME/SITE work meanwhile and acts on your one-word reply at the next boundary. build-executor-log.md is supplementary only.
```

A one-word reply (`OPEN` / `DEFER` / `DROP`) resolves it from a phone with no terminal.
That is the acceptance bar.

---

## 6. L0→L3 Definition of Done

- **L0 (now):** this FRAME doc — schema, composition, control spec, worked example.
- **L1:** `door_options` (+ `door_context`, `door_default`) added to the turn return
  schema (`_RETURN_KEYS`) and prompt; `verdict.category` threaded through
  `ExecutorCycleResult` into `_alert_wall`; `_alert_wall(kind="wall_escalated")`
  renders WHAT/OPTIONS/CONTEXT/WHY-DOOR/DEFAULT and demotes the log link to a
  supplementary trailer.
- **L2:** the R15 control `assert_escalation_self_contained` built + wired into the
  escalation send path, with the degraded-but-loud fail-safe for guard-unavailable.
- **L3:** the full mutation suite green — (a) the real half-escalation raises
  `IncompleteEscalationError`; (b) OPTIONS-removed raises; (c) reverting the guard makes
  (a)/(b) fail (fires on its own defect); (d) guard-unavailable → loud degraded body +
  recorded failure, never a clean generic body; (e) a complete payload renders and
  passes; independence asserted (WHY-DOOR from `classify_action`, not turn text).
  Folded into H19's DoD as its content contract; epistemic PASS.

**Fold into H19:** H21 does not create a parallel mechanism — it **extends H19's own
`_alert_wall` content contract**. On close, H19's DoD gains "escalation body carries the
five self-contained fields; log link is supplementary; missing-decision/options FAILS a
mutation-tested control." H21 is the content half of the same escalation mechanism H19
built the channel for.

**Stays BUILD-GATED:** all L1-L3 work above touches `background/build_executor.py`,
`background/executor_governor.py`, `background/one_way_door.py` (read-only for the class),
and new tests — all BUILD/runtime code, **not writable now** (EPOCH_GATING R1). This doc
authors the design a BUILD fork executes later once the atom is opened.
