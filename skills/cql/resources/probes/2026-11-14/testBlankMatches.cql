library testBlankMatches version '1.0.0'

define Empty: Matches('', '\\s*')
define Spaces: Matches('   ', '\\s*')
define NotBlank: Matches(' a ', '\\s*')
define AnchoredNotBlank: Matches(' a ', '^\\s*$')
