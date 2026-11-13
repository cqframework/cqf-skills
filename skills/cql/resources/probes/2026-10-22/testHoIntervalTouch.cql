library testHoIntervalTouch version '1.0.0'

define "OverlapsClosed": Interval[1, 5] overlaps Interval[5, 10]
define "OverlapsHalfOpen": Interval[1, 5) overlaps Interval[5, 10]
define "MeetsHalfOpen": Interval[1, 5) meets Interval[5, 10]
define "MeetsClosed": Interval[1, 5] meets Interval[5, 10]
define "MeetsClosedAdjacent": Interval[1, 4] meets Interval[5, 10]
