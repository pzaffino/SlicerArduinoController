import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import serial.tools.list_ports
#
# ArduinoConnect
#

class ArduinoConnect(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Arduino Connect" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Developer Tools"]
    self.parent.dependencies = []
    self.parent.contributors = ["Paolo Zaffino (Magna Graecia University of Catanzaro, Italy)", "Domenico Leuzzi (Magna Graecia University of Catanzaro, Italy)", "Virgilio Sabatino (Magna Graecia University of Catanzaro, Italy)", "Andras Lasso (PerkLab, Queen's)", "Maria Francesca Spadea (Magna Graecia University of Catanzaro, Italy)"]
    self.parent.helpText = """
    This module allows to connect and transmit/receive data from Arduino board. On top of this users can build applications.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """ """ # replace with organization, grant and thanks.

    # If needed install serial pylibrary before imporing. If already installed, just import it.
    try:
      import serial
    except ModuleNotFoundError:
      slicer.util.pip_install("pyserial")
      import serial


#
# ArduinoConnectWidget
#

class ArduinoConnectWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    self.logic = ArduinoConnectLogic()

    # Load widget from .ui file (created by Qt Designer)
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/ArduinoConnect.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # connections
    self.ui.applyButton.connect('toggled(bool)', self.onApplyButton)
    self.ui.detectDevice.connect('clicked(bool)', self.On_DetectDeviceButton) 
    self.ui.detectDevice.connect('toggled(bool)', self.Detect_ports) 
    self.ui.portSelectorComboBox.setEnabled(False)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def onApplyButton(self, toggle):
    if toggle:
      self.logic.connect(self.ui.portSelectorComboBox.currentText,self.ui.baudSelectorComboBox.currentText)
      self.ui.applyButton.setText("Disconnect")
      self.ui.applyButton.setStyleSheet("background-color:#ff0000")
    else:
      self.logic.disconnect()
      self.ui.applyButton.setText("Connect")
      self.ui.applyButton.setStyleSheet("background-color:#f1f1f1;")

  def On_DetectDeviceButton(self, clicked):
    buff=[]

    if  clicked:
        self.ui.portSelectorComboBox.setEnabled(True)
        devices = [port.device for port in serial.tools.list_ports.comports() if port[2] != 'n/a']
        text=str(devices)
        buff.append(text)

        self.ui.portSelectorComboBox.clear()
        
        buff_item = next(iter([devices]))  #View single item in list
        
        if(len(buff_item)==0):
            noDeviceMBox = qt.QMessageBox()
            noDeviceMBox.setText("Any device has been found!")
            noDeviceMBox.setIcon(qt.QMessageBox().Warning)
            noDeviceMBox.setWindowTitle("Ports scan")
            noDeviceMBox.exec()
        
        if(devices not in buff):
            self.ui.portSelectorComboBox.addItems(devices) 

  def Detect_ports(self):
    devices = [port.device for port in serial.tools.list_ports.comports() if port[2] != 'n/a']
    self.ui.portSelectorComboBox.clear()
    if  self.ui.detectDevice.isChecked():
        self.ui.portSelectorComboBox.setEnabled(True)
        self.ui.portSelectorComboBox.addItems(devices)
        
    else:
        self.ui.portSelectorComboBox.setEnabled(False)
    return devices

#
# ArduinoConnectLogic
#

class ArduinoConnectLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def connect(self, port,baud):
      import serial
      self.arduino = serial.Serial(port,baud)
      slicer.arduinoData = []
      self.arduinoEndOfLine = '\n'
      self.arduinoRefreshRateFps = 10.0
      qt.QTimer.singleShot(1000/self.arduinoRefreshRateFps, self.pollSerialDevice)

  def disconnect(self):
      self.arduino.close()

  def pollSerialDevice(self):
      if self.arduino.isOpen() and self.arduino.in_waiting == 0: # No messages from arduino
          qt.QTimer.singleShot(1000/self.arduinoRefreshRateFps, self.pollSerialDevice)
      elif self.arduino.isOpen() and self.arduino.in_waiting > 0: # Some messages from arduino
          arduinoReceiveBuffer = self.arduino.readline().decode('ascii')
          if self.arduinoEndOfLine in arduinoReceiveBuffer: # Valid message
              message = arduinoReceiveBuffer.split(self.arduinoEndOfLine)[0]
              message = self.processMessage(message)
              if len(message) >= 1:
                  #slicer.arduinoData.append(message)
                  slicer.arduinoData = message
                  print(slicer.arduinoData)
          qt.QTimer.singleShot(1000/self.arduinoRefreshRateFps, self.pollSerialDevice)

  def processMessage(self, msg):
      return msg


class ArduinoConnectTest(ScriptedLoadableModuleTest):
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
    self.test_ArduinoConnect1()

  def test_ArduinoConnect1(self):
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
    logic = ArduinoConnectLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
