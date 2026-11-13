library testWaIntervalGuard

define "A": 1
define "B": 1
define "Guarded": if "A" < "B" then Interval["A", "B") else Interval["A", "B"]
define "AlsoFine": 2 + 2
