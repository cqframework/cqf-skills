library testBackboneId version '1.0.0'

using FHIR version '4.0.1'
include FHIRHelpers version '4.0.1'

define C: FHIR.Observation.Component { id: 'x' }
define Id: C.id
define WithoutId: FHIR.Observation.Component { code: FHIR.CodeableConcept { text: FHIR.string { value: 'x' } } }
