#!/usr/bin/env python3

import fea
import numpy as np
import stltovoxel
import stltovoxel.stl_reader
from stltovoxel import slice
from stltovoxel import util
def readVoxels(inputFilePath,resolution=90):
    
    mesh = list(stltovoxel.stl_reader.read_stl_verticies(inputFilePath))
    (scale, shift, bounding_box) = stltovoxel.slice.calculateScaleAndShift(mesh, resolution)
    mesh = list(slice.scaleAndShiftMesh(mesh, scale, shift))
    #Note: vol should be addressed with vol[z][x][y]
    vol = np.zeros((bounding_box[2],bounding_box[0],bounding_box[1]), dtype=bool)
    for height in range(bounding_box[2]):
        print('Processing layer %d/%d'%(height+1,bounding_box[2]))
        lines = slice.toIntersectingLines(mesh, height)
        prepixel = np.zeros((bounding_box[0], bounding_box[1]), dtype=bool)
        stltovoxel.perimeter.linesToVoxels(lines, prepixel)
        vol[height] = prepixel
    vol, bounding_box = util.padVoxelArray(vol)
    return (vol,bounding_box,scale,shift)

def writeMesh(mesh,filename):
    file=open(filename,'w')
    file.write('*NODE,nset=all\n')
    for node in mesh.nodes.values():
        file.write(str(node.num))
        for c in node.coord:
            file.write(','+str(c))
        file.write('\n')
    if mesh.linear:    
        file.write('*ELEMENT, type=C3D8, elset=all\n')
    else:
        file.write('*ELEMENT, type=C3D20R, elset=all\n')
        
    for element in mesh.elements.values():
        file.write(str(element.num))
        i=0
        j=0
        file.write(',')
        for n in element.nodes:
            
            file.write(str(n))
            i+=1
            j+=1
            if j<20:
                file.write(',')
            if i>14:
                file.write('\n')
                i=0
            
        file.write('\n')
    
    for sset in mesh.nsets.keys(): #print all node sets
        file.write('*nset,nset='+sset+'\n')
        for num in mesh.nsets[sset]:
            file.write(str(num)+'\n')
    
    for sset in mesh.esets.keys(): #print all element sets
        file.write('*elset,elset='+sset+'\n')
        for num in mesh.esets[sset]:
            file.write(str(num)+'\n')
    
 
    #Add a bed of weak beams under the plate
    beamNodePairs=[]
    shift=30
    file.write('*node,nset=nodeBed\n')
    for n in mesh.nsets['interface']:
        node=mesh.getNode(n)
        newNum=mesh.addNode((node.coord[0],node.coord[1],node.coord[2]-shift))
        newNode=mesh.getNode(newNum)
        beamNodePairs.append([n,newNum])
        file.write(str(newNum)+','+str(newNode.coord[0])+','+str(newNode.coord[1])+','+str(newNode.coord[2])+'\n')
    
    file.write('*element,TYPE=B31,elset=beamBed\n')
    enumStart=mesh.highestElementNumber+1
    i=0
    for p in beamNodePairs:
        file.write(str(enumStart+i)+','+str(p[0])+','+str(p[1])+'\n')
        i+=1
 
    
    '''
    #lock three nodes L1,L2,L3 in the center of the build plate
    X=set()
    Y=set()
    for n in mesh.nsets['buildBottom']:
        node=mesh.getNode(n)
        X.add(node.coord[0])
        Y.add(node.coord[1])
    
    if len(X)%2==0: #if the sets of coordinates contain an even number of elements remove the last one
        X.remove(max(X))
    if len(Y)%2==0:
        Y.remove(max(Y))
    
    OneNodeCoord=[np.median(list(X)),np.median(list(Y))]
    print('OneNodeCoord',OneNodeCoord)
    Z=node.coord[2]
    tol=1e-5
    nodeswithin=mesh.getNodesWithIn(OneNodeCoord[0]-tol,OneNodeCoord[0]+tol,OneNodeCoord[1]-tol,OneNodeCoord[1]+tol,Z-tol,Z+tol)[0]
    #nodeswithin=mesh.getNodesWithIn(OneNodeCoord[0]-tol,OneNodeCoord[0]+tol,OneNodeCoord[1]-tol,OneNodeCoord[1]+tol,-10000000,100000000)[0]
    
    OneNode=mesh.getNode(nodeswithin)
    belongsToElem=mesh.getElement(mesh.getElementsWithNode(OneNode.num)[0]) #first element connected to L1
    bottomNodes=belongsToElem.getFace(2)
    file.write('*NSET,NSET=L1\n')
    file.write(str(bottomNodes[0])+'\n')
    file.write('*NSET,NSET=L2\n')
    file.write(str(bottomNodes[1])+'\n')
    file.write('*NSET,NSET=L3\n')
    file.write(str(bottomNodes[2])+'\n')
    '''
    
    file.close()

