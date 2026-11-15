library testFluentTwoLibrariesReversed version '1.0.0'

include LibB version '1.0.0' called B
include LibA version '1.0.0' called A

define SameSignature: 1.tag()
define DifferentSignatures: 1.widen()
