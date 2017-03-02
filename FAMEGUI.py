#!/usr/bin/env python3

import FAME,sys,os
import fameQT
import about
import settings

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from matplotwidgetFile import matplotWidget

class aboutDialog(QDialog,about.Ui_aboutDialog):
    def __init__(self, parent=None):
        super(aboutDialog,self).__init__(parent)
        self.setupUi(self)
        self.okButton.clicked.connect(self.close)
    def appear(self):
        self.show()


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

class settings(QDialog,settings.Ui_settings): #dialog for setting parameters
    def __init__(self, parent=None):
        super(settings,self).__init__(parent)
        self.setupUi(self)
        
        sets=QSettings('Swerea','FAME')
        self.lastSettingsFile=sets.value('settingsfile')
        del(sets)
        self.readSettings(self.lastSettingsFile)
        
        
        #self.finished.connect(self.returnParameters())
        self.saveButton.clicked.connect(self.save)
        self.saveAsButton.clicked.connect(self.saveAs)
        self.openButton.clicked.connect(self.openSettings)
        self.newButton.clicked.connect(self.newSettings)
        self.rowButton.clicked.connect(self.newRow)
        
        
        
    def appear(self):
        self.setTable()
            
        self.show()
    
    def setTable(self): #populate the qtable with parameters
        self.setWindowTitle('Settings - '+os.path.basename(self.lastSettingsFile))
        if 'comment' in self.parameters:
            self.nameEdit.setText(self.parameters['comment'])
        else:
            self.nameEdit.setText('')
        self.tableWidget.setRowCount(len(self.parameters)-1) #set the number of rows equal to the number of parameter items
        i=0
        for p in self.parameters.keys():
            if p !='comment':
                self.tableWidget.setItem(i,0,QTableWidgetItem(p))
                self.tableWidget.setItem(i,1,QTableWidgetItem(str(self.parameters[p])))
                i+=1
        
    def readSettings(self,filename=None): #read settings from file
        try:
            if not os.path.exists(filename):
                raise Exception('Doesn\'t exist')
        except:
            filename = os.path.abspath(os.path.dirname(os.path.realpath(__file__))+'/default.par')

        self.parameters=FAME.readParameters(filename)
        self.lastSettingsFile=filename
        self.setWindowTitle('Settings - '+os.path.basename(self.lastSettingsFile))
        
    def save(self,filename,saveAs=False):
        self.parameters=self.scrape()#read parameters from dialog
        if saveAs==True    : #if we specify a new filename
            self.lastSettingsFile=filename
        f=open(self.lastSettingsFile,'w')
        for p in self.parameters.keys():
            f.write(p+'='+str(self.parameters[p])+'\n')
        f.close()
        
        #remember last used settingsfile
        sets=QSettings('Swerea','FAME')
        sets.setValue('settingsfile', self.lastSettingsFile)
        del(sets)
        
        self.setWindowTitle('Settings - '+os.path.basename(self.lastSettingsFile))
 
    def saveAs(self):
        filename=QFileDialog.getSaveFileName(self,'Save settings as')
        self.save(filename,saveAs=True)
    
    def openSettings(self):
        filename=QFileDialog.getOpenFileName(self, 'Open settings file...',  '',"FAME settings files (*.par)")
        self.readSettings(filename)
        self.setTable()
        
        sets=QSettings('Swerea','FAME')
        sets.setValue('settingsfile', self.lastSettingsFile)
        del(sets)
    
    def newSettings(self):
        self.parameters={'comment':'new'}
        self.lastSettingsFile='new.par'
        self.setTable()
        
    
    def scrape(self):
        params={}
        params['comment']=self.nameEdit.text()
        rows=self.tableWidget.rowCount()
        for i in range(rows):
            try:
                p=str(self.tableWidget.item(i,0).text())
                v=str(self.tableWidget.item(i,1).text())
                params[p]=v
            except:
                pass
        return params
    
    def newRow(self):
        self.tableWidget.setRowCount(self.tableWidget.rowCount()+1)
    
    def returnParameters(self):
        print('destroy')
        


class MainWindow(QMainWindow,fameQT.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow,self).__init__(parent)
        self.setupUi(self)
        
        self.exportButton.setEnabled(False)

        #GUI connections
        self.loadButton.clicked.connect(self.loadSTL)
        self.exportButton.clicked.connect(self.exportSTL)
        self.actionExit.triggered.connect(app.quit) #connect meny->exit to quit

        
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
    
    def exportSTL(self):
        exportName = QFileDialog.getSaveFileName(self,'Export adjusted STL as')
        
        import shutil
        try:
            shutil.copy(self.resultPath,exportName)
        except:
            pass
        
    def compute(self):
        self.exportButton.setEnabled(False)
        import post,os,shutil
        name=self.inputfname
        parameters=settings.parameters
        
        dir_path = os.path.dirname(os.path.realpath(__file__)) #directory where the FAME.py file resides
        (directory,mesh)=FAME.run(parameters,name,dir_path)
        
        
        FAME.calc(directory=directory,cpus=1)
        
        post.readResults(os.path.relpath(directory+'/am.frd'),mesh)
        stlmesh=post.readSTL(name)
        print('Adjusting STL')
        self.resultPath=os.path.relpath(directory+'/'+os.path.basename(name)[:-4]+'_adjusted.stl')
        #print(resultPath)
        post.adjustSTL(self.resultPath,mesh,stlmesh,scale=1,power=4)
        plot.plot(name=self.resultPath,which='out')
        self.exportButton.setEnabled(True)
 
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
settings=settings()
form = MainWindow()
about=aboutDialog()

form.actionSettings.triggered.connect(settings.appear)
form.actionAbout.triggered.connect(about.appear) #connect the about action to the about dialog

plot=plotter()
form.show() #show main window
app.exec_()
