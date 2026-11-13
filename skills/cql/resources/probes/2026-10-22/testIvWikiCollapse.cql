library testIvWikiCollapse

define "Test1": collapse { Interval[@2021-01-06, @2021-01-08], Interval[@2021-01-08, null] }
define "Test2": collapse { Interval[@2021-01-06, @2021-01-08], Interval[@2021-01-08, null], Interval[@2021-01-15, @2021-01-18] }
define "OpenNull": collapse { Interval[@2021-01-06, @2021-01-08], Interval[@2021-01-08, null) }
