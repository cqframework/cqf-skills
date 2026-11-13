library testWaSingletonGuard

define "Many": { 1, 2 }
define "One": { 7 }
define "GuardMany": if Count("Many") = 1 then singleton from "Many" else null
define "GuardOne": if Count("One") = 1 then singleton from "One" else null
