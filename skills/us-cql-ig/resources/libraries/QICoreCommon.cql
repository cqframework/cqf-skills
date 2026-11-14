/*
@description: Common terminologies and functions used in QICore-based CQL artifacts
@comment: The modelinfo included with this IG is using [derived modelinfo](https://hl7.org/fhir/uv/cql/using-modelinfo.html#derived-modelinfo)
to enable reuse of data elements and libraries. This library is derived from the QICoreCommon shared library used in FHIR-based
quality measure specifications. However, most of the functionality that was defined in previous versions of QICoreCommon is now either
 in [FHIRCommon](https://hl7.org/fhir/uv/cql/Library-FHIRCommon.html) or [USCoreCommon](https://hl7.org/fhir/us/cql/Library-USCoreCommon.html).
*/
library QICoreCommon version '2.0.0'

using QICore version '6.0.0-derived'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1'
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0'

codesystem "ActCode": 'http://terminology.hl7.org/CodeSystem/v3-ActCode'
codesystem "TaskCodeSystem": 'http://hl7.org/fhir/CodeSystem/task-code'

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
code "virtual": 'VR' from ActCode display 'Virtual'

//Task codes
code "Fulfill": 'fulfill' from "TaskCodeSystem" display 'Fulfill'

context Patient

/*
@description: Returns the id of the given uri (i.e. everything after the last slash)
@deprecated: Use the FHIRCommon references patterns instead
*/
define fluent function getId(uri String):
  Last(Split(uri, '/'))

/*
@description: Returns the System.ValueSet instance with the url and version (if present) of the given canonical reference
*/
define fluent function toValueSet(canonical FHIR.canonical):
  System.ValueSet {
    id: canonical.url(),
    version: canonical.version()
  }

/*
@description: Converts the activity extent pattern used to represent negated activities to either a codeableConcept or a value set
@seealso: [Negation In QI Core](negation.html)
*/
define fluent function toActivityExtent(codeableConcept FHIR.CodeableConcept):
  (codeableConcept.ext('http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-notDoneValueSet').value) X
    return
      if X is not null
        then X.toValueSet()
        else codeableConcept

/*
@description: Returns true if this is an actual, as opposed to potential, adverse event
*/
define fluent function isActual(adverseEvent FHIR.AdverseEvent):
  adverseEvent.actuality = 'actual'

/*
@description: Returns actual adverse events, as opposed to potential
*/
define fluent function actual(adverseEvents List<FHIR.AdverseEvent>):
  adverseEvents A
    where A.isActual()

/*
@description: Returns true if this is a potential, as opposed to an actual, adverse event
*/
define fluent function isPotential(adverseEvent FHIR.AdverseEvent):
  adverseEvent.actuality = 'potential'

/*
@description: Returns potential adverse events, as opposed to actual
*/  
define fluent function potential(adverseEvents List<FHIR.AdverseEvent>):
  adverseEvents A
    where A.isPotential()

/*
@description: Returns the value of the recorded extension for a Communication Not Done
*/
define fluent function recorded(communicationNotDone QICore.CommunicationNotDone):
  communicationNotDone.ext('http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-recorded').value as FHIR.dateTime

/*
@description: Returns the negated activity extent for a Communication Not Done
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function topic(communicationNotDone QICore.CommunicationNotDone):
  communicationNotDone.topic.toActivityExtent()

/*
@description: Returns the value of the doNotPerformReason extension for a Device Not Requested
*/
define fluent function doNotPerformReason(deviceNotRequested QICore.DeviceNotRequested):
  deviceNotRequested.ext('http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-doNotPerformReason').value as FHIR.CodeableConcept

/*
@description: Returns the value of the doNotPerform extension for a Device Not Requested
*/
define fluent function doNotPerform(deviceNotRequested QICore.DeviceNotRequested):
  deviceNotRequested.ext('http://hl7.org/fhir/5.0/StructureDefinition/extension-DeviceRequest.doNotPerform').value as FHIR.boolean

/*
@description: Returns the negated activity extent for a Device Not Requested
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function code(deviceNotRequested QICore.DeviceNotRequested):
  deviceNotRequested.code.toActivityExtent()

/*
@description: Returns the value of the abatement extension for a FamilyMemberHistory
*/
define fluent function abatement(familyMemberHistoryCondition QICore.FamilyMemberHistory.Condition):
  familyMemberHistoryCondition.ext('hl7.org/fhir/StructureDefinition/familymemberhistory-abatement').value as Choice<FHIR.date, FHIR.Age, FHIR.boolean>

