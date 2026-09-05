# Measurement — queueing, flapping, or masked, decided by the gate order

*2026-09-05, delivery seat. Pre-registered before any classification:*
`docs/design/PREREGISTRATION_ARE_THE_GATES_QUEUEING_FLAPPING_OR_MASKED_2026-09-05.md`.

**Re-derive:**
`python3 -m tools.commit_refusal_attribution --log <the shared tree>/docs/observability/sim-runner-log.md`

**Read that path twice.** The subject is the running daemon's **working copy**. The committed copy
of the log was truncated to 2026-07-17 on 2026-08-31, so a clean checkout, an isolated worktree, CI
or a `git archive HEAD` extract holds a file with no refusal in it at all. The module now refuses
rather than reporting zero from one — see §4.

---

## 0. The mechanism, which is what makes any of this decidable

`git config core.hooksPath` → `tools/git-hooks`. Every gate in `tools/git-hooks/pre-commit` is
invoked `python3 … || exit 1`, and `commit-msg` runs afterwards with one more. **Serial, fixed
order, stopping at the first refusal.**

Therefore a named cause proves every *earlier* gate passed on that cycle, and says nothing whatever
about the later ones. The order below is derived from those two files, joined to the publisher's
own `_REFUSING_GATE_BANNERS` table by the emitter path that table already carries. Nothing here is
typed by hand.

```
   2.  ?   finding-severity gate          <- banner text not found in its emitter: position UNRESOLVED
   2.1369  finding-class consolidation
   2.1518  RED TEST                       <- the test gate reaching pytest, after everything it prints
   3.419   level-promotion gate
   4.138   site-lane gate
   5.162   moap-coherence gate
   6.127   ruling-archive-question gate
   7.427   consolidation-rhythm gate
   8.263   size-ratchet gate
   9.402   orphan-ratchet
  10.246   company-network-isolation gate
  11.205   file-scope-generated-paths gate
  12.205   annual-report-import ratchet
  13.172   half-hourly-dependency ratchet
  14.343   running-total-order gate
  15.163   scope-evidence ratchet
  16.365   write-time gate                <- commit-msg, i.e. after all fifteen
```

The `?` on finding-severity is the fail-closed path working: its banner is not a literal in the
emitter's source, so its position within the test gate is unresolved and every comparison involving
it comes back UNDECIDABLE rather than guessed.

## 1. Recurrences — is a gate re-breaking, or was it never fixed?

For a cause recurring at `t1 < t3` with something else named in between at `t2`: if any intervening
cause sits **later** in the order, the recurring gate was reached and cleared at `t2`, so it
genuinely re-broke. If every intervening cause sits **earlier**, the gate may have stood broken and
invisible throughout.

```
recurrences of one cause inside one episode (16 total):
     8   50.0%  PROVEN FLAP (reached and cleared in between, so it re-broke)
     5   31.2%  MASKABLE (may have stood broken behind an earlier gate)
     3   18.8%  UNDECIDABLE (a position involved is unknown)
  of the RED TEST recurrences whose node ids were retained: 3 SAME test, 3 DIFFERENT test(s)
```

Which gates actually flap:

| Cause | PROVEN FLAP | MASKABLE | UNDECIDABLE |
|---|---:|---:|---:|
| finding-class consolidation | 4 | 0 | 1 |
| RED TEST | 3 | 2 | 1 |
| level-promotion gate | 1 | 0 | 0 |
| orphan-ratchet | 0 | 2 | 1 |
| site-lane gate | 0 | 1 | 0 |

**finding-class is the flapper**, and it is the earliest gate in the whole hook — which is why its
recurrences are provable and orphan-ratchet's are not.

## 2. Steps — a queue, or new breakage arriving?

Between two consecutive *distinct* causes: a step to a **later** gate is consistent with the first
being cleared and the next revealed. A step to an **earlier** gate proves that gate was *passing* on
the previous cycle and failing on this one — something broke it while the publisher was working.

