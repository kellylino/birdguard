import math
import json
from datetime import datetime, timedelta
from urllib.request import urlopen
from xml.etree.ElementTree import parse
from flask import Flask, render_template, jsonify

app = Flask(__name__)


drone_info = []


@app.route('/')
def webpage():
    global drone_info
    drone_url = urlopen('https://assignments.reaktor.com/birdnest/drones')
    report = parse(drone_url)

    # find out the violated no drone zone rule pilots
    for drone in report.iterfind("capture/drone"):
        x = math.pow(abs(float(drone.findtext("positionX")) - 250000), 2) + math.pow(
            abs(float(drone.findtext("positionY")) - 250000), 2)
        distance = math.sqrt(x)
        if distance <= 100000:
            mydict = {}
            now = datetime.now()
            drone.findtext("serialNumber")
            mydict["serialNumber"] = drone.findtext("serialNumber")
            mydict["datetime"] = now.strftime("%d/%m/%Y %H:%M:%S")
            mydict["distance"] = distance
            drone_info.append(mydict)

    # stored the needed relative information of the pilot
    for i in drone_info:
        serialNumber_url = urlopen("https://assignments.reaktor.com/birdnest/pilots/" + i["serialNumber"])
        data_json = json.loads(serialNumber_url.read())
        i["firstName"] = data_json["firstName"]
        i["lastName"] = data_json["lastName"]
        i["email"] = data_json["email"]
        i["phoneNumber"] = data_json["phoneNumber"]

    # find out the closest distance
    closest_distance = 100
    new_drone_info = []
    for i in drone_info:
        if datetime.now() - datetime.strptime(i["datetime"], "%d/%m/%Y %H:%M:%S") < timedelta(minutes=10):
            if i["distance"] < closest_distance:
                closest_distance = i["distance"]
                new_drone_info.append(i)

    drone_info = new_drone_info
    return render_template("table.html", len=len(drone_info), drone_info=drone_info, closest_distance=closest_distance)


@app.route('/update', methods=["GET"])
# update part of the webpage content
def update():
    global drone_info
    drone_url = urlopen('https://assignments.reaktor.com/birdnest/drones')
    report = parse(drone_url)

    for drone in report.iterfind("capture/drone"):
        x = math.pow(abs(float(drone.findtext("positionX")) - 250000), 2) + math.pow(
            abs(float(drone.findtext("positionY")) - 250000), 2)
        distance = math.sqrt(x)
        if distance <= 100000:
            distance = int(distance/1000)
            mydict = {}
            now = datetime.now()
            drone.findtext("serialNumber")
            mydict["serialNumber"] = drone.findtext("serialNumber")
            mydict["datetime"] = now.strftime("%d/%m/%Y %H:%M:%S")
            mydict["distance"] = distance
            drone_info.append(mydict)

    for i in drone_info:
        serialNumber_url = urlopen("https://assignments.reaktor.com/birdnest/pilots/" + i["serialNumber"])
        data_json = json.loads(serialNumber_url.read())
        i["firstName"] = data_json["firstName"]
        i["lastName"] = data_json["lastName"]
        i["email"] = data_json["email"]
        i["phoneNumber"] = data_json["phoneNumber"]

    closest_distance = 100
    new_drone_info = []
    for i in drone_info:
        if datetime.now() - datetime.strptime(i["datetime"], "%d/%m/%Y %H:%M:%S") < timedelta(minutes=10):
            if i["distance"] < closest_distance:
                closest_distance = i["distance"]
                new_drone_info.append(i)

    drone_info = new_drone_info

    return jsonify({"drone_info": drone_info, "closest_distance": closest_distance})

