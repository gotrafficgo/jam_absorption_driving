import csv
import pdb
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
import matplotlib.colors as mcolors
import os
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset


# ======================================================
# ====================== Configuration =================
# ======================================================

UPSTREAM_FILE = "d_1_jad_detector_upstream_55_0.csv"
DOWNSTREAM_FILE = "d_1_jad_detector_downstream_55_0.csv"
XML_FILE = "d_1_jad_trajectory_55_0.xml"
JAD_FILE = "d_1_jad_strategy_55_0.csv"

FOCUS_X_MIN, FOCUS_X_MAX = 6900, 7100
FOCUS_T_MIN, FOCUS_T_MAX = 380, 600

FIG_SIZE = (5.5, 7)

ALPHA_ORIGINAL = 0.8
LW_ORIGINAL = 0.6

POINT_COLOR = "black"
POINT_SIZE = 40
POINT_FONT = 13

CBAR_TICKS = [0, 30, 60, 90]
CBAR_LABEL = "Speed (km/h)"

TL_RECT = [0, 0.08, 1, 0.98]

SG_MAX_SPEED = 10 # m/s

# ======================================================
# ====================== Load Detector Data ============
# ======================================================

def load_detector_data(filename):
    steps, speeds = [], []
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            steps.append(float(row["step"]))
            speeds.append(float(row["speed"]))
    return steps, speeds


up_steps, up_speeds = load_detector_data(UPSTREAM_FILE)
down_steps, down_speeds = load_detector_data(DOWNSTREAM_FILE)

up_speeds = [v * 3.6 for v in up_speeds]
down_speeds = [v * 3.6 for v in down_speeds]

# ======================================================
# ====================== Create Subplots ==============
# ======================================================

fig, axes = plt.subplots(2, 1, figsize=FIG_SIZE)

# ======================================================
# ====================== Top Plot: Detector ===========
# ======================================================

ax = axes[0]

ax.plot(up_steps, up_speeds, marker="o", markersize=1, linestyle="-",
        linewidth=0.5, alpha=0.7, color="blue", label="Upstream (0.5 km)")
ax.plot(down_steps, down_speeds, marker="o", markersize=1, linestyle="-",
        linewidth=0.5, alpha=0.7, color="red", label="Downstream (7 km)")

ax.axhline(y=SG_MAX_SPEED*3.6, color="black", linewidth=1, linestyle="--")

ax.set_xlabel("Time (step)", fontsize=10)
ax.set_ylabel("Speed (km/h)", fontsize=10, labelpad=14)
ax.set_xlim(200, 1600)
ax.set_ylim(0, 90)
ax.set_yticks([0, 30, SG_MAX_SPEED*3.6, 60, 90])
ax.legend(
    loc="upper right",
    bbox_to_anchor=(1.0, 0.85),   # adjust vertical position
    fontsize=10,
    frameon=False   # remove border
)
ax.text(0.03, 0.05, "(a)",
        color='black', fontsize=12,
        ha='left', va='bottom',
        transform=ax.transAxes,
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", pad=2))   

# ======================================================
# ====================== Insert Zoomed-in Inset =======
# ======================================================

axins = inset_axes(
    ax,
    width="38%",
    height="38%",
    loc="lower right",
    bbox_to_anchor=(-0.01, 0.2, 1, 1),   # shift left + down
    bbox_transform=ax.transAxes,
    borderpad=0.6
)

axins.plot(up_steps, up_speeds, color="blue", marker="o", markersize=2, linewidth=1)
axins.plot(down_steps, down_speeds, color="red", marker="o", markersize=2, linewidth=1)

axins.axhline(y=SG_MAX_SPEED*3.6, color="black", linewidth=1, linestyle="--")

axins.set_xlim(400, 600)
axins.set_ylim(0, 50)
axins.set_xticks([400, 450, 500, 550, 600])
axins.set_yticks([0, 10, 20, 30, 40, 50])
axins.tick_params(labelsize=10)

# mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="black", lw=0.8)

# ======================================================
# ====================== Bottom Plot: Trajectory ======
# ======================================================

ax = axes[1]

times, xs, ids = [], [], []
tree = ET.parse(XML_FILE)
root = tree.getroot()

for timestep in root.findall("timestep"):
    t = float(timestep.get("time"))
    for veh in timestep.findall("vehicle"):
        x = float(veh.get("x"))
        if FOCUS_X_MIN <= x <= FOCUS_X_MAX and FOCUS_T_MIN <= t <= FOCUS_T_MAX:
            times.append(t)
            xs.append(x)
            ids.append(veh.get("id"))

times = np.array(times)
xs = np.array(xs)
ids = np.array(ids)
unique_ids = np.unique(ids)

cmap = plt.colormaps["jet_r"]
norm = mcolors.Normalize(vmin=0, vmax=90)

lc_ref = None

for vid in unique_ids:
    mask = ids == vid
    t_list = times[mask]
    x_list = xs[mask]

    if len(t_list) < 2:
        continue

    v_list = np.diff(x_list) / np.diff(t_list) * 3.6
    v_list = np.insert(v_list, 0, v_list[0])

    points = np.array([t_list, x_list/1000]).T.reshape(-1,1,2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    lc = LineCollection(segments, cmap=cmap, norm=norm, array=v_list,
                        linewidths=LW_ORIGINAL, alpha=ALPHA_ORIGINAL)
    ax.add_collection(lc)

    if lc_ref is None:
        lc_ref = lc

ax.axhline(y=7000/1000, color="black", linewidth=1, linestyle="--")

ax.set_xlim(FOCUS_T_MIN, FOCUS_T_MAX)
ax.set_xticks([400, 450, 500, 550, 600])
ax.set_ylim(6.925, 7.075)
ax.set_yticks([6.95, 7.00, 7.05])
ax.set_xlabel("Time (s)", fontsize=10)
ax.set_ylabel("Space (km)", fontsize=10)
ax.grid(False)
ax.text(0.03, 0.05, "(b)",
        color='black', fontsize=12,
        ha='left', va='bottom',
        transform=ax.transAxes,
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", pad=2))   

# ======================================================
# ====================== E and F Points ===============
# ======================================================

def is_valid(v):
    return v != "" and v is not None

if os.path.exists(JAD_FILE):
    with open(JAD_FILE, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if rows:
        row = rows[-1]
        for p in ["E", "F"]:
            if is_valid(row.get(f"{p}_t")) and is_valid(row.get(f"{p}_x")):
                t = float(row[f"{p}_t"])
                x = float(row[f"{p}_x"]) / 1000
                if FOCUS_T_MIN <= t <= FOCUS_T_MAX and FOCUS_X_MIN/1000 <= x <= FOCUS_X_MAX/1000:
                    ax.scatter(t, x, color=POINT_COLOR, s=POINT_SIZE, zorder=10)
                    ax.text(t, x, f" {p}", fontsize=POINT_FONT,
                            va="bottom", ha="left", color=POINT_COLOR)

# ======================================================
# ====================== Colorbar =====================
# ======================================================

cbar_ax = fig.add_axes([0.12, 0.07, 0.83, 0.021])
cbar = plt.colorbar(lc_ref, cax=cbar_ax, orientation='horizontal')
cbar.set_ticks(CBAR_TICKS)
cbar.ax.set_xlabel(CBAR_LABEL, labelpad=-10)

plt.tight_layout(rect=TL_RECT)

png_name = "jad_detector.png"
plt.savefig(png_name, format="png", dpi=150, bbox_inches="tight")
print(f"Figure saved as: {png_name}")

plt.show()
plt.close()