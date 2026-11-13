library testIvStartsInQuery

define "Events": { Interval[@2026-01-01, @2026-01-10] }
define "Anchors": { Interval[@2026-01-03, @2026-01-05] }
define "WithStart":
  "Events" E
    with "Anchors" A
      such that E start 3 days or less before start of A
