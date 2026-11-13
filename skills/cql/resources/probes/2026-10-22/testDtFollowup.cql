library testDtFollowup

define "DayLeMonth": @2026-01-01 <= @2026-01
define "MonthGeDay": @2026-01 >= @2026-01-01
define "MonthLeDayEnd": @2026-01 <= @2026-12-31
define "SpecAfterHourExample": Date(2014, 7, 15) after hour of DateTime(2014, 7, 11, 14, 0, 0)
define "SpecMsTrueExample": @2024-11-15T12:30:00.0 = @2024-11-15T12:30:00
define "SpecMsFalseExample": @2024-11-15T12:30:00.5 = @2024-11-15T12:30:00
define "SpecMsNullExample": @2024-11-15T12:30:00.5 = @2024-11-14T12:30
define "OffsetAfterAddMonth": timezoneoffset from (@2026-01-31T10:00:00-05:00 + 1 month)
define "DateLessNextDayLocal": @2026-01-15 < @2026-01-16T00:00:00-04:00
define "DateLessNextDayZ": @2026-01-15 < @2026-01-16T00:00:00Z
