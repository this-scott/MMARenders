import subprocess
import csv
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.image as mpimg

#manual only
ROW_TO_SELECT = 1
OUTPUT = 'pictures/RoundtreeRender.png'
TITLE = "Alex Pereria Vs. Khalil Roundtree Jr."

filename = "datasets/Manual.csv"
"""Get Datasheet"""
with open(filename, 'r') as file:
    reader = csv.reader(file)
    rows = list(reader)
    if 0 <= ROW_TO_SELECT < len(rows):
        row = rows[ROW_TO_SELECT][1:]

atkc = [int(item) for item in row]
print(atkc)

"""Aggregate to Limbs"""
left_hand = atkc[0]+atkc[2]
right_hand = atkc[1]+atkc[3]
left_kick = atkc[4]+atkc[6]
right_kick = atkc[5]+atkc[7]
limbs = [left_hand,right_hand,left_kick,right_kick]
maxv = max(limbs)

"""Create colors for datasheet"""
norm = colors.Normalize(vmin=0, vmax=maxv)
plasma = cm.get_cmap('plasma')

colored_values = [plasma(norm(val)) for val in limbs]

for val, rgba in zip(limbs, colored_values):
    print(f"Value: {val}, Color: {rgba}")

"""Run Blender"""
command = [
    "blender",
    "-b",  # Run in background mode
    "blends/readypos.blend",  # Path to the .blend file
    "-P",  # Execute a Python script
    "heatmap_blender.py",  # Path to the Python script
    "--",  # Separator for Blender arguments and script arguments
]

for cv in colored_values:
    for x in cv[0:3]:
        command.append(str(x))
print(command)

process = subprocess.run(command, capture_output=True, text=True)
print("STDOUT:", process.stdout)
print("STDERR:", process.stderr)

"""Add the keymap"""
img = mpimg.imread('pictures/temp.png')

# Basic Matplotlib
fig, ax = plt.subplots(figsize=(6, 6))
img_plot = ax.imshow(img)
ax.axis('off') 

#quarter labels
quarters = [round(q, 2) for q in [0, maxv*0.25, maxv*0.5, maxv*0.75, maxv]]


# Combine ticks
all_ticks = sorted(set(limbs + quarters))

label_dict = {v: name for v, name in zip(limbs, ['left_hand','right_hand','left_kick','right_kick'])}
tick_labels = [f"{label_dict[t]}: {t}" if t in label_dict else str(t) for t in all_ticks]

cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=plasma), ax=ax, orientation='vertical')
cbar.set_ticks(all_ticks)
cbar.ax.set_yticklabels(tick_labels)
cbar.set_label('Frequency to Attack With')

plt.suptitle(TITLE, fontsize=14)

plt.tight_layout()
plt.savefig(OUTPUT, dpi=300)
plt.show()