library testFluentTwoLibraries version '1.0.0'

include LibA version '1.0.0' called A
include LibB version '1.0.0' called B

define SameSignature: 1.tag()
define DifferentSignatures: 1.widen()
define DecimalArgument: 1.0.widen()
