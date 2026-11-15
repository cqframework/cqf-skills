library testCodeEquivalenceCase version '1.0.0'

codesystem "V2-0074": 'http://terminology.hl7.org/CodeSystem/v2-0074'

define Equivalent: Code 'lab' from "V2-0074" ~ Code 'LAB' from "V2-0074"
define Equal: Code 'lab' from "V2-0074" = Code 'LAB' from "V2-0074"
define StringEquivalent: 'lab' ~ 'LAB'
