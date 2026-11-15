library testAllTrueNull version '1.0.0'

define AllTrueWithNull: AllTrue({ true, null as Boolean })
define AndWithNull: true and (null as Boolean)
define AllTrueOnlyNull: AllTrue({ null as Boolean })
