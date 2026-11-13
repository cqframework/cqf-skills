library testTsStrictCast

define function h(v Choice<Integer, String>): cast v as Integer

define "StrictMismatch": h('a')
