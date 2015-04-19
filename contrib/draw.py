#!/usr/bin/python
from glob import glob
from os import path
from math import pi, sqrt, ceil, floor, cos, sin
import random
import sre

dirs=glob("/var/lib/hbs/*/")


packs={}

for i in dirs:
    file=path.join(i,'PROVIDES')
    count=path.basename(path.normpath(i))
    print count
    packs[count]={}
    packs[count]['prov']={}
    packs[count]['req']={}
    info=open(path.join(i,'INFO'))
    data=info.readlines()
    info.close()
    packs[count]['name']=data[0].strip()
    packs[count]['info']=data[1].strip()
    packs[count]['size']=data[2].strip()
    packs[count]['time']=data[3].strip()
    info=open(path.join(i,'FILELIST'))
    data=info.readlines()
    packs[count]['files']=len(data)
    info.close()
    del data, info
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
for pack in packs:
    for dep in packs[pack]['prov']:
        if dep in packs[pack]['req']:
            packs[pack]['req'].remove(dep)

def replace_dep(entry):
    if entry == dep: return pack
    else: return entry

#Translate deps into package names.
for pack in packs:
    for dep in packs[pack]['prov']:
        for i in packs:
            if dep in packs[i]['req']:
                packs[i]['req']=map(replace_dep, packs[i]['req'])

#Shorten the database, count the refs.
for pack in packs:
    packs[pack]["prov"]=0

for pack in packs:
    if len(packs[pack]["req"])==0:
        packs[pack]["req"]=[]
    else:
        packs[pack]["req"].sort()
        known=[]
        for i in packs[pack]["req"]:
            if i not in known:
                known+=[i]
                try:
                    packs[i]["prov"]+=1
                except KeyError:
                    pass
        packs[pack]["req"]=known

#Create "lightning dependencies" instead of "web dependencies"
queue=[]
for pack in packs:
    queue+=[(packs[pack]['prov'], pack)]
queue.sort()

for k, i in queue:
    distant=[]
    supplier=[]
    for dep in packs[i]['req']:
        #for every dep in a package...
        for j in packs[i]['req']:
            if dep==j: continue
            try:
                if dep in packs[j]['req'] and dep not in supplier and dep not in distant:
                    distant+=[dep]
                    supplier+=[j]
                    print "Package:",i,"removed", dep, "("+j+")"
            except KeyError:
                pass
    for j in distant:
        if j in packs[i]['req']:
            packs[i]['req'].remove(j)
            packs[j]['prov']=packs[j]['prov']-1

#get the distance to the center of the galaxy:
largest=(0, 0)
for i in packs:
    if packs[i]['prov'] > largest[0]: largest=(packs[i]['prov'], i)

center=largest[1]
del largest
packs[center]['ring']=0

def get_rings(reff,dist):
    added=[]
    for ref in reff:
        for i in packs:
            if packs[i].has_key('ring') or ref not in packs[i]['req']:
                continue
            else:
                packs[i]['ring']=dist+1
                added+=[i]
    return added

res=[]
rings_=[]
res+=[center]
while len(res)>0:
    rings_+=[res]
    ring=packs[res[0]]['ring']
    res=get_rings(res, ring)

ring+=1
res=[]
for i in packs:
    if not packs[i].has_key("ring"):
        packs[i]["ring"]=ring
        res+=[i]
rings_+=[res]

#2-D stuff

sum=0
for pack in packs:
    coverage=int(ceil(sqrt(float(packs[pack]["size"])/1024)))
    packs[pack]["area"]=coverage
    sum+=coverage

#queue=[]
#for pack in packs:
#    queue+=[(packs[pack]["area"], packs[pack]["prov"], pack)]
#queue.sort()
#queue.reverse()

axis=int(sum*0.8)

