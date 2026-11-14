library USCoreCommonTests version '2.0.0'

using FHIR version '4.0.1'
using USCore version '6.1.0-derived'

include USCoreCommon version '2.0.0' called UC

context Patient

//* _01_ define fluent function race(patient Patient):
define _01_TestRace: Patient.race()

//* _02_ define fluent function ethnicity(patient Patient):
define _02_TestEthnicity: Patient.ethnicity()

//* _03_ define fluent function tribalAffiliation(patient Patient):
define _03_TestTribalAffiliation: Patient.tribalAffiliation()

//* _04_ define fluent function birthSex(patient Patient):
define _04_TestBirthSex: Patient.birthSex()

//* _05_ define fluent function systolic(bloodPressureProfile BloodPressureProfile):
define _05_TestSystolic:
  [Observation] O
    return O.systolic()

//* _06_ define fluent function diastolic(bloodPressureProfile BloodPressureProfile):
define _06_TestDiastolic:
  [Observation] O
    return O.diastolic()

//* _07_ define fluent function isHealthConcern(condition FHIR.Condition):
define _07_TestIsHealthConcern:
  [Condition] C
    where C.isHealthConcern()

// ============================================================================
// Refined unit test demonstration (proposal: unit-testing.html)
// Exercised by the refined-* test cases under
// input/tests/library/USCoreCommonTests using the proposed assertion model
// (operator / expected / tolerance / negated).
// ============================================================================

// Type-aware equality + negation on a coded value
define "Test Birth Sex":
  Patient.birthSex()

// Partial match of a Coding within a list -- the assertion checks that a
// particular OMB race category is present (or absent), not the whole tuple.
define "Test Race Categories":
  (Patient.race()) R return R.ombCategory

/*
TODO: These are really US Core tests...
define TestAge:
  AgeInYears()

define TestAgeAt:
  AgeInYearsAt(@2022-10-14)

define TestPrimitives:
  Patient P
    where P.gender = 'male'
      and P.active is true
      and P.birthDate before Today()
      and P.maritalStatus in "Marital Status"
      and P.maritalStatus ~ "Marital Status - Married"

define TestChoice:
  Patient P
    where P.deceased is false
      or P.deceased before Today()

define TestSlices:
  ["USCore.BloodPressureProfile"] BP
    where BP.systolic().value < 140 'mm[Hg]'
      and BP.diastolic().value < 90 'mm[Hg]'

define TestSimpleExtensions:
  Patient P
    where P.birthsex() = 'M'

define TestComplexExtensions:
  Patient P
    where P.race().ombCategory contains "American Indian or Alaska Native"
      and P.race().detailed contains "Alaska Native"
*/
