# Import the module
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from pymodbus import mei_message
from pymodbus.exceptions import ModbusIOException
import logging

# Configure logging
# logging.basicConfig()
# log = logging.getLogger()
# log.setLevel(logging.DEBUG)

DAT8014_NODE = {
    "ip": "127.0.0.1",
    "site": "BV05",
    "port": 60805
}


# Define a function to get resistances from Dat8014 and convert them to temperature
def get_resistance_from_dat8014():
    # Create a Modbus TCP client object with the server address and port
    client = ModbusTcpClient(DAT8014_NODE['ip'], port=DAT8014_NODE['port'])
    # Connect to the server
    client.connect()
    # Create a request object
    request = mei_message.ReadDeviceInformationRequest(read_code=0x03)
    # Execute the request and get the response
    try:
        response = client.execute(request)
        # Read the first holding register of slave id 1
        result_1 = client.read_holding_registers(0, 1)  # read one register starting from address 0
        decoder_1 = BinaryPayloadDecoder.fromRegisters(result_1.registers, byteorder=Endian.Big, wordorder=Endian.Big)
        value_1 = decoder_1.decode_16bit_float()
        # Read the second holding register of slave id 1
        result_2 = client.read_holding_registers(1, 1)
        decoder_2 = BinaryPayloadDecoder.fromRegisters(result_2.registers, byteorder=Endian.Big, wordorder=Endian.Big)
        value_2 = decoder_2.decode_16bit_float()
        # Return the values
        return value_1, value_2
    except ModbusIOException as e:
        # Handle the exception
        # log.error("Modbus Error: %s", e)
        print(f"[Connection] Failed to connect[ModbusTcpClient({DAT8014_NODE['ip']}:{DAT8014_NODE['port']})]")
        return None, None
    finally:
        # Close the connection
        client.close()


# Define a function to calculate temperature from resistance
def resistance_to_temperature(Rt):
    # Define the constants
    R0 = 1000  # Resistance at 0°C in ohms
    alpha = 0.00385  # Temperature coefficient of resistance in ohms/ohms/°C
    T0 = 0  # Reference temperature in °C
    # Use the formula T = (Rt / R0 - 1) / alpha + T0
    temperature = (Rt / R0 - 1) / alpha + T0
    # Return the temperature value
    return temperature
