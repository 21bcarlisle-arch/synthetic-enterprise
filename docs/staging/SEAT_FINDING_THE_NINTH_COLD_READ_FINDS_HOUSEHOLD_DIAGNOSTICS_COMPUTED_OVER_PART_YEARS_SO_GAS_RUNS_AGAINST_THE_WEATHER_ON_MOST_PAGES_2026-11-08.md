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
