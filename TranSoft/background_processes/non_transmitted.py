# from datetime import datetime, timedelta
from threading import Thread
import time
import requests
import json

NODE = {
    "ip": "127.0.0.1",
    "hostname": "Xmter-5",
    "site": "BV05",
    "PORT": "60205"
}

# Define some constants
QUERY_TIME = 12  # minutes
CIRCLE_TIME = 10  # seconds
NON_TRANSMITTED_READINGS_URL = f"http://{NODE['ip']}:{NODE['PORT']}/handle-non-transmitted-readings"
GET_MASTER_NODES_URL = f"http://{NODE['ip']}:{NODE['PORT']}/system-data-update"


class HandleNonTransmittedReadings(Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True

    def run(self):
        global MASTER_NODE_LIST
        while True:
            print("HandleNonTransmittedReadings(Thread) running")
            # Make a GET request to the transmitter integrity check endpoint
            try:
                master_node_list = requests.get(GET_MASTER_NODES_URL)
                if master_node_list.status_code == 200:
                    MASTER_NODE_LIST = master_node_list.json()
                last_non_transmitted_readings = requests.get(
                    f"{NON_TRANSMITTED_READINGS_URL}/{QUERY_TIME}"
                )
                # Check if the response status code is OK
                if last_non_transmitted_readings.status_code == 200:
                    last_non_transmitted_readings_data = last_non_transmitted_readings.json()
                    print(last_non_transmitted_readings_data)
                else:
                    # Handle non-OK status codes
                    print(f"Request failed: last_non_transmitted_readings")
            except requests.exceptions.RequestException as e:
                # Handle network-related errors
                print(f"RequestException error: HandleNonTransmittedReadings(Thread) while loop")
            except json.JSONDecodeError as e:
                # Handle JSON parsing errors
                print(f"JSON error: HandleNonTransmittedReadings(Thread) while loop")
            time.sleep(CIRCLE_TIME)
