# THE DOOR TEST DEFAULTS TO ACT — stop over-tagging reversible work as one-way (P1, director-decided)

**Staged:** 2026-07-16 by advisor, **director-decided**. Disposition: QUEUE-high
(calibration fix, not new scope). Director's observation: *"It seems to love to
create small one-way doors so it can stop."*

## The real mechanism (name it correctly, or the fix misses)
It is NOT manufacturing doors to get permission to stop. Two structural things
combine:
1. **The door-classifier is miscalibrated toward caution** — genuinely
   reversible actions (archive markers, a scoped slice, a branch edit) get
   TAGGED as door-ish, and the (correct) door rule then says "stop and ask."
   The stopping is the rule working; the MISCLASSIFICATION is the bug.
2. **"Ask the human" is the locally safe move** — the classifier can never be
   blamed for asking, so a quiet gradient pulls every ambiguous call toward
   "ask." Asking is treated as free. It is not: every needless ask is a stall, a
   stopped loop, a director interrupt (last night: two multi-hour stalls partly
   from exactly this).

## The correction — invert the burden of proof (same shape as Rule 0)
**Reversibility is the DEFAULT VERDICT. An action proceeds autonomously UNLESS
it provably matches a one-way-door criterion.** "I'm not sure" resolves to
PROCEED, not ASK. Today the burden is backwards — "might be a door" is treated
as "ask"; it must become "not provably one-way -> proceed."

The one-way-door criteria remain EXACTLY as they are (unchanged walls): real
money; real-world/legal commitment; irretractable public claim; irrecoverable
data loss; security/safety-control change; VALUES/fitness decision; real
customers; director-reserved (repo/keys/accounts/connectors/billing). If it does
not provably match one of these, it is reversible-proceed.

## Three binding rules
1. **A reversible FORM is never a door.** If a safe reversible version of the
   action exists (archive-not-delete, branch-not-main, draft-not-publish,
   flag-off-default), the executor MUST take that form autonomously and MUST NOT
   escalate. "Move to history/" is never a yes/no to the director — it just
   happens. (This is the marker-cleanup case: it should have archived silently.)
2. **Ambiguity resolves to PROCEED, and logs — it does not ask.** When genuinely
   uncertain and the action is reversible, proceed and record the call (so it's
   auditable), rather than stopping. Reserve escalation for provable one-way
   doors. The twin remains available for reversible-but-unclear judgment calls;
   the DIRECTOR is only for true doors.
3. **Escalation has a named cost.** An escalation is not free: it stops the loop
   and consumes director attention. Weigh that cost in the classify step, so the
   gradient stops favouring "ask." A needless ask is a defect, exactly as a
   needless stop is.

## What must NOT change (guard against over-correction)
The actual walls stay hard. Real money, security/safety controls, irreversible
data loss, public claims, values, director-reserved actions — these still stop
and still ask, every time. This fixes the CLASSIFIER'S BIAS, not the door list.
The test is: does the burden of proof sit on "it's a door" (correct) or on "it's
safe to act" (the current bug)? Move it to the former.

## Relationship to the map
Directly reduces the small self-interruptions the director is seeing, and
removes a real source of last night's stalls (reversible actions escalating
instead of proceeding). Folds naturally with Rule 0 (default state is working)
and PROCEED_BY_DEFAULT — this is their calibration, made to actually bite.

## DoD
The one-way-door test amended so reversibility is the default verdict and the
burden of proof is on door-classification; reversible-form actions (archive/
branch/draft/flag-off) proceed autonomously and never escalate; ambiguous-
reversible resolves to proceed-and-log; escalation carries a named cost in the
classifier; the door LIST is unchanged and the hard walls still stop. A
mutation-style check: a reversible action (e.g. archive markers) must NOT
produce an escalation; a true door (e.g. spend real money) MUST.
