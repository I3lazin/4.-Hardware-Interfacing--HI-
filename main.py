from machine import Pin
import time

# Pin definitions
vibrSens = Pin(5, Pin.IN) # Vibration sensor input
redAct = Pin(4, Pin.OUT) # Red actuator output
yelAct = Pin(2, Pin.OUT) # Yellow actuator output
greAct = Pin(1, Pin.OUT) # Green actuator output
btn = Pin(38, Pin.IN, Pin.PULL_DOWN) # Reset button input

# global variables
isVibrating = False
firstVibrationTime = 0
lastVibrationTime = 0
activeMs = 0
alreadyDetected = False
currentState = "Safe"
lastDuration = 0
lastDurationStart = f"{time.localtime()[3]:02d}:{time.localtime()[4]:02d}:{time.localtime()[5]:02d} on {time.localtime()[2]:02d}/{time.localtime()[1]:02d}/{time.localtime()[0]}"


# Detect start of vibration
def vibrationStarted():
    global isVibrating, firstVibrationTime, lastVibrationTime, alreadyDetected, activeMs, lastDurationStart

    if vibrSens.value() == 0:
        if not isVibrating:
            firstVibrationTime = time.ticks_ms()
            lastVibrationTime = firstVibrationTime
            lastDurationStart = f"{time.localtime()[3]:02d}:{time.localtime()[4]:02d}:{time.localtime()[5]:02d} on {time.localtime()[2]:02d}/{time.localtime()[1]:02d}/{time.localtime()[0]}"
            activeMs = 0
            isVibrating = True

        elif isVibrating and not alreadyDetected:
            now = time.ticks_ms()
            activeMs += time.ticks_diff(now, lastVibrationTime)
            lastVibrationTime = now
            alreadyDetected = True

    if isVibrating and vibrSens.value() == 1 and alreadyDetected:
        activeMs += time.ticks_diff(time.ticks_ms(), lastVibrationTime)
        alreadyDetected = False


#  Detect end of vibration and calculate total time
def detectVibrationEnd():
    global isVibrating, firstVibrationTime, lastVibrationTime, lastDuration, lastDurationStart
    timeout = 300 # milliseconds
    quietTime = time.ticks_diff(time.ticks_ms(), lastVibrationTime)

    if quietTime > timeout:
        totalVibrationTime = activeMs / 1000
        isVibrating = False
        lastDuration = totalVibrationTime
        determineState(totalVibrationTime)


# Determine state based on vibration time      
def determineState(vibTime):
    global currentState
    if vibTime > 1 and vibTime <= 3 and currentState != "Warning" and currentState != "Danger":
        currentState = "Safe"
    elif vibTime > 3 and vibTime <= 5 and currentState != "Danger":
        currentState = "Warning"
    elif vibTime > 5:
        currentState = "Danger"
    elif vibTime <= 1:
        currentState = "Danger"
    updateActuators(currentState)

# Update actuators based on current state
def updateActuators(state):
    # reset all actuators
    for pin in [greAct, yelAct, redAct]:
        pin.value(0)

    # select actuator based on state
    if state == "Safe":
        greAct.value(1)
    elif state == "Warning":
        yelAct.value(1)
    elif state == "Danger":
        redAct.value(1)

# Main loop
def main():
    global currentState, lastDuration, lastDurationStart, isVibrating
    while True:
        vibrationStarted()
        if isVibrating:
            detectVibrationEnd()
        if btn.value() == 1 and currentState == "Danger":
            print("Resetting to Safe state.")
            currentState = "Safe"
            time.sleep(0.5)
            updateActuators(currentState)
        if time.ticks_ms() % 5000 == 0:
            print(f"Current State: {currentState}, Last Vibration Duration: {lastDuration:0.2f} seconds, measured at {lastDurationStart}")  
            printed = True
            time.sleep(0.01)

        #testcases
        #TC1
        #print(vibrSens.value())  



    
main()