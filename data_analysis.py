import pandas as pd
import sqlite3

data_frame = None


def create_df():
    global data_frame
    connection = sqlite3.connect('sensor_data.db')
    sql = pd.read_sql_query("SELECT * FROM sensor_readings", connection)
    data_frame = pd.DataFrame(sql, columns=['time', 'temp', 'hum', 'pr', 'db', 'motion'])
    data_frame.set_index('time', inplace=True)
    connection.close()
    
def main():
    print(data_frame)
    
if __name__ == '__main__':
    create_df()
    main()
    
    