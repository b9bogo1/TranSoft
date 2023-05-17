from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort
import time
from datetime import datetime, timedelta
from TranSoft.auth import login_required
from TranSoft import db
from TranSoft.models import Reading
from TranSoft.transmitter import get_resistance_from_dat8014, resistance_to_temperature
from TranSoft.configs_local import PRODUCTION, get_node

bp = Blueprint('reading', __name__)

NODE = get_node()

XMTER_ID = NODE['hostname']
MAX_INTERNAL_LIMIT = 6
Request_Type = "Internal"

NODE_IP = f"{NODE['ip']}:{NODE['port']}"

# Create a dictionary of empty lists for different types of nodes
SYSTEM_NODES = {key: [] for key in
                ["master_list", "transmitter_list", "data_server_list", "maintenance_pc_list", "interface_list"]}


# Define a function that returns the timestamp of the last reading request from an external source
def last_request_time():
    # query the Reading table and get the most recent record by created_at column
    reading = Reading.query.order_by(Reading.created_at.desc()).first()
    # check if the query returned a result
    if reading:
        # return the last_rx attribute of the reading object
        return reading.last_rx
    else:
        # return None or some default value if no result was found
        return None


@bp.route('/')
@login_required
def index():
    # Render an HTML template that displays the readings list
    return render_template('reading/index.html')


# Define a route for handling a POST request to get a reading from a sensor
@bp.route('/get-reading', methods=['POST'])
def get_reading():
    global resistances
    # Get the current timestamp in microseconds
    last_rx = int(time.time() * 1000000)
    # Check if the request is a JSON request
    if not request.is_json:
        # Return a 400 Bad Request error with a message
        return jsonify({"error": "Invalid JSON request"}), 400
    # Get the JSON data from the request
    requestor_data = request.json
    # Get the current timestamp in microseconds for the reading request event
    last_rrq = int(time.time() * 1000000)
    # Call a function to get the resistance values from the sensor
    try:
        resistances = get_resistance_from_dat8014()
    except Exception as e:
        resistances = (None, None)
        # do something with e
        print("Error occurred while requesting resistances: Line 68 in reading.py")
    # Check if the result is a tuple of two None values
    if resistances == (None, None):
        # Return a 500 Internal Server Error with a message
        return jsonify({"error": "Failed to read from the device"}), 500
    # Get the current timestamp in microseconds for the reading response event
    last_rrs = int(time.time() * 1000000)
    # Create a new Reading object with the sensor data and the requestor data
    new_reading = Reading(trans_id=XMTER_ID,
                          rtd_1=resistances[0],  # Resistance value of the first RTD sensor
                          rtd_2=resistances[1],  # Resistance value of the second RTD sensor
                          order_num=requestor_data["order_num"],  # Order number from the requestor
                          requestor_id=requestor_data["requestor"],  # Requestor ID from the requestor
                          temp_1=resistance_to_temperature(resistances[0]),  # Temperature value of the first RTD
                          # sensor calculated from the resistance
                          temp_2=resistance_to_temperature(resistances[1]),  # Temperature value of the second RTD
                          # sensor calculated from the resistance
                          last_rrq=last_rrq,
                          last_rrs=last_rrs,
                          last_rx=last_rx
                          )
    # Add the new Reading object to the database session
    db.session.add(new_reading)
    # Commit the changes to the database
    db.session.commit()
    # Refresh the new reading object with the latest state from the database
    db.session.refresh(new_reading)
    # Update the is_data_transmitted attribute to True and the last_tx attribute to the current timestamp
    if requestor_data["request_type"] == "External":
        new_reading.is_data_transmitted = True
        Request_Type = "External"
    Request_Type = "Internal"
    new_reading.last_tx = int(time.time() * 1000000)
    # Commit the changes to the database
    db.session.commit()
    # Get the latest reading from the database or None if no row is found
    reading = Reading.query.order_by(Reading.created_at.desc()).first()
    # Check if the reading is None
    if reading is None:
        # Return a 404 Not Found error with a message
        return jsonify({"error": "No reading found"}), 404
    # Convert the row to a dictionary
    data = reading.__dict__
    # Remove the non-JSON serializable attributes
    data.pop("_sa_instance_state", None)
    # Convert the datetime object to a string
    data["created_at"] = data["created_at"].strftime("%Y-%m-%d %H:%M:%S")
    # Return a JSON response with the reading data
    return jsonify(data)


