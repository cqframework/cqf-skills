library testDtArithmetic

define "Jan31PlusMonthLeap": @2024-01-31 + 1 month
define "Jan31PlusMonthCommon": @2023-01-31 + 1 month
define "Feb29PlusYear": @2024-02-29 + 1 year
define "Mar31MinusMonth": @2024-03-31 - 1 month
define "Jan31PlusMonthTwice": @2024-01-31 + 1 month + 1 month
define "Jan31PlusTwoMonths": @2024-01-31 + 2 months
define "YearPlus18Months": DateTime(2014) + 18 months
define "MinusDecimalYears": @2016-01-01 - 1.1 years
define "TimeWrap": @T23:30:00 + 1 hour
define "DateTimeAddKeepsOffset": @2026-01-31T10:00:00-05:00 + 1 month
