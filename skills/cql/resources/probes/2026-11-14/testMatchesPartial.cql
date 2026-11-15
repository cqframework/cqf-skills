library testMatchesPartial version '1.0.0'

define LetterInside: Matches('abc', 'b')
define DigitInside: Matches('abc1def', '\\d')
define DigitAnywhere: Matches('abc1def', '.*\\d.*')
define Anchored: Matches('abc1def', '^\\d$')
define Spec153Example: Matches('1,2three', '\\w+')
