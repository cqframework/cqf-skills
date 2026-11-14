library USQualityCoreCommonTests version '0.5.0'

using USQualityCore version '0.5.0'
using USCore version '6.1.0-derived'
using FHIR version '4.0.1'

include FHIRHelpers version '4.0.1'
include USQualityCoreCommon

codesystem "Marital Status Codes": 'http://terminology.hl7.org/CodeSystem/v3-MaritalStatus'
codesystem "CDC Race and Ethnicity Codes": 'urn:oid:2.16.840.1.113883.6.238'
codesystem "CommunicationCategoryCodeSystem": 'http://terminology.hl7.org/CodeSystem/communication-category'
codesystem "SNOMED-CT": 'http://snomed.info/sct'
codesystem "CVX": 'http://hl7.org/fhir/sid/cvx'
codesystem "LOINC": 'http://loinc.org'
codesystem "TaskCodeSystem": 'http://hl7.org/fhir/CodeSystem/task-code'

valueset "Marital Status": 'http://hl7.org/fhir/ValueSet/marital-status'
valueset "CommunicationCodes": 'http://hl7.org/fhir/ValueSet/communication-category'
valueset "DeviceCodes": 'http://example.org/fhir/ValueSet/device-codes' // Random set of device codes from 'http://hl7.org/fhir/ValueSet/device-type'
valueset "ImmunizationCodes": 'http://example.org/fhir/ValueSet/immunization-codes' // Random set of immunization codes from 'http://hl7.org/fhir/us/core/ValueSet/us-core-vaccines-cvx'
valueset "MedicationCodes": 'http://example.org/fhir/ValueSet/medication-codes' // Random set of medication codes from 'http://hl7.org/fhir/ValueSet/medication-codes'
valueset "ObservationCodes": 'http://example.org/fhir/ValueSet/observation-codes' // Random set of observation codes from 'http://hl7.org/fhir/ValueSet/observation-codes'
valueset "ProcedureCodes": 'http://example.org/fhir/ValueSet/procedure-codes' // Random set of procedure codes from 'http://hl7.org/fhir/us/core/ValueSet/us-core-procedure-code'
valueset "TaskCodes": 'http://hl7.org/fhir/ValueSet/task-code'
valueset "NegationReasonCodes": 'http://fhir.org/guides/onc/us-quality-core/ValueSet/us-quality-core-negation-reason'

code "Marital Status - Married": 'M' from "Marital Status Codes"
code "American Indian or Alaska Native": '1002-5' from "CDC Race and Ethnicity Codes"
code "Alaska Native": '1735-0' from "CDC Race and Ethnicity Codes"
code "CommunicationCode": 'alert' from "CommunicationCategoryCodeSystem" display 'Alert'
code "DeviceCode": '156009' from "SNOMED-CT" display 'Spine board'
code "ImmunizationCode": '01' from "CVX" display 'diphtheria, tetanus toxoids and pertussis vaccine'
code "MedicationCode": '26100' from "SNOMED-CT" display 'Codeine phosphate'
code "ObservationCode": '1-8' from "LOINC" display 'Acyclovir [Susceptibility]'
code "ProcedureCode": '7138802' from "SNOMED-CT" display 'Procedure'
code "TaskCode": 'approve' from "TaskCodeSystem" display 'Activate/approve the focal resource'

context Patient

