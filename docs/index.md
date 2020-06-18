<ul>
  <li {% if page.url contains '/getting_started' %}class="active"{% endif %}><a href="/getting_started.md/">Getting started</a></li>
</ul>

# Slicer Arduino Controller

Extension for 3D Slicer that allows connecting and receiving/sending data from/to Arduino boards.
Link between Arduino and Slicer can be obtained via serial port (wireless protocol has to come yet).
Data can be used to control Slicer (e.g. modifying scene appearance) by means of data coming from externals sensors, or to control external devices on basis of data coming from Slicer.

![screenshot](https://raw.githubusercontent.com/pzaffino/SlicerArduinoController/master/ArduinoController_screenshot.png)