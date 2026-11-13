library testTqWaIntervalLow version '1.0.0'

define "Gotcha WholeInterval": Interval[1, null] is Interval<Integer>
define "LowBound": Interval[1, null].low is Integer
define "LowBoundOpenHigh": Interval[1, null).low is Integer
