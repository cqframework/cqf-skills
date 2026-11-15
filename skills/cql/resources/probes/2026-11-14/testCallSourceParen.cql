library testCallSourceParen version '1.0.0'

define function F(x Integer): { x, x + 1 }
define Parenthesised: (F(1)) X return X + 10
