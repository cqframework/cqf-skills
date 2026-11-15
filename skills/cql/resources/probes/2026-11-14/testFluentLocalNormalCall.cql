library testFluentLocalNormalCall version '1.0.0'

define fluent function tag(x Integer): 'local'
define Normal: tag(1)
define Fluent: 1.tag()
