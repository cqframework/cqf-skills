library testTqClosedNullEnd version '1.0.0'

define "EndClosedNull": end of Interval[@2025-12-31T00:00:00Z, null]
define "OverlapsClosedNull": Interval[@2025-12-31T00:00:00Z, null] overlaps Interval[@2026-01-01T00:00:00Z, @2026-12-31T00:00:00Z]
define "DuringClosedNull": Interval[@2026-03-01T00:00:00Z, null] during Interval[@2026-01-01T00:00:00Z, @2026-12-31T00:00:00Z]
define "DuringClosedValue": Interval[@2026-03-01T00:00:00Z, @2026-04-01T00:00:00Z] during Interval[@2026-01-01T00:00:00Z, @2026-12-31T00:00:00Z]
define "DuringOpenNull": Interval[@2026-03-01T00:00:00Z, null) during Interval[@2026-01-01T00:00:00Z, @2026-12-31T00:00:00Z]