@bp.route('/get-latest-reading-saved', methods=['GET'])
def latest_reading_saved():
    reading = Reading.query.order_by(Reading.created_at.desc()).first()
    if reading is None:
        # Return a 404 Not Found error with a message
        return jsonify({"error": "No reading found"}), 404
    reading_dict = reading.as_dict()
    # Convert the datetime object to a string using isoformat method
    reading_dict["created_at"] = reading_dict["created_at"].isoformat(timespec="microseconds")
    return jsonify(reading_dict)


# Define a route for handling a GET request to get a list of readings from the database
@bp.route('/internal-reading-list', methods=['GET'])
def internal_reading_list():
    # Get the latest readings from the database up to the limit
    last_readings = Reading.query.order_by(Reading.created_at.desc()).limit(MAX_INTERNAL_LIMIT).all()
    # Create an empty list to store the reading dictionaries
    data = []
    # Loop through each reading object
    for reading in last_readings:
        # Convert the row to a dictionary using the as_dict method
        reading_dict = reading.as_dict()
        # Convert the datetime object to a string using isoformat method with timespec argument
        reading_dict["created_at"] = reading_dict["created_at"].isoformat(timespec="seconds")
        # Append the reading dictionary to the data list
        data.append(reading_dict)
        # Return a JSON response with the data list
    return jsonify(data)


@bp.route('/system-data-update', methods=["GET", "POST"])
def system_data_update():
    if request.method == 'GET':
        return jsonify(SYSTEM_NODES["master_list"])
    # Get the JSON data from the request
    node_list_data = request.json
    SYSTEM_NODES["master_list"] = node_list_data["master_list"]
    SYSTEM_NODES["transmitter_list"] = node_list_data["transmitter_list"]
    SYSTEM_NODES["data_server_list"] = node_list_data["data_server_list"]
    SYSTEM_NODES["maintenance_pc_list"] = node_list_data["maintenance_pc_list"]
    SYSTEM_NODES["interface_list"] = node_list_data["interface_list"]
    return NODE_IP


@bp.route('/transmitter-integrity-check', methods=['GET'])
def integrity_check():
    lst_request_time = 0
    # Get the last external request time in seconds and
    # Create a dictionary with the flag value
    if last_request_time():
        lst_request_time = last_request_time()
    data = {
        "last_request_time": lst_request_time / 1000000,
        "request_type": Request_Type
    }
    # Return a JSON response with the data dictionary
    return jsonify(data)


@bp.route('/handle-non-transmitted-readings/<int:time_range>', methods=['GET'])
def hdl_non_transmitted_readings(time_range):
    # get the current time
    now = datetime.now()
    # get the time 10 minutes ago
    ten_minutes_ago = now - timedelta(minutes=time_range)
    # Create an empty list to store the reading dictionaries
    data = []
    # query the Reading table and filter by created_at and is_data_transmitted columns
    non_transmitted_readings = db.session.query(Reading) \
        .filter(Reading.created_at >= ten_minutes_ago, Reading.is_data_transmitted == False).all()
    # Loop through each reading object
    for reading in non_transmitted_readings:
        # Convert the row to a dictionary using the as_dict method
        reading_dict = reading.as_dict()
        # Convert the datetime object to a string using isoformat method with timespec argument
        reading_dict["created_at"] = reading_dict["created_at"].isoformat(timespec="microseconds")
        # Append the reading dictionary to the data list
        data.append(reading_dict)
        # Return a JSON response with the data list
    return jsonify(data)


@bp.before_app_request
def load_system_nodes():
    for key in SYSTEM_NODES:
        if SYSTEM_NODES[key] == []:
            g.system_nodes = {}
        else:
            g.system_nodes = SYSTEM_NODES

