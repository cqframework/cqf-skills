library HypertensionCheck version '1.0.0'

using USCore version '6.1.0-derived'
using FHIR version '4.0.1'

include FHIRHelpers version '4.0.1' called FHIRHelpers
include FHIRCommon version '2.0.0' called FC
include USCoreCommon version '2.0.0' called UC

valueset "Essential Hypertension": 'http://example.org/fhir/ValueSet/essential-hypertension'

context Patient

define "Active Confirmed Hypertension Problems":
  ([ConditionProblemsHealthConcernsProfile: "Essential Hypertension"]).active().confirmed()

define "Final Blood Pressure Readings":
  [BloodPressureProfile] BP
    where BP.status = 'final'

define "Most Recent Blood Pressure Reading":
  Last("Final Blood Pressure Readings" BP sort by start of effective.toInterval())

define "Most Recent Systolic Blood Pressure Quantity":
  "Most Recent Blood Pressure Reading".systolic().value as Quantity

define "Patient Race Categories":
  Patient.race().ombCategory
