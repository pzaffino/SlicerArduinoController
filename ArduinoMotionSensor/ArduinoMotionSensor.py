import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import shutil, subprocess, json

#
# ArduinoMotionSensor
#

class ArduinoMotionSensor(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Arduino Motion Sensor" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Developer Tools"]
    self.parent.dependencies = []
    self.parent.contributors = ["Paolo Zaffino (Magna Graecia University of Catanzaro, Italy)", "Virgilio Sabatino (Magna Graecia University of Catanzaro, Italy)",  "Maria Francesca Spadea (Magna Graecia University of Catanzaro, Italy)"]
    self.parent.helpText = """
    This module allows to connect and transmit/receive data from Arduino board. On top of this users can build applications.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """ """ # replace with organization, grant and thanks. 

#
# ArduinoMotionSensorWidget
#

class ArduinoMotionSensorWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    self.ArduinoNode = slicer.mrmlScene.GetFirstNodeByName("arduinoNode")
    self.logic = ArduinoMotionSensorLogic(self.ArduinoNode)

    # Load widget from .ui file (created by Qt Designer)
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/ArduinoMotionSensor.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    
    # connections
   
    self.ui.startButton.connect('toggled(bool)', self.onStartButton)
    # Default values for QLineEdit
    self.ui.offsetText.setText("10")
    
   
   
  def onStartButton(self, toggle):
        self.logic.offset =  float(self.ui.offsetText.text)
       
       
        if toggle:
               
                        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
                        self.sceneModifiedObserverTag=self.ArduinoNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.logic.Motion)
                        self.ui.startButton.setText("Stop Motion")
                        self.ui.startButton.setStyleSheet("background-color:#ff0000")
                        self.ui.offsetText.setEnabled(False)
                        
                
        
        else:
            print("stop")
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
            self.ArduinoNode.RemoveObserver(self.sceneModifiedObserverTag)
            self.ui.startButton.setText("Start Motion")
            self.ui.startButton.setStyleSheet("background-color:#f1f1f1;")
            self.ui.offsetText.setEnabled(True)
        

  def cleanup(self):
  
    pass



#
# ArduinoMotionSensorLogic
#

class ArduinoMotionSensorLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, arduinoNode):
    ScriptedLoadableModuleLogic.__init__(self)
    self.ArduinoNode = arduinoNode
    #self.ArduinoNode = slicer.mrmlScene.GetFirstNodeByName("arduinoNode")
    #sceneModifiedObserverTag = self.ArduinoNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.Motion)
    self.forward=0
    self.left=0
    self.right=0
    
    
  def Motion(self, caller, event):
    message=self.ArduinoNode.GetParameter("Data").strip()
    if(message=="Forward"):
        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
        print("Red View Selected")
        self.forward=1
        self.left=0
        self.right=0
    if(message=="Left"):
        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
        print("Green View Selected")
        self.left=1
        self.forward=0
        self.right=0
    if(message=="Right"):
        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
        print("Yellow View Selected")
        self.right=1
        self.left=0
        self.forward=0
    if(message=='Up'and self.forward>=1):
        print(message)
        self.RedLogic = slicer.app.layoutManager().sliceWidget('Red').sliceLogic()
        self.RedLogic.SetSliceOffset(self.RedLogic.GetSliceOffset()+self.offset)
    if(message=='Down'and self.forward>=1):
        print(message)
        self.RedLogic = slicer.app.layoutManager().sliceWidget('Red').sliceLogic()
        self.RedLogic.SetSliceOffset(self.RedLogic.GetSliceOffset()-self.offset)
    if(message=="Up" and self.left>=1):
        print(message)
        self.GreenLogic = slicer.app.layoutManager().sliceWidget('Green').sliceLogic()
        self.GreenLogic.SetSliceOffset(self.GreenLogic.GetSliceOffset()+self.offset)
    if(message=="Down" and self.left>=1):
        print(message)
        self.GreenLogic = slicer.app.layoutManager().sliceWidget('Green').sliceLogic()
        self.GreenLogic.SetSliceOffset(self.GreenLogic.GetSliceOffset()-self.offset)
    if(message=="Up" and self.right>=1):
        print(message)
        self.YellowLogic = slicer.app.layoutManager().sliceWidget('Yellow').sliceLogic()
        self.YellowLogic.SetSliceOffset(self.YellowLogic.GetSliceOffset()+self.offset)
    if(message=="Down" and self.right>=1):
        print(message)
        self.YellowLogic = slicer.app.layoutManager().sliceWidget('Yellow').sliceLogic()
        self.YellowLogic.SetSliceOffset(self.YellowLogic.GetSliceOffset()-self.offset)
    if(message=="Backward" and self.forward>=1):
        print(message)
        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)
    if(message=="Backward" and self.left>=1):
        print(message)
        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpGreenSliceView)
    if(message=="Backward" and self.right>=1):
        print(message)
        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpYellowSliceView)
  

    
class ArduinoMotionSensorTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    self.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_ArduinoMotionSensor1()

  def test_ArduinoMotionSensor1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import SampleData
    SampleData.downloadFromURL(
      nodeNames='FA',
      fileNames='FA.nrrd',
      uris='http://self.kitware.com/midas3/download?items=5767',
      checksums='SHA256:12d17fba4f2e1f1a843f0757366f28c3f3e1a8bb38836f0de2a32bb1cd476560')
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = ArduinoMotionSensorLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
