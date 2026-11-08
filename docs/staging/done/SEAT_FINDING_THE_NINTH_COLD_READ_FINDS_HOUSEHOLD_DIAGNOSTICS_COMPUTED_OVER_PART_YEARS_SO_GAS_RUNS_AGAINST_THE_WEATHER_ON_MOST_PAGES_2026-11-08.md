**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 4 · **Atom:** `unminted`

# The ninth cold read finds household diagnostics computed over part years, so gas "runs against the weather" on most pages (N24, 2026-11-08)

**Found by.** The ninth cold read's O4 and O24, on the af31e73fa7 book.

**(a) "Gas against the weather"** (`site/explore/index.html`, `hddPanel`).
- The panel sums the household's gas kWh by calendar year and correlates the sums with the year's heating degree
  days.
- Years the household was on supply for only part of are included.
- SYN-2016-250 prints "2016 7,240" and "2021 11,594" against 16,090–17,204 in its full years. The panel then says
  "r = -0.78 — weaker than the heating story predicts. On this household the year-to-year swing is coming from
  something other than temperature".
- **That sentence is false. The swing comes from the part years.**
- Over every gas page with three or more years from 2016–2021 (`/var/tmp/ninth-read/`, inline census):
  - 297 of 304 include a part year;
  - 259 print a negative r, 256 of them with a part year in.
- The census used the six years of degree days the packet prints. The page uses every archive year, so the counts
  are indicative, not the page's own.

**(b) "Winter months run 6.1× summer months on this meter — this home heats with electricity"** is printed for
PROS-2024-0335.
- Its only summer is a 7-day June 2025 stub.
- It also takes gas (2,961 kWh).

**Why it is wrong.** A correlation or a seasonal ratio compares like with like. Part years enter at a fraction of a
year's use, whatever the weather. CalTRACK, which the carbon panel already follows
(`proving_and_showing_household_savings_2026-10-25.md`), sets a minimum data sufficiency before a baseline is read.
The carbon panel withholds part years. These two panels do not.

**A correction to the eighth read.** The eighth read filed its r near 0 "against degree days on two accounts" as the
London-series class. I cannot now say that was right: part years would produce the same reading, and I did not
check for them then.

**Next.** A blind row has been written and landed `checkable: false`. The fix is on the page: use only full
supplied years, and print "too few full years" when fewer than three remain. The heating verdict needs a full summer
and a full winter.

**Reverse.** Delete this file.

## Done

*Delivery seat, 2026-11-08, under the 26 Oct correctness ruling (step 5, examples are a gate).*

**The fix is on the page** (`site/explore/index.html`). Both panels now read whole months on supply only.
- `interiorMonths` drops a series' first and last months. The monthly series carries no day count, so either
  end may be a stub. This also drops a supply that really began on 1 January, which is the safe direction.
- `fullYears` keeps the calendar years with all 12 interior months. That is the carbon panel's
  "12 months billed" (`half_hourly_footprint.Leg.full_year`), less the possible stubs.
- **Gas against the weather** correlates full years only. It names the part years it left out, and it says
  "Too few full years" where it cannot compute r (fewer than four points, as before).
- **The heating verdict** needs every one of Dec, Jan, Feb, Jun, Jul and Aug as a whole month.

**The page's own code over every customer file in `site/data/customers/`.** 586 gas pages, 707 electricity, real
`weather.json`, HEAD against the fix:

| | before | after |
|---|---|---|
| gas pages printing an r | 287 | 151 |
| of which negative | 170 | **62** |
| electricity pages told "heats with electricity" | 70 | 41 |
| electricity pages with no seasonal verdict | 51 | 151 |

**The residual is not part years, and I cannot yet say what it is.** 62 of the 151 full-year-only gas pages still
read r < 0. The ones I looked at have full years whose gas moves about ±3% while degree days move about ±10%.
For example, OCC-17ff099218d5g reads 6,335 / 6,092 / 6,432 / 6,429 kWh over 2020–23, and 2022 is the mildest
of those years. That looks like the world's gas not answering to the weather. That may be the N17 /
SYN-2016-206g world cause, which has a dated exception (recheck 23 Nov, W2_30 and the ERA5 pull). Prediction,
filed before that recheck: once N17's cause is fixed, the negative share among full-year pages falls below a
quarter (now 62/151 = 41%). The page now prints that sentence only where the full years show it, so it is no
longer false on the page.

**The correction to the eighth read stands.** Its "r near 0 on two accounts" may have been part years.

**Test.** `site/explore/test_a_part_year_never_enters_the_weather_or_heating_verdicts.py` drives the page's
`hddPanel` and `seasonalSwing` in node.
- It is red on the parent (3 of 3).
- Three mutations fire: no stub drop; any month counts as a year; one summer month counts as a summer.
- The third first passed, because its fixture's only summer month was also the series' last month. That was a
  missing fixture, not an equivalence, and a whole-June-and-July case now kills it.
- The partition control asserts that a whole year still gets a verdict.

The blind row this finding landed stays `checkable: false`. The runner grades the export, and these panels are
page arithmetic.
