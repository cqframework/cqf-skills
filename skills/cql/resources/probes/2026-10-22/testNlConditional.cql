library testNlConditional

define "IfNull": if (null as Boolean) then 1 else 2
define "CaseWhenNull": case when (null as Boolean) then 1 else 2 end
define "CaseNullComparand": case (null as Integer) when 5 then 1 else 2 end
define "CaseNullItem": case 5 when (null as Integer) then 1 when 5 then 3 else 2 end
define "CoalesceThree": Coalesce(null, null, 3)
define "CoalesceList": Coalesce({ null, 2, 3 })
define "CoalesceAllNull": Coalesce(null as Integer, null as Integer)
