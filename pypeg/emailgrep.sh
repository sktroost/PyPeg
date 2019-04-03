#!/bin/sh
grep -oE '[a-zA-Z0-9]{1,}@[a-zA-Z0-9]{1,}.de' $1
