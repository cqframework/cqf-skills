library testHoUnionNulls version '1.0.0'

define "UnionNulls": { null as Integer, 1 } union { null as Integer }
define "UnionNullsCount": Count({ null as Integer, 1 } union { null as Integer })
define "ControlNoNulls": Count({ 1 } union { 2 })
