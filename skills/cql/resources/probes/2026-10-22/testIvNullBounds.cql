library testIvNullBounds

define "EndClosedNullInt": end of Interval[1, null]
define "EndOpenNullInt": end of Interval[1, null)
define "StartClosedNullInt": start of Interval[null, 5]
define "StartOpenNullInt": start of Interval(null, 5]
define "EndClosedNullDT": end of Interval[@2025-01-01T00:00:00, null]
define "EndOpenNullDT": end of Interval[@2025-01-01T00:00:00, null)
define "EndClosedDT": end of Interval[@2025-01-01T00:00:00, @2025-12-31T00:00:00]
define "HighOpenNullDT": Interval[@2025-01-01T00:00:00, null).high
define "HighClosedNullDT": Interval[@2025-01-01T00:00:00, null].high
