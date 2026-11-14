library HypertensionCheck version '1.0.0'

using USCore version '6.1.0-derived'
using FHIR version '4.0.1'

include FHIRHelpers version '4.0.1' called FHIRHelpers
include FHIRCommon version '2.0.0' called FC
include USCoreCommon version '2.0.0' called UC

valueset "Essential Hypertension": 'http://example.org/fhir/ValueSet/essential-hypertension'
valueset "Blood Pressure Codes": 'http://example.org/fhir/ValueSet/blood-pressure'

context Patient

define "Active Confirmed Hypertension Problems":
  ([ConditionProblemsHealthConcernsProfile: "Essential Hypertension"]).active()

define "Final Blood Pressure Readings":
  [BloodPressureProfile: "Blood Pressure Codes"] BP
    where BP.status = 'final'

define "Most Recent Systolic Blood Pressure Quantity":
  First("Final Blood Pressure Readings" BP sort by start of effective.toInterval() desc).systolic().value as Quantity

define "Patient Race Categories":
  Patient.race().ombCategory
