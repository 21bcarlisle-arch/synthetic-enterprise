# NEVER ASK WITHOUT RECOMMENDING — director ruling, 2026-07-29

**Source:** `docs/staging/done/from_rich_20260729_182313.md` (NTFY, director).
**Status:** ABSORBED — mechanism live and R15-proven both ways, not merely consumed.

## The ruling, verbatim

> You asked three questions and recommended nothing. Two of them weren't mine to
> answer — whether 2022 is a fact or a dial, and whether a trajectory should be
> scripted, are yours to decide with the evidence you have. From now: never ask
> without recommending, and default to acting on your own recommendation and
> telling me what you did. "Here's what I'm doing unless you object" — not "which
> would you like?" Only real money, real people, safety controls, and public
> claims in the company's name need me first. Forgiveness, not permission.

## What changed

Two distinct things, and it matters that they are distinct:

1. **A form requirement.** An ask without a recommendation is now a defect,
   always. Not "preferably paired with a view" — the bare ask is the thing being
   removed. The permitted shape is *"here's what I'm doing unless you object."*
2. **A narrowed escalation set.** Four categories need him first: **real money,
   real people, safety controls, public claims in the company's name.**

### Reconciling the four against the existing eight-item door list

The ruling names four; `background/one_way_door.py` enumerates eight. This is a
restatement, not a repeal — resolved as follows so no wall silently disappears:

| Ruling category | Existing door category | Disposition |
|---|---|---|
| Real money | `REAL_MONEY` | unchanged |
| Real people | `REAL_CUSTOMER_OR_MARKET`, `REAL_WORLD_COMMITMENT` | unchanged |
| Safety controls | `SECURITY_SAFETY_CONTROL`, `PLATFORM_ADMINISTRATION` | unchanged — repo/keys/settings change *what the machine is allowed to do*, which is a safety control by any reading, and was the director's own verbatim reservation on 2026-07-12 |
| Public claims | `IRRETRACTABLE_PUBLIC_CLAIM` | unchanged |
| — | `IRRECOVERABLE_DATA_LOSS` | remains a **wall** (an irreversible act), but is not an *asking* category: don't do it, rather than ask about it |
| — | `VALUES_DECISION` | remains the director's by authorship (the Epoch-4 fitness function). Not a blocking question: recommend, and he overturns |

Net effect on behaviour: the door list is unchanged; what changed is that
everything *outside* it must now arrive as a decision already taken.

