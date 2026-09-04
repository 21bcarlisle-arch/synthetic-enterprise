**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: what the unscreened PROPOSAL side of a `since_field` actually does

*Delivery seat, 2026-09-04, claim `decide-the-proposal-side-of-a-low-water-episode-field-2026-09-04`.
Written BEFORE running any of it. Predictions first, answers below, corrections kept beside them.*

The direction asks one question: should a `since_field` **proposal** that is orderable but is not a
recorded instant (`0`, a negative epoch, `True`, `NaN`) be treated as **absent**, or kept as today?

`guard_episode` screens the PRIOR side only (`_is_start_to_remember`, landed 2026-09-04). Of the
proposal it asks only *can I order this?*. I believe that asymmetry has three consequences nobody
has measured. I am writing down what I expect each to be, then measuring.

## The predictions

**P1 — a zero proposal BEATS a good prior.** `since_fields` is LOW-water, so with
`prev={"t": 1.7e9}` and `new={"t": 0}` the comparison `1.7e9 <= 0` is False and the guard writes
**`0`**. I predict the guard does not merely *tolerate* an unrecordable proposal — it *prefers* it,
because zero is the earliest instant orderable. If so, the framing "the carrier is not repaired" is
too mild: the guard actively converts a healthy episode into a 1970 one on a single bad write.

**P2 — `sim_runner` re-proposes a persisted zero.** Its proposal is
`first if isinstance(first, (int, float)) else stamp` (`sim_runner.py:208`) — an `isinstance` screen
with no positivity and no `bool` test. I predict a persisted `first_failure_ts: 0` survives a
failure write unchanged, and so does `True`.

**P3 — the RUNG 1d producer-starvation reader is a FIFTH hand-roll and renders the 1970 age.**
`supervisor.py:4380` computes `outage = (now - first_ts) if isinstance(first_ts, (int, float))
else 0.0`. I predict `first_failure_ts: 0` yields an outage near **497,000 hours**, that it clears
`PRODUCER_STARVED_MIN_AGE_SECONDS`, and that the PRIORITY ZERO page therefore fires and prints that
figure. This is the same defect the `recorded_instant_seconds` door closed at `_episode_phrase`, at
a surface the sweep did not cover.

**P4 — `ntfy_utils` re-proposes a persisted zero.** `previous.get("since_epoch", now)` is echoed
straight off disk with no screen. I predict the persisted `since_epoch` stays `0` across a failure
write, and that the derived `since` string keeps whatever was on disk beside it — including
`1970-01-01T00:00:00Z` — because the derivation is skipped exactly when the epoch is unrecordable.

**P5 — the misdeclaration refusal does NOT fire on a cold start.** The prior screen `continue`s
before the proposal is type-checked, so I predict `guard_episode({"t": None}, {"t": "banana"},
since_fields=("t",))` returns `{"t": "banana"}` and raises nothing — while the same call with a
live prior raises `EpisodeFieldTypeError`. If so, the guard's stated "deterministic property of the
call site that the first test run surfaces" is false precisely on the first run.

## What I will do with each answer

P1 true → screening the proposal is not a preference, it is a repair, and it lands.
P1 false → I have misread the ordering and the whole case has to be rebuilt from what it does.

P5 true → I will **not** widen where `_refuse` fires in this turn. It is a real hole, but making a
data-dependent value reach a raise inside the failure path of the pipeline the guard monitors is
the exact harm the guard's fail direction exists to prevent, and it deserves its own evidence. It
gets a finding, not a rider.

## The decision I expect to land, stated before the numbers

Treat an orderable-but-not-recorded-instant PROPOSAL as **absent**. With a recorded prior the prior
stands; with no recorded prior the field is written as `None`. It cannot under-report, because the
only proposal it declines is one that dates the episode to before anything here ran, and
`episode_age_seconds` already answers `None` to that value — so **no rendered figure changes** and
the carrier stops re-proposing a lie forever. `_refuse` keeps firing exactly where it fires today.

