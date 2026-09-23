# The two sibling censuses match the call now, and the pattern itself had no control

**Severity:** RECORDED · **Lane:** D_billing_metering

A control that named the wrong defect on one of its three legs, and a narrowing that nothing could
have told us had died. No published figure moves.

Landed: `430fe8360`, `tests/simulation/test_one_home_has_one_headcount.py`.
Claim: `composition-census-matches-pensioner-and-employed-as-bare-substrings` (bound).

## What was asked, and what was done

The children caller-census was tightened to the call shape `_substream(..., "children")` after the
bare `'"children")'` substring reddened on `tools/sample_gate_rss_premium.py`, a file that reads the
cgroup path `<task>/children`. Its two siblings — `pensioner` and `employed` — kept the substring.
Both now match the call, through one shared fingerprint (`_pre_delegation_fingerprint`), because
three copies of one census is how the siblings were left behind in the first place.

## The measurement the item predicted, and it held

The item said the two siblings are "green today by luck of vocabulary, not by construction". That is
a claim nobody had run, so I ran it. Reverting the fingerprint to the bare word and re-running all
three censuses against the live tree:

| census | bare-word pattern | dead pattern (matches nothing) |
|---|---|---|
| composition (pensioner, employed) | **GREEN** | GREEN |
| children | RED on `tools/sample_gate_rss_premium.py` | GREEN |

So the siblings really were passing for a reason unrelated to their subject: there is at this moment
no innocent file in `simulation/company/saas/tools/background` carrying `"pensioner")` or
`"employed")` in another sense. One `record["employed"]` would have been enough.

## What was NOT asked for, and is the more useful half

**A caller census over a tree with no offenders is green whether or not its pattern can see
anything.** The tightened children leg had no control over its own pattern, and neither would the
tightened siblings: the whole of the right-hand column above is the silent failure — kill the
regex and all three censuses go green for ever, and nothing reds.

`test_the_draw_census_still_sees_the_call_it_was_built_for_and_not_the_bare_word` asserts both
directions over the whole partition rather than a leg each (the R15 shape: a guard that refuses
everything passes every per-leg test of it). Positive fixtures are the calls the world actually made
before delegation — the tightened pattern still matches all three in `simulation/premise_trace.py`
at `263b57ac0^`. Negative fixtures are the live `sample_gate_rss_premium.py` line and two ordinary
dict reads. Mutation-proven: the dead pattern reds it naming the draw that stopped matching; the
bare-word pattern reds it naming word-vs-call as the cause.

## Aside, not mine to fix

The static quality ratchet is locally RED on `F401: baseline 264, now 269`. Attributed per dirty
file against HEAD's blob: all five are in `tools/refresh_to_head.py`, another lane's uncommitted
working copy (HEAD=0, working=5). Nothing in my pathspec, and the gate grades the tree the commit
would create, so it did not block this landing — but whoever owns that file will meet it.
