import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import shutil, subprocess, json

# If needed install serial pylibrary before imporing. If already installed, just import it.
try:
  import serial
  import serial.tools.list_ports
except ModuleNotFoundError:
  slicer.util.pip_install("pyserial")
  import serial
  import serial.tools.list_ports


def deviceError(title, message, error_type="warning"):
    deviceMBox = qt.QMessageBox()
    if error_type == "warning":
      deviceMBox.setIcon(qt.QMessageBox().Warning)
    elif error_type == "critical":
      deviceMBox.setIcon(qt.QMessageBox().Critical)
    deviceMBox.setWindowTitle(title)
    deviceMBox.setText(message)
    deviceMBox.exec()

def connectionError():
    connectionMBox = qt.QMessageBox()
    connectionMBox.setIcon(qt.QMessageBox().Critical)
    connectionMBox.setWindowTitle("Connection dropped!")
    connectionMBox.setText("Do you want to try to reconnect?")
    connectionMBox.setStandardButtons(qt.QMessageBox.Yes)
    connectionMBox.addButton(qt.QMessageBox.No)
    connectionMBox.setDefaultButton(qt.QMessageBox.Yes)
    if connectionMBox.exec() == qt.QMessageBox.Yes:
      return True
    else:
      return False

#
# ArduinoAppTemplate
#

class ArduinoAppTemplate():
  """ Template class for writing code on top of Arduino Connector
  """
  def __init__(self):
    self.ArduinoNode = slicer.mrmlScene.GetFirstNodeByName("arduinoNode")

    # Observe ModifiedEvent to be informed when new data arrived from the board
    sceneModifiedObserverTag = self.ArduinoNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.doSomethingWhenNewDataIsRead)

    # Observe ErrorEvent to be informed when connection dropped
    sceneModifiedObserverTag = self.ArduinoNode.AddObserver(vtk.vtkCommand.ErrorEvent, self.doSomethingWhenConnectionDrops)

  def doSomethingWhenNewDataIsRead(self, caller, event):
    #EXAMPLE TO PRINT THE RECEIVED VALUE:
    print("FIRED! %s" % (self.ArduinoNode.GetParameter("Data")))

  def doSomethingWhenConnectionDrops(self, caller, event):
    #EXAMPLE TO PRINT THE CONNECTION ERROR:
    print("CONNECTION DROPPED!")

  def sendDataToArduino(self, message):
    messageSent = slicer.modules.arduinoconnect.widgetRepresentation().self().logic.sendMessage(message)

#
#ArduinoPlotter
#

class ArduinoPlotter():
  def __init__(self, numberOfSamples):

    self.active = True

    self.ArduinoNode = slicer.mrmlScene.GetFirstNodeByName("arduinoNode")
    sceneModifiedObserverTag = self.ArduinoNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.addPointToPlot)

    # Add data into table vtk
    self.tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode")
    self.tableNode.SetName("Arduino plotting table")
    self.table = self.tableNode.GetTable()

    self.numberOfSamples = numberOfSamples
    self.initializeTable()

    # Create plot node
    self.plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", "Amplitude")
    self.plotSeriesNode.SetName("Arduino plot series")
    self.plotSeriesNode.SetAndObserveTableNodeID(self.tableNode.GetID())
    self.plotSeriesNode.SetXColumnName("Samples")
    self.plotSeriesNode.SetYColumnName("Amplitude")
    self.plotSeriesNode.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeLine)
    self.plotSeriesNode.SetLineStyle(slicer.vtkMRMLPlotSeriesNode.LineStyleSolid)
    self.plotSeriesNode.SetMarkerStyle(slicer.vtkMRMLPlotSeriesNode.MarkerStyleSquare)
    self.plotSeriesNode.SetUniqueColor()

    # Create plot chart node
    self.plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode")
    self.plotChartNode.SetName("Arduino plot chart")
    self.plotChartNode.AddAndObservePlotSeriesNodeID(self.plotSeriesNode.GetID())
    self.plotChartNode.SetTitle('Arduino Data')
    self.plotChartNode.SetXAxisTitle('Samples')
    self.plotChartNode.SetYAxisTitle('Amplitude')
    self.plotChartNode.LegendVisibilityOff()
    self.plotChartNode.SetXAxisRangeAuto(True)
    self.plotChartNode.SetYAxisRangeAuto(True)

    # Switch to a layout that contains a plot view to create a plot widget
    self.layoutManager = slicer.app.layoutManager()
    layoutWithPlot = slicer.modules.plots.logic().GetLayoutWithPlot(self.layoutManager.layout)
    self.layoutManager.setLayout(layoutWithPlot)

    # Select chart in plot view
    self.plotWidget = self.layoutManager.plotWidget(0)
    self.plotViewNode = self.plotWidget.mrmlPlotViewNode()
    self.plotViewNode.SetPlotChartNodeID(self.plotChartNode.GetID())

  def initializeTable(self):

    self.table.Initialize()

    self.arrX = vtk.vtkFloatArray()
    self.arrX.SetName("Samples")
    self.table.AddColumn(self.arrX)

    self.arrY = vtk.vtkFloatArray()
    self.arrY.SetName("Amplitude")
    self.table.AddColumn(self.arrY)

    self.table.SetNumberOfRows(self.numberOfSamples)
    for i in range(self.numberOfSamples):
      self.table.SetValue(i, 0, i)
      self.table.SetValue(i, 1, 0)

    self.table.Modified()

  def addPointToPlot(self, caller, event):
    if self.active:
      # Only float data type can be plot
      try:
        messageFloat = float(self.ArduinoNode.GetParameter("Data"))
      except ValueError:
        return

      self.arrY.InsertNextTuple1(messageFloat)
      self.arrY.RemoveFirstTuple()

      self.table.Modified()
      self.plotWidget.plotView().fitToContent()