If P1 is false this paragraph is wrong and stays here anyway.

---

## MEASURED (filled in after, beside the predictions above)

All five confirmed. Two were **understated** and one was **wrong in its detail** — kept here.

| # | predicted | measured | verdict |
|---|---|---|---|
| P1 | a `0` proposal is written back | `guard_episode({"t": 1.7e9}, {"t": 0})` → `{"t": 0}` | **CONFIRMED, and stronger** |
| P2 | `sim_runner` re-proposes a persisted `0` | persisted `0` → written `0`; `-1` → `-1`; `True` → `True` | **CONFIRMED, and stronger** |
| P3 | RUNG 1d renders ~497,000h and fires | fires at **496,815.1h** for `0`, `-1` *and* `True` | **CONFIRMED** |
| P4 | `ntfy` re-proposes `0`; `since` keeps its 1970 string | `since_epoch=0`, `since='1970-01-01T00:00:00Z'`, both intact | **CONFIRMED** |
| P5 | the refusal does not fire on a cold prior | `({"t": None}, {"t": "banana"})` → `{"t": "banana"}`, no raise | **CONFIRMED** |

**P1 was too mild and the framing that came with it was backwards.** I predicted an unrecordable
proposal would *survive*. It does not survive — it **wins**. `since_fields` is LOW-water, so `0` is
the earliest instant orderable, and the guard *preferred* it to a healthy 2026 start. The same in
the other representation: a `1970-01-01` ISO proposal took the field from a live `2026-09-04T10:00`
prior. So the direction's stated risk — that screening the proposal "could turn a data-dependent
value into a silent field-clear" — is the opposite of what screening does here. **With a start on
the prior side, screening the proposal makes the prior STAND.** It is strictly more remembering
than what was there.

**P1 was wrong about the membership of the set.** I expected `True` and `NaN` to be in it. They are
not: `_episode_key` returns `None` for both, so both were already refused as unorderable. The
orderable-but-not-recorded set is exactly the non-positive epochs and their ISO spellings. That
narrows the change and is why it cannot touch `_refuse`.

**P2/P3 were understated in the same direction.** `sim_runner`'s screen is
`isinstance(first, (int, float))`, and `isinstance(True, (int, float))` is `True` in Python — so
`True` is adopted, persisted, and read by RUNG 1d as 496,815 hours. That is the exact value
`episode_monotonic._is_num` has a docstring about refusing, arriving through a door two modules
away.

**P3's real harm is not the figure.** `outage > PRODUCER_STARVED_MIN_AGE_SECONDS` (30 min) is
satisfied by the broken stamp *alone*. A producer that had failed three times in two minutes
cleared the bar and drew a PRIORITY ZERO starvation page. The direction's premise — "the render is
now closed, nothing PUBLISHES 1970 from it any more" — is true of `_episode_phrase` and false here:
this reader is a fifth hand-roll the sweep did not cover.

**P4's severity is lower than it reads, and that is worth saying.** `.ntfy_delivery_state.json`'s
`since` has **no reader in this repository** — grep returns only its writer. It is a carrier and a
human record, not a rendered surface. So P4 is durability, exactly as the direction said; P3 is not.

**P5 stands and gets a finding, not a rider**, as pre-committed. The prior screen `continue`s
before the proposal is type-checked, so `EpisodeFieldTypeError` — the guard's one defence against
a field that "reads as protection and is not" — is silent on precisely the cold-start run the
docstring says would surface it. Not fixed here: making a data-dependent value reach a raise inside
the failure path of the monitored pipeline is the harm the guard's fail direction exists to
prevent, and it needs its own evidence.

### The decision, unchanged by the numbers

Landed as pre-registered: an orderable-but-not-recorded-instant **proposal** is treated as absent.
Six mutations — reverting each of the four repairs, plus the screen answering `True` to everything,
plus the rendered-string leg — are each killed by a named control.

