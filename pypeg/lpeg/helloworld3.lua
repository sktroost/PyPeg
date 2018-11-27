local lpeg = require "lpeg"

R = lpeg.R
S = lpeg.S
P = lpeg.P

local number = {}

local digit = R("09")

-- Matches: 10, -10, 0
number.integer =
	(S("+-") ^ -1) *
	(digit   ^  1)

-- Matches: .6, .899, .9999873
number.fractional =
	(P(".")   ) *
	(digit ^ 1)

-- Matches: 55.97, -90.8, .9 
number.decimal =	
	(number.integer *                     -- Integer
	(number.fractional ^ -1)) +           -- Fractional
	((S("+-") ^ -1) * number.fractional)  -- Completely fractional number

-- Matches: 60.9e07, 9e-4, 681E09 
number.scientific = 
	number.decimal * -- Decimal number
	S("Ee") *        -- E or e
	number.integer   -- Exponent

-- Matches all of the above
number.number =
	number.scientific + number.decimal -- Decimal number allows for everything else, and scientific matches scientific


t = number.number:match(-1232.231)  --> { a = "b", c = "hi", next = "pi" }
