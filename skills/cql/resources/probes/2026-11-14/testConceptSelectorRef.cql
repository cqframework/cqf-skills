library testConceptSelectorRef version '1.0.0'

codesystem "LOINC": 'http://loinc.org'
code "Glucose": '2345-7' from "LOINC"

define ByReference: Concept { "Glucose" }
