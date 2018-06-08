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

* thermExpBuild11 - thermal expansion of build
* thermExpPlate - thermal expansion of plate
* densityPlate - density of plate
* buildDensity - density of build
* elasticPlate - Young's modulous of plate
* elasticBuild - Young's modulous of build
* nu - Poisson's ratio
* yieldPlate - Initial yield of plate
* utsPlate=495 - Ultimate tensile strength of plate
* yieldBuild - Initial yield of build
* utsBuild - Ultimate tensile strength of build
* utsStrainPlate - Strain at UTS of plate
* utsStrainBuild - Strain at UTS of build

###Process parameters
The available process parameters are:

* speed -   the build speed i.e. how fast the component grows in the vertical direction.
* solidify - the temperature of the activated elements
* sinkTemp - temperature of bed

###Other parameters

* comment - description of parameter set 
* resolution - number of elements in the x or y direction (which ever is biggest).



##License
FAME is licensed under the GNU public license version 3.