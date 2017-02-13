#FAME - Free Additive Manufacturing Enhancer
Take your STL-file and simulate the additive manufacturing process.
### Main Features
* Reads an STL
* Simulates the build process
* Outputs an adjusted STL file.

### How to run
```
$ git clone https://github.com/wredenberg/FAME.git
$ cd FAME
$ python3 FAME.py -i ~/path/to/file.stl -p ~/path/to/file.par
```

### Packages required
* python3 (already installed with ubuntu)
* python3-pil (already installed with ubuntu)
* python3-numpy
* numpy-stl (installed with pip3)
* calculix-ccx
