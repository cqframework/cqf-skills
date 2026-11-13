library testDtMsWorkaround version '1.0.0'

define "Control EqualBothMs": @2024-11-15T12:30:00.0Z = @2024-11-15T12:30:00.0Z
define "Gotcha EqualMsVsNone": @2024-11-15T12:30:00.0Z = @2024-11-15T12:30:00Z
define "SameSecond MsVsNone": @2024-11-15T12:30:00.0Z same second as @2024-11-15T12:30:00Z
define "SameSecond HalfVsNone": @2024-11-15T12:30:00.5Z same second as @2024-11-15T12:30:00Z
define "SameMinute MsVsNone": @2024-11-15T12:30:00.0Z same minute as @2024-11-15T12:30:00Z
define "Equiv MsVsNone": @2024-11-15T12:30:00.0Z ~ @2024-11-15T12:30:00Z
define "DurationMs MsVsNone": duration in milliseconds between @2024-11-15T12:30:00.0Z and @2024-11-15T12:30:00Z
