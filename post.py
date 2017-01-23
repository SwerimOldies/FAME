#!/usr/bin/env python3


import fea
import re
import sys
import numpy as np
from stl import mesh

def readSTL(filename):

    stlmesh = mesh.Mesh.from_file(filename)
    return stlmesh
    
def readResults(filename,feamesh):
    cast=re.compile('DISP')
    file=open(filename)
    steps=0
    for line in file: #count the number of steps
        if len(cast.findall(line))>0:
            steps+=1
    print(str(steps)+' steps in results file.')
    
    dispCast=re.compile('([\s-]\d.\d+E[+-]?\d+)')
    nodenumCast=re.compile(' -1\s+(\d+)')
    file.seek(0) #start from beginning of file
    readingResults=False
    countSteps=0
    for line in file:
        if len(cast.findall(line))>0:
            countSteps+=1
        if countSteps>=steps:
            readingResults=True
        if readingResults==True:
            if ' -1 ' in line:
                num=nodenumCast.findall(line)
                data=dispCast.findall(line)
                
                #print(num,data)
                num=int(num[0])
                disp=[float(d) for d in data[0:3]]
                
                try:
                    feamesh.nodes[num].disp=disp
                except KeyError:
                    pass

            if len(re.compile('\s-3').findall(line))>0:
                readingResults=False
                #print('Done')
                break
    file.close()


def readGeom(filename):
    nodes=[]
    elements=[]
    file=open(filename,'r')
    
    tempMesh=fea.mesh([],[])
    
    readingNodes=False
    readingElements=False
    readingNodesets=False
    readingElementsets=False
    for line in file:
        if '*' in line: #reset block
            readingNodes=False
            readingElements=False
            readingNodesets=False
            readingElementsets=False
        if readingNodes:
            data=line.split(',')
            num=int(data[0])
            c1=float(data[1])
            c2=float(data[2])
            c3=float(data[3])
            nodes.append(fea.node(num,[c1,c2,c3]))
        if readingElements:
            data=line.split(',')
            if data[-1]=='\n': #if we have a trailing comma
                data=data[0:-2]
            num=int(data[0])
            enodes=[int(d) for d in data[1:]]
        if readingNodesets:
            tempMesh.add2nset(int(line.split(',')[0]),setname)
        if readingElementsets:
            tempMesh.add2elset(int(line.split(',')[0]),setname)


            elements.append(fea.element(num,enodes))
        
        if '*NODE' in line:
            readingNodes=True
        if '*ELEMENT' in line:
            readingElements=True    
        if 'nset=' in line:
            readingNodesets=True
            setname=line.split(',')[-1]
        if 'elset=' in line:
            readingElementsets=True
            setname=line.split(',')[-1]
        
    feamesh=fea.mesh(nodes,elements,d1=37,d2=41,margin=0.3) #create fea mesh
    feamesh.nsets=tempMesh.nsets
    feamesh.esets=tempMesh.esets
    return feamesh
    