define TestAdverseEvent: ["AdverseEvent"]
define TestAllergyIntolerance: ["AllergyIntolerance"]
define TestBodyStructure: ["BodyStructure"]
define TestCarePlan: ["CarePlan"]
define TestCareTeam: ["CareTeam"]
define TestClaim: ["Claim"]
define TestClaimResponse: ["ClaimResponse"]
define TestCommunication: ["Communication"]
define TestCommunicationNotDone: ["CommunicationNotDone"]
define TestCommunicationRequest: ["CommunicationRequest"]
define TestConditionEncounterDiagnosis: ["ConditionEncounterDiagnosis"]
define TestConditionProblemsHealthConcerns: ["ConditionProblemsHealthConcerns"]
define TestCoverage: ["Coverage"]
define TestDevice: ["Device"]
define TestDeviceNotRequested: ["DeviceNotRequested"]
define TestDeviceRequest: ["DeviceRequest"]
define TestDeviceUseStatement: ["DeviceUseStatement"]
define TestDiagnosticReportLab: ["DiagnosticReportLab"]
define TestDiagnosticReportNote: ["DiagnosticReportNote"]
define TestEncounter: ["Encounter"]
define TestFamilyMemberHistory: ["FamilyMemberHistory"]
define TestFlag: ["Flag"]
define TestGoal: ["Goal"]
define TestImagingStudy: ["ImagingStudy"]
define TestImmunization: ["Immunization"]
define TestImmunizationEvaluation: ["ImmunizationEvaluation"]
define TestImmunizationNotDone: ["ImmunizationNotDone"]
define TestImmunizationRecommendation: ["ImmunizationRecommendation"]
define TestLaboratoryResultObservation: ["LaboratoryResultObservation"]
define TestLocation: ["Location"]
define TestMedication: ["Medication"]
define TestMedicationAdministration: ["MedicationAdministration"]
define TestMedicationAdministrationNotDone: ["MedicationAdministrationNotDone"]
define TestMedicationDispense: ["MedicationDispense"]
define TestMedicationDispenseDeclined: ["MedicationDispenseDeclined"]
define TestMedicationNotRequested: ["MedicationNotRequested"]
define TestMedicationRequest: ["MedicationRequest"]
define TestMedicationStatement: ["MedicationStatement"]
define TestObservation: ["SimpleObservation"]
define TestObservationCancelled: ["ObservationCancelled"]
define TestObservationClinicalTestResult: ["ObservationClinicalResult"]
define TestObservationImagingResult: ["NonPatientObservation"]
define TestObservationSurvey: ["ObservationScreeningAssessment"]
define TestOrganization: ["Organization"]
define TestPatient: ["Patient"]
define TestVitalsPanel: [USCore.VitalSignsProfile]
define TestRespRate: [USCore.RespiratoryRateProfile]
define TestHeartRate: [USCore.HeartRateProfile]
define TestBodyTemp: [USCore.BodyTemperatureProfile]
define TestBodyHeight: [USCore.BodyHeightProfile]
define TestHeadCircum: [USCore.HeadCircumferenceProfile]
define TestBodyWeight: [USCore.BodyWeightProfile]
define TestBMI: [USCore.BMIProfile]
define TestBP: [USCore.BloodPressureProfile]
define TestPractitioner: ["Practitioner"]
define TestPractitionerRole: ["PractitionerRole"]
define TestProcedure: ["Procedure"]
define TestProcedureNotDone: ["ProcedureNotDone"]
define TestRelatedPerson: ["RelatedPerson"]
define TestServiceNotRequested: ["ServiceNotRequested"]
define TestServiceRequest: ["ServiceRequest"]
define TestSpecimen: ["Specimen"]
define TestSubstance: ["Substance"]
define TestTask: ["Task"]
define TestTaskRejected: ["TaskRejected"]
define TestUSCoreImplantableDevice: [USCore.ImplantableDeviceProfile]
define TestUSCoreSmokingStatus: [USCore.SmokingStatusProfile]
define TestUSCorePulseOximetry: [USCore.PulseOximetryProfile]
define TestUSCorePediatricBMIForAge: [USCore.PediatricBMIforAgeObservationProfile]
define TestUSCorePediatricWeightForHeight: [USCore.PediatricWeightForHeightObservationProfile]
define TestUSCorePediatricHeadOccipitalFrontalCircumferencePercentileProfile: [USCore.PediatricHeadOccipitalFrontalCircumferencePercentileProfile]
//define TestUSCoreObservationSDOHAssessment: [USCore.ObservationSDOHAssessment]
//define TestUSCoreObservationSocialHistoryProfile: [USCore.ObservationSocialHistoryProfile]
define TestUSCoreObservationSexualOrientationProfile: [USCore.ObservationSexualOrientationProfile]

// Validate Encounter.diagnosis cardinality
define TestEncounterDiagnosisCardinality:
  exists (First([Encounter]).diagnosis)

