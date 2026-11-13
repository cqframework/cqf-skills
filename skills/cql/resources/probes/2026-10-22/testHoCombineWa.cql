library testHoCombineWa version '1.0.0'

define L: { 'a', null, 'b' }
define Sep: null as String
define "Control": Combine(L, '-')
define "WorkaroundNullSep": Combine((L) X where X is not null, Coalesce(Sep, ''))
define "WorkaroundDash": Combine((L) X where X is not null, Coalesce('-', ''))
