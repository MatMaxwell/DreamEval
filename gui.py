import customtkinter
from tkinter import Toplevel, Text, Scrollbar, RIGHT, Y, END
from PIL import Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import time
import random
from serial_read import current_time, current_temp, current_humidity, current_pr, current_db, current_motion
from serial_read import time_data, temp_data, hum_data, pr_data, db_data, motion_data
from database_manager import clear_database_table, print_database_table, fetch_database_data

# Initialize the main window
root = customtkinter.CTk()
root.geometry("1000x1000")
root.title("DreamEval")

# Global variables for GUI elements
time_var = customtkinter.StringVar(value="N/A")
temp_var = customtkinter.StringVar(value="N/A")
humidity_var = customtkinter.StringVar(value="N/A")
pr_var = customtkinter.StringVar(value="N/A")
db_var = customtkinter.StringVar(value="N/A")
motion_square = None
temp_meter = None
humidity_meter = None
pr_meter = None
db_meter = None

# Define global variables for view frames
data_view_frame = None
graphs_view_frame = None
circuit_view_frame = None
reaction_view_frame = None
evaluation_view_frame = None

# Reaction Test Functions
reaction_label = None
start_button = None
reaction_time_label = None
start_time = 0
test_started = False

# Ensure the animation object is retained
ani = None  # Declare ani as a global variable to keep it in scope

# Function to update the UI in real-time
def update_ui():
    from serial_read import current_time, current_temp, current_humidity, current_pr, current_db, current_motion
    # Update time label
    if current_time is not None:       
        time_var.set(timer_format(current_time))
    else:
        time_var.set("N/A")                         # Show "N/A" if no data
                                                    # Update temperature meter and label
    if current_temp is not None:
        temp_meter.set(current_temp / 100)          # Set the meter to a percentage value
        temp_var.set(f"{current_temp} F")           # Update the label with the current temperature
    else:
        temp_meter.set(0)                           # Set the meter to 0 if no data
        temp_var.set("N/A")                         # Show "N/A" if no data

    # Update humidity meter and label
    if current_humidity is not None:
        humidity_meter.set(current_humidity / 100)  # Set the meter to a percentage value
        humidity_var.set(f"{current_humidity} %")   # Update the label with the current humidity
    else:
        humidity_meter.set(0)                       # Set the meter to 0 if no data
        humidity_var.set("N/A")                     # Show "N/A" if no data

    # Update photoresistor (PR) meter and label
    if current_pr is not None:
        pr_meter.set(current_pr / 1000)             # Set the meter to a percentage value
        pr_var.set(f"{current_pr} Ohm")             # Update the label with the current PR value
    else:
        pr_meter.set(0)                             # Set the meter to 0 if no data
        pr_var.set("N/A")                           # Show "N/A" if no data

    # Update dB meter and label
    if current_db is not None:
        db_meter.set(current_db / 100)              # Set the meter to a percentage value
        db_var.set(f"{current_db} dB")              # Update the label with the current dB value
    else:
        db_meter.set(0)                             # Set the meter to 0 if no data
        db_var.set("N/A")                           # Show "N/A" if no data

    # Update motion indicator color
    if current_motion:
        motion_square.configure(bg_color="green")   # Set the color to green if motion is detected
    else:
        motion_square.configure(bg_color="red")     # Set the color to red if no motion is detected

    root.after(100, update_ui)                      # Schedule the function to run again after 100 milliseconds

