local lpeg = require("lpeg"); lpeg.match(lpeg.P{
    "a";
    a = lpeg.V("b") * lpeg.V("c"),
    b = lpeg.P("b"),
    c = lpeg.P("c")}, "aaa")