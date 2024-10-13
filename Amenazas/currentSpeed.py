import requests
import json


def get_data(point, zoom, key):
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/{zoom}/json?point={point[1]}%2C{point[0]}&unit=KMPH&openLr=false&key={key}"

    response = requests.get(url)

    if response.status_code == 200:
        datos = response.json()

        result = {
            'currentSpeed': datos['flowSegmentData']['currentSpeed'],
            'freeFlowSpeed': datos['flowSegmentData']['freeFlowSpeed'],
            'roadClosure': datos['flowSegmentData']['roadClosure']
        }

        return result
    else:
        print("error")

        return {}


def create_data(road_segments, key, path="tomtom.json"):
    result = {}

    for road in road_segments:
        result[f"({road[0]}, {road[1]})"] = get_data((road[0], road[1]), 10, key)

    json_object = json.dumps(result)

    with open(path, "w") as file:
        file.write(json_object)
