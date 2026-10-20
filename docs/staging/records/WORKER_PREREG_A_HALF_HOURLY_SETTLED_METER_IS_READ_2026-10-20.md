**Severity:** NORMAL · **Lane:** W2_customer_generator · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`

# Pre-registration: a half-hourly-settled meter is read, so C7 stops billing on estimates

*Worker tick, 20 Oct 2026. Filed in the same commit as the change and before any run carries it.*

## The change

`simulation/meter_reads.is_communicating`: a `metering: "HH"` record counts as in smart mode
whatever its id drew (K8: `read_access_and_theft_duties.md` §2.3, last bullet). Of the roster's
seven HH records, only C7 draws traditional mode (C8, C9 and C_IC1–4 do not), so on the roster
this is one account. It answers the read-stream incoherence that the leaver finding left open
under leg (b): C7 was settled on every half hour yet billed 42 estimates out of 42.

At real inputs, over the month-end-28th grid from 2016 to 2025, the feed returns 118 actual reads
out of 120 for C7 with its HH flag, against 4 out of 120 without it. The 2 misses are late remote
reads, which the rule already allows.

## Predictions (baseline: the latest full-window run without this commit; grade on the first one with it)

- **H1.** C7 bills at most 3 estimates in its tenure (it bills 42 now). Every one of them is a
  late remote read.
- **H2.** No account outside C7 changes any read status. *Named fall-back:* an account that moved
  into an HH premise (C8's successor `OCC-d8e674fa38de` reads C8's file) changes only if its
  record carries `metering: "HH"` and its id draws traditional mode. If one does, it is the same
  rule reaching it, and I will name it, not count it as a refutation.
- **H3.** C7's billed/true is within 0.98–1.02 in every full year, 2016–2018. It is
  0.996 / 1.025 / 1.007 today, on an estimate.
- **H4.** The defect-4 sweep, with `KNOWN_OPEN_INVERSIONS` and its excuse emptied, finds 0
  inversions.
- **H5.** Book-wide billed electricity moves by under £500 in total. C7's estimate already sits
  near true use (leg (d)), so actual reads move little money. Most of the change is in when it
  lands, not how much.

**Interaction to keep apart:** leg (b), the CoS-read settlement (`a-change-of-supply-read-settles-beside-the-true-rows`,
in hand on another seat), had C7's closing run of estimates as most of its population's money.
A run carrying both commits, compared with a baseline carrying neither, has two variables.
