import os
import sys
import traci
from scipy.optimize import brentq
import ALL_FUNCTIONS as Func

# ----------------------
# JAD Parameters
# ----------------------
WAVE_SPEED = -15 / 3.6       # 16 km/h -> m/s
FLAG_JAD_PLAN = True
FLAG_JAD_IMPLEMENT = True
JAD_PLAN = {}

# ----------------------
# Check command-line arguments
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
        print("    Example: python d_1_simu_jad.py 55 0")
        sys.exit(1)
else:
    print("--- Please provide two arguments: JAD_SPEED (km/h) and Et_OFFSET (s)")
    print("    Example: python d_1_simu_jad.py 55 0")
    print("    Example: python d_1_simu_jad.py 55 -40")
    print("    Example: python d_1_simu_jad.py 35 0")
    sys.exit(1)

JAD_SPEED = JAD_SPEED_KMH / 3.6  # Convert to m/s

# ----------------------
# Ramp insertion trigger parameters
# ----------------------
RAMP = 1000.0             # Ramp insertion trigger location (m)
THRESHOLD_INSERT = 3.0    # Time headway threshold (s)

# ----------------------
# Detector locations
# ----------------------
DETECTOR_LOC_UPSTREAM = 500
DETECTOR_LOC_DOWNSTREAM = 7000

# -------------------------------
# Stop-and-go detection criteria
# -------------------------------
SG_MAX_SPEED = 10.0   # m/s
SG_MIN_DURATION = 30  # seconds

# ----------------------
# Configuration and parameters
# ----------------------
SUMO_CFG = "run.sumocfg"
sumo_binary = os.path.join(os.environ["SUMO_HOME"], "bin", "sumo")
seed = 1
sumo_cmd = [sumo_binary, "-c", SUMO_CFG, "--start", "--no-warnings", "--seed", str(seed)]


