library testDtPrecision

define "MonthEqDay": @2026-01 = @2026-01-15
define "YearLessDaySameYear": @2026 < @2026-02-15
define "YearLessDayEarlierYear": @2025 < @2026-02-15
define "SameMonthAs": @2026-01 same month as @2026-01-15
define "SameDayAsPartial": @2026-01 same day as @2026-01-15
define "AfterHourDateVsDateTime": @2026-01-15 after hour of @2026-01-14T10:00:00Z
define "DayInInterval": @2026-01-15 in Interval[@2026-01-01, @2026-01-31]
define "MonthInStraddlingInterval": @2026-01 in Interval[@2026-01-15, @2026-02-15]
define "MonthDuringYear": @2026-01 during Interval[@2026-01-01, @2026-12-31]
define "SecondsVsMillisEqual": @2024-11-15T12:30:00.0Z = @2024-11-15T12:30:00Z
define "MillisVsMinuteNull": @2024-11-15T12:30:00.5Z = @2024-11-15T12:30Z
define "SameDayFullControl": @2026-01-15 same day as @2026-01-15
