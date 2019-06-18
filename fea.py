
''' 
This file is part of the FAME distribution https://github.com/Swerim/FAME).
Copyright (c) 2019 Swerim.

This program is free software: you can redistribute it and/or modify  
it under the terms of the GNU General Public License as published by  
the Free Software Foundation, version 3.
 *
This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
General Public License for more details.

You should have received a copy of the GNU General Public License 
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''


import numpy as np
import itertools

import bisect

def snapDown(intvals,x):
    #print intvals,x
    i = bisect.bisect_right(intvals,x)
    return intvals[i-1:i][0]



def findsubsets(S,m): #get all subsets of S with length m
    return set(itertools.combinations(S, m))

def unique(seq):
   # Not order preserving
   keys = {}
   for e in seq:
       keys[e] = 1
   return list(keys.keys())

class node:
    def __init__(self,num,coord):
        self.coord=coord
        self.num=num
        self.disp=[0,0,0]
        self.temp=0
    def getDefCoord():
        return np.add(self.coord,self.disp)
        
class element:
    def __init__(self,num,nodes):
        self.num=num
        self.nodes=nodes
        #elment faces
        
        self.opposite={1:2,2:1,3:5,5:3,4:6,6:4} #the element faces opposing each other
        self.connectedNodes={1:[2,5,4],2:[1,6,3],3:[2,7,4],4:[3,8,1],5:[1,6,8],6:[5,2,7],7:[6,3,8],8:[5,7,4]}
        
        self.toBeDeleted=False #element to be deleted next update
    
    def getFace(self,i): #return node set of face based on face number
        faces=[]
        nodes=self.nodes
        faces.append([nodes[0],nodes[1],nodes[2],nodes[3]]) #1234 f1
        faces.append([nodes[4],nodes[5],nodes[6],nodes[7]]) #5678 f2
        faces.append([nodes[0],nodes[4],nodes[5],nodes[1]]) #1562 f3
        faces.append([nodes[1],nodes[2],nodes[6],nodes[5]]) #2376 f4
        faces.append([nodes[3],nodes[7],nodes[6],nodes[2]]) #4873 f5
        faces.append([nodes[0],nodes[3],nodes[7],nodes[4]]) #1485 f6
        if i==0:
            return faces
        return faces[i-1]
        
    def getAFace(self,nodes): #from a list of nodes find first valid face
        for f in self.getFace(0): #all faces
            if set(f)<=set(nodes): #if we found the sought after face
                return (f,self.getFace(0).index(f)+1)        
    
    def getAllValidFaces(self,nodes): #from a list of nodes return all valid faces
        faces=[]
        for f in self.getFace(0): #all faces
            if set(f)<=set(nodes): #if we found the a face
                faces.append(f)
        return faces
    
    def getFacesWithNodes(self,nodes): #return list of faces that contain the nodes (numbers)
        faces=[]
        for f in self.getFace(0): #all faces
            if set(f)>=set(nodes): #if we found the a face
                faces.append(f)
        return faces
    
    def matchFace(self,nodes): #match unsorted node list with element face. Return the ordered face nodes
        for f in self.getFace(0): #all faces
            if set(f)==set(nodes): #if we found the sought after face
                return (f,self.getFace(0).index(f)+1)        
            
    def getOppositeFace(self,face): #get the node set of the oppisite face
        i=0
        for f in self.getFace(0):
            i+=1
            if set(f)==set(face): #if we found the sought after face
                opposite=self.opposite[i]
                return self.matchFace(self.getFace(opposite))
    
    def getOppositeNode(self,i,f): #given a node number i and a face set get the the opposing node
        (oppositeFace,index)=self.getOppositeFace(f)
        connectedNodes=self.getConnectedNodes(i)
        n=list(set(connectedNodes) & set(oppositeFace))[0]
        return n
    
    
    def getConnectedNodes(self,i):#get nodes connected to a certain node within this element
        cn=[]
        nodePos=self.nodes.index(i)+1
        nodePositions=self.connectedNodes[nodePos]
        for n in nodePositions:
            cn.append(self.nodes[n-1])
        return cn
    
    def getSides(self): #return array of tuple of node numbers representing the 12 sides of the element
        sides=[]
        sides.append((self.nodes[0],self.nodes[1]))
        sides.append((self.nodes[1],self.nodes[2]))
        sides.append((self.nodes[2],self.nodes[3]))
        sides.append((self.nodes[3],self.nodes[0]))
        
        sides.append((self.nodes[4],self.nodes[5]))
        sides.append((self.nodes[5],self.nodes[6]))
        sides.append((self.nodes[6],self.nodes[7]))
        sides.append((self.nodes[7],self.nodes[4]))
        
        sides.append((self.nodes[0],self.nodes[4]))
        sides.append((self.nodes[1],self.nodes[5]))
        sides.append((self.nodes[2],self.nodes[6]))
        sides.append((self.nodes[3],self.nodes[7]))
        return sides
        

        
class mesh:
    def __init__(self,nodes,elements,tol=3e-5,d1=13,d2=17,margin=0.0):
        self.tol=tol
        self.highestNodeNumber=0
        self.highestElementNumber=0
        self.nodes={}
        self.elements={}
        for n in nodes:
            self.nodes[n.num]=n
            if n.num>self.highestNodeNumber:
                self.highestNodeNumber=n.num
        for e in elements:
            self.elements[e.num]=e
            if e.num>self.highestElementNumber:
                self.highestElementNumber=e.num
        self.nsets={}
        self.esets={}
        self.linear=True
       
        self.update()
            
        if len(self.nodes)>0: #only if nodes and elements are already defined
            self.createWebofSectors(d1,d2,margin)
    
    def quad(self): #replace all elements with quadratic ones
        self.linear=False
        for enum in self.elements: #for all elements
            e=self.getElement(enum)
            #print('-------')
            #print(enum)
            for s in e.getSides(): #do this for every side in element e
                
                coord0=self.getNode(s[0]).coord
                coord1=self.getNode(s[1]).coord
                num=self.addNode([(coord0[0]+coord1[0])/2,(coord0[1]+coord1[1])/2,(coord0[2]+coord1[2])/2],merge=True)
                e.nodes.append(num)
                
                
                try: #add element to elemWithNum
                    self.elemWithNode[num].append(enum)
                except(KeyError):
                    self.elemWithNode[num]=[enum]

            #print(e.nodes)
            #for nnum in e.nodes:
            #    print(self.getNode(nnum).coord)
            
    def add2elset(self,num,set):
        if set not in self.esets:
            self.esets[set]=[num]
        else:
            self.esets[set].append(num)
    
    def add2nset(self,num,set):
        if set not in self.nsets:
            self.nsets[set]=[num]
        else:
            self.nsets[set].append(num)
            
    def update(self):
        self.elemWithNode={}
        for e in self.elements.values():
            for n in e.nodes: #assemble dictionary of what elements are connected to a certain node
                if n not in self.elemWithNode:
                    self.elemWithNode[n]=[e.num]
                else:
                    self.elemWithNode[n].append(e.num)


    def createWebofSectors(self,d1=13,d2=17,margin=0):
        x=[n.coord[0] for n in self.nodes.values()]
        y=[n.coord[1] for n in self.nodes.values()]
        z=[n.coord[2] for n in self.nodes.values()]
        self.web1=webOfSectors([min(x),min(y),min(z)],max([max(x)-min(x),max(y)-min(y),max(z)-min(z)]),d1,margin)
        self.web2=webOfSectors([min(x),min(y),min(z)],max([max(x)-min(x),max(y)-min(y),max(z)-min(z)]),d2,margin)
        for n in self.nodes.values():
            self.web1.addNode(n)
            self.web2.addNode(n)
            
    def createEmptyWebofSectors(self,x,y,z,d1=13,d2=17): #create web of sector based on size. Can be used if no mesh has been defined. x = [xmin,xmax] y=[ymin,ymax] z=[zmin,zmax]
        self.web1=webOfSectors([min(x),min(y),min(z)],max([max(x)-min(x),max(y)-min(y),max(z)-min(z)]),d1)
        self.web2=webOfSectors([min(x),min(y),min(z)],max([max(x)-min(x),max(y)-min(y),max(z)-min(z)]),d2)
        
    def getNode(self,num):
        return self.nodes[num]
    
    def getElement(self,num):
        return self.elements[num]
    
    def getElementsWithNode(self,num):
        try:
            e=self.elemWithNode[num]
            return e
        except:
            return []
    
    def getElementsWithNodes(self,nums,any=False): #return elements who has all the nodes in nums. If any than return all elements connected to the specified nodes
        candidates=[] #all elements with a node in nums
        toReturn=[]
        for n in nums:
            candidates+=self.getElementsWithNode(n)
        candidates=unique(candidates)
        if any:
            return candidates
        for enum in candidates:
            e=self.getElement(enum)
            if set(nums) > set(e.nodes): #if the sought after node numbers is a subset of the element nodes
                toReturn.append(enum)
        return unique(toReturn)
    
    def getElementsConnectedToElement(self,num): #get element numbers of all elements connected to element with number num
        elist=[] #list to be returned
        e=self.getElement(num)
        nodes=e.nodes #node numbers of the current element
        for n in nodes:
            elist+=self.getElementsWithNode(n)
        elist=unique(elist)
        index=elist.index(num)
        del elist[index] #remove self from list
        return elist
    
    def isSurfaceElem(self,num):
        e=self.getElement(num)
        e.surfaceNodes=[]
        for f in e.getFace(0): #get all element faces
            if len(self.getElementsWithNodes(f)) == 1:
                e.surfaceNodes=f

                return True 
        return False
    
    # Doesn't include element with just one or two nodes on the surface
    def getFullFaceSurfaceElements(self):
        surf=[]
        for e in self.elements.values():
            if self.isSurfaceElem(e.num):
                surf.append(e.num)
        return surf
    
    #get surface elements and their surface faces
    def getSurfaceElementsWithFaces(self):
        surfElements=self.getFullFaceSurfaceElements() #all surface elements
        surfElementsDic={} #dictionary of all surface elements and their surface face numbers (FEA numbering)
        for enum in surfElements:
            surfFaces=[] #all surface faces of this element
            faces=self.getElement(enum).getFace(0) #all faces of element enum
            i=0
            for f in faces:
                i+=1
                if len(self.getElementsWithNodes(f))==1: #if these nodes are only connected to one element then this face is on the surface
                    surfFaces.append(i)
            surfElementsDic[enum]=surfFaces
        return surfElementsDic
    
    def getSurfaceElements(self): #get all element who has a node on the surface
        surf=[]
        surfaceNodes=set(self.getSurfaceNodes())
        
        for e in self.elements.values():
            if len(set(e.nodes) & surfaceNodes)>0: #is the element has any nodes part of the global set surfaceNodes
                surf.append(e.num)
        return surf
    
 
    def getSurfaceNodes(self):
        surfNodes=[]
        for e in self.elements.values():
            if self.isSurfaceElem(e.num):
                surfNodes+=e.surfaceNodes
        return unique(surfNodes)
    
    def addNode(self,coord,merge=True): #create and add a new node to the mesh.
        self.highestNodeNumber+=1
        number=self.highestNodeNumber
        
        n=node(number,coord)
        self.nodes[number]=n
        
        try:
            self.web1.addNode(n) #also add it to the appropriate sector
            self.web2.addNode(n) #also add it to the appropriate sector
        except AttributeError:
            pass
        
        if merge:
            self.mergeWithCoincidentNodes(n,self.tol)
        
        return number
    
    def addElement(self,nodes): #add element to mesh
        self.highestElementNumber+=1
        number=self.highestElementNumber
        
        
        e=element(number,nodes)
        self.elements[e.num]=e

        for i in nodes:
            if i in self.elemWithNode:
                self.elemWithNode[i].append(number)

            else:
                self.elemWithNode[i]=[number]

        return number
    
    def getnSet(self,setname):# get members of node set
        try:
            nset=self.nsets[setname]
            return nset
        except(KeyError):
            print('Warning. No such node set: '+setname)
            return []
        
    def geteSet(self,setname):# get members of element set
        try:
            elset=self.esets[setname]
            return elset
        except(KeyError):
            print('Warning. No such element set: '+setname)
            return []
                
    def collapseElement(self,e,eSurfNodes):
        #1st pair
        if len(eSurfNodes)==2:
            for surfNode in eSurfNodes:
                n=self.getNode(surfNode)
                nodesToMerge=list(set(e.getConnectedNodes(surfNode))-set(eSurfNodes))
                n1=self.getNode(nodesToMerge[0])
                n2=self.getNode(nodesToMerge[1])
                newCoord=[(n1.coord[0]+n2.coord[0])/2,(n1.coord[1]+n2.coord[1])/2,(n1.coord[2]+n2.coord[2])/2]
                n1.coord=newCoord
                n2.coord=newCoord

        elif len(eSurfNodes)==1:
            n=self.getNode(surfNode)
            nodesToMerge=e.getConnectedNodes(surfNode)
            n1=self.getNode(nodesToMerge[0])
            n2=self.getNode(nodesToMerge[1])
            n3=self.getNode(nodesToMerge[2])
            newCoord=[(n1.coord[0]+n2.coord[0]+n3.coord[0])/3,(n1.coord[1]+n2.coord[1]++n3.coord[0])/3,(n1.coord[2]+n2.coord[2]++n3.coord[0])/3]
            n1.coord=newCoord
            n2.coord=newCoord
            n3.coord=newCoord
            print('collapsing element',e.num,'with surf nodes',eSurfNodes)
        elif len(eSurfNodes)==5:

            A=list(set(eSurfNodes)-set(e.getAFace(eSurfNodes)[0]))
            B=e.getConnectedNodes(A[0])
            C=list(set(B) & set(e.getAFace(eSurfNodes)[0]))
            
            splitNodes=list(set(C) | set(A))

            for surfNode in splitNodes:
                n=self.getNode(surfNode)
                nodesToMerge=list(set(e.getConnectedNodes(surfNode))-set(splitNodes))
                n1=self.getNode(nodesToMerge[0])
                n2=self.getNode(nodesToMerge[1])
                newCoord=[(n1.coord[0]+n2.coord[0])/2,(n1.coord[1]+n2.coord[1])/2,(n1.coord[2]+n2.coord[2])/2]
                n1.coord=newCoord
                n2.coord=newCoord
        self.deleteElement(e.num)        
        
    def splitElement(self,e,eSurfNodes,layers,depth): #split an element. Input element instance, list of node numbers on the surface, no layers and depth. Return element (numbers) of new elements.
        newElements=[]
        layers+=1
        
        (eSurfNodes,faceNumber)=e.matchFace(eSurfNodes)
        (oppFace,oppFaceNumber)=e.getOppositeFace(eSurfNodes)
        
        e1=np.array(self.getNode(eSurfNodes[1]).coord)-np.array(self.getNode(eSurfNodes[0]).coord)
        e2=np.array(self.getNode(eSurfNodes[2]).coord)-np.array(self.getNode(eSurfNodes[0]).coord)
        elementDir=np.cross(e1,e2)
        elementDir=elementDir/np.linalg.norm(elementDir)
        
        v1=np.array([0,0,0])
        newNodes=[]
        for n in eSurfNodes:
            #positive direction of element (normal to the surface


            
            n1=np.array(self.getNode(n).coord)
            n2=np.array(self.getNode(e.getOppositeNode(n,eSurfNodes)).coord)

            if np.linalg.norm(n2-n1)<depth: #check if element is thick enought to be split
                print('Error. Layers are deeper than element thickness. Start with coarser mesh or decrease layer depth')
                return newElements
            v1=(n2-n1)/np.linalg.norm(n2-n1)
            
            projection=1
  
            newNodeCoords=[v1*scalar*projection+n1 for scalar in np.linspace(0,depth,layers)[1:]]

            for c in newNodeCoords:
                nodeNum=self.addNode(c)
                newNodes.append(nodeNum)
                if 'split' in self.nsets:
                    self.nsets['split'].append(nodeNum)
                else:
                    self.nsets['split']=[nodeNum]

        nodesOnLayers=[eSurfNodes]
        for i in range(layers-1):
            nodesOnLayers.append(newNodes[i::layers-1]) #add every layerth-1 node from newNodes
        nodesOnLayers.append(oppFace) #add other side of the old element   
        
        for i in range(layers):
            if(np.inner(elementDir,v1)>0):
                enum=self.addElement(nodesOnLayers[i]+nodesOnLayers[i+1])
            else:
                enum=self.addElement(nodesOnLayers[i+1]+nodesOnLayers[i])
            newElements.append(enum)
        
        return newElements
        

        
    def splitElements(self,layers,depth):
        self.layers=layers
        surfaceElements=self.getSurfaceElements()
        surfaceNodes=self.getSurfaceNodes()
        
        
        for enum in surfaceElements: #first collapse all surface elements with less than 3 nodes on the surface
            e=self.getElement(enum)
            eSurfNodes=list((set(e.nodes) & set(surfaceNodes)))
            
            if len(eSurfNodes)<3: #only two or less nodes on the surface
                #collapse element
                self.collapseElement(e,eSurfNodes)
            
            if len(eSurfNodes)==5:
                self.collapseElement(e,eSurfNodes)

        surfaceElements=self.getSurfaceElements()
        surfaceNodes=self.getSurfaceNodes()

        self.mergeCoincidentNodes(self.tol)
        
        surfaceElements=self.getSurfaceElements()
        surfaceNodes=self.getSurfaceNodes()
        counter=0
        
        for enum in surfaceElements:
            counter+=1
            e=self.getElement(enum)
            eSurfNodes=list((set(e.nodes) & set(surfaceNodes)))
            
            if len(eSurfNodes)==4: #one whole side on the surface
                self.splitElement(e,eSurfNodes,layers,depth)
                self.deleteElement(enum)
                


            elif len(eSurfNodes)==6: #two faces  on surface
                faces=e.getAllValidFaces(eSurfNodes)
                new=self.splitElement(e,faces[0],layers,depth)
                #find start face of split of new[0]
                newSplitFaces=[]
                B=faces[0]
                F=list(set(faces[0]) & set(faces[1]))
                C=[]
                for n in F:
                    C+=self.getElement(new[0]).getConnectedNodes(n)
                C=list(set(C)-set(B))
                E=list(set(F)-set(B))
                A=list(set(F)|set(C))
                A=self.getElement(new[0]).matchFace(A)[0]
                
                newSplitFaces.append(A)
                
                for i in range(layers+1)[1:]: #we don't need to do it for the first element
                    
                    B=self.sharedNodes(new[i-1],new[i])
                    C=list(set(A) & set(B))
                    D=[]
                    for n in C:
                        D+=self.getElement(new[i]).getConnectedNodes(n)
                    E=list(set(D)-set(B))
                    A=list(set(E)|set(C))
                    A=self.getElement(new[i]).matchFace(A)[0]
                    newSplitFaces.append(A)
                    
                for i in range(layers+1):
                    self.splitElement(self.getElement(new[i]),newSplitFaces[i],layers,depth)
                    self.deleteElement(new[i])
                self.deleteElement(enum)
                

            elif len(eSurfNodes)==7: #three faces  on surface
                faces=e.getAllValidFaces(eSurfNodes)
                new=self.splitElement(e,faces[0],layers,depth)
                #find start face of split of new[0]
                newSplitFaces=[]
                B=faces[0]
                F=list(set(faces[0]) & set(faces[1]))
                C=[]
                for n in F:
                    C+=self.getElement(new[0]).getConnectedNodes(n)
                C=list(set(C)-set(B))
                E=list(set(F)-set(B))
                A=list(set(F)|set(C))
                A=self.getElement(new[0]).matchFace(A)[0]
                
                newSplitFaces.append(A)
                
                for i in range(layers+1)[1:]: #we don't need to do it for the first element
                    
                    B=self.sharedNodes(new[i-1],new[i])
                    C=list(set(A) & set(B))
                    D=[]
                    for n in C:
                        D+=self.getElement(new[i]).getConnectedNodes(n)
                    E=list(set(D)-set(B))
                    A=list(set(E)|set(C))
                    A=self.getElement(new[i]).matchFace(A)[0]
                    newSplitFaces.append(A)
                
                new2=[]                
                for i in range(layers+1):
                    new2+=self.splitElement(self.getElement(new[i]),newSplitFaces[i],layers,depth)
                
                #try to find out which face on all the new elements should be used to split with
                nodesOnFaces=[[],[],[],[],[],[]]    
                for e in new2:
                    for i in range(6):
                        nodesOnFaces[i]+=self.getElement(e).getFace(i+1) #faces are numbered 1-6
                faceToStartSplit=-1
                for i in range(6):
                    if set(faces[2])<=set(nodesOnFaces[i]):
                        faceToStartSplit=i+1
                        break
                
                for e in new2:
                    self.splitElement(self.getElement(e),self.getElement(e).getFace(faceToStartSplit),layers,depth)
                
                self.deleteElement(enum)
                for i in range(len(new)):
                    self.deleteElement(new[i])
                for i in range(len(new2)):
                    self.deleteElement(new2[i])
            else:
                print('Error. Don\'t  know how to split this element ('+str(enum)+').',len(eSurfNodes))
        
    def sharedNodes(self,e1,e2): #takes element numbers. Returns node numbers
        elem1=self.getElement(e1)            
        elem2=self.getElement(e2)
        
        n1=elem1.nodes
        n2=elem2.nodes
        
        return list(set(n1) & set(n2))
    def createAndAddElement(self,coord,size): #create and add a new element based on location and size
        n1=self.addNode(coord)
        n2=self.addNode([coord[0]+size[0],coord[1],coord[2]])
        n3=self.addNode([coord[0]+size[0],coord[1]+size[1],coord[2]])
        n4=self.addNode([coord[0],coord[1]+size[1],coord[2]])
        n5=self.addNode([coord[0],coord[1],coord[2]+size[2]])
        n6=self.addNode([coord[0]+size[0],coord[1],coord[2]+size[2]])
        n7=self.addNode([coord[0]+size[0],coord[1]+size[1],coord[2]+size[2]])
        n8=self.addNode([coord[0],coord[1]+size[1],coord[2]+size[2]])
        num=self.addElement([n1,n2,n3,n4,n5,n6,n7,n8])
        return num
    
    def coincident(self,num1,num2,tol): #are the nodes num1 and num2 coincident?
        try:
            n1=self.getNode(num1)
            n2=self.getNode(num2)
            for i in range(3):
                if n1.coord[i]-tol>n2.coord[i] or n1.coord[i]+tol<n2.coord[i]:
                    return False
        except (IndexError,KeyError): #node not available
            return False
        return True
                
    def mergeCoincidentNodes(self,tol):
        import copy
        newNodes=copy.deepcopy(self.nodes) #temporary nodes
        
        counter=0
        replaced=0
        for node in newNodes.values():
            counter+=1
            neighbors=self.web1.getNodesCloseTo(node)
            neighbors+=self.web2.getNodesCloseTo(node)
            neighbors=unique(neighbors)
            for n in neighbors:
                if n!=node.num: #dont compare a node with itself
                    if self.coincident(n,node.num,tol):
                        #print(node.coord)
                        self.replaceNode(node.num,n)

                        replaced+=1
        self.update()
        return replaced
    
    def replaceNode(self,old,new): #replace node old with node new everywhere

        #replace it in sectors
        self.web1.replaceNode(self.getNode(old),self.getNode(new))
        self.web2.replaceNode(self.getNode(old),self.getNode(new))
        
        elemsAffected=self.getElementsWithNode(old)
        for enum in elemsAffected: #update affected elements
            
            elem=self.getElement(enum)
            newNodeList=elem.nodes
            index=elem.nodes.index(old)
            elem.nodes[index]=new
            
            #update elemWithNode dictionary
            try:
                del self.elemWithNode[old]
                self.elemWithNode[new]=elemsAffected
            except:
                pass

        for set in self.nsets.values(): #update all node sets
            try:
                index=set.index(old)
                set[index]=new
            except:
                index=-1
        try:
            self.deleteNode(old) #finally remove the node instance
        except:
            pass
        
        
        
        
        
    def mergeWithCoincidentNodes(self,node,tol): #merge node with all coincident nodes
        replaced=0
    
        neighbors=self.web1.getNodesCloseTo(node)
        neighbors+=self.web2.getNodesCloseTo(node)
        neighbors=unique(neighbors)

        for n in neighbors:
            if n!=node.num: #dont compare a node with itself
                if self.coincident(n,node.num,tol):
                    self.replaceNode(n,node.num)
                    replaced+=1
        return replaced

    def deleteNode(self,num):

        try:
            del self.elemWithNode[num]
        except:
            pass
        
        if self.highestNodeNumber==num: #then we deleted the element with the highest number
            self.highestNodeNumber-=1

            while True:
                try:
                    self.nodes[self.highestNodeNumber]
                    break
                except:
                    self.highestNodeNumber-=1
        try:
            del self.nodes[num]
        except:
            pass
    
    def deleteElement(self,num):
        nodes=self.elements[num].nodes
        del self.elements[num]
        if self.highestElementNumber==num: #then we deleted the element with the highest number
            self.highestElementNumber-=1

            while True:
                try:
                    self.elements[self.highestElementNumber]
                    break
                except:
                    self.highestElementNumber-=1
        for n in nodes:
            try:
                index=self.elemWithNode[n].index(num)
            except:
                pass
            try: 
                del self.elemWithNode[n][index]
            except:
                pass
        
    def huntLoneNodes(self):
        oldNoNodes=len(self.nodes)
        newNodes={} #temporary nodes
        for n in self.nodes.values():
            if not(len(self.getElementsWithNode(n.num))==0):
                newNodes[n.num]=self.nodes[n.num]
                
        
        return oldNoNodes-len(newNodes)
                
    def addElementsToSets(self): #add nodes and elments to sets
        self.esets['surface']=self.getFullFaceSurfaceElements()
        self.nsets['surface']=self.getSurfaceNodes()
        self.esets['layer-0']=self.getFullFaceSurfaceElements()
        layers=[self.getFullFaceSurfaceElements()]
        
        for i in range(1,self.layers):
            connected=[]
            for enum in layers[i-1]:
                connected+=(self.getElementsConnectedToElement(enum))
            connected=unique(connected) #remove duplicates
            nextSet=set(connected)
            for layer in layers:
                nextSet=nextSet-set(layer)
            layers.append(list(nextSet))
            self.esets['layer-'+str(i)]=layers[i]
            
    def getNodesWithIn(self,x1,x2,y1,y2,z1,z2): #returns list of node numbers located in box defined by xyz
        toReturn=[]
        for num in self.nodes:
            n=self.getNode(num)
            if n.coord[0]>x1 and n.coord[0]<x2 and n.coord[1]>y1 and n.coord[1]<y2 and n.coord[2]>z1 and n.coord[2]<z2 :
                toReturn.append(n.num)
        return toReturn
            
         

class sector:
    def __init__(self,coord,nodes,number):
        self.coord=coord
        self.nodes=nodes #node Numbers
        self.number=number
    
    def getNodes(self):
        return self.nodes
    
    def addNode(self,n):
        try:
            self.nodes.index(n)
        except ValueError:
            self.nodes.append(n)
    
class webOfSectors:
    def __init__(self,origin,size,div,margin=0): #generate a web of sectors
        self.sectors={}
        self.xs=[]
        self.ys=[]
        self.zs=[]
        
        origin=[origin[0]-size*margin,origin[1]-size*margin,origin[2]-size*margin]
        size=size*(1+margin*2)
        
        i=0
##        for x in np.linspace(origin[0]-size*0.1,origin[0]+size*1.1,div):
##            for y in np.linspace(origin[1]-size*0.1,origin[1]+size*1.1,div):
##                for z in np.linspace(origin[2]-size*0.1,origin[2]+size*1.1,div):
        for x in np.linspace(origin[0]-size,origin[0]+size,div):
            for y in np.linspace(origin[1]-size,origin[1]+size,div):
                for z in np.linspace(origin[2]-size,origin[2]+size,div):
                    self.sectors[(x,y,z)]=sector([x,y,z],[],i)
                    self.xs.append(x)
                    self.ys.append(y)
                    self.zs.append(z)
                    i+=1
        self.size=size

    def getNodesInSector(self,coord):
        s=self.sectors[tuple(coord)]
        return s.nodes
    
    def getSectorAt(self,coord): #which sector is at this coordinate?
        x=snapDown(self.xs,coord[0])
        y=snapDown(self.ys,coord[1])
        z=snapDown(self.zs,coord[2])

        return self.sectors[(x,y,z)]
    
    def addNode(self,n): #add a node (number) to the appropriate sectors. (node instance as input
        s=self.getSectorAt(n.coord)
        s.addNode(n.num)
        
    def getNodesCloseTo(self,n):
        coord=n.coord
        sec=self.getSectorAt(coord)
        s=sec.getNodes()
        s=unique(s)
        found=s.sort()
        return s
    
    def getNodesCloseToCoord(self,coord):
        sec=self.getSectorAt(coord)
        s=sec.getNodes()
        s=unique(s)
        found=s.sort()
        return s    
    
    def printSectors(self):
        for s in self.sectors.values():
            print('s.coord',s.coord)
            print('nodes',s.nodes)
    
    def replaceNode(self,old,new): #needs the node objects
        sec=self.getSectorAt(old.coord)
        sec.nodes[sec.nodes.index(old.num)]=new.num
        sec.nodes=unique(sec.nodes)
        
