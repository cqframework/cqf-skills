library testWaTupleElementTest

define "T": Tuple { v: null as Integer }
define "WholeTupleTest": "T" is Tuple { v Integer }
define "ElementTest": "T".v is null or "T".v is Integer
