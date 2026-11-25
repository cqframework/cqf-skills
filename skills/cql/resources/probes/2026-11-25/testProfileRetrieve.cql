library testProfileRetrieve version '0.0.1'

using USQualityCore version '0.5.0'
using USCore version '6.1.0-derived'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1'

context Patient

define "Base FHIR": [FHIR.MedicationRequest] R return R.id
define "US Quality Core MedicationRequest": [USQualityCore.MedicationRequest] R return R.id
define "US Quality Core MedicationNotRequested": [USQualityCore.MedicationNotRequested] R return R.id
