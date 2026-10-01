# Pre-registration — the 2025 standing-charge row (written 2026-10-01 18:40 BST, before either arm ran)

Claim `add-the-2025-standing-charge-row-from-the-cap-level-model`.

Change: add 2025 rows read from Ofgem cap level model v1.31 by the method that reproduces 2016-2024
exactly (DD Nil sheets, Total/365, median over the 15 Total rows INCLUDING the model's GB-average
row, day-weighted mean over the calendar year, later column wins on overlap):
electricity 51.23p (was clamped to 2024's 57.11p, -10.30%), gas 29.58p (was 28.57p, +3.54%).

Base sizes from the last default world (`/var/tmp/se-sc-attr/new.json`): 2025 standing charge booked
£6,456.86 electricity, £2,581.01 gas.

Predictions (ARM old = HEAD table, ARM new = HEAD + 2025 rows; one default world each, same base):
- P1. Every settlement record dated before 2025-01-01 is identical in revenue and standing charge
  (nothing reads a 2025 standing charge before 2025). If this fails, something forward-reads.
- P2. 2025 standing charge: electricity -£665 ± £10, gas +£91 ± £5, net -£574 ± £15.
- P3. 2025 revenue moves by about 0.88 x net SC change = -£505, band -£460 to -£574 (0.80x to 1.0x).
  The 12% feedback runs through renewal unit rates; a renewal priced in 2025 sees a lower electricity
  charge, so unit revenue should RISE slightly. I do not know the split by fuel in advance.
- P4. Consumption (kWh) per account identical between arms to 1e-6 (no behavioural feedback on use).

*Timestamp correction, added after the run: the header's "18:40" was my estimate. The file's mtime
is 18:33:12 BST; both arms were launched after it and wrote their results at 18:54-18:55.*
