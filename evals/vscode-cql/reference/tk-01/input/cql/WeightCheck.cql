library WeightCheck version '0.1.0'

using FHIR version '4.0.1'

include FHIRHelpers version '4.0.1' called FHIRHelpers

valueset "Body Weight Codes": 'http://example.org/fhir/ValueSet/body-weight-codes'

parameter "Measurement Period" Interval<DateTime>
parameter "Product Line" String default 'Commercial'

context Patient

define "Weight Observations":
  [Observation: "Body Weight Codes"] O
    where O.status in { 'final', 'amended', 'corrected' }
      and (O.effective as FHIR.dateTime) during "Measurement Period"

define "Has Weight":
  exists "Weight Observations"

define "Is Commercial":
  "Product Line" = 'Commercial'
