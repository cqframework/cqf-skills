library testMdWindowOrig version '1.0.0'

using FHIR version '4.0.1'

define "Window": Interval[start of Encounter.period, end of Encounter.period + 7 days]
