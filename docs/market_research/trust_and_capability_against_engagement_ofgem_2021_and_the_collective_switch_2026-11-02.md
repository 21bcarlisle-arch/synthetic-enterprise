**Knowledge:** the-customer-needs-framework

# Trust and capability: confidence separates engaged from disengaged households by about 31 points and trust by 2 to 6, so capability is a candidate moderator and trust is not yet one (2026-11-02)

This is page 6 of the customer-needs domain as `docs/design/THE_KNOWLEDGE_BASE_STRUCTURE.md` §4 ranks it. It answers
the 30 Oct corpus steer (`docs/staging/advisor/DIRECTOR_STEER_BUILD_THE_CUSTOMER_KNOWLEDGE_CORPUS_AND_PROPOSE_THE_NEXT_SIM_ADDITIONS_2026-10-30.md`),
Ask 1 and Addendum 16:50 step 2, which asks for "trust and capability as moderators" to be tested rather than taken.

Grades as on the sister pages: **D** derived by us from primary data, **P** reported in a primary publication by the
body holding the data, **S** a secondary summary, **A** an assumption with a range.

**Sides.** World: whether a drawn household carries a trust or a capability trait that changes how it shops. Both
are hidden truth. Supplier: neither is observed directly; a supplier sees channel (phone or online), response to
contact, and complaints, and could ask.

No predictions were filed before these sources were read; the 2021 survey was already in the lake and was read for
this page today.

## 0. What each word means here, stated before any number

- **Capability** is Ofgem's CONF2: "How confident or unconfident do you feel about" comparing energy deals, and
  choosing the best deal. It is *stated confidence*, not a tested skill.
- **Trust** is three questions, not one: QTRUST, the energy *sector* "to be fair in the way they deal with customers";
  Q68, *your own* supplier to treat you fairly; Q68, your own supplier to charge a fair price. They are kept apart.
- **Engaged** is Ofgem's: switched supplier, switched tariff or compared, in the past 12 months, self-reported.
  Disengaged is none of these. It is a reported action, so the comparison below is a stated trait against a reported
  behaviour in the same people (the G3 kind of page 5).

## 1. How far each separates engaged from disengaged (P, differences D)

Source: Ofgem/Ipsos Consumer Survey 2021, Engagement report, slides 38-40, 44-45 and 60; fieldwork 19 Aug to 17 Sep
2021, before the crisis; online, n = 4,037 (engaged 2,638, disengaged 1,399). Raw in
`data/lake/ofgem_consumer_survey_2021/`.

| Measure | Engaged | Disengaged | Difference (D) | ±95% (D, simple random sample) |
|---|---|---|---|---|
| Confident choosing the best deal | 75% | 44% | **+31** | ±3.1 |
| Confident comparing deals | 76% | 42% | **+34** | ±3.1 |
| Trust the energy sector | 35% | 33% | +2 | ±3.1 |
| Trust own supplier to treat you fairly | 48% | 42% | +6 | ±3.2 |
| Trust own supplier to charge a fair price | 40% | 36% | +4 | ±3.2 |

The intervals are ours, from the bases, ignoring the survey's weighting and design effect, so they are too narrow if
anything. Ofgem marks the confidence differences significant and says engagement "does not seem to be linked to trust
in the energy sector".

**Confidence separates engagement five times or more as strongly as trust does.** Sector trust does not
separate it at all at this sample size.

## 2. Who lacks confidence (P)

- Prepayment households (n = 339): 44% confident comparing and 49% confident choosing, against 63% and 64% overall;
  41% agree "switching is a hassle I haven't got time for", against 28% overall (slide 60).
- Groups Ofgem names as higher: earning £16k+ 69%, owner occupiers 67%, against 64% overall (slide 38).

**Extended.** Income and tenure move confidence by 3 to 5 points; prepayment by about 15 to 19. Capability is not
mostly the precarity axis wearing another name: on these crossbreaks it tracks the payment route far more than income
or tenure. Prepayment is itself partly imposed (natural experiments page §4), so this does not say which way it runs.

## 3. The messenger effect is familiarity, at least in part (P, differences D)

Source: Ofgem's Collective Switch trials, Trial 1, `data/lake/ofgem_collective_switch_trials_2019/trial_results.csv`.

| Arm | Switched |
|---|---|
| Letters from the supplier | 26.9% |
| The same offer from Ofgem | 15.0% |
| From Ofgem, with a reminder in the supplier's envelope | 18.5% |
| Control | 2.6% |

The packs read the 12-point gap as a trust effect. The reminder arm changes only the envelope, and recovers 3.5 of
the 12 points (D). The sender a household recognises matters; whether that is trust, familiarity or simply opening the
letter is not separable here. **Re-graded:** the messenger effect is P; "trust" as its cause is the advisor's reading
and is **not shown**.

## 4. Verdict on the advisor's synthesis (Addendum 16:50, step 2)

| Pack claim | Verdict |
|---|---|
| Trust and capability are the axes that separate Ofgem's six segments | **Not tested here**: the 2017 segmentation's construction is page 7's subject. |
| Capability is a moderator of shopping | **Supported as a strong correlate** (+31 to +34 points). **Not shown as a cause**: engagement is defined by having acted, and acting may build the confidence. |
| Trust is a cross-cutting moderator | **Not supported as a separator of engagement**: +2 (sector, not distinguishable from 0), +4 to +6 (own supplier). Ofgem's own line that high trust "may also increase inertia" points the other way for the disengaged. |
| The messenger effect shows trust | **Corrected**: the envelope alone recovers 3.5 of the 12 points; familiarity cannot be ruled out. |

## 5. What this changes

**World (under the parsimony ruling of 30 Oct: add a correlation only if it is strong and changes a supplier
result).**
- **Capability** qualifies on strength. It would change a result if the supplier's offers differ in the effort they
  ask (online against phone, assisted switching), which the collective-switch trials show they do. It is a candidate
  for the Ask 2 roadmap, drawn as one trait, correlated with prepayment and only weakly with income.
- **Trust** does not qualify on this evidence. It stays out of the draw. Re-open it if a revealed source shows it
  moves behaviour by more than a few points.

**Supplier.** The supplier cannot see confidence, but it can see the channel a household uses and whether it answers
contact. Those are the observables a capability trait would leave.

## 6. Gaps

- **GAP-TC1:** no GB source links stated confidence to *later* behaviour in the same households; the comparison
  above is cross-sectional with a reported action.
- **GAP-TC2:** the crossbreak by prepayment and the crossbreak by income are separate tables; their overlap is not
  published, so how much of the prepayment gap is income is unknown.
- **GAP-TC3:** the 2021 survey is pre-crisis. Whether the crisis moved confidence or trust is not read here.

## Sources

- Ofgem/Ipsos (2023), *Consumer Survey 2021: Engagement report*,
  https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf
  (lake copy SHA-256 `341a950b3dff6de3736a54fbe5e5f98afcb44f963532276f3a7760e6963e0c04`).
- Ofgem (2019), *Ofgem's Collective Switch Trials*, Trial 1, Figure 4 and paras 4.1-4.3, as read on the natural
  experiments page.