```
steps between consecutive distinct causes (45 total):
    20   44.4%  QUEUE STEP (a later gate revealed)
    13   28.9%  PROVEN NEW BREAKAGE (an earlier gate that was passing broke)
    12   26.7%  UNDECIDABLE (a position involved is unknown)

multi-cycle episodes: 26 | containing a PROVEN FLAP: 5 | containing PROVEN NEW BREAKAGE: 9
```

## 3. Weighted by what it cost — the only ranking that decides anything

Over the 26 bounded multi-cycle episodes, 228.7h of outage:

| Class | Episodes | Outage | Share |
|---|---:|---:|---:|
| contains PROVEN NEW BREAKAGE | 9 | 132.7h | **58.0%** |
| contains a PROVEN FLAP | 5 | 104.5h | 45.7% |
| contains either | 9 | 132.7h | **58.0%** |
| **PURE QUEUE** (only queue steps, no recurrence) | **4** | **25.4h** | **11.1%** |

The 68.8h episode — 28.7% of all outage on its own — contains **both** a proven flap and proven new
breakage. It is not a queue.

## 4. The instrument's own fail-open defect, found while re-running it here

Run from this worktree against the default path, the module used to print:

```
commit_refused cycles: 0
attempts (lifetime):   1306  -> share 0.0%
total bounded outage: 0.0h over 0 episodes
```

A complete, confidently formatted report that the publisher has never once failed — the most
comfortable answer available, from a file that simply does not contain the subject. Both landed
predecessor findings publish `python3 -m tools.commit_refusal_attribution` as their re-derivation
instruction, so anyone checking either of them from a clean tree got that. It now refuses:

```
REFUSED: docs/observability/sim-runner-log.md contains no named commit outcome, so nothing here is measurable.
  read 1306 attempt line(s), 0 of them refused
  The named-outcome vocabulary began 2026-08-13. A file without it is either
  entirely older than that, or it is the COMMITTED copy -- truncated to
  2026-07-17 on 2026-08-31. The subject is the running daemon's working copy.
  Point --log at the shared tree's copy; do not read a zero here as a result.
```
(exit 2)

## 5. The order bias, quantified — P4's magnitude

For each gate, across the 174 refused cycles the episode view covers: how often it was **named**,
how often a *later* gate was named (so it is **proven to have passed**), and how often a *strictly
earlier* gate was named (so its state is **unknowable** — it may have been broken and invisible).

| Gate (hook order) | named | proven passing | unknown |
|---|---:|---:|---:|
| 2 finding-severity gate | 0 | 52 | 122 |
| 2 finding-class consolidation | 31 | 122 | 21 |
| 2 RED TEST | 70 | 52 | 52 |
| 3 level-promotion gate | 12 | 40 | 122 |
| 4 site-lane gate | 20 | 20 | 134 |
| 5 moap-coherence gate | 0 | 20 | 154 |
| 6 ruling-archive-question gate | 0 | 20 | 154 |
| 7 consolidation-rhythm gate | 0 | 20 | 154 |
| 8 size-ratchet gate | 0 | 20 | 154 |
| 9 orphan-ratchet | 16 | 4 | 154 |
| 10 company-network-isolation gate | 0 | 4 | 170 |
| 11 file-scope-generated-paths gate | 1 | 3 | 170 |
| 12 annual-report-import ratchet | 0 | 3 | 171 |
| 13 half-hourly-dependency ratchet | 1 | 2 | 171 |
| 14 running-total-order gate | 0 | 2 | 172 |
| 15 scope-evidence ratchet | 2 | 0 | 172 |
| **16 write-time gate** | **0** | **0** | **174** |

**The write-time gate's state is unknown on every single refused cycle in the window.** "It never
refused a publish" is not an observation about it; it is unobservable. Seven gates have zero named
refusals and over 150 unknown cycles each.

Read the other way: on **52 of 174 refused cycles (29.9%) the entire test suite is proven green**,
because a gate later than the pytest run was named. Those publishes were blocked purely by
governance state.

## Note on 175 vs 174

`attribute()` counts refusal *lines* (175). `cycles()` pairs each outcome with the attempt line
above it and keeps those at or after the window opens; the very first refusal's attempt line
predates the opening stamp, so the episode view covers 174. Pre-existing, unchanged by this turn,
and recorded because the two figures appear side by side above.