def adjustSTL(filename,feamesh,stlmesh,power=4,scale=1):
    tol=1e-5
    def norm(v,n):
        sum=0
        for x in v:
            sum+=np.power(x,n)
        
        return np.power(sum,1/n)
    
    def normalize(v):
        length=ln.norm(v,2)
        #length=sum(v)
        return [x/length for x in v]
    
    import numpy.linalg as ln
    
    #identify the build plate
    #first find the minimum x and y coords
    xmin=1000000
    ymin=1000000
    for i in range(len(stlmesh.v0)):
        v=stlmesh.v0[i] #one vertex
        if v[0]<xmin:
            xmin=v[0]
        if v[1]<ymin:
            ymin=v[0]
    for i in range(len(stlmesh.v1)):
        v=stlmesh.v1[i] #one vertex
        if v[0]<xmin:
            xmin=v[0]
        if v[1]<ymin:
            ymin=v[0]
    for i in range(len(stlmesh.v2)):
        v=stlmesh.v2[i] #one vertex
        if v[0]<xmin:
            xmin=v[0]
        if v[1]<ymin:
            ymin=v[0]
    #get all zmax with that x
    zmax=-1000000000
    for i in range(len(stlmesh.v0)):
        v=stlmesh.v0[i] #one vertex
        if (v[0]==xmin) and (zmax<v[2]):
            zmax=v[2]
    for i in range(len(stlmesh.v1)):
        v=stlmesh.v1[i] #one vertex
        if v[0]==xmin and zmax<v[2]:
            zmax=v[2]
    for i in range(len(stlmesh.v2)):
        v=stlmesh.v2[i] #one vertex
        if v[0]==xmin and zmax<v[2]:
            zmax=v[2]


    def adjust(vertex,scale=1):
        N=[] #list of node coordinates
        displacement=[] #nodal displacements        
        nodeNums=feamesh.web1.getNodesCloseToCoord(vertex)
        nodeNums+=feamesh.web2.getNodesCloseToCoord(vertex)

        nodeNums=fea.unique(nodeNums)
        nodes=[feamesh.getNode(n) for n in nodeNums]
        #naverage=np.array([0.0,0.0,0.0])
        for n in nodes:
            if n.coord[2]>zmax-tol: #not interested in nodes belonging to the build plate
            #if n.coord[2]>-1000: #not interested in nodes belonging to the build plate
                N.append((n.coord))
                displacement.append((n.disp))
                #naverage+=np.array(n.coord)
        #naverage=naverage/len(N)
        N=np.array(N)
                
        try:
            R=N-np.array(vertex) #the vectors from this vertex to all fea nodes
            Dist=ln.norm(R,2,axis=1)
        except ValueError:
            print('Warning. Vertex=',vertex,' has no nodes')
            return vertex
        inf=normalize([np.power(x,power) for x in Dist]) #influence weights
        
        #only use the 10 closest nodes
        #zipSorted=list(zip(*sorted(zip(Dist,displacement))))
        #zipSorted=list(zip(*sorted(zip(Dist,displacement,N))))
        zipSorted=list(zip(*(zip(Dist,displacement,N))))
        nodes2use=40
        dist_short=zipSorted[0][0:nodes2use]
        disp_short=zipSorted[1][0:nodes2use]
        #N_short=(zipSorted[2][0:1][0])
        #disp_temp=zipSorted[1][0:15]
        inf_short=normalize([np.power(x,power) for x in dist_short]) #influence weights
        
        
        adjustment=scale*np.dot(np.array(inf),np.array(displacement))        
        #adjustment=scale*np.dot(np.array(inf_short),np.array(disp_short)) #multiply influence weights with the node dispplacements
        
        if vertex[2]<zmax+tol: #vertices on the plate - build interface should not be adjusted in the z direction
            adjustment[2]=0
            
        vertex=vertex-adjustment
        return vertex
    
    #for every vertex in stlmesh determine fea displacement
    for i in range(len(stlmesh.v0)):
        v=stlmesh.v0[i] #one vertex
        if v[2]>zmax-tol: #exclude the build plate from adjustment
            stlmesh.v0[i]=adjust(v,scale)

        v=stlmesh.v1[i] #one vertex
        if v[2]>zmax-tol:
            stlmesh.v1[i]=adjust(v,scale)

        v=stlmesh.v2[i] #one vertex
        if v[2]>zmax-tol:
            stlmesh.v2[i]=adjust(v,scale)
        

    stlmesh.save(filename)
    

if __name__ == "__main__":
    print('FAME post processing')
    run=True
    import getopt
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], 'r:g:n:o')
    except getopt.GetoptError as err:
        print(str(err))
        run=False
        
    for o, a in opts:
        print(o,a)

        if o in '-r':
            resultsFilename=a;
        if o in '-g':
            geomFilename=a;
        if o in '-n':
            nominalFilename=a;
            outFilename=nominalFilename+'_adjusted'
        if o in '-o':
            outFilename=a;

            
    #filename=args[0]
    #print(args)
    if(run):
        print('Reading geometry')
        feamesh=readGeom(geomFilename)
        print('Reading results')
        readResults(resultsFilename,feamesh)
        print('Reading STL')
        stlmesh=readSTL(nominalFilename)
        print('Adjusting STL')
        adjustSTL(outFilename,feamesh,stlmesh,scale=1,power=4)
    
    
