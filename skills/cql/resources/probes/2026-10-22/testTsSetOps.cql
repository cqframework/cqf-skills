library testTsSetOps

define "U": { 1 } union { 'a' }
define "I": { 1 } intersect { 'a' }
define "E": { 1 } except { 'a' }
define "USame": { 1 } union { 2 }
define "UTupleConv": { Tuple { v: 1 } } union { Tuple { v: 1.5 } }
define "UTupleMixed": { Tuple { v: 1 } } union { Tuple { v: 'a' } }