def writeSteps(layers,startLayer,filename,dwell,conductivity,temp,mesh,powderTemp,conductivityPowder,heating,onlyHeat=False,creep=True):
    file=open(filename,'w')
    step=0
    for i in range(startLayer,layers+1):
        step+=3
        file.write("""**------------------------- Step """+str(step) +"""---------------------------------------------""")
        file.write("""
*Step,INC=1000
*VISCO,CETOL=1e-1
1e-4,"""+str(dwell)+""",1e-10,
**
""")
        file.write("""
*MODEL CHANGE,TYPE=ELEMENT,ADD 
layer_"""+str(i+1))
        
        file.write("""
*End Step
** 
** 
*Step,INC=1000
*HEAT TRANSFER,DELTMX=500
1e-2,"""+str(dwell)+""",1e-10,
**""")

        if i < layers: #dont do this for more layers than exist in model
            file.write("""
*DFLUX,OP=NEW
layer_"""+str(i+1)+',S6,'+str(heating)+"""
""")
        #write film BC 
        
        surf=mesh.getSurfaceElementsWithFaces()
        '''
        file.write('\n*FILM,OP=NEW\n')
        for s in surf.keys():
            for f in surf[s]:
                if not ((s in mesh.esets['buildPlateElements']) and (f==1)): #the bottom of the build plate may have a different condition
                    file.write(str(s)+',F'+str(f)+','+str(powderTemp)+','+str(conductivityPowder)+'\n')
        ''' 
        file.write('\n*FILM\n')          
        file.write('bottomElements,F1'+','+str(temp)+','+str(conductivity)+'\n')
    
        file.write("""
*End Step""")
        if not onlyHeat:
            file.write("""
*Step,INC=1000
*STATIC,TIME RESET
1e-0,"""+str(dwell)+""",1e-10,
*End Step
""")
 
    file.close()
    
def readParameters(filename):
    parameters={}
    file=open(filename,'r')
    for line in file:
        #print(line)
        try:
            p=line.split('=')[0]
            v=line.split('=')[1]

            if p=='resolution':
                parameters['resolution']=int(v)
            elif p=='comment':
                parameters[p]=v
            else:
                parameters[p]=float(v)
        except:
            pass
        
    return(parameters)
    
    
