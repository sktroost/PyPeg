local lpeg = require "lpeg"

P = lpeg.P
R = lpeg.R
S = lpeg.S
C = lpeg.C
match = lpeg.match
any = lpeg.P(1) -- pattern that accepts one character
space = lpeg.S(" \t\n") -- a set with the given chars
digit = lpeg.R("09") -- a set with the range 0-9
lower = lpeg.R("az") -- a set with the range a-z
upper = lpeg.R("AZ") -- a set with the range A-Z
letter = lower + upper -- ’+’ is an ordered choice
alnum = letter + digit
--match(P'a'*P'b'^0,'abbc')
 function maybe(p) return p^-1 end
 digits = R'09'^1
 mpm = maybe(S'+-')
 dot = '.'
 exp = S'eE'
 float = mpm * digits * maybe(dot*digits) * maybe(exp*mpm*digits)
  match(C(float),'2.3')
