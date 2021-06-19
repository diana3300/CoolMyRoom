import os
import time
import signal
import sys
import RPi.GPIO as GPIO
import datetime
from w1thermsensor import W1ThermSensor
import imaplib
import email
import smtplib

# Refresh period
sleepTime = 5
# Write information into log file
fileLog = open('/home/pi/fan_control.log', 'w+', 0)

#########################
# Log messages should be time stamped


def timeStamp():
    t = time.time()
    s = datetime.datetime.fromtimestamp(t).strftime('%Y/%m/%d %H:%M:%S - ')
    return s

# Write messages in a standard format


def printMsg(s):
    fileLog.write(timeStamp() + s + "\n")

# Create a class to easily control a pin given the pin's ID


class Pin(object):
    def __init__(self, id):
        try:
            self.pin = id
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.setwarnings(False)
            printMsg("Initialized: run-fan using GPIO pin: " + str(self.pin))
        except:
            printMsg("If method setup doesn't work, need to run script as sudo")
            exit

    # resets all GPIO ports used by this program
    def exitPin(self):
        GPIO.cleanup()

    def set(self, state):
        GPIO.output(self.pin, state)

# Fan class to control fan's functionality


class Fan(object):
    fanOff = True

    def __init__(self):
        self.fanOff = True

    # Turn the fan on or off
    def setFan(self, temp, on, myPin):
        if on:
            printMsg("Turning fan on " + str(temp))
        else:
            printMsg("Turning fan off " + str(temp))
        myPin.set(on)
        self.fanOff = not on


# Temperature class helps getting the temperature
class Temperature(object):

    def __init__(self):
        self.sensor = W1ThermSensor()

    def getTemperature(self):
        print("Temperature is " + str(self.sensor.get_temperature()))
        return self.sensor.get_temperature()


# used to prevend sending multiple emails
lastEmailDetails = ""

# Email communication combines both sending and reading emails  into one class
# given the credentials of the account to be used to send notifications


class MyEmail(object):
    emaill = email
    emailAddr = ""
    password = ""
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    server = smtplib.SMTP('smtp.gmail.com', 587)
    data = ""

    def __init__(self, emailAddrs, password):
        self.emailAddr = emailAddrs
        self.password = password
        self.mail.login(emailAddrs, password)
        self.mail.list()
        self.mail.select('inbox')
        self.server.starttls()
        self.server.login(self.emailAddr, self.password)
        print("Init myEmail")

# Returns last email's subject
    def getLastEmail(self):
        self.mail.list()
        self.mail.select('inbox')
        typ, data = self.mail.search(None, 'ALL')
        ids = data[0]
        id_list = ids.split()
        latest_email_id = int(id_list[-1])

        i = latest_email_id
        typ, data = self.mail.fetch(i, '(RFC822)')

        for response_part in data:
            if isinstance(response_part, tuple):
                msg = self.emaill.message_from_string(response_part[1])
                self.data = str(msg['date'])
                varSubject = msg['subject']
                varFrom = msg['from']

        varFrom = varFrom.replace('<', '')
        varFrom = varFrom.replace('>', '')

        if len(varSubject) > 35:
            varSubject = varSubject[0:32] + '...'

        print('[' + varFrom.split()[-1] + '] ' + varSubject)
        return varSubject

# Sends an email with no subject but with a given text, to a give email address
    def sendEmail(self, dest, text):
        self.server.sendmail(self.emailAddr, dest, text)

    def closeMail(self):
        self.mail.close()
        self.server.quit()

    def getDetails(self):
        return self.data

# Gmail notification sender, sends and proccesses information to and from given gmail addresses


class Notifier(object):
    sendData = ""

    def __init__(self, emailAddr, password, dest):
        self.email = MyEmail(emailAddr, password)
        self.dest = dest

    def sendTemp(self, text):
        self.email.sendEmail(self.dest, text)

    def readEmail(self):
        response = self.email.getLastEmail().lower()
        self.sendData = self.email.getDetails()
        print(self.sendData)
        if(response.find("fan") != -1):
            if(response.find("on") != -1):
                return "on"
            if(response.find("off") != -1):
                return "off"
        if(response.find("temperature") != -1 or response.find("temp") != -1):
            return "temp"
        return ""


#########################
printMsg("Starting: run-fan")

if __name__ == ('__main__'):
    try:
        myPin = Pin(22)
        myFan = Fan()
        myTemp = Temperature()
        emailSrc = "username@gmail.com"
        emailPass = "password"
        emailDest = "destination@gmail.com"
        notifier = Notifier(emailSrc, emailPass, emailDest)
        while True:
            temp = myTemp.getTemperature()
            if(temp > 26):
                print(temp)
                notifier.sendTemp("Warning! Temperature is : "+str(temp))
            elif(temp < 20):
                notifier.sendTemp("Temperature is : " +
                                     str(temp) + ". Fan has been turned off.")
                if(not myFan.fanOff):
                    myFan.setFan(temp, False, myPin)
            message = notifier.readEmail()
            print(notifier.sendData)
            print(lastEmailDetails)
            if(notifier.sendData != lastEmailDetails):
                if(message == "on" and myFan.fanOff is True):
                    myFan.setFan(temp, True, myPin)
                elif(message == "off" and not myFan.fanOff):
                    myFan.setFan(temp, False, myPin)
                elif(message == "temp"):
                    temp = myTemp.getTemperature()
                    print(temp)
                    notifier.sendTemp("Temperature is " + str(temp))
            lastEmailDetails = notifier.sendData
            time.sleep(sleepTime)
    except KeyboardInterrupt:  # trap a CTRL+C keyboard interrupt
        printMsg("keyboard exception occurred")
        myPin.exitPin()
        fileLog.close()
