library testNlEquality

define "OneEqNull": 1 = null
define "OneEquivNull": 1 ~ null
define "OneNeqNull": 1 != null
define "OneNotEquivNull": 1 !~ null
define "EmptyStringEquivNull": '' ~ (null as String)
define "ListNullEqListNull": { null } = { null }
define "ListNullOneEq": { null, 1 } = { null, 1 }
define "ListNullEquiv": { null, 1 } ~ { null, 1 }
define "TupleBothNullEq": Tuple { x: 1, y: null } = Tuple { x: 1, y: null }
define "TupleMixedNullEq": Tuple { x: 1, y: 1 } = Tuple { x: null, y: 1 }
define "TupleMixedNullFalse": Tuple { x: 1, y: 1 } = Tuple { x: null, y: 2 }
define "TupleBothNullEquiv": Tuple { x: 1, y: null } ~ Tuple { x: 1, y: null }
define "TupleMixedNullEquiv": Tuple { x: 1, y: 1 } ~ Tuple { x: null, y: 1 }
