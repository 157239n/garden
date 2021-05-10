import time, threading, json
from flask import Flask
from gpiozero import LED

app = Flask(__name__)
with open("store") as f: store = [int(elem) for elem in f.readline().strip().split(" ")]
state = {
	"value": 0,
	"remaining": -1, # remaining seconds before switching off
	"schedule": store[:24],
	"scheduleDuration": store[24]
}
lastClock = time.time() # seconds
with open("site.html") as f: site = f.read()
L14 = LED(14); L15 = LED(15); L20 = LED(20); L21 = LED(21)

def on(): state["value"] = 1; L14.on(); L15.on(); L20.on(); L21.on()
def off(): state["value"] = 0; L14.off(); L15.off(); L20.off(); L21.off()
def saveStore():
	with open("store", "w") as f:
		data = [elem for elem in state["schedule"]]
		data.append(state["scheduleDuration"])
		f.write(" ".join(data))

off() # turn off after starting up

@app.route("/state")
def getState(): return json.dumps(state)

@app.route("/turnOn/<int:seconds>")
def turnOn(seconds):
    state["remaining"] = seconds
    on(); return getState()

@app.route("/turnOff")
def turnOff():
    state["remaining"] = -1
    off(); return getState()

@app.route("/changeSchedule/<int:hourWindow>")
def changeSchedule(hourWindow, seconds):
	state["schedule"][hourWindow] = 1 - state["schedule"][hourWindow]
	saveStore(); return getState()

@app.route("/changeScheduleDuration/<int:seconds>")
def changeScheduleDuration(seconds):
	state["scheduleDuration"] = seconds
	saveStore(); return getState()

@app.route("/")
def getSite(): return site

def clock():
    global lastClock; now = time.time()
    state["remaining"] = max(state["remaining"] - (now - lastClock), -1)
    if state["remaining"] < 0: off()
    lastClock = now

    t = time.localtime()
    if state["schedule"][t.tm_hour] == 1 and t.tm_min == 0 and t.tm_sec < 10:
    	turnOn(state["scheduleDuration"])

def set_interval(func, seconds):
    def wrapper(): set_interval(func, seconds); func()
    threading.Timer(seconds, wrapper).start()

set_interval(clock, 1)

app.run(host='0.0.0.0', port=5000)
