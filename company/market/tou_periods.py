"""UK ToU period classification -- public market convention.

Settlement periods 1-48 map to 00:00-00:30 through 23:30-00:00.
Period N covers the half-hour starting at (N-1)*30 minutes from midnight.

UK ToU structure (simplified Agile/smart-tariff convention):
  Peak    -- morning (07:00-11:00) + evening (16:00-20:00) on weekdays
             periods 15-22 and 33-40 on Mon-Fri
  Off-peak -- everything else (nights, weekends, shoulder hours)

This is a public UK energy market convention (Elexon settlement periods).
Not a SIM internal -- any UK supplier knows their own ToU period definitions.
"""
import datetime

_MORNING_PEAK = range(15, 23)
_EVENING_PEAK = range(33, 41)


def is_peak_period(date_str: str, period: int) -> bool:
    """Return True if this settlement period falls in a peak ToU window.

    Peak is morning (07:00-11:00) or evening (16:00-20:00) on weekdays.
    """
    dt = datetime.date.fromisoformat(date_str)
    if dt.weekday() >= 5:
        return False
    return period in _MORNING_PEAK or period in _EVENING_PEAK


def period_start_time(period: int) -> datetime.time:
    total_minutes = (period - 1) * 30
    return datetime.time(total_minutes // 60, total_minutes % 60)