/*
@description: Returns the value of the severity extension for a FamilyMemberHistory
*/
define fluent function severity(familyMemberHistoryCondition QICore.FamilyMemberHistory.Condition):
  familyMemberHistoryCondition.ext('hl7.org/fhir/StructureDefinition/familymemberhistory-severity').value as FHIR.CodeableConcept

/*
@description: Returns the negated activity extent for an Immunization Not Done
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function vaccineCode(immunizationNotDone QICore.ImmunizationNotDone):
  immunizationNotDone.vaccineCode.toActivityExtent()

/*
@description: Returns the value of the recorded extension for a Medication Administration Not Done
*/
define fluent function recorded(medicationAdministrationNotDone QICore.MedicationAdministrationNotDone):
  medicationAdministrationNotDone.ext('http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-recorded').value as FHIR.dateTime

/*
@description: Returns the negated activity extent for a Medication Administration Not Done
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function medication(medicationAdministrationNotDone QICore.MedicationAdministrationNotDone):
  medicationAdministrationNotDone.medication.toActivityExtent()

/*
@description: Returns the value of the recorded extension for a Medication Dispense Declined
*/
define fluent function recorded(medicationDispenseDeclined QICore.MedicationDispenseDeclined):
  medicationDispenseDeclined.ext('http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-recorded').value as FHIR.dateTime

/*
@description: Returns the negated activity extent for a Medication Dispense Declined
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function medication(medicationDispenseDeclined QICore.MedicationDispenseDeclined):
  (medicationDispenseDeclined.medication as FHIR.CodeableConcept).toActivityExtent()

/*
@description: Returns the negated activity extent for a Medication Not Requested
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function medication(medicationNotRequested QICore.MedicationNotRequested):
  medicationNotRequested.medication.toActivityExtent()

/*
@description: Returns the notDoneReason for an ObservationCancelled
*/
define fluent function notDoneReason(observationCancelled QICore.ObservationCancelled):
  observationCancelled.ext('http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-notDoneReason').value as FHIR.CodeableConcept

/*
@description: Returns the negated activity extent for an ObservationCancelled
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function code(observationCancelled QICore.ObservationCancelled):
  observationCancelled.code.toActivityExtent()

/*
@description: Returns the first ccn effective on the given date
*/
define fluent function ccn(organization FHIR.Organization, asOf Date):
  organization.identifier.ccn(asOf)

/*
@description: Returns the first ccn effective as of today
*/
define fluent function ccn(organization FHIR.Organization):
  organization.identifier.ccn()

/*
@description: Returns the first ein effective on the given date
*/
define fluent function ein(organization FHIR.Organization, asOf Date):
  organization.identifier.ein(asOf)

/*
@description: Returns the first ein effective as of today
*/
define fluent function ein(organization FHIR.Organization):
  organization.identifier.ein()

/*
@description: Returns the first npi effective on the given date
*/
define fluent function npi(practitioner FHIR.Practitioner, asOf Date):
  practitioner.identifier.npi(asOf)

/*
@description: Returns the first npi effective as of today
*/
define fluent function npi(practitioner FHIR.Practitioner):
  practitioner.identifier.npi()

/*
@description: Returns the first ein effective on the given date
*/
define fluent function ein(practitioner FHIR.Practitioner, asOf Date):
  practitioner.identifier.ein(asOf)

/*
@description: Returns the first ein effective as of today
*/
define fluent function ein(practitioner FHIR.Practitioner):
  practitioner.identifier.ein()

/*
@description: Returns the first ccn identifier effective on the given date
*/
define fluent function ccnIdentifier(identifiers List<FHIR.Identifier>, asOf Date):
  First(
    identifiers I
      where I.system = 'http://terminology.hl7.org/NamingSystem/CMSCertificationNumber'
        and I.period is null or asOf during I.period
      sort by start of period
  )

/*
@description: Returns the first ccn identifier effective as of today
*/
define fluent function ccnIdentifier(identifiers List<FHIR.Identifier>):
  identifiers.ccnIdentifier(Today())

