library testTsNormalise

define "Normalised": (({ 1 }) X return ToDecimal(X)) intersect { 1.0 }
define "TypedSelector": List<Decimal> { 1 } intersect { 1.0 }
define "Raw": { 1 } intersect { 1.0 }
