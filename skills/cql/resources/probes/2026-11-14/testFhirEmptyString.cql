library testFhirEmptyString version '1.0.0'

using FHIR version '4.0.1'
include FHIRHelpers version '4.0.1'

define S: FHIR.string { value: '' }
define Value: S.value
define ValueIsNull: S.value is null
define Converted: FHIRHelpers.ToString(S)
define Whitespace: FHIR.string { value: ' ' }.value
