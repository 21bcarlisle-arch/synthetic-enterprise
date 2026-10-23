# Pre-registration: the new tier's two point intervals, rounding or model mix

**Severity:** LATENT · **Lane:** H_harness · **Atom:** none (direction) · **Claim:** `the-new-tier-point-fit-is-separated-at-the-next-reading`

*Delivery seat (executor), 2026-10-23 17:15Z. Written BEFORE the per-model split below was computed and
before the director's next reading exists.*

## The question

On the new tier, 06:55-09:45 BST cost USD 7.9 per point and 09:45-15:20 cost USD 12.7
(`docs/staging/advisor/done/DIRECTOR_READING_USAGE_8PCT_FRIDAY_1520_2026-10-23.md`). Each reading is a whole
percent, so each interval carries about ±1 point, and the bands only just overlap (10.2-10.5). Three
explanations: (R) rounding alone; (M) the interval mixes differ by model or token class and the meter weights
them differently from list price; (X) something else (the meter's window, an unpriced model, a transcript the
tool does not read).

## Predictions, before measuring

1. **Prior:** R 55%, M 30%, X 15%.
2. **Mix measurement (now, no reading needed):** the share of weighted USD that is Opus differs between the two
   intervals by **under 15 percentage points**, and the cache-read share by under 15 points. If either moves by
   more, M rises above R.
3. **At the next reading (t2, p2), the third interval 15:20 BST -> t2:** its USD per point, with its ±1-point
   band, overlaps the pooled 9.1-11.7.

## Decision rule at the next reading

- Third interval's band overlaps 9.1-11.7 and the mix moved under 15 points: **R**. Carry the pooled fit from
  the tier change to t2 (`usd_per_point(since=TIER_CHANGED_AT)` over first and last readings).
- The mix moved by 15 points or more: fit points = a*USD_opus + b*USD_rest over the three intervals. If every
  interval's residual is inside ±1 point and a and b differ by more than 30%, **M**: price the forward pace
  at the mix the post-reset lanes will run, not the pooled average.
- Neither: **X**. Carry the pooled fit with the widest band of the three, and file what was ruled out.

**Done means:** the third interval is in `POINT_READINGS`, this file says which of R/M/X held beside the
prediction, and the post-reset weekly pace (88 points over 168 hours, about 0.52 per hour) is set on the dial
from the chosen conversion.

## Results

*(below this line, written after measuring)*

**Mix, measured 17:15Z** (`_priced` over every transcript and subagent, each message once):

| Interval (UTC) | Weighted USD | Opus share | output / 1h write / 5m write / cache read |
|---|---|---|---|
| A 05:55-08:45 | 31.5 | 98.4% | 21 / 30 / 1 / 47% |
| B 08:45-14:20 | 50.8 | 98.7% | 22 / 35 / 2 / 41% |
| C 14:20-17:15 (open) | 23.3 | 99.5% | 22 / 33 / 0 / 44% |

**Prediction 2 held, and M is refuted** for model and token class: Opus moved 0.3 points, the largest class move
is 6 points. Both intervals are one model at one mix, so no meter weighting that differs from list price can
make them differ. 13 `claude-haiku-5-5` messages in B are unpriced (`PRICE` has no Haiku 5.5 row, and no price
is entered here without a source); at Haiku's scale they cannot move B by a point.

**Rounding is narrower than the "bands overlap" line said.** Whether the meter rounds or floors, one conversion
fits both intervals only in **USD 10.16-10.5 per point**, and only at the corner where A carried about 3 points
and B about 5: the 06:55 "0%" truly near 0.5 (round) or 1.0 (floor), 09:45 near 3.5/4.0, 15:20 near 8.5/9.0.
R survives, but only there, so its prior falls from 55% to about 35% and X takes the rest.

**The leading X:** spend on the same allowance that no local transcript records, the director's own claude.ai
and advisor chats or any cloud session. It raises points with no USD beside them, so it LOWERS the measured
USD per point in the interval where it happens; A, the lower interval, is the morning the tier changed and two
readings were relayed. That predicts the measured conversion swings with the director's own chat use, and the
true cost of a point of THIS machine's work is nearer the top of the range.

**Sharp predictions for the next reading, written now.** Let U = weighted USD from 14:20Z to t2.
- **R:** the reading is round(8.5 + U/10.3) if the meter rounds, floor(9.0 + U/10.3) if it floors. Neither
  form allows a reading below 8 + U/10.5.
- **X (off-transcript spend):** the reading runs ahead of R by however much the director chatted; a reading
  more than one point above R's is X, and one point or more below R's refutes both and is "something else".
- At 17:15Z U = 23.3, so R says 10 or 11 now.

**The post-reset pace, conditional.** 88 points over 168 hours is 0.52 points an hour: USD 5.4 an hour at
10.3, 6.6 at 12.7. If X holds, the machine's budget is the allowance less the director's own use, which a
reading cannot see alone; the pace then wants his chat share from him, or a margin. Interval C has run USD 8.0
an hour, about 0.78 points an hour at 10.3, under the 1.4 the pre-reset window allows; nothing to change on
the dial, which is already at its fastest word (`normal`, to 26 Oct 03:00Z).
