#!/usr/bin/env python3

import FAME,sys
import fameQT

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from matplotwidgetFile import matplotWidget

class plotter(QObject): #class to plot the stress strain data
    def __init__(self):
        QObject.__init__(self)

    def plot(self,name,which='in'): #generic plot routine
        print(name)
        from stl import mesh
        from mpl_toolkits import mplot3d
        from matplotlib import pyplot

        # Create a new plot
        if which=='in':
            figure = form.inputSTLgraph.canvas.fig
            graph=form.inputSTLgraph
        elif which=='out':
            figure = form.adjustedSTLgraph.canvas.fig
            graph=form.adjustedSTLgraph
        else:
            print('Error - is it in or out?')
        axes = mplot3d.Axes3D(figure)

        # Load the STL files and add the vectors to the plot
        your_mesh = mesh.Mesh.from_file(name)
        axes.add_collection3d(mplot3d.art3d.Poly3DCollection(your_mesh.vectors))

        # Auto scale to the mesh size
        scale = your_mesh.points.flatten(-1)
        axes.auto_scale_xyz(scale, scale, scale)

        # Show the plot to the screen
        graph.canvas.ax.cla()
        graph.canvas.ax.set_title(name)
        graph.canvas.draw()


class MainWindow(QMainWindow,fameQT.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow,self).__init__(parent)
        self.setupUi(self)
        
        #self.v=warning('really delete?')
        
        
        #GUI connections
        self.loadButton.clicked.connect(self.loadSTL)
        self.computeButton.clicked.connect(self.compute)
        #self.exportButton.clicked.connect(self.export) #connect export button to save as dialog

    def loadSTL(self):
        self.inputfname = QFileDialog.getOpenFileName(self, 'Choose input STL...',  '',"STL files (*.STL *.stl)")
        try:
            plot.plot(self.inputfname,which='in')
            form.inlineEdit.setText(self.inputfname)
        except:
            pass    
    def compute(self):
        import post,os,shutil
        #name=self.inputfname.split('/')[-1]
        name=self.inputfname
        parameters=FAME.readParameters('slm.par')
        #print(parameters)
        dir_path = os.path.dirname(os.path.realpath(__file__)) #directory where the FAME.py file resides
        (directory,mesh)=FAME.run(parameters,name,dir_path)
        FAME.calc(directory=directory,cpus=1)
        
        
        
        #os.chdir(directory)
        post.readResults(directory+'/am.frd',mesh)
        stlmesh=post.readSTL(name)
        print('Adjusting STL')
        post.adjustSTL(os.path.basename(name)[:-4]+'_adjusted.stl',mesh,stlmesh,scale=1,power=4)
        #shutil.copy(name[:-4]+'_adjusted.stl','../'+name[:-4]+'_adjusted.stl')  
        plot.plot(name=name[:-4]+'_adjusted.stl',which='out')
        #plot.plot(name=self.inputfname[:-4]+'_adjusted.stl',which='out')

app = QApplication(sys.argv)
form = MainWindow()

plot=plotter()

form.show() #show main window
app.exec_()
