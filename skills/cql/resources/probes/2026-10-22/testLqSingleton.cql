library testLqSingleton

define "FromEmpty": singleton from List<Integer> { }
define "FromOne": singleton from { 1 }
define "FromNullList": singleton from (null as List<Integer>)
define "FromOneNull": singleton from { null as Integer }
