# CLAUDE.md DECAY AUDIT — first performance, 2026-08-12

**Answering:** `ADVISOR_FINDINGS_CLAUDE_MD_DECAY_AUDIT_2026-08-07.md` §P1/§P2/§P3.
**Doctrine under audit:** MAKE_IT_STICK — *"a rule lives in CLAUDE.md AND as enforced code, or not
at all; prose-only is worse than no rule (illusion of control)."*

CLAUDE.md commits the project to a decay audit at every epoch boundary. Searched
`docs/observability/` on 2026-08-07: zero artefacts. This is the first one. It is the record, not
a claim — every disposition below names the mechanism's location, or names the search that came
back empty.

---

## 0. State at audit time

| | |
|---|---|
| CLAUDE.md | 34,734 chars / 128 lines (limit 35,000 / 200) |
| Headroom | **266 chars** — 0.8% |
| `background/claude_md_integrity.py` | green |
| Commit gate on a CLAUDE.md-only commit | ran **one** test, and not the integrity control |

§P1 (over the ceiling) was closed on 2026-08-10 by `a8a5d9372`, which landed a trim that had
already been written. §P2 was **half**-closed the same day by OPS5, which added `CLAUDE.md` to the
gate's `CANON_SURFACE_FILES` — but pointed it at `test_interim_bypass_retirement.py` only. Measured
this turn:

```
>>> select_targets(['CLAUDE.md'])
['tests/tools/test_interim_bypass_retirement.py']
```

So the size ceiling still could not fail a commit gate on the exact commit shape that breached it
(`52693115b`, a CLAUDE.md edit). The guard existed, the trigger existed, and they were not wired to
each other. Closed this turn — see §4.

---

## 1. Method

Every rule in CLAUDE.md was read and searched for an enforcing mechanism. A rule is **MECHANISED**
only if a named module or test would FAIL on its violation. "The doctrine is mentioned in a
docstring" is not a mechanism. Where the search came back empty, that is stated as a search, not
as an absence of effort.

Five dispositions, not the doctrine's two. The doctrine offers *mechanise or delete*; auditing found
three cases it did not anticipate, and using them silently would be its own decay:

- **MECHANISED** — code + test named. Stays.
- **DELETE** — prose-only, and there is a code point where the mechanism *would* live. Deleting the
  text changes nothing about the running system, because the rule was never in effect.
- **STALE FACT** — the claim is checkable and wrong. Fix or delete the claim.
- **OUT-OF-TREE** — the rule's enforcement point is not in this repository, so no in-repo mechanism
  can reach it. See §5.
- **BEHAVIOURAL** — the rule's subject is a judgment made *inside a turn*, with no artefact and no
  code point to check it against. See §5b.

The last two are the ones that could become an escape hatch, so the bar is stated and held: a rule
qualifies only if there is **no code point at which the check could be written**. Every rule deleted
in §3 fails that bar — each one had an obvious home (the notifier, the digest, `send_ntfy`) and
simply never had anything put in it.

---

## 2. MECHANISED — verified this turn, stays

