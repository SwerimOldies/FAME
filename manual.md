#FAME Manual
##What is FAME?
FAME (Free Additive Manufacturing Enhancer) is a tool that takes a geometry .stl-file, simulates the AM build process and outputs an adjusted .stl-file in order to minimise the thermally induced distortions.

##Installation
There are different ways of installing FAME. Either you clone the project 
''git clone --recursive https://github.com/swerea/fame.git" or you install the .deb-file under releases "https://github.com/Swerea/FAME/releases" (Debian derivatives only).
##Dependencies
FAME relies on the following packages:

* python3
* python3-pil
* python3-numpy
* numpy-stl (installed with pip3)
* calculix-ccx
* pyqt4

###Linux
Either download the .deb-file and install or clone the package and install all the packages mentioned above. You can clone by issuing the command *git clone --recursive github.com/swerea/fame.git*.

###Windows
So far there is no release for Windows. You can however clone the package and install all the dependencies above. Calculix may be acquired by downloading and installing "bConverged".

You can clone by issuing the command *git clone --recursive github.com/swerea/fame.git*.

##Running the command line interface

Run the FAME (or FAME.py) file as FAME -i testArtifact.stl -p slm.par -c 2. The three comman line parameters are:

* -i, the input geometry
* -p, the parameters file
* -c, the number of cpus


##Running the GUI

Run FAMEGUI (or FAMEGUI.py).

1. Click "Load STL-file" and pick the input geometry.
2. Click "Compute" - wait... (could take hours)
3. Click "Export" to save the adjusted geometry as a new STL-file

Go to the "Settings" dropdown meny to change material and process parameters.

##Settings
When FAME starts it reads the Calculix input file *am.inp* and replaces all parameters starting with the #-sign with the corresponding value in the parameter file (.par). 

###Material parameters

* thermExpBot - thermal expansion of build plate
* thermExpCold - thermal expansion of build at 20C
* thermExpHot - thermal expansion of build at 1000C
* creepAcold - Norton creep parameter *A* at 20C
* creepncold - Norton creep parameter *n* at 20C
* creepAmiddle - Norton creep parameter *A* at 500C
* creepnmiddle - Norton creep parameter *n* at 500C
* creepAhot - Norton creep parameter *A* at 1000C
* creepnhot - Norton creep parameter *n* at 1000C
* density - material density
* specHeat - specific heat
* elasticCold - Young's modulous at 20C
* elasticMiddle - Young's modulous at 500C
* elasticHot - Young's modulous at 1500C
* nu - Poisson's ratio
* conductivity - thermal conductivity



###Process parameters
The available process parameters are:

* speed -   the build speed i.e. how fast the component grows in the vertical direction.
* solidify - the temperature of the activated elements
* sinkCond - film condition of bed / build plate interface
* coolDown - time allowed for final coldness of the build
* sinkTemp - temperature of bed

###Other parameters

* comment - description of parameter set 
* resolution - number of elements in the x or y direction (which ever is biggest).



##License
FAME is licensed under the GNU public license version 3.