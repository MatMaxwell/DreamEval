import sqlite3

def create_db():
    """
    Creates a SQLite database table for storing sensor data.
    """
    connection = sqlite3.connect('sensor_data.db')
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensor_readings (
        time INTEGER PRIMARY KEY,
        temp REAL,
        hum REAL,
        pr INTEGER,
        db INTEGER,
        motion INTEGER1
    )
    ''')
    connection.commit()
    connection.close()
    
def insert_data(time, temp, hum, pr, db, motion):
    """
    Inserts a single data point into the database.
    """
    connection = sqlite3.connect('sensor_data.db')
    cursor = connection.cursor()

    try:
        cursor.execute('''
        INSERT INTO sensor_readings (time, temp, hum, pr, db, motion)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (time, temp, hum, pr, db, int(motion)))

        connection.commit()
    except sqlite3.IntegrityError:
        pass  # Ignore duplicate time entries
    finally:
        connection.close()

def print_database_table():
    """
    Prints all data from the sensor_readings table.
    """
    connection = sqlite3.connect('sensor_data.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM sensor_readings")
    rows = cursor.fetchall()
    if not rows:
        print("No data available.")
    for row in rows:
        print(f"Time: {row[0]}, Temperature: {row[1]}, Humidity: {row[2]}, Light: {row[3]}, dB Level: {row[4]}, Motion: {bool(row[5])}")
    connection.close()
    
def clear_database_table():
    """
    Clears all data from the 'sensor_readings' table in the 'sensor_data.db' SQLite database.
    """
    connection = sqlite3.connect('sensor_data.db')
    cursor = connection.cursor()
    cursor.execute("DELETE FROM sensor_readings")
    connection.commit()
    connection.close()

def get_data_by_time(time_value):
    """
    Retrieves and prints a specific data entry by the time key.
    """
    connection = sqlite3.connect('sensor_data.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM sensor_readings WHERE time = ?", (time_value,))
    row = cursor.fetchone()
    if row:
        print(f"Time: {row[0]}, Temperature: {row[1]}, Humidity: {row[2]}, Light: {row[3]}, dB Level: {row[4]}, Motion: {bool(row[5])}")
    else:
        print(f"No data found for time: {time_value}.")
    connection.close()
    
def fetch_database_data():
    """
    Fetches all data from the sensor_readings table.
    Returns:
        List of tuples containing all rows from the sensor_readings table.
    """
    connection = sqlite3.connect('sensor_data.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM sensor_readings")
    rows = cursor.fetchall()
    connection.close()
    return rows