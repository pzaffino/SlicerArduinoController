# SlicerArduinoController
Extension for 3D Slicer that allows connecting and receiving/sending data from/to Arduino boards.
Link between Arduino and Slicer can be obtained via serial port (wireless protocol has to come yet).
Data can be used to control Slicer (e.g. modifying scene appearance) by means of data coming from externals sensors, or to control external devices on basis of data coming from Slicer.

Give a look at the [demo](https://youtu.be/8R6LfBqHNPY) presented at the [Virtual Slicer Project Week 2020](https://projectweek.na-mic.org/PW34_2020_Virtual/).

## How to cite SlicerArduino
If you use SlicerArduino, please cite the following article:

Zaffino P, Merola A, Leuzzi D, Sabatino V, Cosentino C, Spadea MF.
SlicerArduino: A Bridge between Medical Imaging Platform and Microcontroller.
Bioengineering. 2020 Sep;7(3):109.

![screenshot](https://raw.githubusercontent.com/pzaffino/SlicerArduinoController/master/ArduinoController_screenshot.png)


# ArduinoMotionSensor

Extension for 3D slicer that allows to control the Slice View through gestures using
an inexpensive motion sensor compatible with Arduino.

## Developers

Paolo Zaffino (Universita’ degli Studi “Magna Græcia” di Catanzaro, Italy)

Maria Francesca Spadea (Universita’ degli Studi “Magna Græcia” di Catanzaro, Italy)

### Students

Virgilio Sabatino (Universita’ degli Studi “Magna Græcia” di Catanzaro, Italy)

## Getting Started

•	Connect PAJ7620 to “Arduino”. To do this simply connect:

       o	Vin to 3.3 V;
  
       o	Gnd to Gnd;
  
       o	SCL to SCL; 
  
       o	SDA to SDA.
  
•	Connect “Arduino” to the USB port of pc and and run “paj7620_9gestures” code on “arduino IDE”. 

       o The code can be found here: “https://github.com/Seeed-Studio/Gesture_PAJ7620”.
  
•	Connect “Arduino” to “3D Slicer” using “Slicer Arduino Controller” extension.

•	On “ArduinoMotionSensor” extension in “3D Slicer”, choose the desidered offset variation and press “Start Motion” button.

## Motion Control Guide

“Left” = Select Previous View

“Right” = Select Next View

“Up” = Increase Offset

“Down” = Decrease Offset

“Forward” = Enable Full Screen

“Backward” = Disable Full Screen

## Reference List

"Module Icon made by Freepik from www.flaticon.com"



