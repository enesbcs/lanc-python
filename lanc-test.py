#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

RecordStart = [0x18,0x33]
RecordStop  = [0x8C,0x19]

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
    while (pulseIn(self.rpin,1)<5000): # sync to next LANC message
     pass
    while repeats>0:
     for bytenr in range(8):
      time.sleep(self.bitduration)     # LOW after long pause means the START bit of Byte 0 is here, wait START bit duration
      for i in range(8*(bytenr+1)):
       if bytenr<2:
        if self.lancCmd[i]:            # During the first two bytes the adapter controls the line and puts out data
         GPIO.output(self.spin,1)
        else:
         GPIO.output(self.spin,0)
       time.sleep(self.halfbitduration)
       self.lancMessage[i] = GPIO.input(self.rpin) # Read data line during middle of bit
       time.sleep(self.halfbitduration)
      GPIO.output(self.spin,0)
      time.sleep(self.halfbitduration)             # Make sure to be in the stop bit before waiting for next byte
      while GPIO.input(self.rpin)==1:              # Loop as long as the LANC line is +5V during the stop bit or between messages
       pass
     repeats = repeats - 1

 def createcmdarray(self,cmd):  # This function fills the lancCmd array with the bits in the order they should be sent
  for i in range(len(self.lancCmd)):
   self.lancCmd[i] = 0
  for i in range(len(cmd)):
   bs = str(bin(cmd[i]))
   ba = (i*8)
   L = 0
   for ls in reversed(range(len(bs))):     # First byte 1 then byte 2 but with LSB first for both bytes
    try:
     self.lancCmd[ba+L] = int(bs[ls])
    except:
     self.lancCmd[ba+L] = 0
    L=L+1

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
