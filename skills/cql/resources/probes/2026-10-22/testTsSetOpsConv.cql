library testTsSetOpsConv

define "UConv": { 1 } union { 1.5 }
define "IConv": { 1 } intersect { 1.0 }
define "EConv": { 1, 2 } except { 1.0 }
define "UTupleSame": { Tuple { v: 1 } } union { Tuple { v: 2 } }
