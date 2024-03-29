import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import shutil, subprocess, json
import time
from statistics import mean
import statistics


class ArduinoPedalBoard(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "ArduinoPedalBoard" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Developer Tools"]
    self.parent.dependencies = []
    self.parent.contributors = ["Paolo Zaffino (Magna Graecia University of Catanzaro, Italy)", "Domenico Leuzzi (Magna Graecia University of Catanzaro, Italy)", "Maria Francesca Spadea (Magna Graecia University of Catanzaro, Italy)"]
    self.parent.helpText = """
    This module allows to connect and transmit/receive data from Arduino board. On top of this users can build applications.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """ """ # replace with organization, grant and thanks. 


class ArduinoPedalBoardWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    self.ArduinoNode = slicer.mrmlScene.GetFirstNodeByName("arduinoNode")
    self.logic = ArduinoPedalBoardLogic(self.ArduinoNode)

    # Load widget from .ui file (created by Qt Designer)
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/ArduinoPedalBoard.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)      
    self.ui.StartButton.connect('clicked(bool)', self.onWidgetButton1)    
    self.ui.SetOffset.setText("0.5")
    
    # Add vertical spacer
    self.layout.addStretch(1)
    
    # Link to logic class
    self.sceneModifiedObserverTag=self.ArduinoNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.logic.ApplyChange)  
    
  
  def onWidgetButton1(self, clicked): 
          
    # Check Offset value on EditLine 
    if self.ui.SetOffset.text!="":  
        self.logic.OnSetOffset =  float(self.ui.SetOffset.text)
    else:
        self.deviceError("Missed Option", "Missed Offset Input value", "warning")
    
    # Alert for Users (Missed Settings or duplicated)
    
    if self.ui.button1_Choice.currentText=="Change Viewer" and self.ui.button2_Choice.currentText=="Change Viewer" or self.ui.button2_Choice.currentText=="Change Viewer" and self.ui.button3_Choice.currentText=="Change Viewer" or self.ui.button1_Choice.currentText=="Change Viewer" and self.ui.button3_Choice.currentText=="Change Viewer":    
        self.deviceError("Operation Not Valid.", "Changer Views are duplicate. You must choise only one 'Changer'.", "critical")
    
    elif self.ui.button1_Choice.currentText=="Change Viewer" and self.ui.button2_Choice.currentText=="Slice Offset +" and self.ui.button3_Choice.currentText=="Slice Offset +":
        self.deviceError("Operation Not Valid.", "Offset are duplicate. You must choise only one type offset.", "warning")     
    
    elif self.ui.button1_Choice.currentText=="Change Viewer" and self.ui.button2_Choice.currentText=="Slice Offset -" and self.ui.button3_Choice.currentText=="Slice Offset -":             
        self.deviceError("Operation Not Valid.", "Offset are duplicate. You must choise only one type offset.", "warning")
          
    elif self.ui.button1_Choice.currentText=="Select Option" or self.ui.button2_Choice.currentText=="Select Option" or self.ui.button3_Choice.currentText=="Select Option":
        self.deviceError("Missed Option", "Changer Viewer not found! Settings not valid.", "critical")
              
    elif self.ui.button1_Choice.currentText=="Slice Offset +" and self.ui.button2_Choice.currentText=="Slice Offset +" and self.ui.button3_Choice.currentText=="Slice Offset +" or self.ui.button1_Choice.currentText=="Slice Offset +" and self.ui.button2_Choice.currentText=="Slice Offset +" and self.ui.button3_Choice.currentText=="Slice Offset -" or self.ui.button1_Choice.currentText=="Slice Offset +" and self.ui.button2_Choice.currentText=="Slice Offset -" and self.ui.button3_Choice.currentText=="Slice Offset +" or self.ui.button1_Choice.currentText=="Slice Offset -" and self.ui.button2_Choice.currentText=="Slice Offset +" and self.ui.button3_Choice.currentText=="Slice Offset +":
        self.deviceError("Missed Option", "Changer Viewer not found! Settings not valid.", "warning")
                 
    elif self.ui.button1_Choice.currentText=="Slice Offset -" and self.ui.button2_Choice.currentText=="Slice Offset -" and self.ui.button3_Choice.currentText=="Slice Offset -" or self.ui.button1_Choice.currentText=="Slice Offset -" and self.ui.button2_Choice.currentText=="Slice Offset -" and self.ui.button3_Choice.currentText=="Slice Offset +" or self.ui.button1_Choice.currentText=="Slice Offset -" and self.ui.button2_Choice.currentText=="Slice Offset +" and self.ui.button3_Choice.currentText=="Slice Offset -" or self.ui.button1_Choice.currentText=="Slice Offset +" and self.ui.button2_Choice.currentText=="Slice Offset -" and self.ui.button3_Choice.currentText=="Slice Offset -":
        self.deviceError("Missed Option", "Changer Viewer not found! Settings not valid.", "warning")
          
    elif self.ui.button1_Choice.currentText=="Slice Offset +" and self.ui.button2_Choice.currentText=="Change Viewer" and self.ui.button3_Choice.currentText=="Slice Offset +" or self.ui.button1_Choice.currentText=="Slice Offset -" and self.ui.button2_Choice.currentText=="Change Viewer" and self.ui.button3_Choice.currentText=="Slice Offset -" or self.ui.button1_Choice.currentText=="Slice Offset -" and self.ui.button2_Choice.currentText=="Slice Offset -" and self.ui.button3_Choice.currentText=="Change Viewer" or self.ui.button1_Choice.currentText=="Slice Offset +" and self.ui.button2_Choice.currentText=="Slice Offset +" and self.ui.button3_Choice.currentText=="Change Viewer":
        self.deviceError("Missed Option", "Offset are duplicate. You must choise only one type offset.", "warning")
        
    elif self.ui.button1_Choice.currentText=="Change Viewer" and self.ui.SetOffset.text!="" and self.ui.button2_Choice.currentText=="Slice Offset +" and self.ui.button3_Choice.currentText=="Slice Offset -":
        self.ui.button1_Choice.setEnabled(False)
        self.ui.button2_Choice.setEnabled(False)
        self.ui.button3_Choice.setEnabled(False)
        self.ui.SetOffset.setEnabled(False)     
        self.ui.StartButton.setEnabled(False)
        self.ui.StartButton.setStyleSheet("background-color:#008000")
        self.ui.StartButton.setText("Activated")
        self.logic.button1="Change Viewer"
        self.logic.button2="Slice Offset +"
        self.logic.button3="Slice Offset -"
    
    elif self.ui.button1_Choice.currentText=="Change Viewer" and self.ui.SetOffset.text!="" and self.ui.button2_Choice.currentText=="Slice Offset -" and self.ui.button3_Choice.currentText=="Slice Offset +":        
        self.ui.button1_Choice.setEnabled(False)
        self.ui.button2_Choice.setEnabled(False)
        self.ui.button3_Choice.setEnabled(False)
        self.ui.SetOffset.setEnabled(False) 
        self.ui.StartButton.setEnabled(False)
        self.ui.StartButton.setStyleSheet("background-color:#008000")
        self.ui.StartButton.setText("Activated")
        self.logic.button1="Change Viewer"
        self.logic.button2="Slice Offset -"
        self.logic.button3="Slice Offset +"

    elif self.ui.button1_Choice.currentText=="Slice Offset +" and self.ui.SetOffset.text!="" and self.ui.button2_Choice.currentText=="Change Viewer" and self.ui.button3_Choice.currentText=="Slice Offset -":
        self.ui.button1_Choice.setEnabled(False)
        self.ui.button2_Choice.setEnabled(False)
        self.ui.button3_Choice.setEnabled(False)
        self.ui.SetOffset.setEnabled(False) 
        self.ui.StartButton.setEnabled(False)
        self.ui.StartButton.setStyleSheet("background-color:#008000")
        self.ui.StartButton.setText("Activated")
        self.logic.button1="Slice Offset +"
        self.logic.button2="Change Viewer"
        self.logic.button3="Slice Offset -"

    elif self.ui.button1_Choice.currentText=="Slice Offset -" and self.ui.SetOffset.text!="" and self.ui.button2_Choice.currentText=="Change Viewer" and self.ui.button3_Choice.currentText=="Slice Offset +":
        self.ui.button1_Choice.setEnabled(False)
        self.ui.button2_Choice.setEnabled(False)
        self.ui.button3_Choice.setEnabled(False)
        self.ui.SetOffset.setEnabled(False) 
        self.ui.StartButton.setEnabled(False)
        self.ui.StartButton.setStyleSheet("background-color:#008000")
        self.ui.StartButton.setText("Activated")
        self.logic.button1="Slice Offset -"
        self.logic.button2="Change Viewer"
        self.logic.button3="Slice Offset +"  
         
    elif self.ui.button1_Choice.currentText=="Slice Offset +" and self.ui.SetOffset.text!="" and self.ui.button2_Choice.currentText=="Slice Offset -" and self.ui.button3_Choice.currentText=="Change Viewer":
        self.ui.button1_Choice.setEnabled(False)
        self.ui.button2_Choice.setEnabled(False)
        self.ui.button3_Choice.setEnabled(False)
        self.ui.SetOffset.setEnabled(False) 
        self.ui.StartButton.setEnabled(False)
        self.ui.StartButton.setStyleSheet("background-color:#008000")
        self.ui.StartButton.setText("Activated")
        self.logic.button1="Slice Offset +"
        self.logic.button2="Slice Offset -"
        self.logic.button3="Change Viewer"
        
    elif self.ui.button1_Choice.currentText=="Slice Offset -" and self.ui.SetOffset.text!="" and self.ui.button2_Choice.currentText=="Slice Offset +" and self.ui.button3_Choice.currentText=="Change Viewer":
        self.ui.button1_Choice.setEnabled(False)
        self.ui.button2_Choice.setEnabled(False)
        self.ui.button3_Choice.setEnabled(False)
        self.ui.SetOffset.setEnabled(False) 
        self.ui.StartButton.setEnabled(False)
        self.ui.StartButton.setStyleSheet("background-color:#008000")
        self.ui.StartButton.setText("Activated")
        self.logic.button1="Slice Offset -"
        self.logic.button2="Slice Offset +"
        self.logic.button3="Change Viewer"

    
  def deviceError(self, title, message, error_type="warning"):
    deviceMBox = qt.QMessageBox()
    if error_type == "warning":
      deviceMBox.setIcon(qt.QMessageBox().Warning)
    elif error_type == "critical":
      deviceMBox.setIcon(qt.QMessageBox().Critical)
    deviceMBox.setWindowTitle(title)
    deviceMBox.setText(message)
    deviceMBox.exec()
    
  
  def cleanup(self):
    pass
    

class ArduinoPedalBoardLogic(ScriptedLoadableModuleLogic):
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

      self.parameterNode=slicer.vtkMRMLScriptedModuleNode()
      self.parameterNode.SetName("arduinoNode")
      slicer.mrmlScene.AddNode(self.parameterNode)
      
      #Layout Selected (example: Red, Yellow, Green or Complete)
      self.selected_view=0 
      
      self.button1=None
      self.button2=None
      self.button3=None
                               
      
  def ApplyChange(self, caller, event):
  
    message=self.ArduinoNode.GetParameter("Data").strip()

    if message=="1" and self.button1=="Change Viewer":     
        # Counter Check Value Increase
        self.selected_view+=1
        if self.selected_view==1:   
            # Set Slice Node from Scene (Red)     
            self.red_Slice = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)
        if self.selected_view==2:
            # Set Slice Node from Scene (Yellow)
            self.yellow_Slice = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeYellow")
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpYellowSliceView)
        if self.selected_view==3:
            # Set Slice Node from Scene (Green)
            self.green_Slice = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeGreen")   
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpGreenSliceView)  
        if self.selected_view==4:
            # Default LayoutUpView
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)       
            #Reset Counter Check value
            self.selected_view=0            
                  
    if message=="2" and self.button2=="Slice Offset +" and self.selected_view==1 and self.button1=="Change Viewer":
        print("Button UP Pressed, [Operation num.]:",message)
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()+self.OnSetOffset)          
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset()) 
        
    if message=="2" and self.button2=="Slice Offset +" and self.selected_view==2 and self.button1=="Change Viewer":
        print("Button UP Pressed, [Operation num.]:",message)        
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()+self.OnSetOffset)               
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset())    
        
    if message=="2" and self.button2=="Slice Offset +" and self.selected_view==3 and self.button1=="Change Viewer":   
        print("Button UP Pressed, [Operation num.]:",message)         
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()+self.OnSetOffset)             
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())   
        
    if message=="3" and self.button3=="Slice Offset -" and self.selected_view==1 and self.button1=="Change Viewer":
        print("Button DOWN Pressed, [Operation num.]:",message)       
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()-self.OnSetOffset)                                  
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset())     
        
    if message=="3" and self.button3=="Slice Offset -" and self.selected_view==2 and self.button1=="Change Viewer":   
        print("Button DOWN Pressed, [Operation num.]:",message)        
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()-self.OnSetOffset)                 
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset())        
              
    if message=="3" and self.button3=="Slice Offset -" and self.selected_view==3 and self.button1=="Change Viewer":   
        print("Button DOWN Pressed, [Operation num.]:",message)        
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()-self.OnSetOffset)                        
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())
  
    if message=="2" and self.button2=="Slice Offset -" and self.selected_view==1 and self.button1=="Change Viewer":  
        print("Button DOWN Pressed, [Operation num.]:",message)        
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()-self.OnSetOffset)                    
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset())            
        
    if message=="2" and self.button2=="Slice Offset -" and self.selected_view==2 and self.button1=="Change Viewer":
        print("Button DOWN Pressed, [Operation num.]:",message)        
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()-self.OnSetOffset)                 
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset())        
        
    if message=="2" and self.button2=="Slice Offset -" and self.selected_view==3 and self.button1=="Change Viewer":    
        print("Button DOWN Pressed, [Operation num.]:",message)       
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()-self.OnSetOffset)                
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())                   
          
    if message=="3" and self.button3=="Slice Offset +" and self.selected_view==1 and self.button1=="Change Viewer":
        print("Button UP Pressed, [Operation num.]:",message)        
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()+self.OnSetOffset)                                   
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset())         
        
    if message=="3" and self.button3=="Slice Offset +" and self.selected_view==2 and self.button1=="Change Viewer":     
        print("Button UP Pressed, [Operation num.]:",message)         
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()+self.OnSetOffset)                            
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset())        
               
    if message=="3" and self.button3=="Slice Offset +" and self.selected_view==3 and self.button1=="Change Viewer":     
        print("Button UP Pressed, [Operation num.]:",message)        
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()+self.OnSetOffset)                         
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())        
   
    if message=="2" and self.button2=="Change Viewer":         
        self.selected_view+=1      
        if self.selected_view==1:   
            # Set Slice Node from Scene (Red)     
            self.red_Slice = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)                      
        if self.selected_view==2:
            # Set Slice Node from Scene (Yellow)
            self.yellow_Slice = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeYellow")
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpYellowSliceView)                   
        if self.selected_view==3:
            # Set Slice Node from Scene (Green)
            self.green_Slice = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeGreen")   
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpGreenSliceView)                     
        if self.selected_view==4:
            # Default LayoutUpView
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)                      
            self.selected_view=0    
                  
    if message=="1" and self.selected_view==1 and self.button2=="Change Viewer" and self.button1=="Slice Offset +" and self.button3=="Slice Offset -":        
        print("Button UP Pressed, [Operation num.]:",message)            
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()+self.OnSetOffset)                   
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset())
        
    if message=="1" and self.selected_view==2 and self.button2=="Change Viewer" and self.button1=="Slice Offset +" and self.button3=="Slice Offset -":       
        print("Button UP Pressed, [Operation num.]:",message)       
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()+self.OnSetOffset)       
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset())      
        
    if message=="1" and self.selected_view==3 and self.button2=="Change Viewer" and self.button1=="Slice Offset +" and self.button3=="Slice Offset -":
        print("Button UP Pressed, [Operation num.]:",message)
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()+self.OnSetOffset)        
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())
    
    if message=="3" and self.selected_view==1 and self.button2=="Change Viewer" and self.button1=="Slice Offset +" and self.button3=="Slice Offset -":
        print("Button DOWN Pressed, [Operation num.]:",message)            
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()-self.OnSetOffset)                      
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset())        
        
    if message=="3" and self.selected_view==2 and self.button2=="Change Viewer" and self.button1=="Slice Offset +" and self.button3=="Slice Offset -":
        print("Button DOWN Pressed, [Operation num.]:",message)
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()-self.OnSetOffset)                  
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset())
               
    if message=="3" and self.selected_view==3 and self.button2=="Change Viewer" and self.button1=="Slice Offset +" and self.button3=="Slice Offset -":
        print("Button DOWN Pressed, [Operation num.]:",message)
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()-self.OnSetOffset)                   
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())
        
    if message=="1" and self.selected_view==1 and self.button2=="Change Viewer" and self.button1=="Slice Offset -" and self.button3=="Slice Offset +":        
        print("Button DOWN Pressed, [Operation num.]:",message)                   
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()-self.OnSetOffset)                     
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset())
              
    if message=="1" and self.selected_view==2 and self.button2=="Change Viewer" and self.button1=="Slice Offset -" and self.button3=="Slice Offset +":       
        print("Button DOWN Pressed, [Operation num.]:",message)       
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()-self.OnSetOffset)                 
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset())    
       
    if message=="1" and self.selected_view==3 and self.button2=="Change Viewer" and self.button1=="Slice Offset -" and self.button3=="Slice Offset +":
        print("Button DOWN Pressed, [Operation num.]:",message)
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()-self.OnSetOffset)       
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())        
        
    if message=="3" and self.selected_view==1 and self.button2=="Change Viewer" and self.button1=="Slice Offset -" and self.button3=="Slice Offset +":
        print("Button UP Pressed, [Operation num.]:",message)           
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()+self.OnSetOffset)                           
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset())
               
    if message=="3" and self.selected_view==2 and self.button2=="Change Viewer" and self.button1=="Slice Offset -" and self.button3=="Slice Offset +":
        print("Button UP Pressed, [Operation num.]:",message) 
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()+self.OnSetOffset)                       
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset())
               
    if message=="3" and self.selected_view==3 and self.button2=="Change Viewer" and self.button1=="Slice Offset -" and self.button3=="Slice Offset +":
        print("Button UP Pressed, [Operation num.]:",message) 
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()+self.OnSetOffset)                       
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())  
    
    if message=="3" and self.button3=="Change Viewer":         
        self.selected_view+=1        
        if self.selected_view==1:   
            # Set Slice Node from Scene (Red)     
            self.red_Slice = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)            
        if self.selected_view==2:
            # Set Slice Node from Scene (Yellow)
            self.yellow_Slice = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeYellow")
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpYellowSliceView)            
        if self.selected_view==3:
            # Set Slice Node from Scene (Green)
            self.green_Slice = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeGreen")   
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpGreenSliceView)            
        if self.selected_view==4:
            # Default LayoutUpView
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)          
            self.selected_view=0    
    
    if message=="1" and self.selected_view==1 and self.button1=="Slice Offset +" and self.button2=="Slice Offset -" and self.button3=="Change Viewer":       
        print("Button UP Pressed, [Operation num.]:",message)                   
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()+self.OnSetOffset)                           
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset())
        
    if message=="1" and self.selected_view==2 and self.button1=="Slice Offset +" and self.button2=="Slice Offset -" and self.button3=="Change Viewer":       
        print("Button UP Pressed, [Operation num.]:",message)        
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()+self.OnSetOffset)    
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset()) 
                
    if message=="1" and self.selected_view==3 and self.button1=="Slice Offset +" and self.button2=="Slice Offset -" and self.button3=="Change Viewer":       
        print("Button UP Pressed, [Operation num.]:",message) 
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()+self.OnSetOffset)             
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())       
    
    if message=="2" and self.button2=="Slice Offset -" and self.selected_view==1 and self.button3=="Change Viewer":    
        print("Button DOWN Pressed, [Operation num.]:",message)        
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()-self.OnSetOffset)                 
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset())      
               
    if message=="2" and self.button2=="Slice Offset -" and self.selected_view==2 and self.button3=="Change Viewer":
        print("Button DOWN Pressed, [Operation num.]:",message)              
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset()) 
               
    if message=="2" and self.button2=="Slice Offset -" and self.selected_view==3 and self.button3=="Change Viewer":    
        print("Button DOWN Pressed, [Operation num.]:",message)        
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()-self.OnSetOffset)
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())           
    
    if message=="1" and self.selected_view==1 and self.button1=="Slice Offset -" and self.button2=="Slice Offset +" and self.button3=="Change Viewer":       
        print("Button DOWN Pressed, [Operation num.]:",message)                   
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()-self.OnSetOffset)                  
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset())
               
    if message=="1" and self.selected_view==2 and self.button1=="Slice Offset -" and self.button2=="Slice Offset +" and self.button3=="Change Viewer":       
        print("Button DOWN Pressed, [Operation num.]:",message)        
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()-self.OnSetOffset)           
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset())       
        
    if message=="1" and self.selected_view==3 and self.button1=="Slice Offset -" and self.button2=="Slice Offset +" and self.button3=="Change Viewer":       
        print("Button DOWN Pressed, [Operation num.]:",message)
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()-self.OnSetOffset)              
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())

    if message=="2" and self.button2=="Slice Offset +" and self.selected_view==1 and self.button3=="Change Viewer":   
        print("Button UP Pressed, [Operation num.]:",message)        
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()+self.OnSetOffset)  
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset())      
               
    if message=="2" and self.button2=="Slice Offset +" and self.selected_view==2 and self.button3=="Change Viewer":
        print("Button UP Pressed, [Operation num.]:",message)        
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()+self.OnSetOffset)         
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset()) 
               
    if message=="2" and self.button2=="Slice Offset +" and self.selected_view==3 and self.button3=="Change Viewer":    
        print("Button UP Pressed, [Operation num.]:",message)         
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()+self.OnSetOffset)       
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())
        
  
class ArduinoPedalBoardTest(ScriptedLoadableModuleTest):
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
    self.test_ArduinoPedalBoard1()

  def test_ArduinoPedalBoard11(self):
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
    logic = ArduinoPedalBoardLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
