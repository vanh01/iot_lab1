import json
import time
import paho.mqtt.client as mqttclient
import subprocess
import re

print("Iot Gateway")

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "KeOxFjq2fKD3DgCvsSwr"


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setValue":
            temp_data['value'] = jsonobj['params']
            client.publish('v1/devices/me/attributes',
                           json.dumps(temp_data), 1)
    except:
        pass


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

temp = 30
humi = 50
light_intesity = 100
counter = 0

longitude = 106.7
latitude = 10.6


def getCurentLocation():
    p = subprocess.Popen(["powershell.exe", "Add-Type -A System.Device;($a=[Device.Location.GeoCoordinateWatcher]::new()).Start();for(;($b=$a|% Po*n|% L*)|% I*){}$b|select L*e"],
                         stdin=sp.PIPE, stdout=sp.PIPE, stderr=subprocess.STDOUT, text=True)
    p.communicate()
    (out, err) = p.communicate()
    # output :
    #
    #     Latitude        Longitude
    #     --------        ---------
    #     18.476689671821 105.713650936646
    #
    out = re.split('\n', out)

    outt = out[3].split(' ')  # out[3]: 18.476689671821 105.713650936646
    global latitude
    global longitude
    latitude = float(outt[0])
    longitude = float(outt[1])


while True:
    getCurentLocation()
    collect_data = {'temperature': temp,
                    'humidity': humi, 'light': light_intesity, 'longitude': longitude, 'latitude': latitude}
    temp += 1
    humi += 1
    light_intesity += 1
    client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    time.sleep(5)
