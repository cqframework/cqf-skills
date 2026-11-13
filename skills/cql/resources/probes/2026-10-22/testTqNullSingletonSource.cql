library testTqNullSingletonSource version '1.0.0'

define "NullSource": (null as DateTime) X return if X is null then 1 else 2
define "ValueSource": (@2026-01-01T00:00:00Z) X return if X is null then 1 else 2
