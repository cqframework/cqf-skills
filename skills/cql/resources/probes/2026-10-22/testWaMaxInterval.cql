library testWaMaxInterval

define "BothNull": 5 in Interval[null as Integer, null as Integer]
define "MinMax": 5 in Interval[minimum Integer, maximum Integer]
define "MinMaxDate": @2026-06-01 in Interval[minimum Date, maximum Date]
define "OneNullBound": 5 in Interval[minimum Integer, null as Integer]
