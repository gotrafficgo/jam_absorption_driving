import numpy as np
import matplotlib.pyplot as plt


# ===================== LaTeX style =====================
plt.rcParams.update({
    "text.usetex": True,
    "xtick.labelsize": 20,
    "ytick.labelsize": 20,
    "axes.labelsize": 27
})


# ===================== Calculation function =====================
def get_J(delta_w, w, v_t, v_w, v_star):
    numerator   = - v_star * w * delta_w * (v_t - v_w) * (w - v_star)
    denominator = (v_star - w) * (w - v_w) * (v_t - v_star)

    J_dis = numerator / denominator
    J_dur = J_dis / v_star
    return J_dis, J_dur


# ===================== Parameter ranges =====================
param_ranges = {
    'v^*': (40, 80),
    'v_t': (80, 120),
    r'\Delta_w': (20, 100),
    'w': (-20, -10),
    'v_w': (0, 20)
}

param_mid = {
    k: (v[0] + v[1]) / 2
    for k, v in param_ranges.items()
}


# ===================== x-axis labels =====================
xlabels = {
    'v^*': r"$v^*$ (km/h)",
    'v_t': r"$v_t$ (km/h)",
    r'\Delta_w': r"$\Delta_w$ (s)",
    'w': r"$w$ (km/h)",
    'v_w': r"$v_w$ (km/h)"
}


# ===================== Single plot =====================
def plot_one(param, xlabel, num_points=200, save_pdf=True):

    pmin, pmax = param_ranges[param]
    x = np.linspace(pmin, pmax, num_points)

    J_dis_list = []
    J_dur_list = []

    for val in x:
        args = param_mid.copy()
        args[param] = val

        J_dis, J_dur = get_J(
            delta_w=args[r'\Delta_w'],
            w=args['w'],
            v_t=args['v_t'],
            v_w=args['v_w'],
            v_star=args['v^*']
        )

        J_dis_list.append(J_dis / 1000)  # km
        J_dur_list.append(J_dur)         # s

    fig, ax1 = plt.subplots(figsize=(6, 6))


    # ===== Left axis: J_dis =====
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(r"$J_{\mathrm{dis}}$ (km)", color="blue")

    ax1.plot(
        x, J_dis_list,
        color="blue",
        linewidth=4,
        label=r"$J_{\mathrm{dis}}$"
    )

    ax1.tick_params(axis='y', labelcolor="blue")
    ax1.grid(True, linestyle=':', linewidth=2, alpha=0.7)


    # ===== Fix x-axis ticks: min / middle / max =====
    pmid = (pmin + pmax) / 2
    ax1.set_xticks([pmin, pmid, pmax])


    # ===== Right axis: J_dur =====
    ax2 = ax1.twinx()
    ax2.set_ylabel(r"$J_{\mathrm{dur}}$ (s)", color="red")

    ax2.plot(
        x, J_dur_list,
        color="red",
        linestyle="--",
        linewidth=3,
        label=r"$J_{\mathrm{dur}}$"
    )

    ax2.tick_params(axis='y', labelcolor="red")

    fig.tight_layout()


    # ===== Save figure =====
    if save_pdf:
        safe_param = (
            param.replace('^', '')
                 .replace('\\', '')
                 .replace('{', '')
                 .replace('}', '')
        )
        fig.savefig(f"J_vs_{safe_param}.png", bbox_inches='tight')
        print(f"Saved: J_vs_{safe_param}.png")

    plt.show()


# ===================== Auto-plot all =====================
for p in param_ranges:
    plot_one(p, xlabels[p])