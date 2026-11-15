library testFlattenPathSource version '1.0.0'

define T: Tuple { item: { Tuple { a: { 1, 2 } }, Tuple { a: { 3 } } } }
define Flattened: flatten (T.item I return I.a)
