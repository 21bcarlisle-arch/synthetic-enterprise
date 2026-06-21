"""Time-of-Use period classification for UK half-hourly settlement.

Settlement periods 1-48 map to 00:00-00:30 through 23:30-00:00.
Period N covers the half-hour starting at (N-1)*30 minutes from midnight.

UK ToU structure (simplified Agile/smart-tariff convention):
  Peak    — morning (07:00-11:00) + evening (16:00-20:00) on weekdays
             periods 15-22 and 33-40 on Mon-Fri
  Off-peak — everything else (nights, weekends, shoulder hours)

Revenue-neutral design: with approx. 30% of residential consumption in
peak periods, peak_multiplier=1.5 and offpeak_multiplier~=0.79 keeps
expected revenue equal to a flat rate of the same forward price.
(Exact revenue impact emerges from real HH data — the multipliers are
deliberately modest to avoid large redistributions in the first phase.)
"""

import datetime

# Weekday settlement periods classified as peak (1-indexed, both inclusive)
_MORNING_PEAK = range(15, 23)   # 07:00-11:00
_EVENING_PEAK = range(33, 41)   # 16:00-20:00


def is_peak_period(date_str: str, period: int) -> bool:
    """Return True if this settlement period falls in a peak ToU window.

    Peak is defined as morning (07:00-11:00) or evening (16:00-20:00)
    on a weekday (Mon-Fri). All other periods — nights, weekends, and
    shoulder hours — are off-peak.
    """
    dt = datetime.date.fromisoformat(date_str)
    if dt.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    return period in _MORNING_PEAK or period in _EVENING_PEAK


def period_start_time(period: int) -> datetime.time:
    """Return the start time for settlement period N (1-indexed)."""
    total_minutes = (period - 1) * 30
    return datetime.time(total_minutes // 60, total_minutes % 60)
