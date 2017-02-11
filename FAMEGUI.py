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

        #GUI connections
        self.loadButton.clicked.connect(self.loadSTL)
        
        self.stdoutOld=sys.stdout
        sys.stdout = self.EmittingStream()
        sys.stdout.textWritten.connect(self.textBrowser.append)
        
        self.sThread=self.sub_thread()
        self.computeButton.clicked.connect(self.sThread.start)
        self.sThread.started.connect(self.running)
        self.sThread.finished.connect(self.completed)

    def loadSTL(self):
        self.inputfname = QFileDialog.getOpenFileName(self, 'Choose input STL...',  '',"STL files (*.STL *.stl)")
        try:
            plot.plot(self.inputfname,which='in')
            form.inlineEdit.setText(self.inputfname)
        except:
            pass    
    def compute(self):
        import post,os,shutil
        name=self.inputfname
        parameters=FAME.readParameters('slm.par')
        dir_path = os.path.dirname(os.path.realpath(__file__)) #directory where the FAME.py file resides
        (directory,mesh)=FAME.run(parameters,name,dir_path)
        FAME.calc(directory=directory,cpus=1)
        
        post.readResults(directory+'/am.frd',mesh)
        stlmesh=post.readSTL(name)
        print('Adjusting STL')
        post.adjustSTL(os.path.basename(name)[:-4]+'_adjusted.stl',mesh,stlmesh,scale=1,power=4)
        plot.plot(name=name[:-4]+'_adjusted.stl',which='out')
 
    def running(self): #update gui at job start
        self.computeButton.setEnabled(False)
        self.computeButton.setText('Running...')

        
    def completed(self): #update gui at job finish
        self.computeButton.setEnabled(True)
        self.computeButton.setText('Compute')
        
    class EmittingStream(QObject):
        textWritten = Signal(str)
        def write(self, text):
            self.textWritten.emit(str(text).rstrip('\n'))
            
    class sub_thread (QThread):
        def run(self):
            form.compute()

 
app = QApplication(sys.argv)
form = MainWindow()
plot=plotter()
form.show() #show main window
app.exec_()
