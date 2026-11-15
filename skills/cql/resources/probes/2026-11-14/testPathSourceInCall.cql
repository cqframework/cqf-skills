library testPathSourceInCall version '1.0.0'

define T: Tuple { item: { Tuple { a: 1 }, Tuple { a: 2 } } }
define TopLevel: T.item I return I.a
define InsideCall: Count(T.item I return I.a)
