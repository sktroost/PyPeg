import os, sys

if __name__=="__main__":
	luafile=str(sys.argv[1])
	os.system("lua "+luafile+" > result.txt")