library testTsTupleIs

define "NullElem": Tuple { v: null } is Tuple { v Integer }
define "NullElemTyped": Tuple { v: null as Integer } is Tuple { v Integer }
define "IntElem": Tuple { v: 1 } is Tuple { v Integer }
define "StrElem": Tuple { v: 'a' } is Tuple { v Integer }
