/*
@author: Bryn Rhodes
@description: This library defines functions to expose extensions defined
in USCore as fluent functions in CQL, as well as common terminology and functions
used in writing CQL with FHIR and USCore profiles.
*/
library USCoreCommon version '2.0.0'

using FHIR version '4.0.1'
using USCore version '6.1.0-derived'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1'
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0'

codesystem "CVX": 'http://hl7.org/fhir/sid/cvx'
codesystem "ActCode": 'http://terminology.hl7.org/CodeSystem/v3-ActCode'
codesystem "USCoreConditionCategory": 'http://hl7.org/fhir/us/core/CodeSystem/condition-category'
codesystem "CDC Race and Ethnicity Codes": 'urn:oid:2.16.840.1.113883.6.238'
codesystem "CommunicationCategoryCodeSystem": 'http://terminology.hl7.org/CodeSystem/communication-category'
codesystem "IdentifierType": 'http://terminology.hl7.org/CodeSystem/v2-0203'
codesystem "ObservationInterpretation": 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'

codesystem "SNOMED": 'http://snomed.info/sct'

code "Female": '248152002' from SNOMED display 'Female'
code "Male": '248153007' from SNOMED display 'Male'
code "Unknown": '184115007' from SNOMED display 'Patient sex unknown'
code "Nonbinary": '33791000087105' from SNOMED display 'Identifies as gender nonbinary'

codesystem "DataAbsentReason": 'http://terminology.hl7.org/CodeSystem/data-absent-reason'

code "Asked-Declined": 'asked-declined' from DataAbsentReason display 'Asked But Declined'

code "MedicalRecordNumber": 'MR' from "IdentifierType" display 'Medical record number'

// Encounter Class Codes
code "ambulatory": 'AMB' from ActCode display 'ambulatory'
code "emergency": 'EMER' from ActCode display 'emergency'
code "field": 'FLD' from ActCode display 'field'
code "home health": 'HH' from ActCode display 'home health'
code "inpatient encounter": 'IMP' from ActCode display 'inpatient encounter'
code "inpatient acute": 'ACUTE' from ActCode display 'inpatient acute'
code "inpatient non-acute": 'NONAC' from ActCode display 'inpatient non-acute'
code "observation encounter": 'OBSENC' from ActCode display 'observation encounter'
code "pre-admission": 'PRENC' from ActCode display 'pre-admission'
code "short stay": 'SS' from ActCode display 'short stay'
code "virtual": 'VR' from ActCode display 'VR'

// Condition Category Codes
code "health-concern": 'health-concern' from "USCoreConditionCategory" display 'Health Concern'

code "Systolic Blood Pressure": '8480-6' from FHIRCommon.LOINC
code "Diastolic Blood Pressure": '8462-4' from FHIRCommon.LOINC
code "BMI": '39156-5' from FHIRCommon.LOINC
code "Positive": 'POS' from ObservationInterpretation
code "Negative": 'NEG' from ObservationInterpretation

// Prescription Transmission Method
codesystem "Rx Transmission Method": 'http://terminology.hl7.org/CodeSystem/PMIXTransmissionFormRxOriginCodeType'

code "Written Prescription": 'Written Prescription' from "Rx Transmission Method" display 'Written Prescription'
code "Electronic Prescription": 'Electronic Prescription' from "Rx Transmission Method" display 'Electronic Prescription'

context Patient

define fluent function race(patient FHIR.Patient):
  (patient.ext('http://hl7.org/fhir/us/core/StructureDefinition/us-core-race')) E
    return {
      ombCategory: (E.exts('ombCategory')) o return o.value as FHIR.Coding,
      detailed: (E.exts('detailed')) d return d.value as FHIR.Coding,
      text: E.ext('text').value as FHIR.string
    }

define fluent function ethnicity(patient FHIR.Patient):
  (patient.ext('http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity')) E
    return {
      ombCategory: E.ext('ombCategory').value as FHIR.Coding,
      detailed: (E.exts('detailed')) d return d.value as FHIR.Coding,
      text: E.ext('text').value as FHIR.string
    }

