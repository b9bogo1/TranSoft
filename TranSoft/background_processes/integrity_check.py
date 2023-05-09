from threading import Thread
from flask import current_app
from TranSoft import db
from TranSoft.models import Reading
import requests
import uuid
import time
import json
from TranSoft.local_configs import PRODUCTION
from flask import Blueprint

if not PRODUCTION:
    NODE = {
        "ip": "127.0.0.1",
        "hostname": "Xmter-5",
        "site": "BV05",
        "PORT": "60205"
    }
else:
    NODE = {
        "ip": "10.0.0.5",
        "hostname": "Xmter-5",
        "site": "BV05",
        "PORT": "80"
    }

# Define some constants
REQUEST_TYPE = "Internal"
TRANSMITTER_INTEGRITY_CHECK_URL = f"http://{NODE['ip']}:{NODE['PORT']}/transmitter-integrity-check"
GET_LAST_READING_URL = f"http://{NODE['ip']}:{NODE['PORT']}/get-latest-reading-saved"
GET_READINGS_URL = f"http://{NODE['ip']}:{NODE['PORT']}/get-reading"


class TransmitterIntegrityCheck(Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True

    def run(self):
        while True:
            print("Transmitter Integrity check enable every 5 seconds")
            # Make a GET request to the transmitter integrity check endpoint
            try:
                integrity_check_response = requests.get(TRANSMITTER_INTEGRITY_CHECK_URL)
                latest_reading_saved_response = requests.get(GET_LAST_READING_URL)
                # Check if the response status code is OK
                if integrity_check_response.status_code == 200 and latest_reading_saved_response.status_code == 200:
                    # Parse the JSON response to a Python object
                    integrity_check_data = integrity_check_response.json()
                    last_saved_data = latest_reading_saved_response.json()
                    # Get the last request time from the data
                    # last_request_time = integrity_check_data["last_request_time"]
                    last_request_time = last_saved_data["last_rx"] / 1000000
                    # Get the current time in seconds
                    current_time = time.time()
                    # Calculate the flag for the data transfer rate by comparing the current time with the last
                    # request time plus 600 seconds 600 seconds is the maximum allowed interval between requests
                    is_data_transfer_rate_ok = current_time < last_request_time + 600
                    if not is_data_transfer_rate_ok or last_saved_data["is_data_transmitted"] is False:
                        master_data = json.dumps({
                            "requestor": NODE['hostname'],
                            "order_num": int(time.time() * 1000000),
                            "request_type": REQUEST_TYPE
                        })
                        headers = {"Content-Type": "application/json"}
                        response = requests.post(GET_READINGS_URL, data=master_data, headers=headers)
                        if response.status_code is 500:
                            print("DAT8014 not operating as expected")
                        print("Auto saving activated internally")
                else:
                    # Handle non-OK status codes
                    print(f"Request failed with status code {response.status_code}")
            except requests.exceptions.RequestException as e:
                # Handle network-related errors
                print(f"Request error: {e}")
            except json.JSONDecodeError as e:
                # Handle JSON parsing errors
                print(f"JSON error: {e}")
            time.sleep(1)
