**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

# RESULT — on GROSS margin the chosen book is INSIDE the blind spread. On NET margin it is BELOW every blind arm

**Filed 2026-09-11, delivery seat.** Grades all five predictions of
`SEAT_PREREGISTRATION_TWO_FABRIC_BLIND_ARMS_SEPARATE_FEWER_ACCOUNTS_FROM_DIFFERENT_ACCOUNTS_2026-09-11.md`,
landed as **`eed120328`** before either arm had written a byte.

**All five hold. And the one that matters most — PC2 — held its ARITHMETIC and its stated MEANING
is wrong.** That is recorded first, because it is the only reason to file predictions at all.

---

## Five arms, one world

`world_identity.digest` is **`39a192ce04c1eda8` on all five**, so these are directly comparable and
not five runs of five worlds. Two are P6's published pair read back from its own output files
(`/var/tmp/p6_arm_cull.json`, `p6_arm_chosen.json`); one is the other seat's arm, cited from a
result that is **not on origin** (see the finding below); two are this turn's.

| arm | sees fabric? | accounts | cy | gross margin | revenue | bad debt | net margin | net a/cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **A** cull (P6) | no | 91 | 1195.1 | 383,688.97 | 676,791.53 | 11,675.76 | 147,954.26 | 98,643.67 |
| **C′** other seat's blind arm | no | 83 | 1194.9 | 372,220.98 | 657,273.41 | 10,916.13 | 143,776.65 | 94,339.21 |
| **C** this turn, cull truncated to 83 | no | 83 | 1155.4 | 380,829.29 | 689,269.14 | 8,533.78 | 143,764.30 | 94,498.40 |
| **D** this turn, tenure-only chooser | no | 89 | 1199.9 | 386,386.18 | 695,546.19 | 9,462.24 | 149,154.09 | 97,326.44 |
| **B** chosen | **yes** | 83 | 1194.9 | 374,295.73 | 661,157.87 | 14,400.86 | 139,439.50 | 90,409.10 |

## THE RESULT — where the chosen book sits inside the envelope of FOUR fabric-blind books

Neither P6 nor the other seat could ask this, because each had at most two blind arms and an
envelope needs three. With four:

| line | blind envelope | its span | chosen book | verdict |
|---|---:|---:|---:|---|
| **Gross margin** | 372,221 … 386,386 | **3.81%** | 374,296 | **INSIDE** |
| Revenue | 657,273 … 695,546 | 5.82% | 661,158 | **INSIDE** |
| **Bad debt** | 8,534 … 11,676 | 36.82% | 14,401 | **ABOVE all, by +23.34%** |
| **Net margin** | 143,764 … 149,154 | 3.75% | 139,440 | **BELOW all, by −3.01%** |
| Net after cost to serve | 94,339 … 98,644 | 4.56% | 90,409 | **BELOW all, by −4.17%** |

**On gross margin, P6's −2.45% is SMALLER THAN THE SPREAD BETWEEN BLIND BOOKS (3.81%), and the
chosen book falls inside it.** Four books that cannot see a single attribute of a single home
differ from each other by more than the chosen book differs from any of them. **Nothing about the
homes is attributable on that line.** P6's headline figure is real, reproduced and correctly
measured — and it is not evidence that choosing costs gross margin.

**On net margin and net after cost to serve it survives, and cleanly.** The chosen book is below
**every** blind arm, by 3.01% and 4.17% against the nearest one. That is not a spread artefact:
it has to beat four books to be a coincidence and it beats none of them.

**On bad debt it survives most strongly of all.** The chosen book is above every blind arm by
23.34% against the *highest*. The blind arms span 36.82% between themselves — bad debt is by far
the noisiest line here — and the chosen book still clears all of them.

**So the sentence is: choosing for difference does not cost gross margin; it costs BAD DEBT, and
the bad debt is what takes net margin down.** That is the same direction the other seat measured
at matched count, mix and spend (+31.92% bad debt, net margin −3.02%), reached by a different
route, and the agreement of two differently-built instruments is worth more than either.

## The predictions, graded

| | prediction | outcome |
|---|---|---|
| **PC1** | ARM C gross margin below ARM A's £383,688.97 | **HOLDS.** £380,829.29, −0.75% |
| **PC2** | ARM C's gross margin per committed cy exceeds ARM B's £313.24 by >1.0% | **HOLDS on the number, £329.61/cy, +5.22%. ITS STATED MEANING IS WRONG — see below.** |
| **PC3** | ARM D's gross margin within ±1.5% of ARM A's | **HOLDS.** £386,386.18, **+0.70%** |
| **PC4** | ARM C and ARM D bad debt both below ARM B's £14,400.86 | **HOLDS.** −40.74% and −34.29%; both below ARM A's too |
| **PC5** | each run reproduces its own probe | **HOLDS exactly.** See below |

### PC2 held its arithmetic and its inference is refuted — beside the claim, not revised away

PC2 was written as: *"Holding means the blind book earns more per customer-year than the chosen
book at the IDENTICAL account count, so the −2.45% is a COMPOSITION effect and 'fewer accounts'
does not explain it."*

**The number came in at +5.22% and that conclusion is false.** Two things I did not see when I
wrote it:

* **ARM C spends 3.3% fewer customer-years, so dividing by customer-years flatters it.** I
  normalised by the very quantity my arm failed to hold, and read the normalisation as composition.
  **Before dividing two numbers, say what each one counts** — I divided a gross margin earned over
  one book by a budget committed on another shape and called the ratio a property of the homes.
