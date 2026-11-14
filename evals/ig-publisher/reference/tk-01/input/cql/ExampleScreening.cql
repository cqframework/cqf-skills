library ExampleScreening version '0.1.0'

using FHIR version '4.0.1'

include FHIRHelpers version '4.0.1' called FHIRHelpers

codesystem "LOINC": 'http://loinc.org'

code "Body weight": '29463-7' from "LOINC" display 'Body weight'

parameter "Measurement Period" Interval<DateTime>

context Patient

define "Initial Population":
  AgeInYearsAt(date from start of "Measurement Period") >= 18

define "Denominator":
  "Initial Population"

define "Weight Observations":
  [Observation: "Body weight"] O
    where O.status in { 'final', 'amended', 'corrected' }
      and (O.effective as FHIR.dateTime) during "Measurement Period"

define "Numerator":
  exists "Weight Observations"
