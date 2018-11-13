set LUA_DIR=K:\Stefan\GCCLUA\lua-5.3.5
gcc -O2 -shared -s -I %LUA_DIR%\src -L %LUA_DIR%\src -o lpeg.dll lptree.c lpvm.c lpcap.c lpcode.c lpprint.c -llua53