| Rule | Mechanism | Verified |
|---|---|---|
| RULE 0 prime directive | `supervisor.py::_self_refill_draw` rung ladder → `_rule0_harden_draw` floor | rungs read; every lane falls through to a non-empty draw |
| Four reserved classes | `background/one_way_door.py` (sole enumeration) | present, enumerates money/people/claim/safety |
| Permission machinery stays deleted | `tests/background/test_gate_authorization.py::test_the_permission_surface_is_gone` | present |
| Never ask without recommending | `recommendation_guard.check_message`, called from `ntfy_utils.send_ntfy` **first**, ahead of the pytest guard | call site read at `ntfy_utils.py:158` |
| `action_needed` refuses non-reserved asks | `background/action_needed.py` | present |
| Twin is a voice, not a hand | `director_twin._default_invoke` — no permission bypass, `--tools=`, scratch cwd | read at `director_twin.py:101` |
| Level move must be recorded | `gate_authorization.record_level_up_self_certified` + `tools/level_promotion_gate.py` | both present |
| Hook-bypass is a wall | `tools/surgical_land.py` | present |
| Epistemic wall | `tests/architecture/test_epistemic_wall_ratchet.py`, in the gate's always-run `CONTROL_TESTS` | present and wired |
| R14 no figure without its clock | `generate_dashboard_data._check_basis_labels_present` | read at `:1871` |
| R15 controls must be able to fail | mutation tests throughout; `claude_md_integrity`'s own suite is the model | present |
| R17 tick never rests | `supervisor::_forward_discovery_draw` wired into `_self_refill_draw` + `_is_drained_and_gated` | read |
| Coupled triad | `tests/test_coupled_triad_gate.py` | present |
| Regulation is time-indexed | `company/compliance/domain_invariants.py` — 8 × `effective_from` | counted |
| Director input is channel-tagged | `director_input_log` imported live by `ntfy_responder.py:622` and `ntfy_utils.py:190` | read |
| Security profile floor | `background/secrets_location.py`, `background/egress_allowlist.py` | present |
| Tree-lock discipline | `tree_lock()`; the never-across-`git commit` rule is a real deadlock, observed | present |
| CLAUDE.md size + dangling pointers | `background/claude_md_integrity.py` + its suite | green |

---

## 3. PROSE-ONLY — deleted this turn

Each of these was searched for. Each search came back empty. **None of them has ever been in
effect**, so removing the text changes nothing about the running system and makes the file honest.

### 3.1 The NTFY 60-minute bounded-silence rule
> *"While actively working a phase, if 60 minutes pass with no NTFY, send ONE line… clock resets on
> any NTFY."*

**Searched:** `background/notify.py`, `background/ntfy_utils.py` for any elapsed-time bound, any
`3600`, any `bounded silence`. **Empty.** No timer, no clock, no reset. R5 (transition-only
alerting) is the real rule, is stated separately in the R-list, and stays.

### 3.2 MAKE_IT_STICK's own anti-decay metrics
> *"Anti-decay metrics, alarmed every digest: turns waiting on a human (target ZERO bar the four
> reserved), escalations later judged reversible (target ZERO), idle turns with atoms available."*

**Searched:** all of `background/` and `tools/` for any of the three metric names. **Empty.** There
is no digest line, no counter, no alarm. The clause instructing the reader to mechanise rules was
itself the least mechanised text in the file.

The doctrine sentence it sits in — *a rule lives in CLAUDE.md AND as enforced code, or not at all*
— is retained, because this audit and `claude_md_integrity.py` are its mechanism.

### 3.3 P-2, director-repeat auto-escalates
> *"the same complaint/ask voiced twice (any channel) becomes an automatic P1 proposal."*

**Searched:** for any repeat detector across channels. **Empty.** Nothing counts a complaint twice.

### 3.4 P-5, the freshness stamp
> *"PRIORITIES.md carries 'last director review: <date>'… if >7 days stale, request a review in the
> next NTFY."*

**Searched:** for any staleness check on that stamp. **Empty.** And the rule is *currently
breached*: `PRIORITIES.md:3` reads `last director review: 2026-08-03` — nine days. Nothing fired.
This is the cleanest possible demonstration of the doctrine: an unenforced rule is not a weak rule,
it is not a rule.

Not mechanised instead, deliberately: the mechanism would be an NTFY nagging the director to
re-rank, which is an ask on his path — the shape `NTFY_IS_THE_DIRECTOR` names as itself a defect.

### 3.5 LATEST.md before NTFY
> *"Always update and commit LATEST.md before sending NTFY. If stale, fix the root cause."*

**Searched:** `send_ntfy` for any LATEST staleness gate. **Empty** — it checks
`recommendation_guard` and the pytest guard, nothing else. `tools/stamp_latest_md.py` is a stamper
invoked by the publish pipeline, not a gate on the alarm channel.

Not mechanised instead, deliberately: a staleness check inside `send_ntfy` is a **fail-closed check
on the alarm channel**, which would suppress the alert that says publishing is broken exactly when
publishing is broken. That is the fail-silent pattern R15 names. R1 (consumer-verified completion)
already carries the substance.

### 3.6 The multi-atom concurrent-grant paragraph
> *"self-refill can grant N>1 atoms/cycle… one Agent fork per atom."*

