
---

# RESULT, filed against the prediction above

Four arms, eleven daemons, one run. Figures are `modules_behind` per daemon.

| daemon | A both | B content only | C mtime only | D neither |
|---|---|---|---|---|
| deadmans-switch | 0 | 0 | 0 | 5 |
| naive-organ | 0 | 0 | 0 | 5 |
| staging-watcher | 0 | 0 | 0 | 1 |
| supervisor | 0 | 0 | 0 | 2 |
| sim-runner | 5 | **10** | 5 | 10 |
| background-worker | 4 | **8** | 4 | 8 |
| dispatcher / ntfy-responder / sanity-daemon / token-proxy | 0 | 0 | 0 | 0 |
| worker-seat-manager | 1 | 1 | 1 | 1 |
| **stale count** | **3** | **3** | **3** | **7** |

**Prediction 1 held.** D reproduces the loop's condition: seven daemons stale, including the four
that were being restarted every ten minutes. The harness measures the thing.

**Prediction 2 was half right, and the half it got wrong is the finding.** The stale COUNT is 3 in
A, B and C as predicted — but the SETS are not equal. B (content only) leaves sim-runner at 10 and
background-worker at 8, because those two still carry stamps written before `dirty_blobs` existed
and the content mechanism has nothing to compare against. **C equalled A on every single row.**

**So the content stamp adds nothing observable today, and the mtime filter does all the work.**
That is the reverse of what "theirs compares content, which is the actual question" would suggest,
and it refutes the case for deleting the mtime filter outright. The preregistered deletion criterion
(A == B, plus a case where CONTENT catches what MTIME misses) is **not met**: A ≠ B. The mtime
filter stays.

**Prediction 3 held**: zero rows distinguish the two mechanisms on today's tree.

## The finding the arms produced that the prediction did not anticipate

Both mechanisms are REMOVAL filters, so composing them removes a path if EITHER removes it. The
pair is therefore **no better at catching real staleness than the mtime proxy alone** — which is
precisely what "C equalled A on every row" means, read as a property rather than as a coincidence.

And it is not a harmless tie, because the proxy's false NEGATIVE is reachable on this machine:
`cp -p` preserves mtime, so content that genuinely changed can look untouched. This session used
`cp -p` a dozen times restoring files during mutation testing. The composition let the proxy
override the exact answer, in the one direction that leaves stale code serving.

**Disposition, and it is neither of the two the finding offered.** Not "delete the proxy" and not
"keep both composed": the exact answer wins **where it exists**, and the proxy covers only what it
cannot reach — a daemon whose stamp predates the content field. On the arms that is the difference
between sim-runner reading 5 and reading 10. Both controls are mutation-proved (M36: apply the
dating unconditionally; M37: skip it for everyone).

**What I got wrong and am recording rather than revising:** I predicted A == B == C and treated the
count as the outcome. The count was equal and the sets were not, and a stale COUNT is exactly the
kind of reducer this column has now been wrong about three times. I should have preregistered the
per-daemon set as the measurement, not the total.
