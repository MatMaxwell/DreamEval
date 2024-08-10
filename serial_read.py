import serial
import time
from database_manager import insert_data

# Initialize serial connection to Arduino
arduinoData = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
time.sleep(2)

# Global variables to hold the current data
current_time = None
current_temp = None
current_humidity = None
current_pr = None
current_db = None
current_motion = None

# Lists to hold the data for graphs
time_data = []
temp_data = []
hum_data = []
pr_data = []
db_data = []
motion_data = []

# Function to read serial data from Arduino
def read_serial(root):
    global current_time, current_temp, current_humidity, current_pr, current_db, current_motion

    if arduinoData.in_waiting > 0:
        try:
            dataPacket = arduinoData.readline().decode('utf-8', errors='ignore').strip()
            if dataPacket.startswith("Time:"):
                parts = dataPacket.split(", ")
                data_map = {
                    "Time": (int, "current_time", time_data),
                    "Temp": (float, "current_temp", temp_data),
                    "Hum": (float, "current_humidity", hum_data),
                    "PR": (int, "current_pr", pr_data),
                    "dB": (int, "current_db", db_data),
                    "Motion": (lambda x: x.lower() == "true", "current_motion", motion_data)
                }
                
                for part in parts:
                    key, value = part.split(": ")
                    if key in data_map:
                        data_type, global_var_name, data_list = data_map[key]
                        value = data_type(value.split(" ")[0])
                        globals()[global_var_name] = value
                        data_list.append(value)
                
                insert_data(current_time, current_temp, current_humidity, current_pr, current_db, current_motion)
        except UnicodeDecodeError:
            pass  # Ignore lines that cause decoding errors

    root.after(100, read_serial, root)