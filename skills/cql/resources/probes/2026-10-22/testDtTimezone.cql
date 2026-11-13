library testDtTimezone

define "EqualAcrossOffsets": @2012-03-10T10:20:00.999+07:00 = @2012-03-10T09:20:00.999+06:00
define "EqualDifferentInstants": @2012-03-10T10:20:00.999+07:00 = @2012-03-10T10:20:00.999+06:00
define "SameDayAcrossOffsets": @2026-01-15T23:30:00-05:00 same day as @2026-01-16T04:30:00Z
define "EqualSameInstantAcrossMidnight": @2026-01-15T23:30:00-05:00 = @2026-01-16T04:30:00Z
define "DayComponentAsWritten": day from @2026-01-15T23:30:00-05:00
define "DateEqDateTime": @2026-01-15 = @2026-01-15T10:00:00Z
define "DateSameDayDateTime": @2026-01-15 same day as @2026-01-15T10:00:00Z
define "DateLessNextDayDateTime": @2026-01-15 < @2026-01-16T00:00:00Z
define "NoOffsetVsZ": @2026-01-15T10:00:00 = @2026-01-15T10:00:00Z
define "NoOffsetVsLocal": @2026-01-15T10:00:00 = @2026-01-15T10:00:00-04:00
define "NoOffsetVsEST": @2026-01-15T10:00:00 = @2026-01-15T10:00:00-05:00
