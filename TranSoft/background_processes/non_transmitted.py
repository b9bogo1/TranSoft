# from datetime import datetime, timedelta
from threading import Thread
import time
import requests
import json

from TranSoft import db
from TranSoft.models import Reading

# Define some constants
QUERY_TIME = 12  # minutes
CIRCLE_TIME = 10  # seconds
NON_TRANSMITTED_READINGS_URL = "http://127.0.0.1:5000/handle-non-transmitted-readings"


class HandleNonTransmittedReadings(Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True

    def run(self):
        while True:
            print("Handle non transmitted readings every 10 minutes")
            # Make a GET request to the transmitter integrity check endpoint
            try:
                last_non_transmitted_readings = requests.get(
                    f"{NON_TRANSMITTED_READINGS_URL}/{QUERY_TIME}"
                )
                # Check if the response status code is OK
                if last_non_transmitted_readings.status_code == 200:
                    last_non_transmitted_readings_data = last_non_transmitted_readings.json()
                    print(last_non_transmitted_readings_data)
                else:
                    # Handle non-OK status codes
                    print(f"Request failed with status code {last_non_transmitted_readings.status_code}")
            except requests.exceptions.RequestException as e:
                # Handle network-related errors
                print(f"Request error: {e}")
            except json.JSONDecodeError as e:
                # Handle JSON parsing errors
                print(f"JSON error: {e}")
            time.sleep(CIRCLE_TIME)
