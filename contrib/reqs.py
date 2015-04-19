#!/usr/bin/python
from glob import glob
from os import getenv, path, mkdir, stat
from sys import stdout,argv,exit
from cPickle import dump, load;

if len(argv)==1: 
    from readline import *
    parse_and_bind("tab: complete")

dirs=glob("/var/lib/hbs/*/")
comptable=[]

#names=["gqview", "gkrellm"]

dir=path.join(getenv("HOME"),".hbs")
if not (path.exists(dir)): mkdir(dir)
cache=path.join(dir,".query_cache")

if path.exists(cache) and (stat(cache).st_mtime > stat("/var/lib/hbs").st_mtime):
    if len(argv)==1: stdout.write("Loading cache...")
    p=open(cache)
    packs=load(p)
    p.close()
    comptable=[]
    for i in packs: comptable+=[i]
else:
    if len(argv)==1: 
        stdout.write("Gathering data, please wait")
        stdout.flush()
    packs={}
    if len(argv)==1: 
        stdout.write(".")
        stdout.flush()
    for i in dirs:
        file=path.join(i,'PROVIDES')
        count=path.basename(path.normpath(i))
        comptable+=[count]
        packs[count]={}
        packs[count]['prov']={}
        packs[count]['req']={}
        if path.exists(file):
            file=open(file)
            packs[count]['prov']=file.readlines()
            file.close()
        file=path.join(i,'REQUIRES')
        if path.exists(file):
            file=open(file)
            packs[count]['req']=file.readlines()
            file.close()
    
    #Remove autoreferences
    if len(argv)==1: 
        stdout.write(".")
        stdout.flush()
    for pack in packs:
        for dep in packs[pack]['prov']:
            if dep in packs[pack]['req']:
                packs[pack]['req'].remove(dep)
            packs[pack]['req'].sort()
    
    def replace_dep(entry):
        if entry == dep: return pack
        else: return entry
    
    #Translate deps into package names.
    if len(argv)==1: 
        stdout.write(".")
        stdout.flush()
    for pack in packs:
        for dep in packs[pack]['prov']:
            for i in packs:
                if dep in packs[i]['req']:
                    packs[i]['req']=map(replace_dep, packs[i]['req'])
    
    p=open(cache,"w")
    dump(packs,p,2)
    p.close()

if len(argv)==1:
    print " Ready.\nName a package to view its requirements.\nTab-completion available. You can exit with C-c or C-d.\n"

if len(argv)>1:
    longest=0
    for i in argv[1:]:
        if len(i)>longest: longest=len(i)
    format="%%-%is:" % longest
    for i in argv[1:]:
        print format % i,
        if not (packs.has_key(i)):
            print "<unknown_package>"
            continue
    
        deps=[]
        known=[]
        for j in packs[i]["req"]:
            if j not in known:
                deps+=[j.strip()+","]
                known+=[j]
        deps.sort()
        try:
            deps[-1]=deps[-1][:-1]
            for j in deps: print j,
            print
        except IndexError:
            print "<independent>"
if len(argv)>1: exit(0)

def comp(t,v):
    list=[]
    for i in comptable:
        if i.find(t)==0: list+=[i]
    try:
        return list[v]
    except IndexError:
        return None

set_completer_delims('')
set_completer(comp)

while (1):
    try:
        i=raw_input("Query package: ")
    except (EOFError, KeyboardInterrupt):
        break

    if not (packs.has_key(i)):
        print "Unknown package:",i
        continue

    deps=[]
    known=[]
    for j in packs[i]["req"]:
        if j not in known:
            deps+=[j.strip()+","]
            known+=[j]
    deps.sort()
    try:
        deps[-1]=deps[-1][:-1]
        print "Requires: ",
        for j in deps: print j+" ",
        print
    except IndexError:
        print "Independent"
    print

