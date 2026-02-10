import matplotlib.pyplot as plt
import ALL_FUNCTIONS as Func


# -------- Reference positions --------
DETECTOR_DOWNSTREAM = 7000
DETECTOR_UPSTREAM   = 500
RAMP                = 1000

# -------- Canvas settings --------
FIG_SIZE = (5.5, 9)


# ======================================================
# Single plot function
# ======================================================
def plot_for_speed(jad_speed, Et_offset, ax, idx):

    XML_FILE = f"d_1_jad_trajectory_{int(jad_speed)}_{int(Et_offset)}.xml"
    JAD_FILE = f"d_1_jad_strategy_{int(jad_speed)}_{int(Et_offset)}.csv"

    plt.sca(ax)

    lc_for_cbar = None

    subplot_labels = ["(a)", "(b)"]

    # -----------------------------------------------------
    # Load trajectory
    # -----------------------------------------------------
    times, ids, xs = Func.load_trajectory(XML_FILE)

    # ------------------------------
    # Trajectories
    # ------------------------------
    lc_for_cbar = Func.plot_trajectories(ids, lc_for_cbar, times, xs, ax)

    # ------------------------------
    # Reference lines
    # ------------------------------
    Func.plot_reference_lines(ax, times, DETECTOR_DOWNSTREAM, DETECTOR_UPSTREAM, RAMP)

    # ------------------------------
    # JAD strategy
    # ------------------------------
    Func.plot_jad_strategy(JAD_FILE, ax)

    ax.set_xlim(200, 1600)
    ax.set_ylim(0, 8)
    ax.set_ylabel("Space (km)", fontsize=12)

    # ---- Bottom-left JAD Speed annotation (black text + semi-transparent white background + subplot label) ----
    if idx == 0:
        x_text = 0.02
        text = "JAD speed too low"
    else:
        x_text = 0.02
        text = "Wave width underestimated"

    ax.text(
        x_text, 0.03,
        f"{subplot_labels[idx]} {text}",
        transform=ax.transAxes,
        color="black",
        fontsize=12,
        ha="left",
        va="bottom",
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", pad=2)
    )

    return lc_for_cbar


# ======================================================
# Main figure
# ======================================================
fig, axes = plt.subplots(2, 1, figsize=FIG_SIZE, sharex=True)

lc = plot_for_speed(35, 0, axes[0], 0)
lc = plot_for_speed(55, -40, axes[1], 1)
lc_ref = lc

axes[-1].set_xlabel("Time (s)", fontsize=12)


# ======================================================
# Top horizontal colorbar
# ======================================================
cbar_ax = fig.add_axes([0.1, 0.94, 0.84, 0.02])  # [left, bottom, width, height]
cbar = plt.colorbar(lc_ref, cax=cbar_ax, orientation='horizontal', ticklocation='top')
cbar.set_label("Speed (km/h)", labelpad=-7)
cbar.set_ticks([0, 30, 60, 90])

plt.tight_layout(rect=[0, 0, 1, 0.93])


# ======================================================
# Save PNG
# ======================================================
png_name = "jad_trajectory_failed.png"
plt.savefig(png_name, format="png", dpi=150, bbox_inches="tight")
print(f"Figure saved as: {png_name}")

plt.show()
plt.close()