library testSupHeldout2

define "CombineNullSep": Combine({ 'a', null, 'b' }, null)
define "CombineTypedNullSep": Combine({ 'a', 'b' }, null as String)
define "CombineDashSep": Combine({ 'a', null, 'b' }, '-')
define "CombineNoSep": Combine({ 'a', null, 'b' })
define "CombineNoNulls": Combine({ 'a', 'b' }, '-')