def run(parameters,name,dir_path,creep=True):
    import uuid
    uid=str(uuid.uuid4())
    (vol,bounding_box,scale,shift)=readVoxels(name,parameters['resolution'])
    
    layerThickness=1/scale[2]
    dwell=layerThickness/parameters['speed']
    
    mesh=fea.mesh([],[]) #create empty mesh

    mesh.createEmptyWebofSectors([0,bounding_box[0]/scale[0]],[0,bounding_box[1]/scale[1]],[0,bounding_box[2]/scale[2]])
    
    totalLayers=0
    print('Generating mesh...')
    for k in range(bounding_box[2]):
        totalLayers+=1
        print('layer '+str(k+1)+' / '+str(bounding_box[2]))
        for j in range(bounding_box[1]):
            for i in range(bounding_box[0]):
                if vol[k][i][j]==True:
                    x=(i-1)/scale[0]-shift[0]
                    y=(j-1)/scale[1]-shift[1]
                    z=(k-1)/scale[2]-shift[2]
                    num=mesh.createAndAddElement([x,y,z],[1/scale[0],1/scale[1],1/scale[2]])

                    mesh.add2elset(num,'layer_'+str(k-1))
                    enodes=mesh.getElement(num).nodes
                    for n in enodes:
                        mesh.add2nset(n,'layer_'+str(k-1))
    
    quad=False
    if quad:
        print("Replacing linear elements with quadratic ones")
        mesh.quad()
        mesh.update()
    
    print(('nodes',len(mesh.nodes)))
    print(('elements',len(mesh.elements)))

    
    zmin=1e9
    for n in mesh.nodes:
        node=mesh.getNode(n)
        if zmin>node.coord[2]:
            zmin=node.coord[2]


    #Identify the build plate
    Zs=[n.coord[2] for n in mesh.nodes.values()]
    zmin=min(Zs)
    Ys=[n.coord[1] for n in mesh.nodes.values()]
    ymin=min(Ys)
    ymax=max(Ys)
    Xs=[n.coord[0] for n in mesh.nodes.values()]
    xmin=min(Xs)
    xmax=max(Xs)
    
    
    xmins=mesh.getNodesWithIn(xmin-1e-5,xmin+1e-5,-1000000000,100000000,-1000000000,100000000000)
    zmax=-100000000
    for node in xmins: #find the largest z in the xmins nodes
        x=mesh.getNode(node).coord[0]
        z=mesh.getNode(node).coord[2]
        if z>zmax:
            zmax=z
    

    boxSize=[xmax-xmin,ymax-ymin,zmax-zmin]
    
    topOfBuild=-10000000000
    for n in mesh.nodes:
        node=mesh.getNode(n)
        if topOfBuild<node.coord[2]:
            topOfBuild=node.coord[2]
    
    buildBottom=mesh.getNodesWithIn(-1000000000,100000000000,-1000000000,100000000000,+zmin+boxSize[2]-1e-5,+zmin+boxSize[2]+1e-5)
    buildPlate=mesh.getNodesWithIn(-1000000000,100000000000,-1000000000,100000000000,zmin-1e-5,zmin+boxSize[2]+1e-5)
    buildPlateElements=mesh.getElementsWithNodes(buildPlate,any=True)
    top=mesh.getNodesWithIn(-1000000000,100000000000,-1000000000,100000000000,topOfBuild-1e-5,topOfBuild+1e-5)
    
    
    bottomNodes=mesh.getNodesWithIn(-1000000000,100000000000,-1000000000,100000000000,zmin-1e-5,zmin+1e-5) #the very bottom nodes of the plate

    layersInPlate=int(np.round((zmax-zmin)*scale[2]))

    bottomElements=mesh.getElementsWithNodes(bottomNodes,any=True)
    print('layersInPlate '+str(layersInPlate)+' zspan '+str(zmax-zmin)+' scale '+str(scale[2]))
    interface=list(set(buildPlate) & set(mesh.nsets['layer_'+str(layersInPlate)]))
    build=list(set(mesh.nodes)-set(buildPlate))
    buildElements=mesh.getElementsWithNodes(build,any=True)
    buildPlateElements=list(set(mesh.getElementsWithNodes(buildPlate,any=True))-set(mesh.getElementsWithNodes(build,any=True)))
    
    for n in buildBottom:
        mesh.add2nset(n,'buildBottom')
    
    for n in top:
        mesh.add2nset(n,'top')
    
    for n in buildPlate:
        mesh.add2nset(n,'buildPlate')
    
    for e in buildPlateElements:
        mesh.add2elset(e,'buildPlateElements')
        
    for e in bottomElements:
        mesh.add2elset(e,'bottomElements')
        
    for n in build:
        mesh.add2nset(n,'build')
    
    
    for e in buildElements:
        mesh.add2elset(e,'buildElements')
    
    for n in interface:
        mesh.add2nset(n,'interface')
        
    for n in bottomNodes:
        mesh.add2nset(n,'bottomNodes')
        
    mesh.createWebofSectors(d1=37,d2=43)
            
    

    
    import shutil
    import os
    filename=os.path.basename(name)
    print('filename',filename)
    directory=filename+'_'+uid
    if not os.path.exists(directory):
        os.makedirs(directory)
        cwd=os.getcwd()

    
    parseInput(os.path.normpath(dir_path+'/am.inp'),os.path.normpath(directory+'/am.inp'),parameters)
    shutil.copy(os.path.normpath(name),os.path.normpath(directory+'/'))
    
    try: #parameter file may not exist   
        shutil.copy(os.path.normpath(name+'.par'),os.path.normpath(directory+'/'+name+'.par'))
    except:
        pass
    
    
    writeMesh(mesh,os.path.normpath(directory+'/geom.inp'))
    writeSteps(layers=totalLayers-4,startLayer=layersInPlate-1,filename=os.path.normpath(directory+'/steps.inp'),dwell=dwell,conductivityPowder=parameters['conductivityPowder'],conductivity=parameters['sinkCond'],temp=parameters['sinkTemp'],onlyHeat=False,mesh=mesh,powderTemp=parameters['powderTemp'],heating=parameters['heating'],creep=creep)

    return (directory,mesh)

