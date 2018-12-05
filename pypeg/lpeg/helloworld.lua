local lpeg = require("lpeg");
p = lpeg.P"ab"
lpeg.match(lpeg.P{ p + 1 * lpeg.V(1) },"cccccccccccccccccccccccccccccccccab")
