# Import the module
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian
from pymodbus import mei_message


# Define a function to get resistances from Dat8014 and convert them to temperature
def get_resistance_from_dat8014():
    # Create a Modbus TCP client object with the server address and port
    client = ModbusTcpClient('127.0.0.1', port=5020)
    # Connect to the server
    client.connect()
    # Create a request object
    request = mei_message.ReadDeviceInformationRequest(read_code=0x03)
    # Execute the request and get the response
    response = client.execute(request)
    # Read the first holding register of slave id 1
    result_1 = client.read_holding_registers(0, 1)  # read one register starting from address 0
    decoder_1 = BinaryPayloadDecoder.fromRegisters(result_1.registers, byteorder=Endian.Big, wordorder=Endian.Big)
    value_1 = decoder_1.decode_16bit_float()
    # value_1 = resistance_to_temperature(value_1)
    # value_1 = format(value_1, '.3f')
    # Read the second holding register of slave id 1
    result_2 = client.read_holding_registers(1, 1)
    decoder_2 = BinaryPayloadDecoder.fromRegisters(result_2.registers, byteorder=Endian.Big, wordorder=Endian.Big)
    value_2 = decoder_2.decode_16bit_float()
    # value_2 = resistance_to_temperature(value_2)
    # value_2 = format(value_2, '.3f')
    # Close the connection
    client.close()
    return value_1, value_2


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
