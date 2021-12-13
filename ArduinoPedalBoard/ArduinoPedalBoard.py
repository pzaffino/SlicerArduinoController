import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import shutil, subprocess, json


#
# ArduinoPedalBoard
#

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


#
# ArduinoConnectWidget
#

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
    
    #Buttons
    self.ui.SetButton1.connect('clicked(bool)', self.onWidgetButton1) 
    self.ui.SetButton2.connect('clicked(bool)', self.onWidgetButton2) 
    self.ui.SetButton3.connect('clicked(bool)', self.onWidgetButton3) 
    
    # Default values for Offset
    self.ui.SetOffset.setText("0.5")
    
    # Add vertical spacer
    self.layout.addStretch(1)
    
    
    #
    # Method Widget Button1
    #  
  
  def onWidgetButton1(self, clicked): 
      
    global s #Check case Button2 + e Button3 - (initial default value=0) ##Eliminare "global"
    s="0"
    
    global s1 #Check case Button2 - e Button3 + (initial default value=0)
    s1="0"
      
    # Check text EditLine
    if(self.ui.SetOffset.text!=""):  
        self.logic.OnSetOffset =  float(self.ui.SetOffset.text)
    
    else:
        self.deviceError("Missed Option", "Missed Offset Input value", "warning")
    
        self.ui.button1_Choice.setEnabled(True)
        self.ui.button2_Choice.setEnabled(True)
        self.ui.button3_Choice.setEnabled(True)
  
    #
    # Alert
    #
    
    if(((self.ui.button1_Choice.currentText=="Change Viewer") and (self.ui.button2_Choice.currentText=="Change Viewer")) or ((self.ui.button2_Choice.currentText=="Change Viewer") and (self.ui.button3_Choice.currentText=="Change Viewer")) or ((self.ui.button1_Choice.currentText=="Change Viewer") and (self.ui.button3_Choice.currentText=="Change Viewer"))):
        
        self.deviceError("Operation Not Valid.", "Changer Views are duplicate. You must choise only one 'Changer'.", "critical")
    
    
    elif(((self.ui.button1_Choice.currentText=="Change Viewer") and (self.ui.button2_Choice.currentText=="Slice Offset +") and (self.ui.button3_Choice.currentText=="Slice Offset +"))):
        
        self.deviceError("Operation Not Valid.", "Offset are duplicate. You must choise only one type offset.", "warning")
        
    
    elif((self.ui.button1_Choice.currentText=="Change Viewer") and (self.ui.button2_Choice.currentText=="Slice Offset -") and (self.ui.button3_Choice.currentText=="Slice Offset -")):    
            
        self.deviceError("Operation Not Valid.", "Offset are duplicate. You must choise only one type offset.", "warning")
  
        
    # Warning Error    
    elif((self.ui.button1_Choice.currentText=="Select Option") or (self.ui.button2_Choice.currentText=="Select Option") or (self.ui.button3_Choice.currentText=="Select Option")):
    
        self.deviceError("Missed Option", "Changer Viewer not found! Setting not valid.", "warning")
                
    #           
    #Case: Button2 + Button3 -
    #
    
    elif(((self.ui.button1_Choice.currentText=="Change Viewer") and (self.ui.SetOffset.text!="") and (self.ui.button2_Choice.currentText=="Slice Offset +") and (self.ui.button3_Choice.currentText=="Slice Offset -"))):
 
        #Change ComboBox Status
        self.ui.button1_Choice.setEnabled(False)
        self.ui.button2_Choice.setEnabled(False)
        self.ui.button3_Choice.setEnabled(False)

        #Change Offset Status
        self.ui.SetOffset.setEnabled(False) 
        
        #Change Button State
        self.ui.SetButton1.setEnabled(False)
        self.ui.SetButton2.setEnabled(False)
        self.ui.SetButton3.setEnabled(False)
        
        #Link to logic class
        self.sceneModifiedObserverTag=self.ArduinoNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.logic.OnSetButton1)           
        
        #Check case Button2 - e Button3 +
        s=self.check_option="1"
        
    #    
    #Case: Button2 - Button3 +
    #
    
    elif(((self.ui.button1_Choice.currentText=="Change Viewer") and (self.ui.SetOffset.text!="") and (self.ui.button2_Choice.currentText=="Slice Offset -") and (self.ui.button3_Choice.currentText=="Slice Offset +"))):
 
        #Change ComboBox Status
        self.ui.button1_Choice.setEnabled(False)
        self.ui.button2_Choice.setEnabled(False)
        self.ui.button3_Choice.setEnabled(False)
        
        #Change Offset Status
        self.ui.SetOffset.setEnabled(False) 
        
        #Change Button State
        self.ui.SetButton1.setEnabled(False)
        self.ui.SetButton2.setEnabled(False)
        self.ui.SetButton3.setEnabled(False)
        
        #Link to logic class
        self.sceneModifiedObserverTag=self.ArduinoNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.logic.OnSetButton1)
        
        #Check case Button2 - e Button3 +        
        s1=self.check_option="2"

          
    #
    # Method Widget Button2
    #
 
  def onWidgetButton2(self, clicked):  
  
    global s2 #Check case Button1 + e Button3 - (*default value=0*)
    s2="0"
    
    global s3 #Check case Button1 - e Button3 + (*default value=0*)
    s3="0"
      
    # Check text EditLine
    if(self.ui.SetOffset.text!=""):  
        self.logic.OnSetOffset =  float(self.ui.SetOffset.text)
    
    else:
        self.deviceError("Missed Option", "Missed Offset Input value", "warning")
    
        self.ui.button1_Choice.setEnabled(True)
        self.ui.button2_Choice.setEnabled(True)
        self.ui.button3_Choice.setEnabled(True)
  
    #
    # Alert
    #
    
    if(((self.ui.button1_Choice.currentText=="Change Viewer") and (self.ui.button2_Choice.currentText=="Change Viewer")) or ((self.ui.button2_Choice.currentText=="Change Viewer") and (self.ui.button3_Choice.currentText=="Change Viewer")) or ((self.ui.button1_Choice.currentText=="Change Viewer") and (self.ui.button3_Choice.currentText=="Change Viewer"))):
        
        self.deviceError("Operation Not Valid.", "Changer Views are duplicate. You must choise only one 'Changer'.", "critical")
    
    
    elif(((self.ui.button1_Choice.currentText=="Slice Offset +") and (self.ui.button2_Choice.currentText=="Change Viewer") and (self.ui.button3_Choice.currentText=="Slice Offset +"))):
        
        self.deviceError("Operation Not Valid.", "Offset are duplicate. You must choise only one type offset.", "critical")
        
    
    elif((self.ui.button1_Choice.currentText=="Slice Offset -") and (self.ui.button2_Choice.currentText=="Change Viewer") and (self.ui.button3_Choice.currentText=="Slice Offset -")):    
            
        self.deviceError("Operation Not Valid.", "Offset are duplicate. You must choise only one type offset.", "critical")
  
        
    # Warning Error    
    elif((self.ui.button1_Choice.currentText=="Select Option") or (self.ui.button2_Choice.currentText=="Select Option") or (self.ui.button3_Choice.currentText=="Select Option")):
    
        self.deviceError("Missed Option", "Changer Viewer not found! Setting not valid.", "warning")
               
               
    #           
    #Case: Button1 + Button3 -
    #
    
    elif(((self.ui.button1_Choice.currentText=="Slice Offset +") and (self.ui.SetOffset.text!="") and (self.ui.button2_Choice.currentText=="Change Viewer") and (self.ui.button3_Choice.currentText=="Slice Offset -"))):
 
        #Change ComboBox Status
        self.ui.button1_Choice.setEnabled(False)
        self.ui.button2_Choice.setEnabled(False)
        self.ui.button3_Choice.setEnabled(False)

        #Change Offset Status
        self.ui.SetOffset.setEnabled(False) 
        
        #Change Button State
        self.ui.SetButton1.setEnabled(False)
        self.ui.SetButton2.setEnabled(False)
        self.ui.SetButton3.setEnabled(False)
        
        #Link to logic class
        self.sceneModifiedObserverTag=self.ArduinoNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.logic.OnSetButton2)           
        
        #Case Button1 + e Button3 -
        s2=self.check_option="1"
        
    #    
    #Case: Button1 - Button3 +
    #
    
    elif(((self.ui.button1_Choice.currentText=="Slice Offset -") and (self.ui.SetOffset.text!="") and (self.ui.button2_Choice.currentText=="Change Viewer") and (self.ui.button3_Choice.currentText=="Slice Offset +"))):
 
        #Change ComboBox Status
        self.ui.button1_Choice.setEnabled(False)
        self.ui.button2_Choice.setEnabled(False)
        self.ui.button3_Choice.setEnabled(False)
        
        #Change Offset Status
        self.ui.SetOffset.setEnabled(False) 
        
        #Change Button State
        self.ui.SetButton1.setEnabled(False)
        self.ui.SetButton2.setEnabled(False)
        self.ui.SetButton3.setEnabled(False)
        
        #Link to logic class
        self.sceneModifiedObserverTag=self.ArduinoNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.logic.OnSetButton2)
        
        #Check case Button1 - e Button3 +        
        s3=self.check_option="2"
        

    #
    # Method Widget Button3
    #          
           
  def onWidgetButton3(self, clicked):
  
  
    global s4 #Check case Button1 + e Button2 - (*default value=0*)
    s4="0"
    
    global s5 #Check case Button1 - e Button2 + (*default value=0*)
    s5="0"
      
    # Check text EditLine
    if(self.ui.SetOffset.text!=""):  
        self.logic.OnSetOffset =  float(self.ui.SetOffset.text)
    
    else:
        self.deviceError("Missed Option", "Missed Offset Input value", "warning")
    
        self.ui.button1_Choice.setEnabled(True)
        self.ui.button2_Choice.setEnabled(True)
        self.ui.button3_Choice.setEnabled(True)
  
    #
    # Alert
    #
    
    if(((self.ui.button1_Choice.currentText=="Change Viewer") and (self.ui.button2_Choice.currentText=="Change Viewer")) or ((self.ui.button2_Choice.currentText=="Change Viewer") and (self.ui.button3_Choice.currentText=="Change Viewer")) or ((self.ui.button1_Choice.currentText=="Change Viewer") and (self.ui.button3_Choice.currentText=="Change Viewer"))):
        
        self.deviceError("Operation Not Valid.", "Changer Views are duplicate. You must choise only one 'Changer'.", "critical")
    
    
    elif(((self.ui.button1_Choice.currentText=="Slice Offset +") and (self.ui.button2_Choice.currentText=="Change Viewer") and (self.ui.button3_Choice.currentText=="Slice Offset +"))):
        
        self.deviceError("Operation Not Valid.", "Offset are duplicate. You must choise only one type offset.", "warning")
        
    
    elif((self.ui.button1_Choice.currentText=="Slice Offset -") and (self.ui.button2_Choice.currentText=="Change Viewer") and (self.ui.button3_Choice.currentText=="Slice Offset -")):    
            
        self.deviceError("Operation Not Valid.", "Offset are duplicate. You must choise only one type offset.", "warning")
  
        
    # Warning Error    
    elif((self.ui.button1_Choice.currentText=="Select Option") or (self.ui.button2_Choice.currentText=="Select Option") or (self.ui.button3_Choice.currentText=="Select Option")):
    
        self.deviceError("Missed Option", "Changer Viewer not found!", "warning")
        
        
    #           
    #Case: Button1 + Button2 -
    #
    
    elif(((self.ui.button1_Choice.currentText=="Slice Offset +") and (self.ui.SetOffset.text!="") and (self.ui.button2_Choice.currentText=="Slice Offset -") and (self.ui.button3_Choice.currentText=="Change Viewer"))):
 
        #Change ComboBox Status
        self.ui.button1_Choice.setEnabled(False)
        self.ui.button2_Choice.setEnabled(False)
        self.ui.button3_Choice.setEnabled(False)

        #Change Offset Status
        self.ui.SetOffset.setEnabled(False) 
        
        #Change Button State
        self.ui.SetButton1.setEnabled(False)
        self.ui.SetButton2.setEnabled(False)
        self.ui.SetButton3.setEnabled(False)
        
        #Link to logic class
        self.sceneModifiedObserverTag=self.ArduinoNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.logic.OnSetButton3)           
        
        #Case Button1 + e Button3 -
        s4=self.check_option="1"
        
        
    #    
    #Case: Button1 - Button3 +
    #
    
    elif(((self.ui.button1_Choice.currentText=="Slice Offset -") and (self.ui.SetOffset.text!="") and (self.ui.button2_Choice.currentText=="Slice Offset +") and (self.ui.button3_Choice.currentText=="Change Viewer"))):
 
        #Change ComboBox Status
        self.ui.button1_Choice.setEnabled(False)
        self.ui.button2_Choice.setEnabled(False)
        self.ui.button3_Choice.setEnabled(False)
        
        #Change Offset Status
        self.ui.SetOffset.setEnabled(False) 
        
        #Change Button State
        self.ui.SetButton1.setEnabled(False)
        self.ui.SetButton2.setEnabled(False)
        self.ui.SetButton3.setEnabled(False)
        
        #Link to logic class
        self.sceneModifiedObserverTag=self.ArduinoNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.logic.OnSetButton3) ### Fare metodi separati per eliminare il "global"
        
        #Check case Button1 - e Button3 +        
        s5=self.check_option="2"
    
    
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
    

