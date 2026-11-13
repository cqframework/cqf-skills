library testTqAsComponent version '1.0.0'

define function h(v Choice<Integer, String>): v as Integer
define "AsIntegerFromInt": h(1)
define "AsIntegerFromStr": h('a')