// Validate ProcedureNotDone elements
define TestProcedureNotDoneElements:
  [ProcedureNotDone] P
    where P.recorded() on or before day of Today()
      and exists (P.identifier)
      and P.status = 'not-done'
      and P.statusReason is not null
      and P.category is not null
      and P.code is not null
      and P.performed is null

// Validate NotDone...

// CommunicationNotDone
define TestSpecificCommunicationNotDone:
  ["CommunicationNotDone": CommunicationCode]

// TODO: Support this case, need to introduce a terminology contains operator
// This operator is introduced in CQL R2
//define TestSpecificCommunicationNotDoneActual:
//    ["CommunicationNotDone": topic ~ CommunicationCode]
//      union ["CommunicationNotDone": topic ~contains CommunicationCode]

define TestSpecificCommunicationNotDoneExplicit:
  ["CommunicationNotDone"] C
    where C.topic() ~ CommunicationCode
      or CommunicationCode in C.topic()

define TestGeneralCommunicationNotDone:
  ["CommunicationNotDone": CommunicationCodes]

// NOTE: This warning should not be happening, logged a translator issue to investigate: https://github.com/cqframework/clinical_quality_language/issues/1714
define TestGeneralCommunicationNotDoneActual:
  ["CommunicationNotDone": topic in CommunicationCodes]
    union ["CommunicationNotDone": topic ~ CommunicationCodes]

define TestGeneralCommunicationNotDoneExplicit:
  ["CommunicationNotDone"] C
    where C.topic() in CommunicationCodes
      or C.topic() ~ CommunicationCodes

// DeviceNotRequested
define TestSpecificDeviceNotRequested:
  ["DeviceNotRequested": DeviceCode]

// TODO: Support this use case
//define TestSpecificDeviceNotRequestedActual:
//    ["DeviceNotRequested": code ~ DeviceCode]
//      union ["DeviceNotRequested": code ~contains DeviceCode]

define TestSpecificDeviceNotRequestedExplicit:
  [DeviceNotRequested] D
    where D.code() ~ DeviceCode
      or DeviceCode in D.code()

define TestGeneralDeviceNotRequested:
  ["DeviceNotRequested": DeviceCodes]

// NOTE: This warning should not be happening, logged a translator issue to investigate: https://github.com/cqframework/clinical_quality_language/issues/1714
define TestGeneralDeviceNotRequestedActual:
  ["DeviceNotRequested": code in DeviceCodes]
    union ["DeviceNotRequested": code ~ DeviceCodes]

define TestGeneralDeviceNotRequestedExplicit:
  ["DeviceNotRequested"] D
    where D.code() in DeviceCodes
      or D.code() ~ DeviceCodes

define TestGeneralDeviceNotRequestedCodeExplicit:
  ["DeviceNotRequested"] D
    where D.code() in DeviceCodes

define TestGeneralDeviceNotRequestedValueSetExplicit:
  ["DeviceNotRequested"] D
    where D.code() ~ DeviceCodes

// ImmunizationNotDone
define TestSpecificImmunizationNotDone:
  ["ImmunizationNotDone": ImmunizationCode]

// TODO: Support this use case
//define TestSpecificImmunizationNotDoneActual:
//    ["ImmunizationNotDone": vaccineCode ~ ImmunizationCode]
//      union ["ImmunizationNotDone": vaccineCode ~contains ImmunizationCode]

define TestSpecificImmunizationNotDoneExplicit:
  ["ImmunizationNotDone"] I
    where I.vaccineCode() ~ ImmunizationCode
      or ImmunizationCode in I.vaccineCode()

define TestGeneralImmunizationNotDone:
  ["ImmunizationNotDone": ImmunizationCodes]

// NOTE: This warning should not be happening, logged a translator issue to investigate: https://github.com/cqframework/clinical_quality_language/issues/1714
define TestGeneralImmunizationNotDoneActual:
  ["ImmunizationNotDone": vaccineCode in ImmunizationCodes]
    union ["ImmunizationNotDone": vaccineCode ~ ImmunizationCodes]

