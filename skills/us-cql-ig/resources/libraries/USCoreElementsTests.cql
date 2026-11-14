library USCoreElementsTests version '2.0.0'

using FHIR version '4.0.1'
using USCore version '6.1.0-derived'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1'
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0'
include USCoreCommon version '2.0.0' called UC
include USCoreElements version '2.0.0' called UCE

context Patient

// NOTE: Many of these expressions are tested as part of the libraries for the example questionnaires
// This test suite is intended to eventually provide exhaustive coverage, contributions are welcome.

// Patient Patterns

// _01_01_ define fluent function ageInDaysAt(patient Patient, asOf Date):
// _01_02_ define fluent function ageInDays(patient Patient):
// _01_03_ define fluent function ageInMonthsAt(patient Patient, asOf Date):
// _01_04_ define fluent function ageInMonths(patient Patient):
// _01_05_ define fluent function ageInYearsAt(patient Patient, asOf Date):
// _01_06_ define fluent function ageInYears(patient Patient):
// _01_07_ define fluent function name(patient Patient):
// _01_08_ define fluent function usualName(patient Patient):
// _01_09_ define fluent function officialName(patient Patient):
// _01_10_ define fluent function firstNonOfficialNonUsualName(patient Patient):
// _01_11_ define fluent function memberID(coverage FHIR.Coverage):
// _01_12_ define fluent function policyNumber(coverage FHIR.Coverage):
// _01_13_ define fluent function medicalRecordNumber(patient Patient):
// _01_14_ define fluent function name(practitioner Practitioner):
// _01_15_ define fluent function usualName(practitioner Practitioner):
// _01_16_ define fluent function officialName(practitioner Practitioner):
// _01_17_ define fluent function firstNonOfficialNonUsualName(practitioner Practitioner):
// _01_18_ define fluent function name(practitioner Practitioner):
// _01_19_ define fluent function firstName(name HumanName):
// _01_20_ define fluent function middleNames(name HumanName):
// _01_21_ define fluent function lastName(name HumanName):
// _01_22_ define fluent function firstMiddleLast(name HumanName):
// _01_23_ define fluent function lastFirstMiddle(name HumanName):

// Allergy/Intolerance
// _02_01_ define "All Allergies and Intolerances":
// _02_02_ define "Active Confirmed Allergies and Intolerances":
// _02_03_ define "Common Allergies and Intolerances":
// _02_04_ define "Active Confirmed Common Allergies and Intolerances":
// _02_05_ define "No Known Allergies (Not Asked)":
// _02_06_ define "No Known Allergies (Confirmed)":

// Condition
// _03_01_ define "All Conditions":
// _03_02_ define "All Problem List Items":
// _03_03_ define "Active Confirmed Problem List Items":
// _03_04_ define "All Encounter Diagnoses":
// _03_05_ define "All Health Concerns":

// Laboratory Diagnostic Report
// _04_01_ define "All Diagnostic Reports for Laboratory Results":

// Diagnostic Report
// _05_01_ define "All Diagnostic Report Notes":

// Encounter
// _06_01_ define "All Encounters":
// _06_02_ define "All Performed Encounters":

// Immunization
// _07_01_ define "All Immunizations":
// _07_02_ define "All Completed Immunizations":

// Implantable Device
// _08_01_ define "All Implantable Devices":

// Laboratory Result
// _09_01_ define "All Laboratory Results":
// _09_02_ define "Resulted Laboratory Results":

// Medication Request
// _10_01_ define "Most Recent Medication Request":
// _10_02_ define "All Medication Requests":
// _10_03_ define "Active Medication Orders":
// _10_04_ define "All Medications":
define _10_04_TestAllMedications:
  UCE."All Medications"

// Pediatric BMI for Age
// _11_01_ define "Pediatric BMI for Age":
// _11_02_ define "Pediatric BMI for Age All Statuses":

// Pediatric Head Circumference Percentile
// _12_01_ define "Pediatric Head Circumference Percentile":

// Pediatric Weight for Height
// _13_01_ define "Pediatric Weight for Height":
// _13_02_ define "Pediatric Weight for Height All Statuses":

// Procedure
// _14_01_ define "All Procedures":
// _14_02_ define "All Performed Procedures":

// Pulse Oximetry
// _15_01_ define "Pulse Oximetry":
// _15_02_ define "Pulse Oximetry All Statuses":

