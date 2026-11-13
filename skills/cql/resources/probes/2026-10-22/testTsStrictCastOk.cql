library testTsStrictCastOk

define function h(v Choice<Integer, String>): cast v as Integer

define "StrictMatch": h(1)