# Converts seconds to hours miuntes and seconds
def timer_format(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# Function to print all data from the database
def print_database_table():
    # Fetch data from the database
    data = fetch_database_data()

    # Create a new top-level window
    new_window = Toplevel(root)
    new_window.title("Database Table")
    new_window.geometry("800x600")

    # Create a text widget with a scrollbar
    text_widget = Text(new_window, wrap='none')
    text_widget.pack(side='left', fill='both', expand=True)

    scrollbar = Scrollbar(new_window, orient='vertical', command=text_widget.yview)
    scrollbar.pack(side=RIGHT, fill=Y)

    text_widget.config(yscrollcommand=scrollbar.set)

    # Insert the database data into the text widget
    for row in data:
        text_widget.insert(END, f"Time: {row[0]}, Temperature: {row[1]}, Humidity: {row[2]}, Light: {row[3]}, dB Level: {row[4]}, Motion: {bool(row[5])}\n")

    # Make the text widget read-only
    text_widget.config(state='disabled')

# Clear all data in the data lists
def reset_graphs():
    # Clears data from all global lists
    time_data.clear()
    temp_data.clear()
    hum_data.clear()
    pr_data.clear()
    db_data.clear()
    motion_data.clear()

# Function to update the graphs with the latest data
def update_graphs(i):
    # Check if there is data in time_data and if all data lists have the same length
    if time_data and len(time_data) == len(temp_data) == len(hum_data) == len(pr_data) == len(db_data) == len(motion_data):
        # Clear the current plot on ax1 and plot the new temperature data
        ax1.clear()  # Clear the previous plot
        ax1.plot(time_data, temp_data, label="Temperature (F)")  # Plot temperature vs time
        ax1.legend(loc="upper left")  # Add a legend to the plot

        # Clear the current plot on ax2 and plot the new humidity data
        ax2.clear()  # Clear the previous plot
        ax2.plot(time_data, hum_data, label="Humidity (%)")  # Plot humidity vs time
        ax2.legend(loc="upper left")  # Add a legend to the plot

        # Clear the current plot on ax3 and plot the new PR data
        ax3.clear()  # Clear the previous plot
        ax3.plot(time_data, pr_data, label="PR (Ohm)")  # Plot PR vs time
        ax3.legend(loc="upper left")  # Add a legend to the plot

        # Clear the current plot on ax4 and plot the new volume data
        ax4.clear()  # Clear the previous plot
        ax4.plot(time_data, db_data, label="Volume (dB)")  # Plot volume vs time
        ax4.legend(loc="upper left")  # Add a legend to the plot

        # Clear the current plot on ax5 and plot the new motion data
        ax5.clear()  # Clear the previous plot
        # Convert the motion data from True/False to 1/0
        # This is done so that we can plot the data as integers
        motion_int_data = [1 if motion else 0 for motion in motion_data]

        # Plot the converted motion data
        ax5.plot(time_data, motion_int_data, label="Motion (True/False)")

        # Add a legend to the plot
        ax5.legend(loc="upper left")

# Function to show a specific view
def show_view(view):
    global data_view_frame, graphs_view_frame, circuit_view_frame, reaction_view_frame, evaluation_view_frame, ani
    
    # Hide all view frames before showing the selected one
    data_view_frame.pack_forget()
    graphs_view_frame.pack_forget()
    circuit_view_frame.pack_forget()
    reaction_view_frame.pack_forget()
    evaluation_view_frame.pack_forget()
    
    
    if view == "data":
        data_view_frame.pack(fill="both", expand=True)
    elif view == "graphs":
        graphs_view_frame.pack(fill="both", expand=True)
    elif view == "reaction":
        reaction_view_frame.pack(fill="both", expand=True)
    elif view == "evaluation":
        evaluation_view_frame.pack(fill="both", expand=True)
    elif view == "circuit":
        circuit_view_frame.pack(fill="both", expand=True)

# Helper function to create a meter
def create_meter(frame, title, label_var):
    title_label = customtkinter.CTkLabel(master=frame, text=title, font=("Helvetica", 20))
    title_label.pack(pady=5)
    data_label = customtkinter.CTkLabel(master=frame, textvariable=label_var, font=("Helvetica", 40))
    data_label.pack(pady=5)
    meter = customtkinter.CTkProgressBar(master=frame, orientation="horizontal", width=600, height=30)
    meter.pack(pady=10)
    return meter

# Function to start the reaction test
def start_reaction_test():
    global start_time, test_started
    reaction_label.configure(text="Wait for green...", bg_color="yellow")
    start_button.configure(state="disabled")
    root.after(random.randint(2000, 5000), change_to_green)

# Function to change the reaction label to green
def change_to_green():
    global start_time, test_started
    reaction_label.configure(text="Press SPACE now!", bg_color="green")
    start_time = time.time()
    test_started = True

# Function to record the reaction time
def record_reaction(event):
    global test_started
    if test_started:
        reaction_time = time.time() - start_time
        reaction_label.configure(text=f"Reaction Time: {reaction_time:.3f} seconds", bg_color="white")
        reaction_time_label.configure(text=f"Reaction Time: {reaction_time:.3f} seconds")
        start_button.configure(state="normal")
        test_started = False

# Function to setup the GUI
def setup_gui(root):
    global time_var, temp_var, humidity_var, pr_var, db_var, motion_square, temp_meter, humidity_meter, pr_meter, db_meter
    global data_view_frame, graphs_view_frame, circuit_view_frame, reaction_view_frame, evaluation_view_frame, ani
    global reaction_label, start_button, reaction_time_label

    # Create a frame for the top buttons
    button_frame = customtkinter.CTkFrame(master=root)
    button_frame.pack(side="top", fill="x")

    # Define the list of button labels
    buttons = ["Data", "Graphs", "Reaction", "Evaluation", "Circuit"]

    # Create buttons for each view
    for button in buttons:
        # Create a button with the label and assign a command
        new_button = customtkinter.CTkButton(
            master=button_frame,                          # Parent frame for the button
            text=button,                                  # Button label
            command=lambda b=button: show_view(b.lower()) # Command to call when clicked
        )
        # Add the button to the frame and set its layout
        new_button.pack(side="left", padx=10)

    # Create a frame for the views
    view_frame = customtkinter.CTkFrame(master=root)
    view_frame.pack(fill="both", expand=True)

    # Data View setup
    data_view_frame = customtkinter.CTkFrame(master=view_frame)
    data_view_frame.pack(fill="both", expand=True)

    # Variables to hold the sensor data
    time_var = customtkinter.StringVar(value="N/A")
    temp_var = customtkinter.StringVar(value="N/A")
    humidity_var = customtkinter.StringVar(value="N/A")
    pr_var = customtkinter.StringVar(value="N/A")
    db_var = customtkinter.StringVar(value="N/A")

    # Create Clock on top
    title_time = customtkinter.CTkLabel(master=data_view_frame, text="Time", font=("Helvetica", 20))
    title_time.pack(pady=10)
    data_label = customtkinter.CTkLabel(master=data_view_frame, textvariable=time_var, font=("Helvetica", 40))
    data_label.pack(pady=10)
    
    # Create meters for data view
    temp_meter = create_meter(data_view_frame, "Temperature", temp_var)
    humidity_meter = create_meter(data_view_frame, "Humidity", humidity_var)
    pr_meter = create_meter(data_view_frame, "Photoresistance", pr_var)
    db_meter = create_meter(data_view_frame, "Volume", db_var)

    # Motion indicator
    motion_square = customtkinter.CTkLabel(master=data_view_frame, text="Motion", width=100, height=100, corner_radius=50, bg_color="red", font=("Helvetica", 20))
    motion_square.pack(pady=10)

    # Create a bottom frame for the buttons within data_view_frame
    bottom_frame = customtkinter.CTkFrame(master=data_view_frame)
    bottom_frame.pack(side="bottom", fill="x", pady=10)

    # Create a button to clear the database
    clear_button = customtkinter.CTkButton(master=bottom_frame, text="Clear Database", command=clear_database_table)
    clear_button.pack(side="left", padx=10)

    # Create a button to print the database table
    print_button = customtkinter.CTkButton(master=bottom_frame, text="Print Database", command=print_database_table)
    print_button.pack(side="left", padx=10)

    # Graphs View setup
    graphs_view_frame = customtkinter.CTkFrame(master=view_frame)

    # Reset button for graphs
    reset_button = customtkinter.CTkButton(master=graphs_view_frame, text="Reset Graphs", command=reset_graphs)
    reset_button.pack(pady=10)

    # Create the figure for plotting graphs
    fig = Figure(figsize=(8, 6), dpi=100)
    global ax1, ax2, ax3, ax4, ax5
    ax1 = fig.add_subplot(511)
    ax2 = fig.add_subplot(512)
    ax3 = fig.add_subplot(513)
    ax4 = fig.add_subplot(514)
    ax5 = fig.add_subplot(515)

    # Canvas to display the figure
    canvas = FigureCanvasTkAgg(fig, master=graphs_view_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    # Circuit View setup
    circuit_view_frame = customtkinter.CTkFrame(master=view_frame)

    # Load and display the image
    image = Image.open("DreamEval_Circuit.png")
    image = image.resize((761, 861), Image.LANCZOS)  # Resize image to fit the window
    circuit_image = customtkinter.CTkImage(dark_image=image, size=(761, 861))

    image_label = customtkinter.CTkLabel(master=circuit_view_frame, text="", image=circuit_image)
    image_label.pack(pady=10, padx=10, anchor="center")

    # Reaction View setup
    reaction_view_frame = customtkinter.CTkFrame(master=view_frame)
    reaction_view_frame.pack(fill="both", expand=True)

    # Create labels and buttons for the reaction view
    reaction_label = customtkinter.CTkLabel(master=reaction_view_frame, text="Press 'Start' to begin", font=("Helvetica", 16))
    reaction_label.pack(pady=20)
    
    start_button = customtkinter.CTkButton(master=reaction_view_frame, text="Start", command=start_reaction_test)
    start_button.pack(pady=20)
    
    reaction_time_label = customtkinter.CTkLabel(master=reaction_view_frame, text="", font=("Helvetica", 16))
    reaction_time_label.pack(pady=20)
    
    root.bind("<space>", record_reaction)

    # Evaluation View setup
    evaluation_view_frame = customtkinter.CTkFrame(master=view_frame)
    evaluation_view_frame.pack(fill="both", expand=True)

    # Initial view will be the data view
    show_view("data")

    # Start the animation for the graphs
    ani = animation.FuncAnimation(fig, update_graphs, interval=1000, cache_frame_data=False)

# Ensure setup_gui, update_ui, and root are defined at the module level for import
__all__ = ["setup_gui", "update_ui", "root"]

if __name__ == "__main__":
    setup_gui(root)
    update_ui()
    root.mainloop()