// Smoking Status
// _16_01_ define "Smoking Status":
// _16_02_ define "Smoking Status All Statuses":
// _16_03_ define "Most Recent Smoking Status":

// Vital Signs
// _17_01_ define "All Vital Signs":
// _17_02_ define "All Vital Signs All Statuses":

// Respiratory Rate
// _18_01_ define "All Respiratory Rate Measurements":
// _18_02_ define "All Respiratory Rate Measurements All Statuses":

// Heart Rate
// _19_01_ define "All Heart Rate Measurements":
// _19_02_ define "All Heart Rate Measurements All Statuses":

// Body Temperature
// _20_01_ define "All Body Temperature Measurements":
// _20_02_ define "All Body Temperature Measurements All Statuses":

// Body Height
// _21_01_ define "All Body Height Measurements":
// _21_02_ define "All Body Height Measurements All Statuses":

// Head Circumference
// _22_01_ define "All Head Circumference Measurements":
// _22_02_ define "All Head Circumference Measurements All Statuses":

// Body Weight
// _23_01_ define "All Body Weight Measurements":
// _23_02_ define "All Body Weight Measurements All Statuses":

// Body Mass Index
// _24_01_ define "All Body Mass Index Measurements":
// _24_02_ define "All Body Mass Index Measurements All Statuses":

// Blood Pressure
// _25_01_ define "All Blood Pressure Measurements":
// _25_02_ define "All Blood Pressure Measurements All Statuses":

// Systolic Blood Pressure
// _26_01_ define "Systolic Blood Pressure":
  
// Diastolic Blood Pressure
// _27_01_ define "Diastolic Blood Pressure":

// Body Surface Area
// _28_01_ define "Most Recent BSA":
// _28_02_ define function CalculateBSA(alg System.String, height System.Quantity, weight System.Quantity):

// ServiceRequest
// _29_01_ define "All ServiceRequests":
// _29_02_ define function MostRecentSR(serviceRequests List<"FHIR.ServiceRequest">):
// _29_03_ define fluent function mostRecentSR(serviceRequests List<"FHIR.ServiceRequest">):
// _29_04_ define function RequestingProvider(serviceRequest FHIR.ServiceRequest):
// _29_05_ define function ServicingProvider(serviceRequest FHIR.ServiceRequest):
// _29_06_ define function BillingProvider(coverage FHIR.Coverage):
// _29_07_ define function RelatedCondition(serviceRequest FHIR.ServiceRequest):
// _29_08_ define "Research Subject":
// _29_09_ define "All Clinical Trials":
// _29_10_ define "Clinical Trial Organization":
// _29_11_ define function "GetServiceRequestReasonCondition"(serviceRequest ServiceRequest):
// _29_12_ define function Requester(medicationRequest MedicationRequestProfile):
// _29_13_ define function RequesterRole(medicationRequest MedicationRequestProfile):

// ============================================================================
// Refined unit test demonstration (proposal: unit-testing.html)
// The expressions below are exercised by the refined-* test cases under
// input/tests/library/USCoreElementsTests. Those cases use the proposed
// assertion model (operator / expected / tolerance / negated) together with a
// pinned evaluationDateTime so that relative-timing and floating-point results
// are reproducible regardless of when the suite is run.
// ============================================================================

// Relative timing -- resolves against the evaluationDateTime pinned by the
// test context (Now()/Today()), not the wall clock.
define "Test Age In Days":
  Patient.ageInDays()

define "Test Age In Years":
  Patient.ageInYears()

// Floating point + unit-aware -- BSA is a square root of a unit-converted
// ratio, so the result is rarely a round decimal, and the source height/weight
// may be recorded in a variety of units.
define "Test Height":
  (UCE."All Body Height Measurements").mostRecent().value

define "Test Weight":
  (UCE."All Body Weight Measurements").mostRecent().value

define "Test BSA (Mosteller)":
  UCE.CalculateBSA('Mosteller', "Test Height", "Test Weight")

define "Test BSA (DuBois and DuBois)":
  UCE.CalculateBSA('DuBois and DuBois', "Test Height", "Test Weight")

// Partial list matching -- the assertion checks that particular medication
// requests are included/excluded, not that the whole set matches a fixture.
define "Test Active Medication Orders":
  UCE."Active Medication Orders"



