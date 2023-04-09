#!/usr/bin/python
# -*- coding: utf-8 -*-

### Based on work from : Edoardo Paolo Scalafiotti <edoardo849@gmail.com> ,Gary Beldon, Miroslav Kuhajda.

import os
import time
import signal
import sys
from datetime import datetime
sys.path.append('/storage/.kodi/addons/virtual.rpi-tools/lib')
import RPi.GPIO as GPIO

### Some basic configuration.
FAN_PIN   = ???   ### RaspberryPi GPIO PI used to drive PWM pin of Fan
WAIT_TIME = 5     ### [s] Time to wait between each refresh ( loop turn )
FAN_MIN   = 0     ### [%] Fan minimum speed.
PWM_FREQ  = 25000 ### [Hz] Change this value if fan has strange behavior

### Configurabled temperature to fan speed.
###
### Raspberry Pi is designed to maximum CPU temperature 85°C so FAN maximum spin is set to 85°C.
###
###          < 20°C =>   0% PWM FAN speed ( FAN stops - no noise )
###     20°C - 29°C =>   0% PWM FAN speed ( FAN stops - no noise )
###     30°C - 39°C =>   0% PWM FAN speed ( FAN stops - no noise )
###     40°C - 49°C =>  25% PWM FAN speed ( FAN spins at 1/4 throttle )
###     50°C - 59°C =>  50% PWM FAN speed ( FAN spins at 1/2 throttle )
###     60°C - 69°C =>  75% PWM FAN speed ( FAN spins at 3/4 throttle )
###     70°C - 79°C => 100% PWM FAN speed ( FAN spins at full throttle )
###          > 80°C => 100% PWM FAN speed ( FAN spins at full throttle )
###
tempSteps  = [20, 30, 40, 50, 60, 70,  80]  ### [°C]
speedSteps = [0,  0,  0,  25, 50, 75, 100]  ### [%]

### Fan speed will change only of the difference of temperature is higher than hysteresis
hyst = 2

### Setup GPIO pin
GPIO.setmode(GPIO.BOARD)
GPIO.setup(FAN_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setwarnings(False)
fan = GPIO.PWM(FAN_PIN, PWM_FREQ)
fan.start(0)

i = 0
cpuTemp = 0
fanSpeed = 0
cpuTempOld = 0
fanSpeedOld = 0

### CHECK - We must set a speed value for each temperature step
if len(speedSteps) != len(tempSteps):
    print("Numbers of temp steps and speed steps are different")
    exit(0)

try:
    while 1:
        ### Read CPU temperature
        cpuTempFile = open("/sys/class/thermal/thermal_zone0/temp", "r")
        cpuTemp = float(cpuTempFile.read()) / 1000
        cpuTempFile.close()

        ### Calculate desired fan speed
        if abs(cpuTemp - cpuTempOld) > hyst:
            ### Below first value, fan will run at min speed.
            if cpuTemp < tempSteps[0]:
                fanSpeed = speedSteps[0]
            ### Above last value, fan will run at max speed
            elif cpuTemp >= tempSteps[len(tempSteps) - 1]:
                fanSpeed = speedSteps[len(tempSteps) - 1]
            ### If temperature is between 2 steps, fan speed is calculated by linear interpolation
            else:
                for i in range(0, len(tempSteps) - 1):
                    if (cpuTemp >= tempSteps[i]) and (cpuTemp < tempSteps[i + 1]):
                        fanSpeed = round((speedSteps[i + 1] - speedSteps[i])
                                         / (tempSteps[i + 1] - tempSteps[i])
                                         * (cpuTemp - tempSteps[i])
                                         + speedSteps[i], 1)
            if fanSpeed != fanSpeedOld:
                if (fanSpeed != fanSpeedOld and (fanSpeed >= FAN_MIN or fanSpeed == 0)):
                    ### If fanSpeed is different from previous loop turn, then print info
                    now = datetime.now()
                    d_local = now.strftime("%d-%m-%Y")
                    t_local = now.strftime("%H:%M:%S")
                    print("date_local='{dl}', time_local='{tl}', cpu_temp='{ct}' ( last_value='{cto}' ), fan_speed='{fs}' ( last_value='{fso}' )".format(dl=d_local, tl=t_local, ct=cpuTemp, fs=fanSpeed, cto=cpuTempOld, fso=fanSpeedOld))
                    ### Change variables and fan speed
                    fan.ChangeDutyCycle(fanSpeed)
                    fanSpeedOld = fanSpeed
            cpuTempOld = cpuTemp

        ### Wait until next refresh
        time.sleep(WAIT_TIME)
    #while 1 loop

### If a keyboard interrupt occurs (ctrl + c), the GPIO is set to 0 and the program exits.
except KeyboardInterrupt:
    print("PWM fan control script interrupted")
    GPIO.cleanup()
    sys.exit()