* **The other seat's arm holds count, year mix AND spend, and it lands at £372,220.98 — BELOW ARM
  B.** At genuinely matched shape the blind book earns *less* than the chosen one, so composition
  on gross margin is a small **positive**, not the negative my inference asserted.

**The envelope above is what actually settles it, and it says neither of us should be claiming a
gross-margin composition effect in either direction**, because the effect is smaller than the
spread between blind books. My pre-registration named the outcome it would find hardest to write
up as "PC2 failing while PC3 holds". What happened is worse for it than that: PC2 passed and was
wrong anyway, which a pass/fail grade could not have caught.

### PC3 is the one that had to hold for anybody's decomposition to mean anything

ARM D runs the **entire shipped mechanism** — the `k` bisection, the year cover, the NNLS weight
fit, the headroom invariant — with `CHOICE_AXES` stripped to `("customer_years",)`. One variable
against ARM B: what the axes can SEE.

It lands at **+0.70% gross margin against the cull**, inside the ±1.5% band, at 89 accounts and
1199.9 cy. **So the selection MACHINERY does not move the P&L; only the fabric information does.**

This was the confound nobody had named, and it is the load-bearing result of this turn: it is what
licenses reading the other seat's C′ → B leg as composition rather than as an artefact of routing a
book through the chooser's fitting. Had PC3 failed, P6's −2.45% could not have been read as a
statement about homes at all, and every conclusion on this page and theirs would have been void.

**And ARM D falsifies the P6 result doc's own explanation of the shrink**, as the pre-registration
predicted it would before any P&L existed. P6 said the chooser *"spends the same customer-year
budget on fewer, longer-tenured accounts"* — but the tenure axis alone settles **89** accounts, not
83. The shrink from 91 to 83 is the **fabric** axes forcing distinct medoids, not `customer_years`
concentrating the budget.

### PC5 — determinism across the process boundary

Each arm's standalone probe reproduces its own full run's campaign cross-check **exactly**:

```
              probe seed 42     run's _p6_campaign      probe seed 20260724   predicted
ARM C   83 settled / 1160.6   83 settled / 1160.6      83 / 1155.4           83 / 1155.4
ARM D   88 settled / 1194.7   88 settled / 1194.7      89 / 1199.9           89 / 1199.9
```

ARM D's 89-at-base-seed against 88-at-seed-42 is **two seeds, not nondeterminism** — the same shape
P6 recorded for its own 84-vs-83.

## What this arm CANNOT say

* **ARM C is a weaker instrument than the other seat's and this page says so.** It truncates the
  systematic rule globally, so it holds count but lands at a different year mix and 3.3% less
  spend. It is a fourth point in the blind envelope, which is what it is used for here; it is
  **not** a clean one-variable arm and PC2's failure of inference is the direct cost of my having
  treated it as one.
* **One seed.** All five arms are deterministic at a fixed seed. The blind envelope is a spread
  over four *book shapes*, not over four *worlds*, so it bounds "how much does the P&L move when
  you change which blind book you settle" and says nothing about sampling error across worlds. The
  −3.01% net-margin and +23.34% bad-debt clearances are stated as orderings against four arms, not
  as confidence intervals.
* **Not publishable pounds.** All five arms ran `SIM_FAST_MODE=1`, identically, so the differences
  are clean and the absolute figures are not comparable to `docs/reports/run_output_latest.json`.
  **Nothing here belongs on a page as a headline.**
* **A labelling artefact, inherited.** ARM C and ARM D both reach the book through
  `choose_settled_sample`, so their run records say `settlement_selection: chosen_weighted` though
  neither saw a home on the fabric axes. No figure depends on it.
* **The two arms ran concurrently.** P6's `8dcffd8d1` discharged that question by measurement for
  its own pair, and this turn did not re-discharge it for these two. The world digest is identical
  across all five and both probes reproduce both runs, which is evidence and not the same thing.

## The harness

`/var/tmp/p6_arm3.py`, ARM C as `cull83` and ARM D as `tenure`; the probe that fixed each arm's
book before any run is `/var/tmp/p6_probe_arms.py`. **Both are reproduced in full in the
pre-registration's own commit message and in `eed120328`.** ARM C returns the systematic
`int((i+1)r) > int(i*r)` positions at `r = 83/n` through `choose_settled_sample`'s contract, with
uniform weights `n/83`; ARM D patches `CHOICE_AXES` and `demand_vector` and touches nothing else.

**This path collided with the other seat's harness of the same name and this seat's write destroyed
theirs.** Recorded in
`docs/staging/SEAT_FINDING_ONE_CLAIM_ID_TWO_SEATS_TWO_FORKED_TREES_AND_THE_COMPLETE_ANSWER_IS_STRANDED_ON_THE_SIDE_THAT_CANNOT_LAND_2026-09-11.md`,
along with the fact that their result, their pre-registration and both their findings are in 34
commits that never reached origin. **Their selection artefact `/var/tmp/p6_armC.json` survives and
their arm is reproducible from it.**

## Where this leaves P6 and what is next

P6 is undisturbed: its arms reproduce from its own output files to the penny. What changes is what
may be said about its number.

* **"The chosen book is 2.45% worse on gross margin" must not be read as a cost of choosing.** The
  figure is correct and the inference is not available: four fabric-blind books span 3.81% on that
  line and the chosen one is inside them.
* **The real, surviving cost of choosing is bad debt**, and through it net margin. Both clear the
  blind envelope outright.
* **Next:** the other seat named the arm that splits its −2.99% size-and-timing leg into *fewer*
  and *earlier* — 83 accounts at **A's** year mix and A's spend. This turn's ARM C is that arm on
  the mix and misses it on the spend. Running it at matched spend is one 13-minute arm and it is
  the last one this question needs.
