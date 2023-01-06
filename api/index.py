import math
import json
import time
from datetime import datetime, timedelta
from urllib.request import urlopen
from xml.etree.ElementTree import parse
from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from threading import Lock


app = Flask(__name__)


pilot_info = []
closest_distance = 100
data_lock = Lock()


def service():
    print(time.ctime(), "Service")

    global pilot_info, closest_distance
    with data_lock:
        drone_url = urlopen('https://assignments.reaktor.com/birdnest/drones')
        report = parse(drone_url)
        capture = report.find("capture")

        # find out the violated no drone zone rule pilots
        for drone in report.iterfind("capture/drone"):
            x = math.pow(abs(float(drone.findtext("positionX")) - 250000), 2) + math.pow(
                abs(float(drone.findtext("positionY")) - 250000), 2)
            distance = math.sqrt(x)
            if distance <= 100000:
                distance = int(distance / 1000)
                if distance < closest_distance:
                    closest_distance = distance
                mydict = {}
                drone.findtext("serialNumber")
                mydict["serialNumber"] = drone.findtext("serialNumber")
                mydict["datetime"] = datetime.strptime(capture.get("snapshotTimestamp"), "%Y-%m-%dT%H:%M:%S.%fZ")
                mydict["distance"] = distance
                pilot_info.append(mydict)

        # stored the needed relative information of the pilot
        for i in pilot_info:
            serialNumber_url = urlopen("https://assignments.reaktor.com/birdnest/pilots/" + i["serialNumber"])
            data_json = json.loads(serialNumber_url.read())
            i["firstName"] = data_json["firstName"]
            i["lastName"] = data_json["lastName"]
            i["email"] = data_json["email"]
            i["phoneNumber"] = data_json["phoneNumber"]

        # find out the closest distance
        if len(pilot_info) > 0:
            new_pilot_info = []
            latest_snapshot_time = pilot_info[-1]["datetime"]
            for i in pilot_info:
                if latest_snapshot_time - i["datetime"] < timedelta(minutes=10):
                    new_pilot_info.append(i)

            pilot_info = new_pilot_info
        return pilot_info, closest_distance


@app.route('/')
def webpage():
    with data_lock:
        return render_template("table.html")


@app.route('/update', methods=["GET"])
# update part of the webpage content
def update():
    with data_lock:
        return jsonify({"pilot_info": pilot_info, "closest_distance": closest_distance})


_scheduler = BackgroundScheduler()
_scheduler.add_job(service, "interval", seconds=2)
_scheduler.start()