define TestGeneralImmunizationNotDoneExplicit:
  ["ImmunizationNotDone"] I
    where I.vaccineCode() in ImmunizationCodes
      or I.vaccineCode() ~ ImmunizationCodes

// MedicationAdministrationNotDone
define TestSpecificMedicationAdministrationNotDone:
  ["MedicationAdministrationNotDone": MedicationCode]

// TODO: Support this use case
//define TestSpecificMedicationAdministrationNotDoneActual:
//    ["MedicationAdministrationNotDone": medication ~ MedicationCode]
//      union ["MedicationAdministrationNotDone": medication ~contains MedicationCode]

define TestSpecificMedicationAdministrationNotDoneExplicit:
  ["MedicationAdministrationNotDone"] I
    where I.medication() ~ MedicationCode
      or MedicationCode in I.medication()

define TestGeneralMedicationAdministrationNotDone:
  ["MedicationAdministrationNotDone": MedicationCodes]

// NOTE: This warning should not be happening, logged a translator issue to investigate: https://github.com/cqframework/clinical_quality_language/issues/1714
define TestGeneralMedicationAdministrationNotDoneActual:
  ["MedicationAdministrationNotDone": medication in MedicationCodes]
    union ["MedicationAdministrationNotDone": medication ~ MedicationCodes]

define TestGeneralMedicationAdministrationNotDoneExplicit:
  ["MedicationAdministrationNotDone"] I
    where I.medication() in MedicationCodes
      or I.medication() ~ MedicationCodes

// MedicationDispenseDeclined
define TestSpecificMedicationDispenseDeclined:
  ["MedicationDispenseDeclined": MedicationCode]

// TODO: Support this use case
//define TestSpecificMedicationDispenseDeclinedActual:
//    ["MedicationDispenseDeclined": medication ~ MedicationCode]
//      union ["MedicationDispenseDeclined": medication ~contains MedicationCode]

define TestSpecificMedicationDispenseDeclinedExplicit:
  ["MedicationDispenseDeclined"] I
    where I.medication() ~ MedicationCode
      or MedicationCode in I.medication()

define TestGeneralMedicationDispenseDeclined:
  ["MedicationDispenseDeclined": MedicationCodes]

// NOTE: This warning should not be happening, logged a translator issue to investigate: https://github.com/cqframework/clinical_quality_language/issues/1714
define TestGeneralMedicationDispenseDeclinedActual:
  ["MedicationDispenseDeclined": medication in MedicationCodes]
    union ["MedicationDispenseDeclined": medication ~ MedicationCodes]

define TestGeneralMedicationDispenseDeclinedExplicit:
  ["MedicationDispenseDeclined"] I
    where I.medication() in MedicationCodes
      or I.medication() ~ MedicationCodes

// MedicationNotRequested
define TestSpecificMedicationNotRequested:
  ["MedicationNotRequested": MedicationCode]

// TODO: Support this use case
//define TestSpecificMedicationNotRequestedActual:
//    ["MedicationNotRequested": medication ~ MedicationCode]
//      union ["MedicationNotRequested": medication ~contains MedicationCode]

define TestSpecificMedicationNotRequestedExplicit:
  ["MedicationNotRequested"] I
    where I.medication() ~ MedicationCode
      or MedicationCode in I.medication()

define TestGeneralMedicationNotRequested:
  ["MedicationNotRequested": MedicationCodes]

// NOTE: This warning should not be happening, logged a translator issue to investigate: https://github.com/cqframework/clinical_quality_language/issues/1714
define TestGeneralMedicationNotRequestedActual:
  ["MedicationNotRequested": medication in MedicationCodes]
    union ["MedicationNotRequested": medication ~ MedicationCodes]

define TestGeneralMedicationNotRequestedExplicit:
  ["MedicationNotRequested"] I
    where I.medication() in MedicationCodes
      or I.medication() ~ MedicationCodes

// ObservationCancelled
define TestSpecificObservationCancelled:
  ["ObservationCancelled": ObservationCode]