def parseInput(infilename,outfilename,parameters): #read infile and replace all parameters with actual numbers
    workfile = None
    with open(infilename, 'r') as file :
      workfile = file.read()

    # replace paremeters with actual numbers
    for key in parameters.keys():
        print(key+','+str(parameters[key]))
        workfile = workfile.replace('#'+key,str(parameters[key]))

    # Write the file
    with open(outfilename, 'w') as file:
      file.write(workfile)

def calc(directory,cpus=1): #Run calculix.
    print('Solving..')
    import os
    os.chdir(directory)
    os.environ['OMP_NUM_THREADS']=str(cpus)
    os.system('ccx am > ccx_output.txt')
    os.chdir('../')
    
if __name__ == "__main__":
    print("""
    ------------------------------------------------
    |                    FAME                      |
    ------------------------------------------------
    """)
    import getopt,sys,os,shutil
    
    creep=True
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], 'i:p:c:')
    except getopt.GetoptError as err:
        print(str(err))
        run=False
    cpus=1
    for o, a in opts:
        print(o,a)
        if o in '-i':
            name=a
        if o in '-p':
            parameterFilename=a;
        if o in '-c':
            cpus=int(a)
    
    if 'nocreep' in args:
        creep=False
        print('No creep steps')
    
    if 'noadjust' in args:
        scale=-1
    else:
        scale=1

    
    dir_path = os.path.dirname(os.path.realpath(__file__)) #directory where the FAME.py file resides

    parameters=readParameters(parameterFilename)
    (directory,mesh)=run(parameters,name,dir_path,creep)
    calc(directory=directory,cpus=cpus)

    import post
    post.readResults(os.path.normpath(directory+'/am.frd'),mesh)
    stlmesh=post.readSTL(name)
    print('Adjusting STL')
    resultPath=os.path.relpath(directory+'/'+os.path.basename(name)[:-4])
    post.adjustSTL(resultPath,mesh,stlmesh,scale=scale,power=3)
    

    shutil.copy(os.path.relpath(directory+'/'+os.path.basename(name)[:-4]+'_adjusted.stl'),os.path.relpath(os.path.basename(name)[:-4]+'_adjusted.stl'))
        
