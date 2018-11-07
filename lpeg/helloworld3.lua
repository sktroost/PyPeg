local lpeg = require "lpeg"

P = lpeg.P
R = lpeg.R
S = lpeg.S
C = lpeg.C
match = lpeg.match
any = lpeg.P(1) -- pattern that accepts one character
--space = lpeg.S(" \t\n") -- a set with the given chars
digit = lpeg.R("09") -- a set with the range 0-9
lower = lpeg.R("az") -- a set with the range a-z
upper = lpeg.R("AZ") -- a set with the range A-Z
letter = lower + upper -- ’+’ is an ordered choice
alnum = letter + digit
lpeg.locale(lpeg)
local space = lpeg.space^0
local name = lpeg.C(lpeg.alpha^1) * space
local sep = lpeg.S(",;") * space
local pair = lpeg.Cg(name * "=" * space * name) * sep^-1
local list = lpeg.Cf(lpeg.Ct("") * pair^0, rawset)
t = list:match("a=b, c = hi; next = pi")  --> { a = "b", c = "hi", next = "pi" }
