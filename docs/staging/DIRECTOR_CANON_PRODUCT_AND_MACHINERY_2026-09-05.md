**Severity:** LATENT · **Lane:** A_strategy_governance

*(Header line added by the delivery seat, 2026-09-05, transcribing the severity the
document and its own commit message both already declare — `Severity: LATENT` in the
**Type:** line below, `Severity LATENT` in the commit subject. Nothing else is changed.
The seat did not decide this value and is not entitled to; it made a declared one
machine-readable, because without the line `finding_severity` reads the document as
UNCLASSIFIED and every merge of `origin/main` — including the reconciler's own, on the
deadman cadence — is refused. Why the director's document could arrive without the line
at all, and why that is the gate's defect and not his, is filed as
`SEAT_FINDING_THE_DIRECTORS_OWN_STAGED_DOCUMENT_WEDGED_EVERY_MERGE...`.)*

# [DIRECTOR-CANON] — Product and machinery: what counts, and what the machine owes the lanes (2026-09-05)

**Type:** [CANON — a definition and a standing rule about how work is chosen. Severity: LATENT. Mechanism is the delivery seat's; the definitions and the properties are the director's.]

---

## 1. The measured problem

The re-ranking canon landed at 18:19Z on 4 September. In the ten hours after it, **sixty-six commits landed and not one was on R1** — the item ranked first. Publisher refusals, episode carriers, dedup memory, census rows, worktree markers, reconciler advances. Every individual fix was defensible. The night's product output was nil.

This is not the first instance. It is the pattern the director has named at least a dozen times across three weeks, in canon, in briefs, and in the console.

**Why it keeps happening, stated plainly.** "Work the lanes, not the harness" has only ever existed as prose. Nothing refuses a machinery commit, nothing counts them, nothing makes a night of sixty-six of them fail anything. Meanwhile the machinery side has real mechanisms: findings that draw themselves, blockers that outrank, alarms that fire hourly, a publisher that wedges loudly. **The harness pulls; the lanes only ask.**

That asymmetry is not a matter of will. This project's own finding is that every rule which decayed was an exhortation and every rule that held was a mechanism, and CLAUDE.md's own standard is that a rule lives in prose *and* as enforced code, or not at all. This rule has never had its second half. The advisor has added to the problem by ending paste after paste with "spend the week in the lanes", which is another exhortation in a project that has documented that exhortations evaporate.

**And a second cause that must not be dismissed:** the machinery genuinely was broken each time. A publisher that cannot publish is a real problem and no rule should let it be ignored. What is missing is not permission to ignore — it is a **budget**.

---

## 2. The definitions

**Product** is anything that exists inside the simulated world: the world, and the supplier living in it. Households, weather, prices, demand, meters and reads, competitors, the wall, tariffs, bills, hedging, collections, credit, beliefs, the score. **The test: if a real energy supplier or a real market would have it, it is product.**

**Machinery** is what exists only because this is built by an autonomous harness: publishers, gates, alarms, censuses, reconcilers, worktrees, the map, the class registers, the seat and its plumbing. **A real supplier has none of it.**

**Two rulings so this is not argued case by case.**

- **The website is presentation.** It publishes product but is not product. Under the weekly-cadence ruling it should mostly be quiet. It counts as neither.
- **The bill validator is product.** Being auditable is part of what a real supplier is; bill validation is a real service in the GB market. That it also tests us is a side effect, not its category.

The lane names already carry most of this — the W, C, D, B, E and F lanes are product, H_harness is not — so the measure should be close to free.

---

## 3. The standing rule

**Machinery work must earn its place.** It earns it when something a reader or a customer depends on is broken, or when the machine genuinely cannot land work. It does **not** earn its place because it is loud, adjacent, newly discovered, or because a finding the machine filed itself is sitting at the top of a queue.

When a machinery item fails that test, file it and move on. The registers exist so a defect can wait without being lost. A filed defect is not a forgotten one.

**The selector, not the dial.** The re-rank set R1–R5 to 75% of a weighted draw and the ratio did not change, because the dial is not what chooses: blocking findings, publisher wedges and self-generated repairs all jump ahead of a weighted draw. Product work must be able to win against machinery work, not only against other atoms. How is the delivery seat's to decide — it can see what actually picks the next thing.

**The floor.** A stretch that produces no product progress is itself a finding about how work is being chosen, and it outranks the machinery item that displaced it.

---

## 4. Measure it, so nobody has to read commit logs

The share of a stretch that went to product against machinery is to be **measured and visible**, with the ratio itself becoming a finding when it goes wrong.

The director should not be discovering this by reading sixty-six commit titles, and neither should the seat. A number that is watched changes behaviour; a sentence in a document has now failed to, a dozen times.

**Deliberately not specified:** the threshold, the window, the exact form. Choose them from what the record shows, not from a number picked because a number was needed — and remember that the smallest mechanism that can fail is the right one. This must not become machinery about machinery, which would be the defect performing itself.

---

## 5. What this does not change

Essential repairs stay essential. Nothing here asks the machine to leave publishing broken, to ignore a blocking finding about a published figure, or to let the tree wedge. The claim is narrower and harder: **most machinery work is not essential, and it has been winning anyway.**

## WORK THIS CREATES (canonical, in-document)
1. The product/machinery distinction expressed where work is chosen, not only where it is described.
2. The selector changed so product work can win against machinery work.
3. The split measured and visible, with a bad ratio filing itself.
4. The floor: a stretch with no product progress is a finding.

— Director canon, 2026-09-05. This has been said in prose a dozen times and prose is what this project has proven does not hold. It gets a mechanism now, or it will be said a thirteenth time.