def run_simulation():
    """
    SUMO main simulation loop
    - First vehicle braking disturbance
    - Ramp insertion and three-stage control
    - Upstream / downstream dual detector monitoring
    - Export CSV after simulation
    """
    end_time = Func.get_simulation_end_time(SUMO_CFG)
    traci.start(sumo_cmd)

    step = 0
    target_vehicle = None
    stopped = False

    # -------------------------------
    # Upstream / downstream detector monitoring
    # -------------------------------
    last_pos_up = {}
    last_pos_down = {}
    sg_state_up = {}
    sg_state_down = {}
    records_up = []
    records_down = []

    # -------------------------------
    # Jam-absorption strategy
    # -------------------------------
    flag_jad_plan = FLAG_JAD_PLAN
    last_position_insert = {}
    inserted_count = 0
    insertion_info = None

    A = B = C = D = E = F = None
    Duration_AB = Duration_BC = None

    while step < end_time:
        traci.simulationStep()
        veh_ids = traci.vehicle.getIDList()

        # ----------------------------------
        # First vehicle natural braking
        # ----------------------------------
        target_vehicle, stopped = Func.handle_first_vehicle_braking(
            step, veh_ids, target_vehicle, stopped
        )

        # ----------------------------------
        # Upstream detection
        # ----------------------------------
        last_pos_up, events_up, _ = Func.detector(
            step, veh_ids, last_pos=last_pos_up, location=DETECTOR_LOC_UPSTREAM,
            sg_state=sg_state_up, sg_max_speed=SG_MAX_SPEED, sg_min_duration=SG_MIN_DURATION
        )
        if events_up:
            records_up.extend(events_up)

        # ----------------------------------
        # Downstream detection
        # ----------------------------------
        last_pos_down, events_down, sg_down = Func.detector(
            step, veh_ids, last_pos=last_pos_down, location=DETECTOR_LOC_DOWNSTREAM,
            sg_state=sg_state_down, sg_max_speed=SG_MAX_SPEED, sg_min_duration=SG_MIN_DURATION
        )
        if events_down:
            records_down.extend(events_down)

        # ----------------------------------
        # Print information if stop-and-go is detected
        # ----------------------------------
        if sg_down is not None:
            F = (sg_down["t_start"], DETECTOR_LOC_DOWNSTREAM)
            E = (sg_down["t_end"], DETECTOR_LOC_DOWNSTREAM)
            vw = sg_down["v_min"]

            E = (E[0] + Et_OFFSET, E[1])  # Add buffer time for point A

            print(
                f"\n[SG detected at {sg_down['location']} m] "
                f"start={sg_down['t_start']} s, "
                f"end={sg_down['t_end']} s, "
                f"duration={sg_down['duration']} s, "
                f"v_start={sg_down['v_start']:.2f} m/s, "
                f"v_end={sg_down['v_end']:.2f} m/s, "
                f"v_min={sg_down['v_min']:.2f} m/s, "
                f"v_mean={sg_down['v_mean']:.2f} m/s"
            )

        # ----------------------------------
        # Check ramp insertion opportunity
        # ----------------------------------
        if E is not None and F is not None:
            last_position_insert, insertion_info = Func.check_insertion_opportunity_at_ramp(
                RAMP, THRESHOLD_INSERT, step, veh_ids, last_position_insert
            )

        # ----------------------------------
        # Execute JAD strategy (once: compute A/B/C + insertion)
        # ----------------------------------
        if insertion_info and E and F and flag_jad_plan:
            A = (step, RAMP)
            vt = insertion_info["leader_v"]

            # JAD Plan
            B, C, D = Func.plan_jad(JAD_SPEED, WAVE_SPEED, A, E, F, vt, vw)
            Duration_AB = int(B[0] - A[0])
            Duration_BC = int(C[0] - B[0])

            print(
                f"[JAD Input] "
                f"A ({int(A[0])},{int(A[1])}), "
                f"E ({int(E[0])},{int(E[1])}), "
                f"F ({int(F[0])},{int(F[1])}), "
                f"vt={vt:.2f} m/s, vw={vw:.2f} m/s, w={WAVE_SPEED:.2f} m/s"
            )

            print(
                f"[JAD Strategy] "
                f"A ({int(A[0])},{int(A[1])}), "
                f"B ({int(B[0])},{int(B[1])}), "
                f"C ({int(C[0])},{int(C[1])})"
            )

            P1, P2, P3 = Func.get_feasible_region_of_A(
                E, F, vt, vw, JAD_SPEED, WAVE_SPEED, DETECTOR_LOC_UPSTREAM
            )

            print(
                f"[Feasible Region of A] "
                f"P1 ({int(P1[0])},{int(P1[1])}), "
                f"P2 ({int(P2[0])},{int(P2[1])}), "
                f"P3 ({int(P3[0])},{int(P3[1])})"
            )

            if FLAG_JAD_IMPLEMENT:
                inserted_count = Func.insert_vehicle_at_ramp(
                    JAD_PLAN, step, insertion_info, inserted_count
                )

            flag_jad_plan = False

        # ----------------------------------
        # Control inserted vehicles at each step
        # ----------------------------------
        if FLAG_JAD_IMPLEMENT and JAD_PLAN is not None:
            Func.control_inserted_vehicles(JAD_PLAN, JAD_SPEED, step, Duration_AB, Duration_BC)

        step += 1

    traci.close()

    # ----------------------------------
    # Save results
    # ----------------------------------
    if FLAG_JAD_PLAN:
        Func.save_result(
            JAD_SPEED, WAVE_SPEED, Et_OFFSET, records_up, records_down,
            A, B, C, D, E, F,
            P1, P2, P3,
            vt, vw
        )

    print("Simulation finished\n")

    # ----------------------------------
    # Rename trajectory file
    # ----------------------------------
    old_name = "trajectory.xml"
    new_name = f"d_1_jad_trajectory_{int(JAD_SPEED*3.6)}_{int(Et_OFFSET)}.xml"

    if os.path.exists(old_name):
        os.rename(old_name, new_name)
        print(f"File saved as: {new_name}\n")
    else:
        print("trajectory.xml file not found")


# ======================================================
# Main entry
# ======================================================
if __name__ == "__main__":
    run_simulation()