The mechanism (`_maturity_map_draw_concurrent`) exists, but `MAX_CONCURRENT_FORKS = 1` since
2026-08-03 makes an N>1 grant arithmetically impossible: the draw does `build_atoms[:1]` and every
later lane gets a budget of zero. The paragraph described a capability that cannot occur and
**contradicted the TOKEN BUDGET rule ten lines below it**. The budget rule wins; the paragraph goes.

### 3.7 The NEXT_PHASE.md paragraph
> *"NEXT_PHASE.md proposals: must name the gap or roadmap item served…"*

`NEXT_PHASE.md` **does not exist** — not at the repo root, not under `docs/`. A rule governing the
contents of a file that is not there.

### 3.8 Three key-learnings that outlived their subject

- *"REVIEW_GATE must only match on actual pane idleness."* The REVIEW_GATE matcher is **gone** —
  the only surviving mentions are two test docstrings citing the *class* of bug ("must match
  idleness, not prose mentioning the string") as a named failure mode. The class lives where it is
  used; the instance rule governs nothing.
- *"sim_runner TimeoutExpired must be caught."* It **is** caught, at `sim_runner.py:98` and `:244`.
  The code holds the learning; the reminder is redundant.
- *"Staging-watcher notifies Rich, not the agent. Poll `docs/staging/` yourself."* Polling is
  mechanised — `worker_tick` draws through `find_work`, and `worker-tick.path` wakes on a new
  staged file within seconds. The instruction to remember to poll is obsolete.
- *"Local models confabulate endpoints."* Exhortation with no mechanism, on a lane (qwen3:14b) that
  is now marginal. Deleted per doctrine.

---

## 4. STALE FACTS — fixed this turn

| Claim in CLAUDE.md | Reality | Action |
|---|---|---|
| `session_watchdog.py::MAIN_SESSION_MODEL` | `session_watchdog.py` was **deleted** 2026-07-17 (OPS1 collapse, 1,380 lines). The live seat manager is `worker_seat.py`, `MODEL` at `:37`. | repointed |
| `ntfy_responder.py` writes inbound messages **(>25 chars)** | The length gate was **removed**; `ntfy_responder.py:377` records "what used to be here: a `len(message) < 25` gate". The claim also contradicted *"no PIN, no minimum length"* three paragraphs later, in the same file. | threshold dropped |
| `supervisor.py:326-355` (the in_progress re-surface scanners) | `:326` is `_is_daemon_marker`. The scanners are at `:362-366`. Line numbers rot; symbols do not. | repointed to symbol names |
| "88 atoms and a website" | `maturity_map.yaml` holds **296** atoms | count removed — it is live state, and CLAUDE.md's own DON'T-ACCRETE rule says live status goes to `LATEST.md`, never here |
| "24,845 tests collected" | **26,285** collected this turn | same; removed |

The last two are the same defect twice: CLAUDE.md instructs that live status lives in
`docs/status/LATEST.md` and then carries two live counts itself. Both were wrong.

---

## 5. OUT-OF-TREE — a finding about the doctrine, not an exemption

Two rules survive with no in-repo mechanism, and mechanising them here is **not possible**, not
merely unbudgeted:

1. **The agent may never widen its own sandbox profile** (security profile, `--dangerously-skip-permissions`
   scope, credentials, egress allowlist).
2. **Routine creation must set minimal `allowed_tools` + empty connectors, then re-fetch and diff
   before first run** (R1). Searched for any `RemoteTrigger`/`allowed_tools` handling code:
   **empty** — because a Routine's config lives on Anthropic's servers, not in this tree.

A control an agent can edit is not a control on that agent. Both of these govern the boundary
between the simulation and the real machine, which is the one place this repo's own doctrine
("everything inside the simulation is reversible") does not apply.

**Recorded so the next audit does not re-derive it:** the doctrine's "mechanise or delete" is
correct for every rule whose subject is inside the repo, and under-specified for the handful whose
subject is the repo's own real-world capability surface. Deleting those because they cannot be
mechanised in-tree would remove the only statement of the boundary. They stay, compressed, and
flagged in CLAUDE.md itself as OUT-OF-TREE so the next reader does not re-open the question.

---

## 5b. BEHAVIOURAL — retained, and why this is not the escape hatch

One rule and one rule-set survive as prose because the decision they govern happens inside a turn
and leaves no artefact to check:

- **SELF-INTERRUPT DISCIPLINE** — "your own findings get staged-doc disposition: QUEUE by default,
  INTERRUPT only when the machine is genuinely blocked." There is no code point. The choice is made
  by the reader at the moment of noticing, and the only trace it leaves is the thing it produced.
  Its *reporting* half ("report atoms-below-target every digest") **did** have a code point, had
  nothing in it, and was deleted — see §3.2's sibling. Note also that `naive_organ.py:562` carries a
  regex to *parse* an "N atoms below target" claim that no code anywhere emits: a consumer built for
  a producer that was never written.
- **The two design-lens sets** (portability, scale-readiness) — review lenses applied at phase
  design, explicitly framed as such in their own docs.

**Why this is not a loophole.** The bar is "no code point exists", not "no code was written". Each
rule deleted in §3 had an obvious home and an empty one: the 60-minute bound belonged in the
notifier, the anti-decay metrics in the digest, P-5 in a staleness check, LATEST-before-NTFY in
`send_ntfy`. That is the difference between a rule nobody enforced and a rule nothing *can*.

Both retained items were also compressed rather than left at full length — prose that survives an
audit should still have to earn its characters.

---

## 6. What was built alongside this audit

**The size ceiling can now fail a commit gate.** `tests/tools/test_claude_md_integrity.py` added to
`CANON_SURFACE_TESTS` in `tools/pre_commit_test_gate.py`, so any commit touching `CLAUDE.md` runs
the integrity control at commit time rather than discovering the breach in the publish suite hours
later — which is what happened for four days from 2026-08-03.

**Proven able to fail** (R15 — a gate extension that passes on everything is the fail-open pattern
this project names). `tests/tools/test_pre_commit_gate_canon_surface.py`:

- asserts `select_targets(['CLAUDE.md'])` contains the integrity test — fails if the wiring is
  removed;
- mutation: builds an over-limit CLAUDE.md in a tmp tree and asserts the selected test actually
  goes red on it, so the selection is proven to be a *live* control, not a name in a list;
- asserts the trigger stays narrow — an unrelated docs commit still selects nothing.

`MAX_CHARS` was **not** touched. It is 35,000, as doctrine.

---

## 7. Result — measured, not projected

| | Before | After |
|---|---|---|
| CLAUDE.md | 34,734 chars / 128 lines | **32,684 chars / 119 lines** |
| Headroom under the 35,000 ceiling | 266 chars (0.8%) | **2,316 chars (6.6%)** — 8.7× |
| Prose-only rules with an empty code point | 10 | **0** |
| Stale facts | 5 | **0** |
| Tests run on a CLAUDE.md-only commit | 1, and not the integrity control | **2, including it** |

Net −2,050 chars, which understates the trim: **−3,750 chars deleted or compressed**, against
**+1,700 added** — the tiering rule, the note recording that the ceiling is now gated, and the
pointer to this audit. The file is smaller *and* says more that is true.

Verified this turn:

```
$ python3 background/claude_md_integrity.py
CLAUDE.md integrity OK

$ python3 -c "from tools.pre_commit_test_gate import select_targets; print(select_targets(['CLAUDE.md']))"
['tests/tools/test_claude_md_integrity.py', 'tests/tools/test_interim_bypass_retirement.py']

$ python3 -m pytest tests/tools/test_claude_md_integrity.py tests/tools/test_pre_commit_gate_canon_surface.py
56 passed
```

`MAX_CHARS` is unchanged at 35,000.

## 9. Next audit

The trigger in CLAUDE.md is "every epoch boundary", which produced zero audits in the file's
lifetime — a cadence with no clock is the same defect class as the rules deleted in §3. This audit
is dated; the next one should be triggered by *this file's* age rather than by an epoch boundary
nobody declares. Flagged, not built — mechanising the audit cadence is a separate atom, and
building it silently inside a trim would be the accretion `DON'T ACCRETE` forbids.
