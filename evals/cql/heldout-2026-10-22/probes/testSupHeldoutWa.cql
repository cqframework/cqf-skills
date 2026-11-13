library testSupHeldoutWa

define L: { 'a', null, 'b' }
define Sep: null as String
define "Workaround": Combine((L) X where X is not null, Coalesce(Sep, ''))
define "WorkaroundDash": Combine((L) X where X is not null, Coalesce('-', ''))
define "Control": Combine(L, '-')
