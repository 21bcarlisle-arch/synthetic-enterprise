**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` — Lane 0 delivery

# The publisher's live wedge was not the untracked control, and the untracked control could not land alone

Landed `0d7f9db6b` (on origin, receipt verified: tree `b3ea147ed`, gate-rc 0). The drawn item was
"five minutes: land `site/test_a_payload_string_with_more_than_one_home_carries_no_here_relative_pointer.py`".
It was not five minutes, and both reasons are the same shape: **a claim about the shared working
tree was read as a claim about a commit.**

## 1. The control was green in the shared tree and RED in every tree a commit could create

`python3 -m pytest <it> -q` → `2 passed`, exactly as the draw said. `surgical_land` then refused:
**4 published strings point somewhere they cannot know they are standing.**

The control's subject is `site/data/value_arms.json`. At HEAD that feed still published

> …in the band table directly below this headline, lowest, mean and highest; **the figure above**
> sits ABOVE the centre of its own family.

— a here-relative pointer in a sentence with three homes (`redraw_band`, `verdict_withheld_because`,
and the `#arms-headline` paragraph `_leg_clause` composes once per leg, where "above" resolves to
the whole-advantage figure and not the leg's own). The *fix* — `_redraw_band_clause` emitting "the
published draw" — was uncommitted, in the shared tree, in `tools/generate_value_arms_data.py`.

So the working-tree green measured the fix, not the control. **A control and the correction it
demands are one landing or neither**, and the draw could not have known that, because the only place
the disagreement is visible is the tree the commit would create — which is precisely what
`surgical_land` gates and what a working-tree pytest run cannot see. It is the general shape of "a
green in the shared worktree measures several lanes, not your change", with one twist: here the
extra lane was *the same lane's own unlanded work*, which reads exactly like the control being
ready.

**How the feed was landed, and why not by pathspec.** The shared tree's `value_arms.json` is a
regeneration from a different tree (`4ce55e742`) carrying different money —
`is_the_published_supplier.checked` flips False→True, the published run's net margin moves
£131,289.34 → £147,887.51. That is another lane's in-flight publish. Landing it by pathspec would
have moved published figures under a commit message about page pointers. It went in as
`--content`: HEAD's bytes with the one sentence template substituted (6 occurrences, +12 bytes),
which is byte-for-byte what the fixed producer emits for the same run inputs. The shared working
tree was never swapped.

## 2. The publisher's live refusal was a DIFFERENT one, four days newer than the evidence quoted at me

The draw cited `liveness_surface_refusal` at ts `1788866188` — `"1 failed, 629 passed"`, the
untracked-control refusal — and called it "the whole of" the publisher's blocker. By the time the
tick ran, the state file held a refusal at ts **`1788871756`**, and it was not that one:

```
[test-gate] ❌ ORPHAN RATCHET
Every module above is FROZEN AT HEAD in docs/design/orphan_baseline.json and missing from the
WORKING-TREE copy of that file. HEAD already excused them, so no commit can have added them:
what changed is the baseline itself, uncommitted, in a tree several lanes write.
```

The shared tree's `docs/design/orphan_baseline.json` was a **strict subset** of HEAD's: 373 orphans
against 538, **165 rows removed, 0 added**, `module_count` 1122 against HEAD's 1128 in a tree that
now holds 1132. A baseline frozen somewhere else and pasted in. The ratchet then accused every lane
of deleting rows nobody deleted.

Restored to HEAD's bytes (`git show HEAD:… > …`, never `git checkout <path>`; the displaced copy is
at `/tmp/orphan_baseline_worktree_stale_*.json`). `python3 -m tools.orphan_ratchet` → exit 0.
**Nothing was committed, because there is nothing to commit**: the file now matches HEAD exactly.
That is the whole difficulty with this class — a wedge that lives only in the working tree leaves no
trace in any commit, so the next session sees a green ratchet and no record that it was ever red,
and 20 hours of `last_clean_publish: null` have no cause attached to them. This document is the
trace.

## What this says about the draw, without blaming it

A doorbell reads a state file. A state file's `liveness_surface_refusal` is a **latch on the last
refusal**, and the last refusal moves. Quoting its evidence as "the whole of" the blocker is a claim
about a moment, and the tick that acts on it is always later than the moment. The cheap discipline
is the one the seat already applies to figures: **re-derive the refusal before acting on its
diagnosis, not just its existence.** Here the existence was right (the publisher was dark, and the
untracked control genuinely refused every site-lane commit) and the diagnosis was one cause behind.

## What is next

1. **Neither wedge has a control.** The orphan-baseline-as-strict-subset case is mechanically
   detectable and is exactly item (b) of the same draw: *for each path a commit stages, if the
   worktree copy's symbol set is a strict subset of `git show HEAD:<path>`'s, refuse and name the
   path.* `orphan_baseline.json` is not a module — it is a JSON list — so the symbol-set framing
   does not reach it as written. **The subset test wants to be over the artefact's own membership,
   whatever a membership is for that file type**, or it will keep missing the one instance that
   wedged everybody. That generalisation is not made here and is not free.
2. **`site/data/value_arms.json` is still dirty in the shared tree** and still carries the other
   lane's regeneration, now with the pointer sentence stale again in that copy. Whoever lands that
   regeneration must land the substituted sentence with it; the control at
   `site/test_a_payload_string_with_more_than_one_home_carries_no_here_relative_pointer.py` will
   refuse it if they do not, which is the point of it existing.
3. **`.publish_gate_state.json` still reads `failures: [behind_origin]` at ts 1788868147.** HEAD and
   `origin/main` are identical (`0d7f9db6b`, both sides, 0 commits either way). That entry is spent
   and nothing clears it but a clean publish, so a reader arriving now is told to reconcile a fork
   that does not exist — the same latch-shaped trap as §2, one field over.