/*
@description: Returns the value of the first ccn identifier effective on the given date
*/
define fluent function ccn(identifiers List<FHIR.Identifier>, asOf Date):
  identifiers.ccnIdentifier(asOf).value

/*
@description: Returns the value of the first ccn identifier effective as of today
*/
define fluent function ccn(identifiers List<FHIR.Identifier>):
  identifiers.ccnIdentifier().value

/*
@description: Returns the first ein identifier effective on the given date
*/
define fluent function einIdentifier(identifiers List<FHIR.Identifier>, asOf Date):
  First(
    identifiers I
      where I.system = 'urn:oid:2.16.840.1.113883.4.4'
        and I.period is null or asOf during I.period
      sort by start of period
  )

/*
@description: Returns the first ein identifier effective as of today
*/
define fluent function einIdentifier(identifiers List<FHIR.Identifier>):
  identifiers.einIdentifier(Today())

/*
@description: Returns the value of the first ein identifier effective on the given date
*/
define fluent function ein(identifiers List<FHIR.Identifier>, asOf Date):
  identifiers.einIdentifier(asOf).value

/*
@description: Returns the value of the first ein identifier effective as of today
*/
define fluent function ein(identifiers List<FHIR.Identifier>):
  identifiers.einIdentifier().value

/*
@description: Returns the first npi identifier effective on the given date
*/
define fluent function npiIdentifier(identifiers List<FHIR.Identifier>, asOf Date):
  First(
    identifiers I
      where I.system = 'http://hl7.org/fhir/sid/us-npi'
        and I.period is null or asOf during I.period
      sort by start of period
  )

/*
@description: Returns the first npi identifier effective as of today
*/
define fluent function npiIdentifier(identifiers List<FHIR.Identifier>):
  identifiers.npiIdentifier(Today())

/*
@description: Returns the value of the first npi identifier effective on the given date
*/
define fluent function npi(identifiers List<FHIR.Identifier>, asOf Date):
  identifiers.npiIdentifier(asOf).value

/*
@description: Returns the value of the first npi identifier effective as of today
*/
define fluent function npi(identifiers List<FHIR.Identifier>):
  identifiers.npiIdentifier().value

/*
@description: Returns the value of the recorded extension for a Procedure
*/
define fluent function recorded(procedure QICore.Procedure):
  procedure.ext('http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-recorded').value as FHIR.dateTime

/*
@description: Returns the value of the recorded extension for a Medication Administration Not Done
*/
define fluent function recorded(procedureNotDone QICore.ProcedureNotDone):
  procedureNotDone.ext('http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-recorded').value as FHIR.dateTime

/*
@description: Returns the negated activity extent for a Procedure Not Done
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function code(procedureNotDone QICore.ProcedureNotDone):
  procedureNotDone.code.toActivityExtent()

/*
@description: Returns the value of the recorded extension for a Medication Administration Not Done
*/
define fluent function reasonRefused(serviceNotRequested QICore.ServiceNotRequested):
  serviceNotRequested.ext('http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-doNotPerformReason').value as FHIR.CodeableConcept

/*
@description: Returns the negated activity extent for a Service Not Requested
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function code(serviceNotRequested QICore.ServiceNotRequested):
  serviceNotRequested.code.toActivityExtent()

/*
@description: Returns the negated activity extent for a Task Rejected
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function code(taskRejected QICore.TaskRejected):
  taskRejected.code.toActivityExtent()

/*
@description: Creates a list of integers from 1 to how many days are in the interval. Note, this wont create an index for
the final day if it is less than 24 hours. This also includes the first 24 hour period.
*/
define fluent function toDayNumbers(Period Interval<DateTime>):
  ( expand { Interval[1, duration in days between start of Period and end of Period]} ) DayNumber
    return end of DayNumber

/*
@description: Creates a list of 24 hour long intervals in an interval paired with the index (1 indexed) to which 24 hour interval it is.
Note that the result will include intervals that are closed at the beginning and open at the end
*/
define fluent function daysInPeriod(Period Interval<DateTime>):
  ( Period.toDayNumbers()) DayIndex
    let startPeriod: start of Period + (24 hours * (DayIndex - 1)),
    endPeriod: if (hours between startPeriod and end of Period < 24) then startPeriod
      else start of Period + (24 hours * DayIndex)
    return Tuple {
      dayIndex: DayIndex,
      dayPeriod: Interval[startPeriod, endPeriod)
    }
