import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

THRESHOLD_INSERT = 3.0

FILE = "d_1_jad_trajectory_55_0.xml"   # Change to your file path

# ----------------------------
# Parse XML file
# ----------------------------
tree = ET.parse(FILE)
root = tree.getroot()

# Data structure: { time: { vehicle_id: {"x":..., "lane":..., "speed":...} } }
data = {}

for timestep in root.findall("timestep"):
    t = float(timestep.get("time"))
    data[t] = {}

    for veh in timestep.findall("vehicle"):
        vid = veh.get("id")
        x = float(veh.get("x"))
        lane = veh.get("lane")
        speed = float(veh.get("speed"))

        data[t][vid] = {"x": x, "lane": lane, "speed": speed}

# ----------------------------
# Find the moment each vehicle crosses 1000m
# ----------------------------
crossings = []  # Stores (time, vehicle_id) crossing points

times = sorted(data.keys())

for vid in set(v for t in times for v in data[t].keys()):
    for i in range(1, len(times)):
        t_prev = times[i - 1]
        t_now = times[i]

        if vid not in data[t_prev] or vid not in data[t_now]:
            continue

        x_prev = data[t_prev][vid]["x"]
        x_now = data[t_now][vid]["x"]

        if x_prev < 1000 <= x_now:
            crossings.append((t_now, vid))
            break

# ----------------------------
# Calculate time headway
# ----------------------------
plot_t = []
plot_headway = []

for t, vid in crossings:
    ego = data[t][vid]
    x_ego = ego["x"]
    lane_ego = ego["lane"]
    v_ego = ego["speed"]

    if v_ego < 0.1:
        continue  # Avoid division by zero

    # Find the vehicle in front: same lane and closest ahead
    x_front = None
    for other_vid, other in data[t].items():
        if other_vid == vid:
            continue
        if other["lane"] != lane_ego:
            continue
        if other["x"] > x_ego:
            if x_front is None or other["x"] < x_front:
                x_front = other["x"]

    if x_front is None:
        continue  # No vehicle ahead

    headway_time = (x_front - x_ego) / v_ego

    plot_t.append(t)
    plot_headway.append(headway_time)

# ----------------------------
# Plotting (single plot, no subplot)
# ----------------------------
plt.figure(figsize=(5.5, 3.4))
ax = plt.gca()

ax.scatter(plot_t, plot_headway, s=10, alpha=1, color="blue")
ax.axhline(y=THRESHOLD_INSERT, color="black", linewidth=1, linestyle="--")

ax.set_xlabel("Time (s)", fontsize=11, labelpad=10)
ax.set_ylabel("Time Headway (s)", fontsize=11, labelpad=8)

ax.set_xlim(200, 1600)
ax.set_ylim(1.5, 4)

plt.tight_layout()  # Automatically adjust spacing to avoid overlap

# ----------------------------
# Save as PDF
# ----------------------------
pdf_name = "jad_headway.pdf"
plt.savefig(pdf_name, format="pdf", dpi=150, bbox_inches="tight")
print(f"Figure saved as: {pdf_name}")

plt.show()