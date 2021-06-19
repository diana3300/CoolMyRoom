Team Members:
  Bulea Teodora,
  Vornicu Floris-Diana

Resources:
  hackster.io: https://www.hackster.io/408451/cool-my-room-630a33

Elevator Pitch: Automated gmail based temperature control system for any room

Story: 
  The project is inspired by the unpleasant times when the temperature is high both outside and inside the users' homes. 
  We want to offer the possibility to remotely control the cooling system of the house no matter the location of the user so that when they arrive home,
  the temperature is at a satisfying level.
  The purpose of the project is to be able to control a fan via gmail as the user can request the room temperature at any time. 
  Moreover, the user receives emails when the temperature in the room reaches 26 degrees Celsius or above. 
  After being informed of the temperature, the user can choose to activate or deactivate the fan via gmail. 
  However, the fan will turn off by itself when a preset temperature is reached.

Things used in the project: 
  Hardware Components:
    Raspberry Pi Zero
    Temperature Sensor
    Axial Fan
    General Purpose Transistor NPN
    Resistor 220 ohm X4
    Male/Female Jumper Wires X8
    Breadboard
    Switching Wall Power Supply
  Software OSs, Apps and online services:
    Raspberry Pi Raspbian
    PuTTY
    Python 3.8 
    Python Module for GPIO 


Configuration:

  Install python 3.8 via >sudo apt install python 3.8, check version with >python --version
  Install module for GPIO (> sudo apt-get install python-dev python-rpi.gpio)
  Configure 1-wire interface and temperature sensor
