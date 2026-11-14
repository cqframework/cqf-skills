library DiabetesStatinCheck version '1.0.000'

using USQualityCore version '0.5.0'
using USCore version '6.1.0-derived'
using FHIR version '4.0.1'

include FHIRHelpers version '4.0.1' called FHIRHelpers
include FHIRCommon version '2.0.0' called FHIRCommon
include CQMConcepts version '0.5.000' called CQMConcepts

valueset "Office Visit": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1001'
valueset "Diabetes": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.103.12.1001'
valueset "Statin Therapy": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.117.1.1.1'

parameter "Measurement Period" Interval<DateTime>

context Patient

define "Qualifying Encounters":
  [Encounter: "Office Visit"] OfficeVisit
    where OfficeVisit.status = 'finished'
      and OfficeVisit.period during "Measurement Period"

define "Encounters With Diabetes":
  "Qualifying Encounters" QualifyingEncounter
    where exists (
        [USQualityCore.ConditionEncounterDiagnosis: "Diabetes"] DiabetesDiagnosis
          where DiabetesDiagnosis.encounter.references(QualifyingEncounter)
      )
      or exists (
        [USQualityCore.ConditionProblemsHealthConcerns: "Diabetes"] DiabetesProblem
          where DiabetesProblem.isActive()
      )

define "Has Statin Order":
  exists (
    [USQualityCore.MedicationRequest: "Statin Therapy"] StatinOrder
      where StatinOrder.authoredOn during "Measurement Period"
  )

define "Diabetic Patients Without Statin Order":
  exists "Encounters With Diabetes"
    and not "Has Statin Order"
