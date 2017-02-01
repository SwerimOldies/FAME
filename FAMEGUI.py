#!/usr/bin/env python3

import FAME,sys
import fameQT

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class plotter(QObject): #class to plot the stress strain data
    def __init__(self):
        QObject.__init__(self)

    def plot(self,name,x,y): #generic plot routine
        form.Graph.canvas.ax.cla()
        form.Graph.canvas.ax.set_xlabel('strain / %')
        form.Graph.canvas.ax.set_ylabel('stress / MPa')
        form.Graph.canvas.ax.set_title(name)
        form.Graph.canvas.ax.plot(x,y)
        form.Graph.canvas.draw()

    def plot_material(self,mat): #prepare the stress strain curve for plotting
        x=[0]
        y=[0]
        yield_strain=mat.stress[0]/float(mat.E);
        x.append(yield_strain)
        y.append(mat.stress[0])
        for i in range(len(mat.strain)):
            x.append(mat.strain[i]+mat.stress[i]/float(mat.E)) #add the elatic strain component
            y.append(mat.stress[i])

        self.plot(mat.name,[i*100 for i in x],[i/1e6 for i in y])


class MainWindow(QMainWindow,fameQT.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow,self).__init__(parent)
        self.setupUi(self)
        
        #self.v=warning('really delete?')
        
        
        #GUI connections
        #self.exportButton.clicked.connect(self.export) #connect export button to save as dialog
        #self.availtagsList.itemClicked.connect(self.availTagClicked)
        #self.seltagsList.itemClicked.connect(self.selTagClicked)
        #self.materialList.itemClicked.connect(self.materialClicked)
        #self.deleteButton.clicked.connect(self.v.exec_) #connect delete button with delete warning
        #self.v.accepted.connect(self.delete) #if delete warning is clicked DO IT then run DELETE()
    


app = QApplication(sys.argv)
form = MainWindow()

plot=plotter()

form.show() #show main window
app.exec_()