**SUPERSEDED same evening by `DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY_2026-07-29.md`
item 5** (confirmed directly on NTFY, `docs/staging/done/from_rich_20260729_192946.md`:
*"'safety control' means protecting a real person, real money, or a public claim in the
company's name. A control that stops a simulation is not one — re-tag those and release
them."*). The row above reading `SECURITY_SAFETY_CONTROL`/`PLATFORM_ADMINISTRATION` as
"unchanged... a safety control by any reading" is now WRONG and kept here only as the
historical record of what this doc believed a few hours earlier. The reserved set actually
enforced in `background/one_way_door.py` (as of commit landing this note) is: `REAL_MONEY`,
`REAL_WORLD_COMMITMENT`, `IRRETRACTABLE_PUBLIC_CLAIM`, `REAL_CUSTOMER_OR_MARKET`, and the new
`LIVE_CREDENTIAL_EXPOSURE` (split out of `PLATFORM_ADMINISTRATION` with its real-world
consequence named: a leaked live credential lets someone who is not the director act, and
spend, as him). `SECURITY_SAFETY_CONTROL`, `VALUES_DECISION`, `IRRECOVERABLE_DATA_LOSS`, and
the settings-half of `PLATFORM_ADMINISTRATION` are now RELEASED — still classified (a verdict
carries `advisory_category`), never gated. See `one_way_door.py`'s own module docstring for
the live, authoritative statement; this file is not it.

## The mechanism (MAKE_IT_STICK)

Prose-only rules here have a perfect record of decaying. `background/recommendation_guard.py`
is the mechanism, wired into `background/ntfy_utils.py::send_ntfy` — the one channel
the director actually reads.

- A message that **asks** and **recommends nothing** raises `RecommendationRequired`
  and is never posted.
- The carve-out is **delegated to `one_way_door.classify_action`**, not re-enumerated
  (DON'T ACCRETE) — the reserved list stays in exactly one place.
- **Fail-loud, never fail-silent** (R15): a blocked message raises at its call site.
  It is never dropped or silently rewritten; a lost alert would be worse than the
  defect being fixed.
- **Blocking is safe here, measured not assumed:** at wiring time there were 6
  `send_ntfy` call sites across `background/` + `tools/`, none containing a question
  mark. Blast radius on existing callers: zero.
- **R15 mutation-proven both ways.** `check_message` → always-return: 7 tests fail
  (including the live-wiring test). Always-raise: 11 fail (every permit case, and
  every director-reserved carve-out). Restored: 17 pass.

### One fail-open closed on the way

The carve-out is only as good as the classifier behind it. `"Approve £4,000/month
of real spend on the Elexon data feed?"` matched **nothing** in `REAL_MONEY` — the
commonest phrasing of a real purchase was absent, so the wall read PROCEED on real
spending. Patterns widened (approve/spend/subscription/credit-card/out-of-pocket).

Deliberately **not** added: a bare currency-amount regex. This project prints
simulated £ figures on every surface, so `[£$]\d+` would fire constantly on the
simulation's own output — a control false-positive that jams the pipeline is its
own defect. Every added pattern pairs money with a real-world spend context.

Widening detection is safety-**increasing**, so it needs no director authorisation:
the console convention governs safety-*reducing* changes.

---

# The two questions, now answered

The director declined these as not his. Both are decided below on the evidence,
per the ruling.

## Q1 — Is 2022 a fact or a dial?

### DECISION: a **fact**. It is not a dial and may not be tuned.

**Evidence** (SPINE_3 DISCOVER, commit `52fc590bb`, verified against disk):
wholesale gas today is **replayed real history** — `gas_prices_history.py:1-27`
(FRED `PNGASEUUSDM` TTF proxy), `:73-90` (monthly value repeated daily),
`sim/gas_data/nbp_sap.csv` (3,446 records, 2016-01-01..2025-06-07), read at the
wall by `sim_interface.py:313-315`. No branch, no month table, no date-keyed
multiplier constructs the crisis.

The 2022 inversion is a **measured property of the real record**, computed this
pass rather than recalled: detrended shape spread is positive in every year
2016-2024 (+0.009..+0.605) and negative in **exactly one** — 2022, at −0.387.

**Why that settles it.** R13 says the baseline world (real history +
externally-calibrated generators) may change *only* for fidelity-to-reality
reasons, decided blind to company P&L. 2022 being inverted **is** reality.
Treating it as a dial would mean tuning the world's factual record, which is the
precise thing R13 forbids.

**The dial that genuinely exists, and is the director's:** *which window the
company lives through*. Running the company through 2021-22 rather than 2017-18 is
a named, versioned **curriculum** decision (R13), and his by right. The *shape* of
2022 is not on that menu.

## Q2 — Should a trajectory be scripted?

### DECISION: **No.** Generate it from state; do not script it.

**Evidence:** the one hardcoded trajectory (`crisis_2021_22.yaml:26-33`) is
**inert**. The only spine importer outside `spine.py` is `run_rotation.py:58`
(ledger stamping), so no generator consumes `paths_as_of`. Nothing is lost by
declining to wire it up — this decision forfeits no working capability.

**Reasoning:**

1. **A scripted path is unfalsifiable.** It can only ever produce the crisis its
   author already imagined. The COUPLED TRIAD rule — *no company capability is
   complete until it has faced a world that can defeat it* — cannot be satisfied by
   a world whose defeats were all authored in advance.
2. **It is a standing invitation to R13 drift.** The agent controls both sides of
   the wall. A scripted trajectory is exactly the surface on which "the world" gets
   quietly adjusted until company results look right.
3. **The generated form is strictly better and already designed.** The SPINE_3
   FRAME's stock-and-flow — fill-dependent injection/withdrawal bounds running in
   *opposite* directions — crosses the spread through zero with **no calendar
   term**, and the same mechanism produces the post-refill collapse B6 needs. It can
   yield inversions nobody designed. That is the entire point.

**What I did with it:** recorded as the standing answer; the inert
`crisis_2021_22.yaml` is **queued** for removal rather than deleted here. This tick
is explicitly LANE-3 DISCOVER/FRAME with BUILD epoch-gated, and per
SELF_INTERRUPT_DISCIPLINE my own findings queue by default. Flagging plainly: the
decision is made, the one-line deletion is not yet executed.

---

## The honest note

The director is right that these were mine, and the failure has a shape worth
naming: **both questions were already answered by evidence I had gathered myself
in the same pass.** The DISCOVER work established that gas is replayed real
history and that the scripted path is inert — which settles Q1 and Q2
respectively. I gathered the evidence, then asked anyway.

That is not a knowledge gap. It is a reflex to seek ratification, which is what
PROCEED_BY_DEFAULT and MAKE_IT_STICK have both already ruled against, and what the
100:1 acting bias exists to overcome. Hence a mechanism on the channel rather than
another line of prose.