#
# ArduinoConnectLogic
#


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
      
      #Counter Check Value for change views
      self.check_view=0 
      
      
  def OnSetButton1(self, caller, event):
  
    message=self.ArduinoNode.GetParameter("Data").strip()
    
    if(message=="1"):     
      
        # Counter Check Value Increase
        self.check_view+=1
        
        if(self.check_view==1):   
            # Set Slice Node from Scene (Red)
            
            self.red_Slice = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)
            
        if(self.check_view==2):
            # Set Slice Node from Scene (Yellow)
            self.yellow_Slice = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeYellow")
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpYellowSliceView)
            
        if(self.check_view==3):
            # Set Slice Node from Scene (Green)
            self.green_Slice = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeGreen")   
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpGreenSliceView)
            
        if(self.check_view==4):
            # Default LayoutUpView
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
            
            self.check_view=0    #Reset Counter Check value 
          
          
    #    
    # Case Button2 + Button3 -
    #          
            
    if((message=="2") and (self.check_view==1) and (s=="1")):
    
        print("Button DOWN Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()+self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset())            
        
    if((message=="2") and (self.check_view==2) and (s=="1")):

        print("Button DOWN Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()+self.OnSetOffset)   
        
        # Print Slice Node Offset
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset()) 
        
        
    if((message=="2") and (self.check_view==3) and (s=="1")):
    
        print("Button DOWN Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()+self.OnSetOffset)
        
        # Print Slice Node Offset
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())          
          
          
    if((message=="3") and (self.check_view==1) and (s=="1")): 
        print("Button UP Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()-self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset()) 
        
        
    if((message=="3") and (self.check_view==2) and (s=="1")):  
    
        print("Button UP Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()-self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset())        
        
       
    if((message=="3") and (self.check_view==3) and (s=="1")):  
    
        print("Button UP Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()-self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())


    
    #    
    # Case Button2 - Button3 +
    #
    
    if((message=="2") and (self.check_view==1) and (s1=="2")):
    
        print("Button DOWN Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()-self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset())            
        
    if((message=="2") and (self.check_view==2) and (s1=="2")):

        print("Button DOWN Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()-self.OnSetOffset)   
        
        # Print Slice Node Offset
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset()) 
        
    if((message=="2") and (self.check_view==3) and (s1=="2")):

    
        print("Button DOWN Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()-self.OnSetOffset)
        
        # Print Slice Node Offset
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset()) 
          
          
    if((message=="3") and (self.check_view==1) and (s1=="2")): 
        print("Button UP Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()+self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset()) 
        
        
    if((message=="3") and (self.check_view==2) and (s1=="2")):  
    
        print("Button UP Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()+self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset())        
        
       
    if((message=="3") and (self.check_view==3) and (s1=="2")):  
    
        print("Button UP Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()+self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())  
    
 

  #
  # OnSetButton2 Method
  #
  
  
  def OnSetButton2(self, caller, event):    
    
    message=self.ArduinoNode.GetParameter("Data").strip()
    
    if(message=="2"):     
       
        # Counter Check Value Increase
        self.check_view+=1
        
        if(self.check_view==1):   
            # Set Slice Node from Scene (Red)
            
            self.red_Slice = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)
       
        if(self.check_view==2):
            # Set Slice Node from Scene (Yellow)
            self.yellow_Slice = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeYellow")
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpYellowSliceView)
            
        if(self.check_view==3):
            # Set Slice Node from Scene (Green)
            self.green_Slice = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeGreen")   
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpGreenSliceView)
            
        if(self.check_view==4):
            # Default LayoutUpView
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
            
            self.check_view=0    #Reset Counter Check value 
            
    #    
    # Case Button1 + Button3 -
    #          
            
    if((message=="1") and (self.check_view==1) and (s2=="1")):
    
        print("Button DOWN Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()+self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset())            
        
    if((message=="1") and (self.check_view==2) and (s2=="1")):

        print("Button DOWN Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()+self.OnSetOffset)   
        
        # Print Slice Node Offset
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset()) 
        
        
    if((message=="1") and (self.check_view==3) and (s2=="1")):
    
        print("Button DOWN Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()+self.OnSetOffset)
        
        # Print Slice Node Offset
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())          
          
          
    if((message=="3") and (self.check_view==1) and (s2=="1")): 
        print("Button UP Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()-self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset()) 
        
        
    if((message=="3") and (self.check_view==2) and (s2=="1")):  
    
        print("Button UP Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()-self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset())        
        
       
    if((message=="3") and (self.check_view==3) and (s2=="1")):  
    
        print("Button UP Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()-self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())


    
    #    
    # Case Button1 - Button3 +
    #
    
    if((message=="1") and (self.check_view==1) and (s3=="2")):
    
        print("Button DOWN Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()-self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset())            
        
    if((message=="1") and (self.check_view==2) and (s3=="2")):

        print("Button DOWN Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()-self.OnSetOffset)   
        
        # Print Slice Node Offset
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset()) 
        
    if((message=="1") and (self.check_view==3) and (s3=="2")):

    
        print("Button DOWN Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()-self.OnSetOffset)
        
        # Print Slice Node Offset
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset()) 
          
          
    if((message=="3") and (self.check_view==1) and (s3=="2")): 
        print("Button UP Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()+self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset()) 
        
        
    if((message=="3") and (self.check_view==2) and (s3=="2")):  
    
        print("Button UP Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()+self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset())        
        
       
    if((message=="3") and (self.check_view==3) and (s3=="2")):  
    
        print("Button UP Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()+self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())  


  #
  # OnSetButton3 Method  
  #

  def OnSetButton3(self, caller, event):
  
    message=self.ArduinoNode.GetParameter("Data").strip()
    
    if(message=="3"):     
       
        # Counter Check Value Increase
        self.check_view+=1
        
        if(self.check_view==1):   
            # Set Slice Node from Scene (Red)
            
            self.red_Slice = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)
       
        if(self.check_view==2):
            # Set Slice Node from Scene (Yellow)
            self.yellow_Slice = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeYellow")
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpYellowSliceView)
            
        if(self.check_view==3):
            # Set Slice Node from Scene (Green)
            self.green_Slice = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeGreen")   
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpGreenSliceView)
            
        if(self.check_view==4):
            # Default LayoutUpView
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
            
            self.check_view=0    #Reset Counter Check value 
         
         
    #    
    # Case Button1 + Button2 -
    #          
            
    if((message=="1") and (self.check_view==1) and (s4=="1")):
    
        print("Button DOWN Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()+self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset())            
        
    if((message=="1") and (self.check_view==2) and (s4=="1")):

        print("Button DOWN Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()+self.OnSetOffset)   
        
        # Print Slice Node Offset
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset()) 
        
        
    if((message=="1") and (self.check_view==3) and (s4=="1")):
    
        print("Button DOWN Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()+self.OnSetOffset)
        
        # Print Slice Node Offset
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())          
          
          
    if((message=="2") and (self.check_view==1) and (s4=="1")): 
        print("Button UP Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()-self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset()) 
        
        
    if((message=="2") and (self.check_view==2) and (s4=="1")):  
    
        print("Button UP Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()-self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset())        
        
       
    if((message=="2") and (self.check_view==3) and (s4=="1")):  
    
        print("Button UP Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()-self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset())


    
    #    
    # Case Button1 - Button2 +
    #
    
    if((message=="1") and (self.check_view==1) and (s5=="2")):
    
        print("Button DOWN Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()-self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset())            
        
    if((message=="1") and (self.check_view==2) and (s5=="2")):

        print("Button DOWN Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()-self.OnSetOffset)   
        
        # Print Slice Node Offset
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset()) 
        
    if((message=="1") and (self.check_view==3) and (s5=="2")):

    
        print("Button DOWN Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()-self.OnSetOffset)
        
        # Print Slice Node Offset
        print("Offset Green Slice:",self.green_Slice.GetSliceOffset()) 
          
          
    if((message=="2") and (self.check_view==1) and (s5=="2")): 
        print("Button UP Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.red_Slice.SetSliceOffset(self.red_Slice.GetSliceOffset()+self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Red Slice:",self.red_Slice.GetSliceOffset()) 
        
        
    if((message=="2") and (self.check_view==2) and (s5=="2")):  
    
        print("Button UP Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.yellow_Slice.SetSliceOffset(self.yellow_Slice.GetSliceOffset()+self.OnSetOffset)    
                
        # Print Slice Node Offset
        print("Offset Yellow Slice:",self.yellow_Slice.GetSliceOffset())        
        
       
    if((message=="2") and (self.check_view==3) and (s5=="2")):  
    
        print("Button UP Pressed, [Operation num.]:",message)
        
        # Changing Slice Node Offset 
        self.green_Slice.SetSliceOffset(self.green_Slice.GetSliceOffset()+self.OnSetOffset)    
                
        # Print Slice Node Offset
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