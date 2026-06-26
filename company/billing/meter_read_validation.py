"""Customer meter read validation: drift detection, reversal, transposition."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ReadSource(str, Enum):
    CUSTOMER = 'customer'
    ESTIMATED = 'estimated'
    SMART_METER = 'smart_meter'
    ENGINEER_VISIT = 'engineer_visit'


class ValidationResult(str, Enum):
    ACCEPTED = 'accepted'
    QUERIED = 'queried'
    REJECTED = 'rejected'


class ValidationFlag(str, Enum):
    REVERSAL = 'reversal'
    EXCESSIVE_DAILY_RATE = 'excessive_daily_rate'
    LOW_DAILY_RATE = 'low_daily_rate'
    TRANSPOSITION_LIKELY = 'transposition_likely'
    METER_ADVANCE_ZERO = 'meter_advance_zero'
    OUTLIER = 'outlier'


@dataclass(frozen=True)
class MeterReadValidation:
    read_date: dt.date
    read_value: float
    previous_read: float
    previous_read_date: dt.date
    expected_daily_kwh: float
    source: ReadSource

    @property
    def days_elapsed(self) -> int:
        return max(1, (self.read_date - self.previous_read_date).days)

    @property
    def advance_kwh(self) -> float:
        return round(self.read_value - self.previous_read, 2)

    @property
    def implied_daily_kwh(self) -> float:
        return round(self.advance_kwh / self.days_elapsed, 2)

    @property
    def flags(self) -> List[ValidationFlag]:
        found = []
        if self.advance_kwh < 0:
            found.append(ValidationFlag.REVERSAL)
        if self.advance_kwh == 0 and self.days_elapsed > 7:
            found.append(ValidationFlag.METER_ADVANCE_ZERO)
        if self.implied_daily_kwh > self.expected_daily_kwh * 3.0:
            found.append(ValidationFlag.EXCESSIVE_DAILY_RATE)
        elif self.implied_daily_kwh < self.expected_daily_kwh * 0.2 and self.advance_kwh >= 0:
            found.append(ValidationFlag.LOW_DAILY_RATE)
        transposed = self._check_transposition()
        if transposed:
            found.append(ValidationFlag.TRANSPOSITION_LIKELY)
        return found

    def _check_transposition(self) -> bool:
        digits = str(int(self.read_value))
        if len(digits) < 2:
            return False
        transposed_val = float(digits[-1] + digits[:-1])
        transposed_advance = transposed_val - self.previous_read
        if transposed_advance < 0:
            return False
        transposed_daily = transposed_advance / self.days_elapsed
        implied = self.implied_daily_kwh
        if implied == 0:
            return False
        return (abs(transposed_daily - self.expected_daily_kwh) <
                abs(implied - self.expected_daily_kwh))

    @property
    def result(self) -> ValidationResult:
        fs = self.flags
        if ValidationFlag.REVERSAL in fs or ValidationFlag.EXCESSIVE_DAILY_RATE in fs:
            return ValidationResult.REJECTED
        if fs:
            return ValidationResult.QUERIED
        return ValidationResult.ACCEPTED

    def summary(self) -> dict:
        return {
            'read_date': self.read_date.isoformat(),
            'read_value': self.read_value,
            'advance_kwh': self.advance_kwh,
            'implied_daily_kwh': self.implied_daily_kwh,
            'expected_daily_kwh': self.expected_daily_kwh,
            'result': self.result.value,
            'flags': [f.value for f in self.flags],
        }
