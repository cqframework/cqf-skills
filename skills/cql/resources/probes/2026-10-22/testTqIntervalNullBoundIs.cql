library testTqIntervalNullBoundIs version '1.0.0'

define "BothValues": Interval[1, 5] is Interval<Integer>
define "NullHighClosed": Interval[1, null] is Interval<Integer>
define "NullHighOpen": Interval[1, null) is Interval<Integer>
define "BothNullTyped": Interval[null as Integer, null as Integer] is Interval<Integer>
define "StartOpenBothNull": start of Interval(null as Integer, null as Integer)
define "EndOpenBothNull": end of Interval(null as Integer, null as Integer)
