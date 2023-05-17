from threading import Thread
import time
import requests
import json
from TranSoft.configs_local import get_node

NODE = get_node()

# Define some constants
QUERY_TIME = 12  # minutes
CIRCLE_TIME = 10  # seconds
NON_TRANSMITTED_READINGS_URL = f"http://{NODE['ip']}:{NODE['port']}/handle-non-transmitted-readings"
GET_MASTER_NODES_URL = f"http://{NODE['ip']}:{NODE['port']}/system-data-update"


class HandleNonTransmittedReadings(Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True

    def run(self):
        global MASTER_NODE_LIST
        while True:
            print(f"HandleNonTransmittedReadings(Thread) running every {CIRCLE_TIME} seconds")
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
                    if len(last_non_transmitted_readings_data) >= 1:
                        global master_node
                        master_nodes = requests.get(GET_MASTER_NODES_URL).json()
                        for node in master_nodes:
                            if node['power'] == len(master_nodes) - 1:
                                master_node = node
                        url = f"http://{master_node['ip']}:{master_node['port']}/save-unsaved-readings"
                        for reading in last_non_transmitted_readings_data:
                            reading_data = json.dumps(reading)
                            headers = {"Content-Type": "application/json"}
                            sent_non_transmitted_data = requests.post(url, data=reading_data, headers=headers)
                            if not sent_non_transmitted_data.status_code == 200:
                                print("Saving non Saved reading failed...")
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
