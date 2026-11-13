library testHoDateDateTime version '1.0.0'

define "DateEqDate": @2026-01-15 = @2026-01-15
define "DateEqDateTimeMidnight": @2026-01-15 = @2026-01-15T00:00:00.000-04:00
define "DateSameDayDateTime": @2026-01-15 same day as @2026-01-15T10:00:00.000-04:00
define "DateTimeEqDateTime": @2026-01-15T00:00:00.000-04:00 = @2026-01-15T00:00:00.000-04:00
