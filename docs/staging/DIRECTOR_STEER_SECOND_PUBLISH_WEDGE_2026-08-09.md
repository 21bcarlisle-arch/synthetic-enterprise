# [DIRECTOR-STEER] — After the second publish wedge (2026-08-09)

**Type:** [DIRECTOR STEER — decided items closed; DO-NEXT ordered; verbatim the director's text, staged by the ops advisor on standing proceed-with-veto.]

ANCHOR. Publishing was down ~10h. Two causes, both now found: a gate that could only time out and whose timeout counted as a pass, and untracked files in the shared index causing the write-time gate to refuse every publish commit. The fail-open is closed (1fd85cb27). No real publish commit has been confirmed to land yet.

DECIDED — not open for redesign:
1. Evidence of publishing is a publish COMMIT landing, never a green gate. The gate going green is what was wrong.
2. The staleness detector's permanently-red state is NOT a caveat. A stale process caused today's outage. A detector for that failure mode that is always red will be ignored exactly as reliably as one that is blind. Both fail the same way: nobody acts.
3. The register findings staged this morning (EPC certificate wrongness, absence correlation, the property-type wall leak) are Epoch 3 work and are to be REGISTERED, not built. The wall leak alone is Epoch 1 debt and may be closed now. Do not pull the rest forward.

DO NEXT, in order:
1. Confirm a real publish commit has landed and say so plainly if it has not.
2. Get tools/run_annual_report.py into version control. HEAD has no run entry point; the only copy is one working tree on one machine, and a fresh checkout or git clean reproduces today's outage — including on the cloud box, the designated seat destination. On the provenance record: you were right not to fabricate one. Write a truthful record instead — origin unknown to you, committed under director instruction to close a single-point-of-failure exposure, proper record owed by the owning lane. A record stating the record is missing is accurate, not fabricated. If the write-time gate still refuses an honest disclosure, stop and report that — a gate that blocks truthful provenance is its own finding.
3. Make the staleness signal mean "stale with respect to code this daemon actually loads." Your own refinement; it is now the work, not the footnote.

OBSERVATIONS — no action required, worth carrying:
- The failure path wrote to the state the alarm reads, so the failure silenced its own alarm. That is a class, not an instance. Where else can a check's failure clear the signal that the check failed?
- The suite grew past a fixed wall. The new ceiling is sound and growth now fails loudly rather than silently — but nothing watches suite duration, so the same shape recurs, just noisily.
- Staging is ~38 deep, oldest 4 August. Alarms now preempt the draw; the backlog is a separate problem and will not drain on its own.

## WORK THIS CREATES (canonical, in-document)
1. A plain landed-or-not statement on the publish commit. 2. tools/run_annual_report.py committed with a truthful unknown-origin provenance record (or the gate-blocks-truth finding instead). 3. The staleness signal redefined to code-actually-loaded. 4. The three observations carried as named classes where the machine judges them mintable.

— Directed 2026-08-09; drafted with the lab-front advisor; staged by the ops advisor, hash-verified.
