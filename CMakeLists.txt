cmake_minimum_required(VERSION 3.13.4)

project(ArduinoController)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/ArduinoController")
set(EXTENSION_CATEGORY "Developer Tools")
set(EXTENSION_CONTRIBUTORS "Paolo Zaffino (Magna Graecia University of Catanzaro, Italy), Domenico Leuzzi (Magna Graecia University of Catanzaro, Italy), Virgilio Sabatino (Magna Graecia University of Catanzaro, Italy), Andras Lasso (PerkLab, Queen's), Maria Francesca Spadea (Magna Graecia University of Catanzaro, Italy)")
set(EXTENSION_DESCRIPTION "Extension for 3D Slicer that allows controlling Slicer using Arduino devices.")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/pzaffino/SlicerArduinoController/master/ArduinoController.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/pzaffino/SlicerArduinoController/master/ArduinoController_screenshot.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(ArduinoConnect)
add_subdirectory(ArduinoMotionSensor)
>>>>>>> 542cd5b95665dd16aa7893a3b6b2e79ee8cd7d5f
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
