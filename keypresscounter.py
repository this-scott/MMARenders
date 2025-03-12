import keyboard
import time
import matplotlib.pyplot as plt
import csv
import numpy as np

# Create a list for each key type
timestamps = {
    'q': [],  # jabs
    'w': [],  # cross
    'e': [],  # hookl
    'r': [],  # hookr
    't': [],  # bkl
    'y': [],  # bkr
    'a': [],  # hkl
    's': []   # hkr
}
running = True

jabs = 0
cross = 0
hookl = 0
hookr = 0
bkl = 0
bkr = 0
hkl = 0
hkr = 0

print("Press 'q', 'w', 'e', 'r', 't', 'y', 'a', or 's' to log presses. Press 'p' to stop and generate the chart.")

while running:
    event = keyboard.read_event()
    if event.event_type == keyboard.KEY_DOWN:
        key = event.name.lower()
        
        # Record timestamp for valid keys
        if key in timestamps:
            timestamps[key].append(time.time())
            
            # Update counter based on the key
            if key == "q":
                jabs += 1
                print(f"q pressed. Total count: {jabs}")
            elif key == "w":
                cross += 1
                print(f"w pressed. Total count: {cross}")
            elif key == "e":
                hookl += 1
                print(f"e pressed. Total count: {hookl}")
            elif key == "r":
                hookr += 1
                print(f"r pressed. Total count: {hookr}")
            elif key == "t":
                bkl += 1
                print(f"t pressed. Total count: {bkl}")
            elif key == "y":
                bkr += 1
                print(f"y pressed. Total count: {bkr}")
            elif key == "a":
                hkl += 1
                print(f"a pressed. Total count: {hkl}")
            elif key == "s":
                hkr += 1
                print(f"s pressed. Total count: {hkr}")
        elif key == "p":
            print("Stopping logging and generating chart...")
            running = False


with open("timestamps.csv", 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(timestamps)

key_labels = {
    'q': 'Jabs',
    'w': 'Cross',
    'e': 'Left Hook',
    'r': 'Right Hook',
    't': 'Left Low Kick',
    'y': 'Right Low Kick',
    'a': 'Left High Kick',
    's': 'Right High Kick'
}

# Plot each key's timestamps
for i, (key, times) in enumerate(timestamps.items()):
    if times: 
        # Converting absolute timestamps to relative time
        if times:
            start_time = min([t for sublist in timestamps.values() for t in sublist]) if any(timestamps.values()) else 0
            relative_times = [t - start_time for t in times]
            
            # y values increase by 1 for each press
            y = np.arange(len(relative_times))
            
            plt.plot(relative_times, y, label=key_labels[key], marker='o', linewidth=2)

plt.xlabel("Time (seconds)")
plt.ylabel("Count (cumulative)")
plt.title("Key Presses Over Time")
plt.legend()
plt.grid(True)
plt.show()