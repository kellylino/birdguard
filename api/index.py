from urllib.request import urlopen
from xml.etree.ElementTree import parse
from flask import Flask, render_template

app = Flask(__name__)

drone_info = []


@app.route('/')
def webpage():
    global drone_info
    drone_url = urlopen('https://assignments.reaktor.com/birdnest/drones')
    report = parse(drone_url)
    deviceId = report.find("deviceInformation").get("deviceId")

    return render_template("table.html", deviceId=deviceId)
