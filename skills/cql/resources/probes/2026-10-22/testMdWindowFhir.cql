library testMdWindowFhir version '1.0.0'

using FHIR version '4.0.1'

include FHIRHelpers version '4.0.1' called FHIRHelpers

define function FollowUpWindow(E FHIR.Encounter):
  Interval[start of E.period, end of E.period + 7 days]

define Visit: FHIR.Encounter {
  period: FHIR.Period {
    start: FHIR.dateTime { value: @2025-01-17T10:00:00.000Z },
    end: FHIR.dateTime { value: @2025-01-17T14:00:00.000Z }
  }
}
define "Window": FollowUpWindow(Visit)
