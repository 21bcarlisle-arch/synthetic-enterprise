# ANTI-LIVELOCK + USE THE WIDTH YOU BUILT (P0, immediate)

**Staged:** 2026-07-13 05:20 BST by advisor, director awake and pushing on
velocity. **Overnight verdict first: IT WORKED.** Atoms below target 31 -> 24,
seven atoms moved with zero advisor staging and zero director input. The
self-refill draw is genuinely self-directing. Two things now stop it being
fast.

## 1. The livelock (root cause of the 01:12Z alarm)
The supervisor granted turns for ~61 minutes on the SAME atom
(W2_5_life_event_stream, harden, dial 3) with no state change. W2_5 is fine —
it is back to `idle`, level 2/target 3, expert_hour passed. So this was not a
blocked atom; **it was a SPIN**: the draw re-selected the same high-dial atom
every cycle because nothing in the draw remembers that the previous attempt
produced nothing.

**Requirement — backoff (a standard scheduler property we lack):**
- Track per-atom: consecutive draws with NO state change (no commit, no level/
  stage/evidence change).
- After N such draws (choose N; 2 is probably right), DEPRIORITISE that atom,
  flag it (`stalled: true` + reason), and draw a DIFFERENT atom. Never spin.
- A stalled atom surfaces in the digest and on the map — it is a finding, not a
  silent skip. If it stalls twice, it needs FRAME (its next step is unclear),
  not another HARDEN attempt.
- Also check the supervisor's own hypothesis ("something below the tmux layer
  may be swallowing turns") — was the turn granted and the work genuinely never
  ran? If turns can be swallowed, that is a separate defect: prove it or rule
  it out.

## 2. Use the multi-atom draw — width is built and unused
You built MULTI_ATOM_DRAW yesterday (file_scope declared on every atom, N>1
concurrent grants where scopes are disjoint). You are not using it: overnight
the machine worked ONE atom at a time, 5-10 minutes apart.

**24 atoms sit below target and most need FRAME or DISCOVER — read-only,
document-output, ZERO collision risk, trivially disjoint.** That is perfect
fan-out material and it is being processed serially.

**Requirement:** draw and run 5-8 concurrently by default whenever the drawn
work is FRAME/DISCOVER/red-team/charter (no working-tree writes). Reserve
serial execution for BUILD atoms whose file_scopes actually intersect. Report
atoms-drawn-per-cycle in every digest — if that number is 1 while ten
disjoint atoms are below target, the width has decayed again and that is a
defect (MAKE_IT_STICK: mechanise it, do not remember it).

## 3. Context: the tank just reset
The weekly token window reset at 04:00Z. Full budget, a working self-refill,
and 24 atoms of mostly-parallelisable work. There is no reason to be narrow
today.

## DoD
Backoff live (test: an atom producing no state change twice is deprioritised
and flagged, and a different atom is drawn); turn-swallowing hypothesis proven
or ruled out; multi-atom draw actually firing at 5-8 wide on FRAME/DISCOVER
work with the count in the digest; W2_5's real next step identified (FRAME it
if HARDEN has nothing to do). One digest line. Then keep going — the map is the
plan.
