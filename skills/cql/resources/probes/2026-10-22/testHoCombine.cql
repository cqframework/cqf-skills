library testHoCombine version '1.0.0'

define "CombineNoNulls": Combine({ 'a', 'b' }, '-')
define "CombineNullElement": Combine({ 'a', null, 'b' }, '-')
define "CombineTypedNullSep": Combine({ 'a', 'b' }, null as String)
define "CombineUntypedNullSep": Combine({ 'a', null, 'b' }, null)
define "CombineNoSepNullElement": Combine({ 'a', null, 'b' })
define "CombineNoSepNoNulls": Combine({ 'a', 'b' })
