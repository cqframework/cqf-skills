library DiabetesScreening version '1.0.0'

using FHIR version '4.0.1'

include FHIRHelpers version '4.0.1' called FHIRHelpers

codesystem "LOINC": 'http://loinc.org'

valueset "Diabetes": 'http://example.org/fhir/ValueSet/diabetes'

code "HbA1c": '4548-4' from "LOINC" display 'Hemoglobin A1c'

parameter "Measurement Period" Interval<DateTime>

context Patient

define "Has Diabetes":
  exists [Condition: "Diabetes"]

define "HbA1c Results":
  [Observation: "HbA1c"] O
    where O.status = 'final'
