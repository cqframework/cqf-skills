library testRetrieveFluentParen

using FHIR version '4.0.1'

define fluent function c(x List<FHIR.Condition>): x

define "A": ([Condition]).c()
