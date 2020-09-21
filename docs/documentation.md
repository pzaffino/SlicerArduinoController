### Menu

* [Home](https://pzaffino.github.io/SlicerArduinoController/index)
* [Examples](https://pzaffino.github.io/SlicerArduinoController/examples)
* [Developers](https://pzaffino.github.io/SlicerArduinoController/developers)
* [How to cite SlicerArduino](https://pzaffino.github.io/SlicerArduinoController/citations)

# Documentation

## Getting started

* From 3D Slicer extension manager
  
  Install the "ArduinoController" extension from the extension manager.
  Available only for the nigthly (preview) relases.

* From source

  Download the source code from github (master branch) and add the "ArduinoConnect" folder to the module paths (Edit menu -> Application Settings -> Modules tab -> Additional module paths (use the arrows on the right of the box)).

## Extension graphical user interface

The GUI extension offers the following capabilities:

* Detect connected serial devices
* Setup baud rate and sampling frequency
* Connect/disconnect the device

* Set and run Arduino IDE

* Send messages
* Show and plot data stream coming from Arduino device

## Details about Slicer integration

SlicerArduino creates a vtkMRMLScriptedModuleNode() and use it for storing data coming from the board.
In this way will be possible to take advantage of the notify mechanism already implemented into the vtkMRMLNode.
The user has just to observe the node and so it will be possible to execute a custom function when a node parameter changes (because it contains a new valure arrived from the board).

Without this system the data read from Arduino would be almost useless, and the integration/cooperation with the Slicer environment strongly limited.

## Receive and send data via python code

Once the device has been connected by using the extension GUI, data can be received and sent via python code.
A template class is:

```python
class ArduinoAppTemplate():
  def __init__(self):

    self.ArduinoNode = slicer.mrmlScene.GetFirstNodeByName("arduinoNode")
    sceneModifiedObserverTag = self.ArduinoNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.doSomethingWhenNewDataIsRead)

  def doSomethingWhenNewDataIsRead(self, caller, event):
    #EXAMPLE TO PRINT THE RECEIVED VALUE:
    print("FIRED! %s" % (self.ArduinoNode.GetParameter("Data")))

  def sendDataToArduino(self, message):
    messageSent = slicer.modules.arduinoconnect.widgetRepresentation().self().logic.sendMessage(message)
```
