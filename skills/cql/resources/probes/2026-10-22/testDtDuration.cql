library testDtDuration

define "MonthsBetweenMonthEnd": months between @2014-01-31 and @2014-02-01
define "DifferenceMonthsMonthEnd": difference in months between @2014-01-31 and @2014-02-01
define "YearsBetweenLeap": years between @2012-02-29 and @2014-02-28
define "YearsBetweenBoundary": years between @2011-12-31 and @2012-01-01
define "DifferenceYearsBoundary": difference in years between @2011-12-31 and @2012-01-01
define "UncertainDays": days between @2014-01-15 and @2014-02
define "UncertainGt2": days between @2014-01-15 and @2014-02 > 2
define "UncertainGt20": days between @2014-01-15 and @2014-02 > 20
define "UncertainGt50": days between @2014-01-15 and @2014-02 > 50
define "HoursAcrossOffsets": hours between @2017-03-12T01:00:00-07:00 and @2017-03-12T03:00:00-06:00
define "DaysAcrossOffsets": days between @2017-03-12T00:00:00-07:00 and @2017-03-13T00:00:00-06:00
define "DifferenceDaysAcrossOffsets": difference in days between @2017-03-12T00:00:00-07:00 and @2017-03-13T00:00:00-06:00
