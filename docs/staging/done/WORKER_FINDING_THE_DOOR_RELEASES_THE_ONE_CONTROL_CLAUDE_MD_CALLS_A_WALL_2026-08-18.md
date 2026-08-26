# WORKER FINDING (LATENT, H_harness, backlog) — the door releases the one control CLAUDE.md calls a wall

**Found:** 2026-08-18, worker tick, LANE 3 DISCOVER on `EP19_counterparty_qualification_paths`.
**Rank:** backlog. **Queued per SELF-INTERRUPT DISCIPLINE, not fixed on sight** — see § Why queued.
**Severity:** LATENT · **Lane:** H_harness — no act of this class has been taken; the defect is that
nothing would stop one.

## The finding

`background/one_way_door.py` is, per CLAUDE.md, *"the SOLE enumeration"* of what is reserved. Run against
the one control CLAUDE.md calls a wall, it says proceed. `observed-with-evidence`, 2026-08-18:

```
"Add smartenergycodecompany.co.uk to the egress allowlist in background/egress_allowlist.py"
  -> is_one_way_door=False, category=None      "no one-way-door category matched -- proceed"
"Widen this agent's egress allowlist to reach Ofgem"
  -> is_one_way_door=False, category=None      "no one-way-door category matched -- proceed"
"Change the sandbox security profile"
  -> is_one_way_door=False, advisory=security_safety_control (a RELEASED category) -> "PROCEED"
```

Against CLAUDE.md:

> *"changing what THIS machine is allowed to do — the security profile, `--dangerously-skip-permissions`
> scope, credentials, **egress allowlist** — is not a simulation-internal act, so it stays
> director-console-only and the agent may never widen its own. **This is the ONLY authentication
> convention that survives the rip-out.**"*

and

> *"**Profile changes are director-console-only — the agent can NEVER alter its own profile**, full stop,
> regardless of tier/reversibility framing elsewhere in this file."*

The `security_safety_control` category conflates two populations the 2026-07-29 ruling separated on
purpose: controls that stop a **simulation** (released, correctly — *"a 'safety control' that stops a
simulation is NOT one of these"*) and this agent's own **real-world** reach (never released, in the
sentence with "full stop" in it). The classifier has no way to tell them apart and lands on PROCEED
for both.

### Three instances, one shape, one atom

This is the third time the same shape has been found, twice on this atom:

1. **2026-08-15** — seven of seven gated counterparty acts read PROCEED while the *sentence describing*
   the boundary classified as a door. Repaired: six patterns, R15 both directions.
2. **2026-08-18 (this finding)** — the allowlist/profile acts read PROCEED.
3. **2026-08-18, same tick** — after the 2026-08-15 repair, *"Appoint an existing ECVNA…"* and
   *"Complete CVA Qualification testing with Elexon under BSCP70"* **still** read PROCEED. Both are
   engaging a real organisation. The 2026-08-15 patterns require *an acting verb beside a named real
   body*, and neither phrasing has that shape — `Elexon` is not in the named-body list.

Instance 3 matters for how instance 2 gets fixed: the 2026-08-15 repair worked by enumerating shapes, and
the enumeration is already leaking two days later. A fourth round of patterns is the treadmill, not the
repair.

## Why the 2026-08-12 decay audit does not already cover this

CLAUDE.md says the routine-creation rule and the sandbox-profile rule *"stay prose by necessity, not by
neglect"*, and the stated reason is **out-of-tree**: *"a Routine's config lives on Anthropic's servers, so
no in-repo mechanism can enforce this."*

That reason is sound for the security profile and for `--dangerously-skip-permissions` — both live outside
the repo. **It does not hold for the egress allowlist.** `background/egress_allowlist.py` is an in-repo
Python module with an enumerable tuple (`ALLOWED_HOST_SUFFIXES`). It is the one member of CLAUDE.md's
"profile / skip-permissions / credentials / egress allowlist" sentence that a mechanism can actually
reach. Prose-by-necessity was ruled for the list; it was never argued for this member of it.

## Why queued rather than fixed on sight

The 2026-08-15 precedent — *"widening detection is safety-INCREASING, which that module's own two prior
widenings establish needs no authorisation"* — does **not** transfer cleanly, and that is the reason to
queue rather than the excuse:

- That repair widened detection **within** an already-reserved class. This one would **un-release a
  category the director explicitly released** on 2026-07-29. Splitting `security_safety_control` into
  "stops a simulation" (released) and "changes this machine's real-world reach" (reserved) is a change to
  the shape of a director ruling, not an extension inside it.
- The failure mode is asymmetric in the dangerous direction: a category that over-gates can wedge lanes.
  The 2026-08-15 pass found two first cuts that jammed the very lane doing the work.

## Checks recorded for the doer

1. **Split the category, do not add a fourth round of patterns.** Instance 3 shows pattern enumeration is
   already leaking. The distinction wanted is *subject* (this machine's real-world reach vs. simulation
   state), not vocabulary.
2. **The likely durable control is not in the door at all — it is a commit-time gate on
   `ALLOWED_HOST_SUFFIXES`.** The door classifies a *described* act, so it only fires if someone thinks to
   ask it; a gate on the tuple fires on the act itself. Compare `tools/pre_commit_test_gate.py`'s existing
   treatment of CLAUDE.md. Recommend building that first and treating the door change as secondary.
3. **R15 both directions, and the null control is the released half.** Removing the change must flip the
   allowlist/profile acts back to PROCEED **and move nothing else** — in particular every
   simulation-internal "safety control" phrasing must stay PROCEED, or the 2026-07-29 rip-out has been
   partially reverted by the back door. That null control is the whole point: it is what distinguishes
   this from re-erecting permission machinery.
4. **Blast-radius census before landing**, as 2026-08-15 did: classify all `block_reason`/`blocked_on`
   strings in `maturity_map.yaml` with and without the change and confirm 0 newly gate, so no atom
   silently leaves the draw.
5. **Do not gate the reading of the allowlist, only its widening.** `check_allowed()` is called on every
   guarded request; a control that fires there would be a live producer outage.
6. **Fold in instance 3 while the file is open** (`Elexon` and the appoint/engage-an-agent shape), but as
   a separate commit from the category split — they have different blast radii and different reviewers.

## Consumer waiting on this

`docs/design/EP19_COUNTERPARTY_QUALIFICATION_REGISTER.md`'s Owner column is, as of 2026-08-18, a **mixed
instrument**: nine rows derived from the classifier, two asserted from CLAUDE.md because the classifier
fails open on them. It says so in the document. That caveat comes out when this lands, and not before.

## Null control stated

This finding is closed when the acts above gate **and** every simulation-internal safety-control phrasing
still proceeds. If both move, the fix is wrong in the direction that matters most to this project.
