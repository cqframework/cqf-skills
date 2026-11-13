library testIvNullOps

define "PointInClosedNull": @2026-06-01 during Interval[@2025-01-01, null]
define "PointInOpenNull": @2026-06-01 during Interval[@2025-01-01, null)
define "PointInClosed": @2026-06-01 during Interval[@2025-01-01, @2026-12-31]
define "IvDuringClosedNull": Interval[@2026-02-01, @2026-03-01] during Interval[@2025-01-01, null]
define "IvDuringOpenNull": Interval[@2026-02-01, @2026-03-01] during Interval[@2025-01-01, null)
define "OverlapsClosedNull": Interval[@2026-02-01, @2026-03-01] overlaps Interval[@2025-01-01, null]
define "OverlapsOpenNull": Interval[@2026-02-01, @2026-03-01] overlaps Interval[@2025-01-01, null)
define "OverlapsOpenNullBefore": Interval[@2024-02-01, @2024-03-01] overlaps Interval[@2025-01-01, null)
define "EndsAfterClosedNull": end of Interval[@2025-01-01, null] after @2026-12-31
define "EndsAfterOpenNull": end of Interval[@2025-01-01, null) after @2026-12-31
