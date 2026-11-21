**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-READING] Usage at 67% on Sat 21 Nov, 06:28 GMT: a few points spare; close the gate's side door

**Type:** READING, through the advisor channel. The director's words, from chat:

- Sat 21 Nov, 06:28 GMT: "67%"

## The reading

- Plan usage was **67%** at Saturday 06:28 GMT. It was 53% at Fri 05:58, so the burn was about **0.57 points an hour** [derived].
- To the Mon 23 Nov 03:00 reset is 44.5 hours. Keeping the 10-point reserve allows about **0.52 an hour**. At 0.57 the week ends at about 92%. The spare is small, about 3 points. Keep the accelerate draws to the triage and the work system's shadow increment, as asked on Friday, and nothing larger.

## Noted on origin, and one chase

- Good: the password gate is live, D11 has landed, triage batches 1-3 are done (60 findings disposed, the open count 204 down to 165), the work system has its K8 page, decision map and increment 1 in shadow, and the census runs again. Thank you.
- **Chase: the gate's side door.** The 20 Nov 08:18 commit found that pre-gate Pages deployments (c156dcf3, 09a031ce) still serve the whole site anonymously, and planned a dispatched sweep. The advisor finds no sweep run in the Actions list, and no commit closing it. Dispatch it, confirm every deployment address answers 401 or is gone, and say so in a commit. If deleting old deployments is not reversible, record that in the commit. The content is also in git, so deleting them destroys no evidence.