#
# Arduino Monitor
#

class ArduinoMonitor():
  """ Class for plotting arduno data into a separate window
  """
  def __init__(self):

    self.ArduinoNode = slicer.mrmlScene.GetFirstNodeByName("arduinoNode")
    sceneModifiedObserverTag = self.ArduinoNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.addLine)

    self.monitor = qt.QTextEdit()
    self.monitor.setWindowTitle("Arduino monitor")
    self.monitor.setReadOnly(True)
    self.monitor.show()

    self.messageLenghtLimit = 50

  def addLine(self, caller, event):
    message = self.ArduinoNode.GetParameter("Data")

    if len(message) > self.messageLenghtLimit:
      message = "WARNING: message too long to be shown here\n"
    elif len(message) <= self.messageLenghtLimit and not message.endswith("\n"):
      message = message + "\n"

    self.monitor.insertPlainText(message)

    # Show always the last message
    verticalScrollBar = self.monitor.verticalScrollBar()
    verticalScrollBar.setValue(verticalScrollBar.maximum)

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

#
# ArduinoConnectWidget
#

class ArduinoConnectWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Add Arduino Node
    self.parameterNode = slicer.vtkMRMLScriptedModuleNode()
    self.parameterNode.SetName("arduinoNode")
    slicer.mrmlScene.AddNode(self.parameterNode)

    # Plotter
    self.plotter = None

    # Configuration
    self.configFileName = __file__.replace("ArduinoConnect.py", "Resources%sArduinoConnectConfig.json" % (os.sep))
    with open(self.configFileName) as f:
      self.config = json.load(f)

    self.logic = ArduinoConnectLogic()
    connectionDropErrorObserverTag = self.parameterNode.AddObserver("EndEvent", self.onConnectionEndEvent)
    connectionDropErrorObserverTag = self.parameterNode.AddObserver("StartEvent", self.onConnectionStartEvent)

    # Load widget from .ui file (created by Qt Designer)
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/ArduinoConnect.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set IDE labels
    self.arduinoIDEExe = self.config["IDEExe"]
    if self.arduinoIDEExe == "":
      self.arduinoIDEExe = self.autoFindIDEExe()
    self.ui.IDEPathText.setText(self.arduinoIDEExe)

    # connections
    self.ui.portSelectorComboBox.setEnabled(False)
    self.ui.detectDevice.connect('clicked(bool)', self.onDetectDeviceButton)
    self.ui.connectButton.connect('toggled(bool)', self.onConnectButton)
    self.ui.setIDEButton.connect('clicked(bool)', self.onSetIDEButton)
    self.ui.runIDEButton.connect('clicked(bool)', self.onRunIDEButton)
    self.ui.sendButton.connect('clicked(bool)', self.onSendButton)
    self.ui.monitorButton.connect('clicked(bool)', self.onMonitorButton)
    self.ui.plotterButton.connect('toggled(bool)', self.onPlotterButton)
    self.ui.samplesToPlotText.textChanged.connect(self.onSamplesToPlot)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Default values for QLineEdit
    self.ui.samplesPerSecondText.setText("10")
    self.ui.samplesToPlotText.setText("30")

  def cleanup(self):
    pass

  def writeConfig(self):
    with open(self.configFileName, 'w') as json_file:
      json.dump(self.config, json_file)

  def autoFindIDEExe(self):
    arduinoIDEExe = shutil.which("arduino")
    if arduinoIDEExe is None:
      return ""
    else:
      return arduinoIDEExe

  def onConnectionStartEvent(self, *argv):
    self.ui.connectButton.setText("Disconnect")
    self.ui.connectButton.setStyleSheet("background-color:#ff0000")
    self.ui.connectButton.setChecked(True)
    self.ui.portSelectorComboBox.setEnabled(False)
    self.ui.baudSelectorComboBox.setEnabled(False)
    self.ui.detectDevice.setEnabled(False)
    self.ui.sendButton.setEnabled(True)
    self.ui.samplesPerSecondText.setEnabled(False)

  def onConnectionEndEvent(self, *argv):
    self.ui.connectButton.setText("Connect")
    self.ui.connectButton.setStyleSheet("background-color:#f1f1f1;")
    self.ui.connectButton.setChecked(False)
    self.ui.portSelectorComboBox.setEnabled(True)
    self.ui.baudSelectorComboBox.setEnabled(True)
    self.ui.detectDevice.setEnabled(True)
    self.ui.sendButton.setEnabled(False)
    self.ui.samplesPerSecondText.setEnabled(True)

  def onConnectButton(self, toggle):

    # clicked connect and the device list has elements
    if toggle and self.ui.portSelectorComboBox.currentText != "":

      self.connected = self.logic.connect(self.ui.portSelectorComboBox.currentText,
                                          self.ui.baudSelectorComboBox.currentText,
                                          self.ui.samplesPerSecondText.text)

      if self.connected:
        self.ui.connectButton.setText("Disconnect")
        self.ui.connectButton.setStyleSheet("background-color:#ff0000")
        self.ui.portSelectorComboBox.setEnabled(False)
        self.ui.baudSelectorComboBox.setEnabled(False)
        self.ui.detectDevice.setEnabled(False)
        self.ui.sendButton.setEnabled(True)
        self.ui.samplesPerSecondText.setEnabled(False)
      else:
        deviceError("Device not found", "Impssible to connect the selected device.", "critical")
        self.ui.connectButton.setChecked(False)
        self.ui.connectButton.setText("Connect")
        self.ui.connectButton.setStyleSheet("background-color:#f1f1f1;")

    # clicked connect but device list has no elements
    elif toggle and self.ui.portSelectorComboBox.currentText == "":
      deviceError("Ports scan", "Any device has been set!", "warning")
      self.ui.connectButton.setChecked(False)
      return

    # clicked disconnect with a running connection
    elif not toggle and self.logic.arduinoConnection is not None and self.connected:
      self.logic.disconnect(disconnectedByUser=True)
      self.ui.connectButton.setText("Connect")
      self.ui.connectButton.setStyleSheet("background-color:#f1f1f1;")
      self.ui.portSelectorComboBox.setEnabled(True)
      self.ui.baudSelectorComboBox.setEnabled(True)
      self.ui.detectDevice.setEnabled(True)
      self.ui.sendButton.setEnabled(False)
      self.ui.samplesPerSecondText.setEnabled(True)

  def onDetectDeviceButton(self, clicked):

    self.ui.portSelectorComboBox.setEnabled(True)
    self.ui.portSelectorComboBox.clear()

    devices = [port.device for port in serial.tools.list_ports.comports() if port[2] != 'n/a']

    if len(devices)==0:
      deviceError("Ports scan", "Any device has been found!", "warning")
    elif len(devices)>0:
      for device in devices:
        self.ui.portSelectorComboBox.addItem(device)

  def onSetIDEButton(self, clicked):
    dialog = qt.QFileDialog()
    self.arduinoIDEExe = dialog.getOpenFileName(None, "Arduino IDE executable", os.path.expanduser("~"))
    self.ui.IDEPathText.setText(self.arduinoIDEExe)

    # Update config
    self.config["IDEExe"] = self.arduinoIDEExe
    self.writeConfig()

  def onRunIDEButton(self, clicked):
    if self.arduinoIDEExe != "":
      subprocess.Popen(self.arduinoIDEExe)

  def onSendButton(self, clicked):
    message = self.ui.messageText.text
    self.logic.sendMessage(message)

  def onMonitorButton(self, clicked):
    monitor = ArduinoMonitor()

  def onPlotterButton(self, clicked):
    if clicked and self.plotter is None:
      self.plotter = ArduinoPlotter(int(self.ui.samplesToPlotText.text))
      self.ui.plotterButton.setText("Stop plotting")

    if not clicked and self.plotter is not None:
      self.plotter.active = False
      self.ui.plotterButton.setText("Plot data")

    if clicked and self.plotter is not None:
      self.plotter.active = True
      self.ui.plotterButton.setText("Stop plotting")

  def onSamplesToPlot(self, event):
    samplesToPlot = int(self.ui.samplesToPlotText.text)
    if self.plotter is not None and samplesToPlot > 0:
      self.plotter.numberOfSamples = samplesToPlot
      self.plotter.initializeTable()

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

  def __init__(self):
    ScriptedLoadableModuleLogic.__init__(self)

    import serial

    self.parameterNode = slicer.mrmlScene.GetFirstNodeByName("arduinoNode")
    self.arduinoConnection = None

  def sendMessage(self, messageToSend):
    if self.arduinoConnection is not None:
      self.arduinoConnection.write(str.encode(messageToSend))
      return True
    else:
      return False

  def connect(self, port=None, baud=None, samplesPerSecond=None):

    if port is not None and baud is not None and samplesPerSecond is not None:
      self.port = port
      self.baud = baud
      self.samplesPerSecond = samplesPerSecond

    self.arduinoEndOfLine = '\n'
    self.arduinoRefreshRateFps = float(self.samplesPerSecond)

    try:
      self.arduinoConnection = serial.Serial(self.port, self.baud)
      self.disconnectedByUser = False
    except serial.serialutil.SerialException:
      return False

    qt.QTimer.singleShot(1000/self.arduinoRefreshRateFps, self.pollSerialDevice)
    return True

  def disconnect(self, disconnectedByUser):
    if disconnectedByUser:
      self.arduinoConnection.close()
    self.disconnectedByUser = disconnectedByUser
    self.arduinoConnection = None

  def pollSerialDevice(self):
    if self.disconnectedByUser:
      return
    try:
        if self.arduinoConnection.isOpen() and self.arduinoConnection.in_waiting == 0: # No messages from arduino
          qt.QTimer.singleShot(1000/self.arduinoRefreshRateFps, self.pollSerialDevice)
        elif self.arduinoConnection.isOpen() and self.arduinoConnection.in_waiting > 0: # Some messages from arduino
          arduinoReceiveBuffer = self.arduinoConnection.readline().decode('ascii')
          if self.arduinoEndOfLine in arduinoReceiveBuffer: # Valid message
            message = arduinoReceiveBuffer.split(self.arduinoEndOfLine)[0]
            message = self.processMessage(message)
            if len(message) >= 1:
              # Fire a message even if the message is unchanged
              if message == self.parameterNode.GetParameter("Data"):
                self.parameterNode.Modified()
              else:
                self.parameterNode.SetParameter("Data", message)

            qt.QTimer.singleShot(1000/self.arduinoRefreshRateFps, self.pollSerialDevice)

    except (IOError, AttributeError):
      self.disconnect(disconnectedByUser=False)
      self.parameterNode.InvokeEvent("EndEvent")
      self.parameterNode.InvokeEvent("ErrorEvent")

      userWantsToReconnect = connectionError()
      if userWantsToReconnect:
        reconnected = self.connect()

        if not reconnected:
          qt.QTimer.singleShot(1000/self.arduinoRefreshRateFps, self.pollSerialDevice)
        else:
          self.parameterNode.InvokeEvent("StartEvent")

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
