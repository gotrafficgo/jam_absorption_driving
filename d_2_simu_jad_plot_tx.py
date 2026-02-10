import matplotlib.pyplot as plt
import sys
import ALL_FUNCTIONS as Func


# =========================================================
# Global parameters
# =========================================================
FIG_SIZE = (5.5, 5)

# ---- Detector positions (m) ----
DETECTOR_DOWNSTREAM = 7000
DETECTOR_UPSTREAM   = 500
RAMP                = 1000



# =========================================================
# Main plotting function
# =========================================================
def plot_for_speed(JAD_SPEED_KMH, Et_OFFSET):

    XML_FILE = f"d_1_jad_trajectory_{int(JAD_SPEED_KMH)}_{int(Et_OFFSET)}.xml"
    JAD_FILE = f"d_1_jad_strategy_{int(JAD_SPEED_KMH)}_{int(Et_OFFSET)}.csv"

    # -----------------------------------------------------
    # Load trajectory
    # -----------------------------------------------------
    times, ids, xs = Func.load_trajectory(XML_FILE)

    # -----------------------------------------------------
    # Create figure
    # -----------------------------------------------------
    fig = plt.figure(figsize=FIG_SIZE)
    ax = fig.add_axes([0.1, 0.1, 0.85, 0.75])
    lc_for_cbar = None

    # ------------------------------
    # Plot trajectories
    # ------------------------------
    lc_for_cbar = Func.plot_trajectories(ids, lc_for_cbar, times, xs, ax)


    # -----------------------------------------------------
    # Reference lines
    # -----------------------------------------------------
    Func.plot_reference_lines(ax, times, DETECTOR_DOWNSTREAM, DETECTOR_UPSTREAM, RAMP)


    # -----------------------------------------------------
    # JAD Strategy
    # -----------------------------------------------------
    Func.plot_jad_strategy(JAD_FILE, ax)


    # -----------------------------------------------------
    # Axes & colorbar
    # -----------------------------------------------------
    ax.autoscale()
    ax.set_xlabel("Time (s)", fontsize=12)
    ax.set_ylabel("Space (km)", fontsize=12)
    ax.set_xlim(200, 1600)
    ax.set_ylim(0, 8)

    cbar_ax = fig.add_axes([0.1, 0.88, 0.85, 0.03])
    cbar = plt.colorbar(lc_for_cbar, cax=cbar_ax, orientation='horizontal')
    cbar.set_label("Speed (km/h)", labelpad=-7)
    cbar.set_ticks([0, 30, 60, 90])
    cbar.ax.xaxis.set_ticks_position('top')
    cbar.ax.xaxis.set_label_position('top')

    # -----------------------------------------------------
    # Save figure
    # -----------------------------------------------------
    plt.savefig(f"jad_trajectory_{int(JAD_SPEED_KMH)}_{int(Et_OFFSET)}.png", dpi=150, bbox_inches="tight")
    plt.show()
    plt.close()


# =========================================================
# Entry point
# =========================================================
if __name__ == "__main__":

    # ----------------------
    # Check command line arguments
    # ----------------------
    if len(sys.argv) > 2:
        try:
            # First argument: JAD_SPEED_KMH
            JAD_SPEED_KMH = float(sys.argv[1])

            # Second argument: Et_OFFSET (used directly, no conversion)
            Et_OFFSET = float(sys.argv[2])

            print(f"JAD_SPEED: {int(JAD_SPEED_KMH)} km/h, Et_OFFSET: {Et_OFFSET}")

        except ValueError:
            print("--- Invalid arguments. Please provide two arguments: JAD_SPEED (km/h) and Et_OFFSET (s)")
            print("    Example: python d_2_simu_jad_plot_tx.py 55 0")
            sys.exit(1)
    else:
        print("--- Please provide two arguments: JAD_SPEED (km/h) and Et_OFFSET (s)")
        print("    Example: python d_2_simu_jad_plot_tx.py 55 0")
        sys.exit(1)
    
    
    plot_for_speed(JAD_SPEED_KMH, Et_OFFSET)