### Menu

* [Home](https://pzaffino.github.io/SlicerArduinoController/index)
* [Documentation](https://pzaffino.github.io/SlicerArduinoController/documentation)
* [Developers](https://pzaffino.github.io/SlicerArduinoController/developers)
* [How to cite SlicerArduino](https://pzaffino.github.io/SlicerArduinoController/citations)

# Examples


## Receiving data from Arduino:

In this example, a distance sensor (SHARP 2Y0A2) will be used to edit a Slicer linear transformation.
The transformation can be used to translate whatever model/volume in Slicer.

The code for Arduino is the following (sensor connected to pin A0):

```cpp

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

The code to be written into the Python shell embedded in Slicer is the following (set the proper transformation node ID according to the specific Slicer scene):

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
    self.matrix.SetElement(2, 3, float(self.ArduinoNode.GetParameter("Data")))
    
    # Update transformation node
    self.transform.SetMatrixTransformToParent(self.matrix)
    
    # Refresh Slicer views
    slicer.util.resetSliceViews()

# Instantiate object, this will enable the quasi-real time probe control
controller = ExternalTransformationController()
```

Once the link has been established by using of SlicerArduino, the data coming from the sensor (move a hand back and forward) will edit the transformation node that, in turn, will move the associated model/volume.


## Send data to Arduino:

In this example a linear servomotor (Actuonix L16 Actuator 50mm) is controlled by using a translation computed by Slicer.
The example mimics a radiotherapy couch correction on basis of the alignment of daily and planning CTs.

The Arduino code is (sensor connected to pin 9):
```cpp
/*
 * range servo ms 1000 -- 2000 -> 0 -- 4.8 cm
 * 1 ms -> 0.0048 cm
 * 1 cm -> 208.3 ms
 */

//Includes
#include <Servo.h>

//Defines
#define LINEARACTUATORPIN 9      //Linear Actuator Digital Pin

Servo LINEARACTUATOR;           // create servo objects to control the linear actuator

int minValue = 1000;
int maxValue = 2000;
float translation;

void setup()
{  
  Serial.begin(9600);
  
  //initialize servo/linear actuator objects
  LINEARACTUATOR.attach(LINEARACTUATORPIN, minValue, maxValue);   // attaches/activates the linear actuator as a servo object    
 
  //use the writeMicroseconds to set the linear actuators to their default positions
  LINEARACTUATOR.writeMicroseconds(minValue);
  delay(1000);

}

void loop()
{
  delay(100);

  if (Serial.available() > 0)
  {
    translation = Serial.parseFloat() * 0.1; // Slicer use mm
    //Serial.println(translation);
      
    if (translation <= 4.8) // max displacement
    {
      LINEARACTUATOR.writeMicroseconds(minValue + (translation*208.3));
      }    
    
    }

}

```

The code to be written into the Python shell embedded in Slicer is the following (set the proper transformation node ID according to the specific Slicer scene):

```python
# Get transformation node from Slicer scene
transformation_node = slicer.mrmlScene.GetNodeByID("vtkMRMLLinearTransformNode4")

# Get transformation matrix from node
transformation_matrix = transformation_node.GetMatrixTransformFromParent()

# Get z translation
z_translation = transformation_matrix.GetElement(2,3)

# Send translation to Arduino board
slicer.modules.arduinoconnect.widgetRepresentation().self().logic.sendMessage("%.3f" % (z_translation))
```
