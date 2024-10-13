import requests

url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/10/json?point=52.41072%2C4.84239&unit=KMPH&openLr=false&key=HXrIieVQprYHX2oB6vi02KA4LU2fd1cl"
response = requests.get(url)

if response.status_code == 200:
    datos = response.json()

    print(f"CurrentSpeed: {datos['flowSegmentData']['currentSpeed']}")
    print(f"FreeFlowSpeed: {datos['flowSegmentData']['freeFlowSpeed']}")
else:
    print("error")
