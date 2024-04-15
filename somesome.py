import serial
from datetime import datetime
import tkinter as tk
import threading

# Try to open the serial port
try:
    ser = serial.Serial('COM38', 115200, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE)
except serial.SerialException as e:
    print(f"Could not open serial port: {e}")
    exit(1)

def read_serial(text_widget):
    while True:
        if ser.in_waiting > 0:
            try:
                line = ser.read(ser.in_waiting)  # read all available bytes
                hex_line = ' '.join(f'{i:02X}' for i in line)  # convert to hexadecimal
                now = datetime.now().strftime("%d.%m.%Y %H:%M:%S.%f")[:-3]  # Get the current time with milliseconds
                text_widget.insert(tk.END, f"{now} ", "green")
                text_widget.insert(tk.END, "[RX] - ", "green")
                text_widget.insert(tk.END, f"{hex_line}\n", "red")
            except serial.SerialException as e:
                text_widget.insert(tk.END, f"Error reading from serial port: {e}\n")
                break


def start_reading(text_widget):
    threading.Thread(target=read_serial, args=(text_widget,), daemon=True).start()

def send_command():
    command = '1B 50 1B 51 01'  # The command to send
    bytes_command = bytes.fromhex(command)  # Convert the command to bytes
    ser.write(bytes_command)  # Send the command over the serial port
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S.%f")[:-3]  # Get the current time with milliseconds
    text_widget.insert(tk.END, f"{now} ", "green")
    text_widget.insert(tk.END, "[TX] - ", "green")
    text_widget.insert(tk.END, f"{command}\n", "blue")  # Print the command to the text widget

def send_custom_command():
    command = custom_command_entry.get()  # Get the command from the entry widget
    if command:  # If the command is not empty
        bytes_command = bytes.fromhex(command)  # Convert the command to bytes
        ser.write(bytes_command)  # Send the command over the serial port
        now = datetime.now().strftime("%d.%m.%Y %H:%M:%S.%f")[:-3]  # Get the current time with milliseconds
        text_widget.insert(tk.END, f"{now} ", "green")
        text_widget.insert(tk.END, "[TX] - ", "green")
        text_widget.insert(tk.END, f"{command}\n", "blue")  # Print the command to the text widget
    custom_command_entry.delete(0, tk.END)  # Clear the entry widget


# Create the application window
root = tk.Tk()
text_widget = tk.Text(root)
text_widget.pack()

# Define the tags for the different colors
text_widget.tag_config("green", foreground="green")
text_widget.tag_config("blue", foreground="blue")
text_widget.tag_config("red", foreground="red")

# Create the entry widget for custom commands
custom_command_entry = tk.Entry(root)
custom_command_entry.pack()

# Create the button for the "Confirm 01" command
confirm_button = tk.Button(root, text="Confirm 01", command=send_command)
confirm_button.pack()

# Create the button for sending custom commands
custom_command_button = tk.Button(root, text="Send Custom Command", command=send_custom_command)
custom_command_button.pack()

# Start reading from the serial port in a separate thread
start_reading(text_widget)

# Start the application
root.mainloop()