define fluent function tribalAffiliation(patient FHIR.Patient):
  (patient.ext('http://hl7.org/fhir/us/core/StructureDefinition/us-core-tribal-affiliation')) E
    return {
      tribalAffiliation: E.ext('tribalAffiliation').value as CodeableConcept,
      isEnrolled: E.ext('isEnrolled').value as boolean
    }

/*
@description: Returns the [birthSex](https://hl7.org/fhir/us/core/STU6.1/StructureDefinition-us-core-patient-definitions.html#diff_Patient.extension:birthsex) element as defined for the USCore patient profile
*/
define fluent function birthSex(patient FHIR.Patient):
  patient.ext('http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex').value as FHIR.code

/*
@deprecated
@description: Returns the [sex](https://hl7.org/fhir/us/core/STU6.1/StructureDefinition-us-core-patient-definitions.html#diff_Patient.extension:sex) element as defined for the USCore patient profile
@comment: NOTE: This element has been deprecated in future versions of US Core. The `.individualSex()` function should be used instead.
*/
define fluent function sex(patient FHIR.Patient):
  patient.ext('http://hl7.org/fhir/us/core/StructureDefinition/us-core-sex').value as FHIR.code

/*
@description: Returns the [sex](https://hl7.org/fhir/us/core/STU8.0.1/StructureDefinition-us-core-patient-definitions.html#key_Patient.extension:sex) element as defined for the USCore patient profile
@comment: The definition of this element has expanded over versions. For backwards-compatibility the original .sex() function as defined in STU6 is still available, but deprecated. This function is
forward-compatible, returning values as defined in the individualSex extension, even if they are defined in the instance using the deprecated sex extension.
*/
define fluent function individualSex(patient FHIR.Patient):
  patient P
    let 
      individualSex: P.ext('http://hl7.org/fhir/us/core/StructureDefinition/us-core-individual-sex').value as FHIR.Coding,
      sex: P.ext('http://hl7.org/fhir/us/core/StructureDefinition/us-core-sex').value as FHIR.code
    return {
      Coalesce(individualSex, sex.toIndividualSex())
    }

/*
@description: Maps the code value of a patient sex element to a Coding value (i.e. code with system) as expected in the individualSex element
*/
define fluent function toIndividualSex(sex FHIR.code):
  case sex.value
    when '248152002' then "Female"
    when '248153007' then "Male"
    when '184115007' then "Unknown"
    when '33791000087105' then "Nonbinary"
    when 'asked-declined' then "Asked-Declined"
    else null
  end

/*
@description: Returns all [sexParameterForClinicalUse](https://hl7.org/fhir/extensions/StructureDefinition-patient-sexParameterForClinicalUse.html) elements for the patient
*/
define fluent function sexParameterForClinicalUse(patient FHIR.Patient):
  (patient.exts('http://hl7.org/fhir/StructureDefinition/patient-sexParameterForClinicalUse')) E
    return {
      value: E.ext('value').value as FHIR.CodeableConcept,
      period: E.ext('period').value as FHIR.Period,
      comment: E.ext('comment').value as FHIR.string,
      supportingInfo: (E.exts('supportingInfo')) SI return SI.value as Choice<FHIR.CodeableConcept, FHIR.Reference>,
      intendedClinicalUse: (E.exts('intendedClinicalUse')) CU return CU.value as Choice<FHIR.CodeableConcept, FHIR.Reference>
    }

/*
@description: Returns all [sexParameterForClinicalUse](https://hl7.org/fhir/extensions/StructureDefinition-patient-sexParameterForClinicalUse.html) 
elements for the patient applicable as of the given date and time
@comment: Returns sexParameterForClinicalUse elements defined for the patient that either have no period specified, or have a period that includes 
the specified asOf. Elements are returned in descending chronological order by the start of the period element (so the most recent element is first).
*/
define fluent function sexParameterForClinicalUse(patient FHIR.Patient, asOf System.DateTime):
  (patient.sexParameterForClinicalUse()) SPCU
    where asOf is null or SPCU.period is null or asOf during SPCU.period
    sort by start of period desc