// TODO: Support this use case
//define TestSpecificObservationCancelledActual:
//    ["ObservationCancelled": code ~ ObservationCode]
//      union ["ObservationCancelled": code contains ObservationCode]

define TestSpecificObservationCancelledExplicit:
  ["ObservationCancelled"] I
    where I.code() ~ ObservationCode
      or ObservationCode in I.code()

define TestGeneralObservationCancelled:
  ["ObservationCancelled": ObservationCodes]

// NOTE: This warning should not be happening, logged a translator issue to investigate: https://github.com/cqframework/clinical_quality_language/issues/1714
define TestGeneralObservationCancelledActual:
  ["ObservationCancelled": code in ObservationCodes]
    union ["ObservationCancelled": code ~ ObservationCodes]

define TestGeneralObservationCancelledExplicit:
  ["ObservationCancelled"] I
    where I.code() in ObservationCodes
      or I.code() ~ ObservationCodes

// ProcedureNotDone
define TestSpecificProcedureNotDone:
  ["ProcedureNotDone": ProcedureCode]

// TODO: Support this use case
//define TestSpecificProcedureNotDoneActual:
//    ["ProcedureNotDone": code ~ ProcedureCode]
//      union ["ProcedureNotDone": code ~contains ProcedureCode]

define TestSpecificProcedureNotDoneExplicit:
  ["ProcedureNotDone"] I
    where I.code() ~ ProcedureCode
      or ProcedureCode in I.code()

define TestGeneralProcedureNotDone:
  ["ProcedureNotDone": ProcedureCodes]

// NOTE: This warning should not be happening, logged a translator issue to investigate: https://github.com/cqframework/clinical_quality_language/issues/1714
define TestGeneralProcedureNotDoneActual:
  ["ProcedureNotDone": code in ProcedureCodes]
    union ["ProcedureNotDone": code ~ ProcedureCodes]

define TestGeneralProcedureNotDoneExplicit:
  ["ProcedureNotDone"] I
    where I.code() in ProcedureCodes
      or I.code() ~ ProcedureCodes

// ServiceNotRequested
define TestSpecificServiceNotRequested:
  ["ServiceNotRequested": ProcedureCode]

// TODO: Support this use case
//define TestSpecificServiceNotRequestedActual:
//    ["ServiceNotRequested": code ~ ProcedureCode]
//      union ["ServiceNotRequested": code ~contains ProcedureCode]

define TestSpecificServiceNotRequestedExplicit:
  ["ServiceNotRequested"] I
    where I.code() ~ ProcedureCode
      or ProcedureCode in I.code()

define TestGeneralServiceNotRequested:
  ["ServiceNotRequested": ProcedureCodes]

// NOTE: This warning should not be happening, logged a translator issue to investigate: https://github.com/cqframework/clinical_quality_language/issues/1714
define TestGeneralServiceNotRequestedActual:
  ["ServiceNotRequested": code in ProcedureCodes]
    union ["ServiceNotRequested": code ~ ProcedureCodes]

define TestGeneralServiceNotRequestedExplicit:
  ["ServiceNotRequested"] I
    where I.code() in ProcedureCodes
      or I.code() ~ ProcedureCodes

// TaskRejected
define TestSpecificTaskRejected:
  ["TaskRejected": TaskCode]

// TODO: Support this use case
//define TestSpecificTaskRejectedActual:
//    ["TaskRejected": code ~ TaskCode]
//      union ["TaskRejected": code contains TaskCode]

define TestSpecificTaskNotDoneExplicit:
  ["TaskRejected"] I
    where I.code() ~ TaskCode
      or TaskCode in I.code()

define TestGeneralTaskRejected:
  ["TaskRejected": TaskCodes]

// NOTE: This warning should not be happening, logged a translator issue to investigate: https://github.com/cqframework/clinical_quality_language/issues/1714
define TestGeneralTaskRejectedActual:
  ["TaskRejected": code in TaskCodes]
    union ["TaskRejected": code ~ TaskCodes]

define TestGeneralTaskRejectedExplicit:
  ["TaskRejected"] I
    where I.code() in TaskCodes
      or I.code() ~ TaskCodes
