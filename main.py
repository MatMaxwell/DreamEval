from gui import setup_gui, update_ui, root
from serial_read import read_serial
from database_manager import create_db

# Setup GUI
setup_gui(root)

# Setup Database
create_db()

# Schedule the first call to read data and update the UI
root.after(100, read_serial, root)
root.after(100, update_ui)

# Start the main loop to display the window
root.mainloop()