def dump_data(filename):
    
    file=open(filename,"w")
    file.write("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN"
    "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
    <svg xml:space="preserve">
    """)
    
    #draw connecting lines
    for pack in packs:
        for i in packs[pack]["req"]:
            try:
                x=packs[i]["pos"][0]+(float(packs[i]["area"])/2)
                y=packs[i]["pos"][1]+(float(packs[i]["area"])/2)
                x1=packs[pack]["pos"][0]+(float(packs[pack]["area"])/2)
                y1=packs[pack]["pos"][1]+(float(packs[pack]["area"])/2)
                file.write("<path style=\"fill:none;fill-rule:evenodd;stroke:black;stroke-opacity:0.5;stroke-width:0.2pt;stroke-linejoin:miter;stroke-linecap:butt;fill-opacity:1;\"\nd=\"M "+str(x1)+" "+str(y1)+" L "+str(x)+" "+str(y)+"\"/>\n")      
            except KeyError:
                pass
    
    #draw packages
    for pack in packs:
        file.write("<rect id=\""+packs[pack]["name"]+"\"\n\
    style=\"fill:none;stroke-width:2pt;stroke:#000000\"\n\
    width=\"" +str(packs[pack]["area"])+"\"\n\
    height=\""+str(packs[pack]["area"])+"\"\n\
    x=\""+str(packs[pack]["pos"][0])+"\"\n\
    y=\""+str(packs[pack]["pos"][1])+"\"\n/>\n")
    
    #write text
    for pack in packs:
        x=packs[pack]["pos"][0]+(float(packs[pack]["area"])/2)
        y=packs[pack]["pos"][1]+packs[pack]["area"]+12
        file.write("<text style=\"fill:black;stroke:none;font-family:Arial;font-style:normal;font-weight:normal;font-size:12;text-anchor:middle;writing-mode:lr;fill-opacity:1;stroke-opacity:1;stroke-width:1pt;stroke-linejoin:miter;stroke-linecap:butt;\"\nx=\""+str(x)+"\"\ny=\""+str(y)+"\"\n>\n<tspan>"+packs[pack]["name"]+"</tspan></text>\n")
    
    file.write("</svg>\n")
    file.close()

#place packages
ringwidth=axis/ring

for X in range(1,len(rings_)-1):
    
    queue=[]
    for i in rings_[X]:
        queue+=[(packs[i]['prov'], i)]
    queue.sort()
    
    rings_[X]=[]
    for i, n in queue:
        rings_[X]+=[n]
    
    ind=len(rings_[X])
    rc=0
    for i in range(0,int(ind/2)):
        rings_[X].insert(ind-rc,rings_[X][i])
        del(rings_[X][i])
        i+=1
        rc+=1
        
spc=20
level=0
for ring in rings_:
    length=0
    max=0
    for i in ring:
        if packs[i]["area"] > max: max=packs[i]["area"]
        length+=packs[i]["area"]
    length+=spc*len(ring) #for spacing
    pos=0-length/2
    for i in ring:
        packs[i]["pos"]=(pos, level)
        pos+=packs[i]["area"]+spc
    level+=max+600



for ring in rings_:
    angle=0
    radius=0
    for i in ring:
        radius+=packs[i]["area"]+30
    step=float(pi)/radius
    rad=0
    for i in ring:
        (x, y)=packs[i]["pos"]
        x=rad
        rad=rad+30+packs[i]["area"]
        y=int(sin(angle)*400)
        x=int(rad-radius/2)
        packs[i]["pos"]=(x,y)
        angle+=step*(30+packs[i]["area"])



#for pack in packs:
#    sphere=packs[pack]["ring"]
#    packs[pack]["pos"]=(random.randint((sphere+1)*ringwidth/-2, (sphere+1)*ringwidth/2), random.randint(sphere*ringwidth+50,(sphere+1)*ringwidth))

#packs[center]['pos']=(0, 0)

dump_data("schemata.svg")

##shuffle them around
#for i in range(10):
#    print "Iteration", i
#    for pack in packs:
#        x=0
#        y=0
#        posx=packs[pack]["pos"][0]
#        posy=packs[pack]["pos"][1]
#        for body in packs:
#            if body == pack: continue
#            posx1=packs[body]["pos"][0]
#            posy1=packs[body]["pos"][1]
#            xd=abs(posx1)-abs(posx)
#            yd=abs(posy1)-abs(posy)
#            xd=abs(xd)
#            yd=abs(yd)
#            
##            #Prevent(?) colisions...
##            if xd < packs[pack]["area"]:
##                yd+=packs[pack]["area"]
##            if yd < packs[pack]["area"]:
##                yd+=packs[pack]["area"]
#
#            if body in packs[pack]["req"]:
#                #pull
#                if posx < posx1: x+=xd
#                else: x-=xd
#                if posy < posy1: y+=yd
#                else: y-=yd
#            else:
#                #push
#                xm=0
#                ym=0
#                if posx < posx1: xm-=30
#                else: xm+=30
#                if posy < posy1: ym-=30
#                else: ym+=30
#                if xd < 40: x+=xm
#                if yd < 40: y+=ym
#
#        #Apply movement
#        x=int(float(x)/(len(packs[pack]["req"])+packs[pack]["prov"]+1))
#        y=int(float(y)/(len(packs[pack]["req"])+packs[pack]["prov"]+1))
##        print "Wektor:",x/axis,y/axis
##        print "Move by:", x, y
#
#        x+=packs[pack]["pos"][0]
#        y+=packs[pack]["pos"][1]
#        x=int(x)
#        y=int(y)
#        packs[pack]["pos"]=(x, y)
#
#dump_data("/shm/2.svg")
#
