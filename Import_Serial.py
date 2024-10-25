import serial
import paho.mqtt.client as mqtt
import time
import matplotlib.pyplot as plt

def RemoveOutlier(bpm, lower_threshold=40, upper_threshold=180):
    """
    Function to check if the BPM data is within the valid range.
    By default, values between 40 and 180 are considered normal.
    """
    if lower_threshold <= bpm <= upper_threshold:
        return True
    else:
        return False

# MQTT Configuration
mqtt_broker = "13.211.13.221"  # Updated IP address
mqtt_port = 1883  # Standard MQTT port
mqtt_topic = "patient/heartbeat"  # Topic to publish to

# Create MQTT client
client = mqtt.Client()

# Connect to the MQTT broker
try:
    client.connect(mqtt_broker, mqtt_port, 60)
    print(f"Connected to MQTT broker at {mqtt_broker}")
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")
    exit(1)

ser = serial.Serial("/dev/rfcomm0", 9600)  # Serial port setup
ser.write(str.encode('Start\r\n'))  # Start serial communication

bpm_data = []
data_window_size = 5  # Size of the data window for BPM

def CheckBPMForWarning(bpm):
    """
    Check if the BPM exceeds the warning threshold (100).
    """
    threshold_for_warning = 100
    if bpm > threshold_for_warning:
        return True
    else:
        return False

# Initialize lists to store BPM values for plotting
bpm_values = []
timestamps = []

plt.ion()  # Interactive mode on for real-time plotting
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)  # Initialize an empty line plot

# Continuous loop to receive and process data
while True:
    if ser.in_waiting > 0:
        rawserial = ser.readline()
        cookedserial = rawserial.decode('utf-8').strip('\r\n')
        print(cookedserial)  # Print raw data received from serial (e.g., "75.3")

        try:
            bpm = float(cookedserial)  # Convert the data to BPM
            # Validate if the BPM data is within the valid range
            if RemoveOutlier(bpm):
                print(f"Valid BPM: {bpm}")

                # If the list exceeds the window size, remove the oldest data
                if len(bpm_data) >= data_window_size:
                    bpm_data.pop(0)

                # Add the valid BPM value to the list
                bpm_data.append(bpm)
                average_bpm = sum(bpm_data) / len(bpm_data)
                print(f"Average BPM: {average_bpm}")

                # If the average BPM exceeds the warning threshold, print a warning message
                if CheckBPMForWarning(average_bpm):
                    print("Warning: BPM is above 100!")

                # Publish the average BPM to the MQTT broker
                client.publish(mqtt_topic, average_bpm)
                print(f"Published BPM {average_bpm} to topic '{mqtt_topic}'")

                # Append the values for plotting
                bpm_values.append(average_bpm)
                timestamps.append(time.time())  # Use current time as x-axis value

                # Update the plot
                line.set_xdata(timestamps)
                line.set_ydata(bpm_values)
                ax.relim()
                ax.autoscale_view()
                fig.canvas.draw()
                fig.canvas.flush_events()

            else:
                print(f"Outlier Detected: {bpm}")  # Handle outlier data
        except ValueError:
            print(f"Invalid Data: {cookedserial}")  # Handle non-numeric data

    client.loop()  # MQTT client loop
    time.sleep(1)  # Wait 1 seconds before reading again