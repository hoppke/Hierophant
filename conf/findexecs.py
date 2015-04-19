#!/usr/bin/python

from os import walk, path, lstat
import sre, sys

def notice(msg): print("\033[1mNOTICE: "+msg+"\033[0m")
def error(msg):
    sys.stderr.write("\033[31;1mERROR: "+msg+"\033[0m\n")
    sys.exit(1)

if len(sys.argv) != 2:
    DIR=path.normpath(sys.argv[1])+'/'
    banfile=sys.argv[2]
    pref_len=len(DIR)
else:
    error("No directory and banfile given to the "+sys.argv[0]+" script")

file=open(banfile,"r")
ban=[]

for i in file.readlines():
    ban+=[sre.compile(i.strip())]
file.close()

lib_re=sre.compile("^.*\.so(\.[0-9]+)*$")

def judgement(suspect):
    """Checks if a file isn't banned."""
    for i in ban:
        if i.match(suspect):
            return 1
    return 0

hardlinked_inodes=[]
for top, dirs, files in walk(DIR):
    for i in files:
        file=path.join(top,i)
        if not judgement(file[pref_len:]):
            info=lstat(file)
            if ((info.st_mode&00111)!=0 or lib_re.match(i)) and (info.st_mode&033000)==0:
                #File is an exe/lib and regular (not a symlink, pipe etc.)
                if info.st_nlink==1:
                    #Single file, print right away
                    print file
                elif (info.st_dev, info.st_ino) not in hardlinked_inodes:
                    #New hardlink, print and add to "already seen"
                    print file
                    hardlinked_inodes+=[(info.st_dev, info.st_ino)]
