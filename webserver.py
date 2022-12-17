import time, threading, json, os, pickle as dill
from flask import Flask
from gpiozero import LED
import dill

os.chdir("/home/pi/repos/garden")

def replaceInFile(file, _from, _to):
    with open(file) as f: data = f.read().replace(str(_from), str(_to))
    with open(file, "w") as f: f.write(data)

app = Flask(__name__)
def sampleState():
    return {"value": 0,
            "remaining": -1, # remaining seconds before switching off
            "schedule": [0]*24,
            "scheduleDuration": 60,
            "activatedTime": 0 } # for total time on today
pins = [14, 15, 20, 21]; states = {i:sampleState() for i in pins}
def saveStore():
    with open("store", "wb") as f: f.write(dill.dumps(states))
if not os.path.exists("store"): saveStore()
with open("store", "rb") as f: states = dill.loads(f.read())
lastClock = time.time() # seconds
with open("site.html") as f: site = f.read()
leds = {i:LED(i) for i in pins}

def on(i): states[i]["value"] = 1; leds[i].on()
def off(i): states[i]["value"] = 0; leds[i].off()

for i in pins: off(i) # turn off after starting up

@app.route("/state")
def getState(): return json.dumps(states)

@app.route("/turnOn/<int:pin>/<int:seconds>")
def turnOn(pin, seconds):
    states[pin]["remaining"] = seconds
    on(pin); return getState()

@app.route("/turnOff/<int:pin>")
def turnOff(pin):
    states[pin]["remaining"] = -1
    off(pin); return getState()

@app.route("/changeSchedule/<int:pin>/<int:hourWindow>")
def changeSchedule(pin, hourWindow):
    states[pin]["schedule"][hourWindow] = 1 - states[pin]["schedule"][hourWindow]
    saveStore(); return getState()

@app.route("/changeScheduleDuration/<int:pin>/<int:seconds>")
def changeScheduleDuration(seconds):
    states[pin]["scheduleDuration"] = seconds
    saveStore(); return getState()

@app.route("/")
def getSite(): return site.replace("let states = {};", f"let states = {getState()};")

def clock():
    global lastClock; now = time.time()
    for pin in pins:
        if states[pin]["value"]: states[pin]["activatedTime"] += now - lastClock;
        states[pin]["remaining"] = max(states[pin]["remaining"] - (now - lastClock), -1)
        if states[pin]["remaining"] < 0: off(pin)

        t = time.localtime()
        if states[pin]["schedule"][t.tm_hour] == 1 and t.tm_min == 0 and t.tm_sec < 10 and states[pin]["scheduleDuration"] > 0:
            turnOn(pin, states["scheduleDuration"])
        if t.tm_hour == 0 and t.tm_min == 0 and t.tm_sec < 10:
            states[pin]["activatedTime"] = 0
    lastClock = now

def set_interval(func, seconds):
    def wrapper(): set_interval(func, seconds); func()
    threading.Timer(seconds, wrapper).start()

set_interval(clock, 1)

app.run(host='0.0.0.0', port=5000)