/*
@description: Returns the single systolic blood pressure component of the given blood pressure observation
@comment: This function will return `null` if there is no component with a code of `"Systolic Blood Pressure"`, and will throw an error 
if there are multiple components with that code.
*/
define fluent function systolic(bloodPressure FHIR.Observation):
  singleton from (
    bloodPressure.component C
      where C.code ~ "Systolic Blood Pressure"
  )

/*
@description: Returns the single diastolic blood pressure component of the given blood pressure observation
@comment: This function will return `null` if there is no component with a code of `"Diastolic Blood Pressure"`, and will throw an error
if there are multiple components with that code.
*/
define fluent function diastolic(bloodPressure FHIR.Observation):
  singleton from (
    bloodPressure.component C
      where C.code ~ "Diastolic Blood Pressure"
  )

/*
@description: Returns the assertedDate for a given allergy/intolerance, i.e. the date on which the existence of the allergy/intolerance was first asserted or acknowledged 
*/
define fluent function assertedDate(allergyIntolerance FHIR.AllergyIntolerance):
  allergyIntolerance.ext('http://hl7.org/fhir/StructureDefinition/condition-assertedDate').value as FHIR.dateTime

/*
@description: Returns true if the given condition is a health concern
*/
define fluent function isHealthConcern(condition FHIR.Condition):
  exists (
    condition.category C
      where C ~ "health-concern"
  )

/*
@description: Returns the assertedDate for a given condition, i.e. the date on which the existence of the condition was first asserted or acknowledged 
*/
define fluent function assertedDate(condition FHIR.Condition):
  condition.ext('http://hl7.org/fhir/StructureDefinition/condition-assertedDate').value as FHIR.dateTime

/*
@description: Returns Observations in the given list that have an interpretation of positive
*/
define fluent function positive(observations List<FHIR.Observation>):
  observations O
    where exists (O.interpretation I where I ~ "Positive")

/*
@description: Returns Observations in the given list that have an interpretation of negative
*/
define fluent function negative(observations List<FHIR.Observation>):
  observations O
    where exists (O.interpretation I where I ~ "Negative")

/*
@description: Returns Observations in the given list whose effective time is during the given Encounter, accurate to the minute
*/
define fluent function during(observations List<FHIR.Observation>, encounter FHIR.Encounter):
  observations O
    where O.effective.toInterval() during minute of encounter.period

/*
@description: Returns Observations sorted chronologically by their effective time
*/
define fluent function chronologically(observations List<FHIR.Observation>):
  observations O
    sort by start of effective.toInterval()

/*
@description: Returns Observations chronologically by their effective time, on or after the start of the effective time of the given Observation
*/
define fluent function chronologicallyAfter(observations List<FHIR.Observation>, observation FHIR.Observation):
  observations O
    where O.effective.toInterval() starts on or after start of observation.effective.toInterval()
    sort by start of effective.toInterval()

/*
@description: Returns true if the given diagnostic report has a status of final, appended, amended, or corrected; false otherwise
*/
define fluent function isComplete(diagnosticReport FHIR.DiagnosticReport):
  diagnosticReport.status in { 'final', 'appended', 'amended', 'corrected' }

/*
@description: Returns diagnostic reports that have a status of final, appended, amended, or corrected
*/
define fluent function complete(diagnosticReports List<FHIR.DiagnosticReport>):
  diagnosticReports dr
    where dr.isComplete()

/*
@description: Returns the [transmissionMethod](http://hl7.org/fhir/us/pdmp/StructureDefinition/pdmp-extension-rx-transmission-method) element for the given MedicationDispense 
*/
define fluent function transmissionMethod(medicationDispense FHIR.MedicationDispense):
  medicationDispense.ext('http://hl7.org/fhir/us/pdmp/StructureDefinition/pdmp-extension-rx-transmission-method').value as FHIR.Coding
