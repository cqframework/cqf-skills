library testNlLogic

define "NullAndFalse": (null as Boolean) and false
define "NullAndTrue": (null as Boolean) and true
define "NullOrTrue": (null as Boolean) or true
define "NullOrFalse": (null as Boolean) or false
define "NullXorTrue": (null as Boolean) xor true
define "NotNull": not (null as Boolean)
define "FalseImpliesNull": false implies (null as Boolean)
define "NullImpliesTrue": (null as Boolean) implies true
define "NullImpliesFalse": (null as Boolean) implies false
define "IsTrueNull": (null as Boolean) is true
define "IsFalseNull": (null as Boolean) is false
define "IsNullNull": null is null
