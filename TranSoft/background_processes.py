import requests
import json
import time

REQUEST_TYPE = "Internal"
REQUESTOR = "Xmter-BV37"
HANDLE_NON_TRANSMITTED_READINGS_CIRCLE_TIME = 600


def transmitter_integrity_check():
    is_data_transfer_rate_ok = None
    while True:
        time.sleep(5)  # Sleep for 5 seconds
        print("Transmitter Integrity check enable every 5 seconds")
        # Make a GET request to the transmitter integrity check endpoint
        try:
            integrity_check_response = requests.get("http://127.0.0.1:5000/transmitter-integrity-check")
            latest_reading_saved_response = requests.get("http://127.0.0.1:5000/get-latest-reading-saved")
            # Check if the response status code is OK
            if integrity_check_response.status_code == 200 and latest_reading_saved_response.status_code == 200:
                # Parse the JSON response to a Python object
                integrity_check_data = integrity_check_response.json()
                last_saved_data = latest_reading_saved_response.json()
                # Get the last request time from the data
                last_request_time = integrity_check_data["last_request_time"]
                # Get the current time in seconds
                current_time = time.time()
                # Calculate the flag for the data transfer rate by comparing the current time with the last request
                # time plus 600 seconds 600 seconds is the maximum allowed interval between requests
                is_data_transfer_rate_ok = current_time < last_request_time + 600
                if not is_data_transfer_rate_ok or last_saved_data["is_data_transmitted"] == False:
                    master_data = json.dumps({
                        "requestor": REQUESTOR,
                        "order_num": int(time.time() * 1000000),
                        "request_type": REQUEST_TYPE
                    })
                    headers = {"Content-Type": "application/json"}
                    response = requests.post("http://127.0.0.1:5000/get-reading", data=master_data, headers=headers)
            else:
                # Handle non-OK status codes
                print(f"Request failed with status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            # Handle network-related errors
            print(f"Request error: {e}")
        except json.JSONDecodeError as e:
            # Handle JSON parsing errors
            print(f"JSON error: {e}")
    print("Transmitter integrity check thread stopped.")


def handle_non_transmitted_readings():
    # define the dictionary of parameters
    params = {
        "time_in_seconds": HANDLE_NON_TRANSMITTED_READINGS_CIRCLE_TIME + 60
    }
    while True:
        time.sleep(2)  # Sleep for 2 seconds
        time.sleep(HANDLE_NON_TRANSMITTED_READINGS_CIRCLE_TIME)  # Sleep for 600 seconds or 10 minutes
        print("Handle non transmitted readings every 2 minutes")
        # Make a GET request to the transmitter integrity check endpoint
        try:
            last_non_transmitted_readings = requests.get("http://127.0.0.1:5000/last_non_transmitted_readings")
            # Check if the response status code is OK
            if last_non_transmitted_readings.status_code == 200:
                last_non_transmitted_readings_data = last_non_transmitted_readings.json()
                print(last_non_transmitted_readings_data)
        except requests.exceptions.RequestException as e:
            # Handle network-related errors
            print(f"Request error: {e}")
        except json.JSONDecodeError as e:
            # Handle JSON parsing errors
            print(f"JSON error: {e}")


handle_non_transmitted_readings()
