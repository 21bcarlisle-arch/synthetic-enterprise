# THE EXTERNAL-TRUTH WALL — one law, five altitudes

**Atom:** `W4_3_external_truth_wall` (maturity_map.yaml, epoch 2, L0→L2, lane `W4_the_wall`,
constitutional). **Source:** `docs/staging/done/RETRO_ACTIONS_THE_THREE_GAPS.md`, ATOM 3.
**Author:** FRAME/constitutional-authoring pass, 2026-07-16. This doc is the artifact the
atom's DoD asks for: the law named, designed, and tied to the mechanisms that already
enforce fragments of it.

---

## 0. The law, stated once

> **No component's self-report counts as evidence of its own success. Every success
> claim — a turn ran, a check passed, an alarm can fire, a rule is enforced, work
> advanced, a level was reached — must be verifiable by a signal the component
> cannot itself generate. A self-certified success is a theatre control by
> construction.**

This is a **WALL** (Rule 0's terminology), not a dial: it is never traded off, widened,
or paused for velocity. It sits beside the epistemic wall (§3) as a second, orthogonal
boundary this project enforces — the first says the company cannot read the SIM's
internals; this one says **no part of the system may read its own claim as if it were
an independent check of that claim.**

## 1. Why this project keeps rediscovering the same failure

Eleven honest retrospectives exist. Read across them, five "different" failure themes
recur:

| Theme | Named instance |
|---|---|
| T1 fail-silent controls | a watchdog/liveness signal the watchdog itself refreshes; a control that passes when unavailable (R15's FAIL-SILENT pattern) |
| T2 shared-domain coupling | RNG draws sharing a substream so one subsystem's new draw silently shifts another's (the 01:09Z incident, C-S2) |
| T3 local-vs-global truth | a per-retro "strike" counter that never accumulated across retros, so two independent incidents both discovered "third strike" for the same class six days apart |
| T4 prose-decay of rules | exhortations ("fan out," "don't idle," "ntfy me when blocked") that evaporated, versus mechanisms (the Stop hook, the idle-turn counter) that held (MAKE_IT_STICK) |
| T5 transport-vs-content trust | an NTFY message or injected wake text treated as if arriving-on-a-channel were the same as being-authorized (R7/R8) |

Filed separately, these look like five unrelated engineering lessons — a monitoring
lesson, a concurrency lesson, a bookkeeping lesson, a process lesson, a security
lesson. **They are not five lessons. They are one failure, observed at five different
altitudes of the same stack:**

- T1 is the failure at the **control** altitude: the checker trusts its own liveness.
- T2 is the failure at the **state** altitude: a subsystem trusts a shared draw as
  independent when it isn't.
- T3 is the failure at the **aggregation** altitude: a count trusts its own local
  scope as if it were the global truth.
- T4 is the failure at the **rule** altitude: a policy trusts its own prose as if
  restating it were the same as enforcing it.
- T5 is the failure at the **channel** altitude: a directive trusts its own arrival
  as if transport implied authorization.

In every case the same substitution happens: **an internally-generated signal (I
said X, I ran, I counted, I was told) stands in for an externally-verifiable fact (a
commit landed, a mutation fired, a global tally, a console-authenticated turn).**
The retrospectives kept "fixing" the instance (patch the watchdog, name the RNG
substream, build one register, add R7) without ever naming the substitution itself —
which is exactly why the class kept re-arriving wearing a new costume. Naming it once,
here, is the point of this atom: the next incident should be recognized as *this*,
not relearned as a sixth theme.

## 2. The test

Before any claim (a turn succeeded, a control passed, a level moved, a rule holds, a
message is a directive) is allowed to close a loop, gate a decision, or count as
evidence, ask exactly one question:

> **Is this signal internally-derived, or externally-verified?**

- **Internally-derived** — produced, computed, or asserted by the same component
  whose success it purports to prove (a daemon's own "I'm alive" flag; a fork's own
  free-text claim of the level it reached; a message's mere presence on a channel;
  a rule restated in prose with no code path enforcing it). **This does not count as
  evidence.** It may be logged, displayed, or used as a hint, but it cannot close a
  gate, satisfy a DoD, or silence an alarm.
- **Externally-verified** — produced or checked by something the component cannot
  itself steer: an independent clock, a git commit on origin, a mutation test that
  injects the named defect and confirms the control fires, a re-fetch by the actual
  consumer, a console-authenticated human turn, a global register computed from raw
  data rather than trusted from a claim. **This is what may count.**

The test is not "is there a check" — a tautological check (F1_epistemic_verifier's own
worry, R15) can exist and still fail this test if the checked value is derived from
the same source it is checking. The test is independence of origin: **could the
component that makes the claim also make the check pass without the underlying thing
being true?** If yes, the signal is internal and worthless as evidence, no matter how
official it looks.

## 3. Relation to the epistemic wall (SIM ⟂ company)

The project already has one constitutional wall: **the company cannot see inside the
SIM** (`CLAUDE.md` §Architectural Laws, `company/interfaces/sim_interface.py`,
`tools/epistemic_verifier.py` / atom `F1_epistemic_verifier`). That wall is about
*information the company is not entitled to* — future data, internal generator state.
It answers "could a real UK energy supplier know this?"

The External-Truth Wall is a **different axis, not a restatement**: it is not about
what a component may *see*, it is about what a component's own *say-so* may be trusted
to *prove*. The epistemic wall would still be necessary even if every component were
perfectly honest about its own success; the External-Truth Wall would still be
necessary even if the SIM/company boundary were airtight. They compose: the epistemic
wall governs the **visibility** of a signal (may this reader see it at all), the
External-Truth Wall governs the **provenance** of a signal (may this signal's own
source vouch for it). A signal can pass the epistemic wall (it's a legitimate
observable) and still fail this one (the observer is grading its own homework) —
exactly what F1/F2 (§5) found in the map-write path.

Both are WALLS under Rule 0: never crossed, no exceptions, and both are checked by
`tools.epistemic_verifier` at phase close (currently scoped to the SIM/company
barrier; extending its remit to the External-Truth Wall's structural pattern —
self-report vs. independent check — is a natural next BUILD slice, logged as an open
item in §8, not done in this FRAME pass).

## 4. The five facets this project already built — read as ONE wall

Each of these was authored independently, in response to its own incident, with no
shared name. Read together they are facets of §0-1, not five separate rules:

| Facet | What it actually enforces (retrospectively) |
|---|---|
| **R1**, consumer-verified completion | An artifact is done only when its *external consumer's own fetch* confirms it — never the producer's claim that it shipped. |
| **R9**, evidence before narrative | An incident report may not assert a claim (especially one implying an external actor) until the most direct available *external* evidence has been checked — a narrative is not evidence for itself. |
| **R11**, verify to the rendered value | "Done" for a user-visible change means the *live fetched* page, never the code, the deploy log, or the author's description of the deploy. |
| **R15**, controls must be able to FAIL | A control counts as evidence only once a *mutation test* — an independent, adversarial exercise the control did not design — proves it fires on its own named defect. Untestable-by-mutation controls (LLM judges) require *outcome*-testing instead; no verdict-organ is exempt. |
| **The naive organ** (`docs/design/NAIVE_ORGAN_DESIGN.md`, atom `H11_naive_organ`) | A structurally amnesiac process that recomputes claims from *raw data* rather than trusting the system's own prose about itself (T2/T6 triggers: "the claim says X, the raw MAP/RUNHIST says Y — which is true?"). Its own documented limit (§BQ-1) is exactly this wall's edge case: it catches *incoherence* between a claim and the system's raw data, not a *coherent* lie where both agree — because a fully self-consistent false world has no external signal left to catch it against. That is not a flaw in the organ; it is proof the External-Truth Wall, not the organ alone, is the actual load-bearing law — the organ is one enforcement mechanism of it, and inherits its blind spot honestly. |

R1/R9/R11/R15 and the naive organ were each independently reinvented because no
single doc held them as instances of one principle — precisely the T4 (prose-decay)
failure this atom exists to close. This section is that missing index.

## 5. The concrete instance just built: F1/F2 map-reconciliation

`docs/design/MAP_TRUTH_RECONCILIATION.md` (2026-07-15/16) is the freshest, most
literal proof of §0 and is worth walking through because it was found and fixed
*before* this doc named the general law — i.e. it is independent corroboration, not
an example constructed to fit the thesis after the fact.

- **The internal signal:** a BUILD fork's free-text claim, in its turn output, of
  "the level I reached" — folded into `maturity_map.yaml` later by a *separate,
  disconnected* hand-edit. The claim and the commit were never atomic; a crash,
  misjudgment, or plain forgetting between the two left the map's `level_current`
  wrong with **nothing to alarm on it**, because the only thing checking the claim
  was the same process that made it.
- **Why it passed the epistemic wall and still failed this one:** the level claim
  was a legitimate observable (no SIM-internals violation) — and still untrustworthy,
  because its *source of truth was itself*.
- **F1 (atomic level-write):** makes the internal signal **impossible to detach**
  from an external one — the fork writes a structured `docs/design/atom_status/<id>.yaml`
  inbox *in the same commit* as its code, so the claim and the git-verifiable fact
  land atomically. Origin's commit graph — not the fork's prose — is now the
  reconcilable anchor.
- **F2 (fail-closed reconciliation guard):** treats an **unresolved** self-report as
  a *failed* check, not a neutral one — an inbox left unfolded at rest is a
  divergence signal, and the loop **stops** rather than proceeding on trust. This is
  R15's FAIL-SILENT pattern applied to the map itself: an unreconciled claim is
  scored as failure, never as an absence of evidence.
- **The mutation proof:** `tests/controls/test_map_reconciliation.py` plants a fake
  inbox and asserts the guard fires, then clears it and asserts the guard passes —
  R15's own bar, applied to the wall's own enforcement mechanism.

F1+F2 together are this wall's law applied to exactly one signal (a maturity-map
level). The reason this atom exists is to make sure the *next* signal — a daemon's
liveness, a routine's persisted config, a digest's headline figure — gets the same
question asked of it *before* an incident forces the answer, not after.

## 6. Enforcement table — existing mechanism → wall facet → fails-closed how

| Mechanism | Facet enforced | What makes the check external, not internal |
|---|---|---|
| `tools/epistemic_verifier.py` (F1) | epistemic wall (§3), extend to this wall (§8) | Runs read-only over the diff at phase close; the code under test cannot alter the verifier's own output. |
| `background/sanity_daemon.py` (F2) | R1/R15 | Population-level statistical checks + Qwen-skeptic pass over sim/company *output*, not over its own log of having run. |
| `tools/merge_atom_status.py` + `tests/controls/test_map_reconciliation.py` | §5, R15 | Fold is git-commit-atomic; the reconciliation guard's pass/fail is computed from the *inbox's presence at rest*, a fact the claiming component cannot suppress once it has left a trace. |
| R1 (consumer-verified completion) | §0 general case | The check is literally defined as "the consumer's own fetch," structurally excluding the producer's say-so. |
| R7/R8 (NTFY carries zero authority) | T5 (transport-vs-content) | A directive's *channel of arrival* is never accepted as its *authorization*; correlation against a staged doc or console turn is the external check. |
| R9 (evidence before narrative) | T5/general | Bars asserting an externality-implying conclusion ahead of checking the one direct artifact (e.g. channel history) that would settle it. |
| R15 (mutation-tested controls) | §2's test, made procedural | Operationalizes "could the component make the check pass without the thing being true?" as a runnable adversarial test. |
| Naive organ T2/T6 triggers | §0 general case | Recomputes the data-surface value independently of the claims-surface prose before treating a claim as true (§4 caveat: incoherence only). |
| `background/director_twin.py` read-only enforcement | related but distinct — a **capability** wall (twin cannot act), not a truth wall — included here because it uses the identical *proof method*: a real failed-write test, not an assertion, is what makes "read-only" externally verified rather than internally claimed. |

## 7. Recommended extension (not built in this pass): naive-organ trigger #9

`RETRO_ACTIONS_THE_THREE_GAPS.md` ATOM 3 asks for an eighth naive-organ trigger (its
own numbering calls it "#9" against the organ's seven; the organ's design doc numbers
its triggers T1–T7, so the natural next slot is **T8**): *a success claimed without
an externally-verifiable signal → question it.* This doc recommends, but does not
implement, that addition to `docs/design/NAIVE_ORGAN_DESIGN.md` — the organ's design
and BUILD ownership belongs to atom `H11_naive_organ`, and this FRAME pass is scoped
to naming the law, not editing a sibling atom's design file. The mechanical shape
would mirror T2/T6: scan the claims surface for a success/pass/complete assertion,
check whether its evidence_refs resolve to anything the claiming component did not
itself produce (a commit SHA, a mutation-test result, a consumer re-fetch, a
director-turn timestamp), and fire if none does. Filed here as an open item so it is
found the next time H11 is drawn, rather than re-derived from scratch.

## 8. Named limits (R10 — a class, not an instance, but still finite)

- **Coherent delusion is out of scope for the mechanised test alone** (inherited
  from the naive organ's own BQ-1, §4): if every internal signal agrees with every
  other internal signal, §2's test cannot distinguish "verified" from "a
  self-consistent world that happens to be wrong," because nothing external was
  consulted. The wall's mechanisms (R1 consumer fetch, R15 mutation test, F1/F2
  atomic commit) work because each ties the claim to *something outside the
  claiming component's control surface* — a real external artifact. Where no such
  artifact exists yet (a brand-new capability with no independent consumer), the
  honest answer is: **this signal cannot yet be verified externally, and must be
  labeled as internally-asserted only**, not silently treated as proven.
- **This is a WALL, not a checklist to complete once.** Like the epistemic wall, it
  is enforced per-signal, forever, at every future phase close — not a one-time
  audit. §6's table will grow; it is not meant to be exhaustive on the day this doc
  is written.
- **Extending `tools.epistemic_verifier` to check this wall's pattern generally**
  (not just SIM/company) is logged as an open BUILD item, not done here (FRAME
  scope only, per this atom's own task grant).

## 9. Status / DoD

This doc satisfies the atom's L0→L2 DoD as framed by `RETRO_ACTIONS_THE_THREE_GAPS.md`
ATOM 3: the law is **named** (§0), its **test** is stated (§2), it is **cross-referenced**
to R1/R9/R11/R15, the epistemic wall, and the naive organ as facets rather than
separate rules (§3-4), and it is **tied to a concrete, already-built instance** (F1/F2
map-reconciliation, §5) plus a live enforcement table (§6). What remains open and is
explicitly logged rather than silently deferred: the CLAUDE.md pointer-line (left to
the orchestrator per this atom's task grant — CLAUDE.md is at 34,766/35,000 chars),
the naive-organ T8 trigger (§7, H11's BUILD ownership), and extending
`epistemic_verifier`'s remit beyond the SIM/company barrier (§8). None of these
open items block the law from being named and usable today; they are the wall's own
next enforcement slices, not gaps in the law itself.
