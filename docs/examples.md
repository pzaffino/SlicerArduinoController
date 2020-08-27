### Menu

* [Home](https://pzaffino.github.io/SlicerArduinoController/index)
* [Documentation](https://pzaffino.github.io/SlicerArduinoController/documentation)
* [Developers](https://pzaffino.github.io/SlicerArduinoController/developers)

# Examples


## Receiving data from Arduino:

In this example, a distance sensor (SHARP 2Y0A2) will be used to edit a Slicer linear transformation.
The transformation can be used to move whatever model/volume in Slicer.

The code for Arduino is the following:
(sensor connected to pin A0)

```C

int sensorpin = 0;                      // analog pin used to connect the sharp sensor
int val = 0;                            // variable to store the values from sensor(initially zero)
float scalefactor = 10.0;               // this depends on the specific slicer scene

void setup()
{
  Serial.begin(9600);                   // starts the serial monitor
}
 
void loop()
{
  val = analogRead(sensorpin);          // reads the value of the sharp sensor
  Serial.println(val * scalefactor);    // prints the value of the sensor to the serial monitor
  delay(200);                           // wait for this much time before printing next value
}

```

The Python code to be written into the Slicer shell is the following:
(set the proper transformation ID according to the specific Slicer scene)

```python
class ExternalTransformationController():
  """
  Class for probe control.
  """
  
  def __init__(self):

    # Get Arduino node from Slicer scene
    self.ArduinoNode = slicer.mrmlScene.GetFirstNodeByName("arduinoNode")
    
    # Add observer to Arduino node and define the function to execute when an parameter is modified
    sceneModifiedObserverTag = self.ArduinoNode.AddObserver(vtk.vtkCommand.ModifiedEvent,
                               self.editTransformation)
    
    # Get Transformation node from the scene
    self.transform = slicer.mrmlScene.GetNodeByID("vtkMRMLLinearTransformNode7")
    
    # Initialize identity matrix to be used for probe translation
    self.matrix = vtk.vtkMatrix4x4()

  def editTransformation(self, caller, event):
    """
    Function ran when an parameter into the Arduino node is modified.
    """
    
    # Edit matrix according to the data read from the distance sensor
    self.matrix.SetElement(1, 3, float(self.ArduinoNode.GetParameter("Data")))
    
    # Update transformation node
    self.transform.SetMatrixTransformToParent(self.matrix)


# Instantiate object, this will enable the quasi-real time probe control
controller = ExternalTransformationController()
```

Once the link has been established by using of SlicerArduino, the data coming from the sensor (move a hand back and forward) will edit the transformation node that in turn will move the associated model/volume.


## Send data to Arduino:
