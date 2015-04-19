#!/usr/bin/python
import glob
from os.path import islink
import sys

print """
This script removes trailing slashes from symlinks in /var/lib/hbs/*
It would be wise to make a backup copy of /var/lib/hbs just in case.

[Press ENTER to continue, C-c to abort.]""",

try:
	temp=raw_input()
except KeyboardInterrupt:
	sys.exit("\nAborting. Have a nice day!")

for f in glob.glob("/var/lib/hbs/*"):
	a=open(f+"/FILELIST")
	lista=a.readlines()
	a.close()
	nowa_lista=[]
	for i in lista:
		j=i[i.find(":/")+1:-1]
		if (j.endswith("/") and islink(j[:-1])):
			nowa_lista.append(i[:-2]+'\n')
		else: nowa_lista.append(i)
	a=open(f+"/FILELIST","w")
	a.writelines(nowa_lista)
	a.close()

