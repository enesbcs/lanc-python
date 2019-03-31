#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

RecordStart = 0x1833
RecordStop  = 0x8C19

def bin(s):
    return str(s) if s<=1 else bin(s>>1) + str(s&1)

class LANC:
 bitduration = ((104-7)/1000000.0)
 halfbitduration = (52/1000000.0)

 def __init__(self,receivepin,senderpin):
  self.rpin = receivepin
  self.spin = senderpin
  self.lancCmd = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
  self.lancMessage = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(self.rpin, GPIO.IN)
  GPIO.setup(self.spin, GPIO.OUT)
  GPIO.output(self.spin,0)

 def pulseIn(self,pin,value):
    if not value in [0,1]:
     return 0
    scounter = 1
    while GPIO.input(pin)!=value:
     if scounter<1000:
      scounter+=1
     else:
      break
    pstart = time.time()
    while GPIO.input(pin)==value:
     pass
    time_passed = float(time.time()-pstart)*1000000 # convert seconds to microseconds
    return time_passed

 def sendLanc(self,repeats):
    while (pulseIn(self.rpin,1)<5000):
     pass # sync to next LANC message
    while repeats>0:
     for bytenr in range(8):
      time.sleep(self.bitduration)
      for i in range(8*(bytenr+1)):
       if bytenr<2:
        if self.lancCmd[i]:
         GPIO.output(self.spin,1)
        else:
         GPIO.output(self.spin,0)
       time.sleep(self.halfbitduration)
       self.lancMessage[i] = GPIO.input(self.rpin)
       time.sleep(self.halfbitduration)
      GPIO.output(self.spin,0)
      time.sleep(self.halfbitduration)
      while GPIO.input(self.rpin)==1:
       pass
     repeats = repeats - 1

 def createcmdarray(self,cmd):
  tc = str(bin(cmd))
  for i in range(len(self.lancCmd)):
   self.lancCmd[i] = 0
  l = 0
  for i in reversed(range(len(tc))):
   self.lancCmd[l] = int(tc[i])
   l=l+1

 def displaymessage(self):
  print(self.lancMessage)
  for i in range(len(self.lancMessage)):
   self.lancMessage[i] = 0

print("Press CTRL-C if no response")
lcom = LANC(17,27) # Receiver pin: GPIO17, Sender pin: GPIO27
print("Sending record start command")
lcom.createcmdarray(RecordStart)
lcom.sendLanc(4)
time.sleep(10)
lcom.displaymessage()
print("Sending record stop command")
lcom.createcmdarray(RecordStop)
lcom.sendLanc(4)
lcom.displaymessage()
