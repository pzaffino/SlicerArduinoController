### Menu

* [Home](https://pzaffino.github.io/SlicerArduinoController/index)
* [Examples](https://pzaffino.github.io/SlicerArduinoController/examples)
* [Developers](https://pzaffino.github.io/SlicerArduinoController/developers)

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
