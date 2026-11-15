library testConceptSelectorLiteral version '1.0.0'

codesystem "LOINC": 'http://loinc.org'
code "Glucose": '2345-7' from "LOINC"

define ByLiteral: Concept { Code '2345-7' from "LOINC" }
define DeclaredCodeInIt: "Glucose" ~ ByLiteral
