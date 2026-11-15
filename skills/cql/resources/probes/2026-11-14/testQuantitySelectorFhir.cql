library testQuantitySelectorFhir version '1.0.0'

using FHIR version '4.0.1'
include FHIRHelpers version '4.0.1'

define Unqualified: Quantity { value: 4.0, unit: 'mg' }
define IsFhir: Unqualified is FHIR.Quantity
define Qualified: System.Quantity { value: 4.0, unit: 'mg' }
define Literal: 4.0 'mg'
