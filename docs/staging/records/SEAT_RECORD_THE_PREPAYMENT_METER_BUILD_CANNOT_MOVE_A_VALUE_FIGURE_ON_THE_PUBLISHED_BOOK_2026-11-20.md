**Severity:** LATENT · **Lane:** B_commercial · **Atom:** `unminted`

# The prepayment meter build (f0445b2dc) cannot move a value figure on the published book (20 Nov)

Claim `prepayment-build-is-checked-against-the-value-figures`. This answers the open row in DIRECTION.yaml
`what_i_got_wrong`: "the value pair should be unaffected. That is the commit's own claim, and no pair has checked
it." Books read: `run_output_7f0723b46e_20261118T110420Z.json` (A) against
`run_output_67d454905c_20261119T184502Z.json` (B). Both share world digest `cdba75ebb9197b33` and the full window
to 2025-06-07. 7f0723b46e is an ancestor of 67d454905c, and 107 commits lie between them.

## The grade

**The row can be graded true. f0445b2dc cannot have moved any company figure in B, and it cannot move one in the
0.12 pair.** The commit was right about the result and wrong about the reason. "Changes no company code" does not
make a build inert: f0445b2dc does change what the company's door answers. It is inert because of how that answer
is used:

1. The world's new reports reach the company through `get_meter_supply_events`. The company's only reader is
   `CollectionsDesk._read_supply_events` (`company/billing/collections_journey.py`).
2. That reader changes a decision in one place only. `_self_disconnection_check` in
   `company/billing/winter_moratorium.py` reads `record.evidence` only for `EnforcementAction.METER_RECOVERY`.
   The watch's dates and `met=True` are the same before and after, because the door already answered `[]` for an
   account with no meter.
3. `METER_RECOVERY` is asked only from `_pause_recovery`. That runs only from `_read_meter_recoveries`, and only
   for a meter the desk fitted (`self._meters`).
4. No meter is fitted. `method_prepayment_offer_take_up_share` defaults to 0.0 at both commits, and at 870201d1e7.
   The 0.12 pair's driver (`/var/tmp/vtc-driver/driver.py`) sets no toggle. Both books contain no
   `recovery_through_the_meter`, `credit_facilities_on_meter` or `interruption_answered` row.
5. The new draws use their own substreams, keyed per account (`SUPPLY_EVENT_STREAM`, `OVER_3H_STREAM`), so no
   other draw shifts. The summary is written to the world-walk-truth companion file, never to run_output. In B it
   reads 109 prepayers on a meter and 723 interruptions, 451 of them over 3h.

**When this stops holding:** the claim holds while take-up is 0. If take-up is switched on (or once step 2 of
energy_vulnerability_observables s.7, cold and money coupling, lands), a stock prepayer the desk later fits will
carry its interruptions into the METER_RECOVERY gate. From then on a pair on a tree without f0445b2dc measures a
different company.

## What moved between the books, and what can account for it

| Figure | A (7f0723b46e) | B (67d454905c) | Change | f0445b2dc? |
|---|---|---|---|---|
| Net margin after cost to serve | 303,074.94 | 295,149.41 | −7,925.53 | no (above) |
| Total net | 750,224.98 | 743,901.35 | −6,323.63 | no |
| Revenue | 3,166,717.09 | 3,200,292.03 | +33,574.95 | no |
| Gross | 1,841,206.33 | 1,849,654.51 | +8,448.18 | no |
| Cost to serve | 447,150.04 | 448,751.94 | +1,601.90 (17 accounts) | no |
| Realised bad debt | 8,114.21 | 7,721.82 | −392.39 | no |
| Provisioned net | 624,519.36 | 615,927.89 | −8,591.48 | no |
| Enterprise value | 276,127.72 (222 accts) | 264,822.52 (224 accts) | −11,305.20 | no |
| Churned billing accounts | 358 | 356 | −2 | no |
| SVT departures / home move-outs | 252 / 272 | 251 / 271 | −1 / −1 | no |
| Bills | 53,605 | 53,798 | +193 | no |

Per customer (`per_customer_lifetime`, 1,306 legs in both books, the same 1,306):

| Group | Legs | Net moved | Mean change in net margin after cost to serve |
|---|---|---|---|
| Stock prepayers (billed through `prepayment` in B; the same 174 in A) | 174 | 127 | −£18.41 |
| Everyone else | 1,132 | 826 | −£4.17 |

The prepayers' larger fall is made by who they are, not by f0445b2dc. I fitted the change per year against
kWh/day and kWh/day² with a prepayer indicator, over legs billed at least 180 days. The indicator reads:
electricity net **−£12.22/yr (se 23.69)**, electricity revenue −£41.94 (se 78.80), gas net −£0.36 (se 1.41). Each
is within one standard error of zero. The raw gap is consumption: net falls most on low-use legs in both groups.
That fits c71d2521d moving network cost from per kWh to per day, which 3d75dfd74e graded as charged exactly on B.
This regression is a check for consistency and has little power. The proof is the code path above.

**Which commit moved the totals: I cannot yet say.** Between the books, besides f0445b2dc: c71d2521d (W3_3
network split), b484f20447 and 843143e131 (W1_14 ERA5 cells in the weather store), 4accbb828d (W2_30 OCC- gas
legs), 11449fa884 and 7d96a372e7 (EPC register), 944eaf3a6f and 1c5351d187 (close set-off), and four KNIFE3
commits that state byte-equal replays. Bills first differ in 2016 for 312 legs, so the cause is not one late
year. 3d75dfd74e has already said the same of the W3_3 network line ("the population moved too ... cannot be
attributed"). The one-variable reading for the margin is that W3_3 replay. It is not a new run to queue here.

## What this means for the 0.12 pair

The pair runs on 870201d1e7, a salvage fork that is not an ancestor of 7f0723b46e. Its tree lacks f0445b2dc,
and by the argument above that absence changes nothing the pair measures. The fork also lacks c71d2521d, the
ERA5 cells and W2_30. Each of those moves £ levels in the book. A pair's **difference** between its arms depends
on the retention desk and transfers to the published book only as far as those world changes leave the flip
households alone. That is a separate question from this row, and I have not tested it.

## Queued

The code-path argument is a reading, not a measurement. The one-variable confirmation is the run at 67d454905c
with f0445b2dc reverted, against 67d454905c as it stands: same seed, 2016 window. Prediction, filed now:
**run_output byte-equal apart from `run_identity_fields`, and only the world-walk-truth companion differs, by its
`prepayment_supply_events` key.** It is handed on as `f0445b2dc-one-variable-replay`.
