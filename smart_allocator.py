import marimo

__generated_with = "0.23.1"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # The Tetris of Hotel Rooms

    About a third of hotel rooms sit empty on any given night. Some of that is pricing.
    Some of it is demand. And some of it is a quieter problem: **rooms that look sold out
    but aren't**, because the PMS can't see across how bookings are scattered inside each
    room type.

    This notebook walks through two decisions every revenue manager makes daily —
    **how to assign bookings to rooms** and **when to upgrade a guest at no charge** —
    and puts numbers on what each one is worth.
    """)
    return


@app.cell
def _():
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import matplotlib.ticker as mticker

    plt.rcParams.update(
        {
            "axes.grid": True,
            "grid.color": "#E5E7EB",
            "grid.linewidth": 0.6,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
            "font.size": 14,
            "axes.titlesize": 18,
            "axes.labelsize": 14,
            "xtick.labelsize": 12,
            "ytick.labelsize": 12,
        }
    )

    PAL = {
        "revenue": "#2A9D8F",
        "variable": "#F4A261",
        "channel": "#E76F51",
        "fixed": "#A5A5A5",
        "profit": "#264653",
        "tier1": "#93C5FD",
        "tier2": "#3B82F6",
        "tier3": "#1E3A8A",
        "opened": "#10B981",
        "lost": "#DC2626",
        "upgrade": "#F59E0B",
    }
    return PAL, mpatches, mticker, np, plt


@app.cell
def _():
    TIERS = ("Standard", "Deluxe", "Suite")
    DEFAULT_ADR = {"Standard": 120, "Deluxe": 170, "Suite": 260}
    DEFAULT_CPOR = {"Standard": 30, "Deluxe": 42, "Suite": 58}
    return DEFAULT_ADR, DEFAULT_CPOR, TIERS


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Why nights look sold out that aren't

    Guests book a room **type** ("Standard Double"), not a specific room. The PMS
    assigns each booking to a physical room on arrival — first-come-first-served,
    more or less. That's fine when the hotel is half empty. When it fills up, the
    calendar fragments: Room 101 has a stay Mon–Wed, Room 102 has Tue–Thu, Room 103
    has Wed–Fri. A guest now asking for a 3-night stay starting Tuesday gets told
    "sold out" — even though a small reshuffle inside the Standard Double type would
    open one up.

    Below is the smallest possible version: six rooms, two weeks, eight bookings.
    On the left, how the PMS assigned them. On the right, the same bookings
    re-shuffled to close the gaps. The green-hatched blocks are new bookable
    3-night windows that appeared out of thin air.
    """)
    return


@app.cell(hide_code=True)
def _(PAL, np, plt):
    _rooms = 6
    _days = 14
    _rng = np.random.default_rng(7)

    _bookings = [
        (0, 3),
        (4, 2),
        (8, 3),
        (2, 2),
        (5, 3),
        (10, 2),
        (1, 2),
        (7, 4),
    ]

    def _fcfs(_n_rooms, _n_days, _bks):
        _cal = np.zeros((_n_rooms, _n_days), dtype=int)
        _assignments = []
        for _i, (_s, _l) in enumerate(_bks):
            for _r in range(_n_rooms):
                if _cal[_r, _s : _s + _l].sum() == 0:
                    _cal[_r, _s : _s + _l] = _i + 1
                    _assignments.append((_r, _s, _l, _i + 1))
                    break
            else:
                _assignments.append((None, _s, _l, _i + 1))
        return _cal, _assignments

    def _tetris(_n_rooms, _n_days, _bks):
        _order = sorted(range(len(_bks)), key=lambda _i: (-_bks[_i][1], _bks[_i][0]))
        _cal = np.zeros((_n_rooms, _n_days), dtype=int)
        _assignments = [None] * len(_bks)
        for _idx in _order:
            _s, _l = _bks[_idx]
            _best_room = None
            _best_slack = 10**9
            for _r in range(_n_rooms):
                if _cal[_r, _s : _s + _l].sum() != 0:
                    continue
                _left_gap = _s
                for _j in range(_s - 1, -1, -1):
                    if _cal[_r, _j] != 0:
                        _left_gap = _s - 1 - _j
                        break
                _right_gap = _n_days - (_s + _l)
                for _j in range(_s + _l, _n_days):
                    if _cal[_r, _j] != 0:
                        _right_gap = _j - (_s + _l)
                        break
                _slack = min(_left_gap, _right_gap)
                if _slack < _best_slack:
                    _best_slack = _slack
                    _best_room = _r
            if _best_room is not None:
                _cal[_best_room, _s : _s + _l] = _idx + 1
                _assignments[_idx] = (_best_room, _s, _l, _idx + 1)
            else:
                _assignments[_idx] = (None, _s, _l, _idx + 1)
        return _cal, _assignments

    def _count_windows(_cal, _k):
        _windows = []
        for _r in range(_cal.shape[0]):
            _run = 0
            for _d in range(_cal.shape[1]):
                if _cal[_r, _d] == 0:
                    _run += 1
                else:
                    _run = 0
                if _run == _k:
                    _windows.append((_r, _d - _k + 1, _k))
        return _windows

    _cal_a, _asg_a = _fcfs(_rooms, _days, _bookings)
    _cal_b, _asg_b = _tetris(_rooms, _days, _bookings)

    _w_a = _count_windows(_cal_a, 3)
    _w_b = _count_windows(_cal_b, 3)

    _fig, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True)

    def _draw(_ax, _asg, _wins, _title, _subtitle):
        for _a in _asg:
            if _a[0] is None:
                continue
            _r, _s, _l, _i = _a
            _ax.barh(
                _r,
                _l,
                left=_s,
                height=0.78,
                color=PAL["tier2"],
                edgecolor="#1E3A8A",
                linewidth=1.2,
                zorder=3,
            )
            _ax.text(
                _s + _l / 2,
                _r,
                f"#{_i}",
                ha="center",
                va="center",
                color="white",
                fontsize=10,
                fontweight="bold",
                zorder=4,
            )
        for _r, _s, _k in _wins:
            _ax.barh(
                _r,
                _k,
                left=_s,
                height=0.78,
                color="white",
                edgecolor=PAL["opened"],
                linewidth=2.0,
                hatch="///",
                zorder=2,
            )
        _ax.set_xlim(-0.5, _days - 0.5)
        _ax.set_ylim(-0.8, _rooms - 0.2)
        _ax.invert_yaxis()
        _ax.set_xticks(range(_days))
        _ax.set_xticklabels([f"{_d + 1}" for _d in range(_days)], fontsize=10)
        _ax.set_yticks(range(_rooms))
        _ax.set_yticklabels([f"Room {_r + 1}" for _r in range(_rooms)], fontsize=11)
        _ax.set_xlabel("Day")
        _ax.set_title(_title, fontweight="bold", pad=10)
        _ax.text(
            0.5,
            1.06,
            _subtitle,
            transform=_ax.transAxes,
            ha="center",
            va="bottom",
            fontsize=11,
            color="#475569",
        )
        _ax.grid(axis="x", color="#F1F5F9", linewidth=0.5, zorder=1)
        _ax.grid(axis="y", visible=False)
        for _spine in ["top", "right"]:
            _ax.spines[_spine].set_visible(False)

    _draw(
        _ax1,
        _asg_a,
        [],
        "Before: first-come-first-served",
        f"{len(_w_a)} bookable 3-night windows visible to the PMS",
    )
    _draw(
        _ax2,
        _asg_b,
        _w_b,
        "After: reshuffled (same inventory)",
        f"{len(_w_b)} bookable 3-night windows — {len(_w_b) - len(_w_a)} new ones (hatched)",
    )

    plt.tight_layout()
    plt.gca()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Should we upgrade this guest? The math

    The second decision is less visible but just as costly when it goes wrong.
    A guest books a Standard. You have a Deluxe sitting empty. Do you put them in it?

    The instinct says "yes, free upgrade, they'll be happy." The instinct is wrong
    as often as it's right. The decision turns on four numbers, not vibes:

    - **P_c** — probability another guest books the cheaper tier in this window.
    - **P_e** — same for the expensive tier.
    - **N_c, N_e** — rooms currently free in each tier.
    - **ΔCPOR** — the extra variable cost of an upgraded stay (bigger room, more linens).

    Upgrading **preserves** a cheap room (good if P_c is high and N_c is tight)
    and **consumes** an expensive room (bad if P_e is high and N_e is tight).
    It also costs a little more to service, but buys a small bump in review quality.
    You should upgrade when:

    $$\Delta \text{EV} = \underbrace{\text{expected cheap bookings saved} \cdot \text{ADR}_c}_{\text{upside}} \; - \; \underbrace{\text{expected expensive bookings lost} \cdot \text{ADR}_e}_{\text{downside}} \; - \; \Delta \text{CPOR} \; + \; r \; > \; 0$$

    The calculator below makes this concrete. Slide the probabilities and inventory;
    the heatmap shows which combinations tip the decision.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    lambda_c = mo.ui.slider(
        0.0, 10.0, step=0.25, value=5.0,
        label="Expected cheap arrivals (λ_c)", full_width=True,
    )
    lambda_e = mo.ui.slider(
        0.0, 10.0, step=0.25, value=2.0,
        label="Expected expensive arrivals (λ_e)", full_width=True,
    )
    n_c_ui = mo.ui.slider(
        1, 15, step=1, value=3,
        label="Cheap rooms free (N_c)", full_width=True,
    )
    n_e_ui = mo.ui.slider(
        1, 15, step=1, value=6,
        label="Expensive rooms free (N_e)", full_width=True,
    )
    delta_cpor_ui = mo.ui.slider(
        0.0, 30.0, step=1.0, value=12.0,
        label="Extra cost of upgraded stay, ΔCPOR (EUR)", full_width=True,
    )
    review_lift_ui = mo.ui.slider(
        0.0, 20.0, step=0.5, value=5.0,
        label="Review-quality lift (EUR per upgrade)", full_width=True,
    )

    mo.hstack(
        [
            mo.vstack(
                [mo.md("**Demand (remaining window)**"), lambda_c, lambda_e]
            ),
            mo.vstack(
                [mo.md("**Inventory & costs**"), n_c_ui, n_e_ui, delta_cpor_ui, review_lift_ui]
            ),
        ],
        widths=[1, 1],
    )
    return delta_cpor_ui, lambda_c, lambda_e, n_c_ui, n_e_ui, review_lift_ui


@app.cell(hide_code=True)
def _(
    DEFAULT_ADR,
    PAL,
    delta_cpor_ui,
    lambda_c,
    lambda_e,
    mpatches,
    n_c_ui,
    n_e_ui,
    np,
    plt,
    review_lift_ui,
):
    _adr_c = DEFAULT_ADR["Standard"]
    _adr_e = DEFAULT_ADR["Deluxe"]

    def _delta_ev(_lc, _le, _nc, _ne, _dcpor, _r, _ac, _ae):
        _cheap_saved = max(0.0, _lc - (_nc - 1)) - max(0.0, _lc - _nc)
        _exp_lost = max(0.0, _le - (_ne - 1)) - max(0.0, _le - _ne)
        _cheap_saved = min(1.0, _cheap_saved)
        _exp_lost = min(1.0, _exp_lost)
        return _cheap_saved * _ac - _exp_lost * _ae - _dcpor + _r

    _grid = 60
    _lc_axis = np.linspace(0, 10, _grid)
    _le_axis = np.linspace(0, 10, _grid)
    _LC, _LE = np.meshgrid(_lc_axis, _le_axis)
    _Z = np.zeros_like(_LC)
    for _i in range(_grid):
        for _j in range(_grid):
            _Z[_i, _j] = _delta_ev(
                _LC[_i, _j],
                _LE[_i, _j],
                n_c_ui.value,
                n_e_ui.value,
                delta_cpor_ui.value,
                review_lift_ui.value,
                _adr_c,
                _adr_e,
            )

    _fig, _ax = plt.subplots(figsize=(11, 7))

    _vmax = max(abs(_Z.min()), abs(_Z.max()), 1.0)
    _mesh = _ax.pcolormesh(
        _LC,
        _LE,
        _Z,
        shading="auto",
        cmap="RdYlGn",
        vmin=-_vmax,
        vmax=_vmax,
        zorder=1,
    )
    _ax.contour(_LC, _LE, _Z, levels=[0], colors="#111827", linewidths=2.0, zorder=2)

    _current = _delta_ev(
        lambda_c.value,
        lambda_e.value,
        n_c_ui.value,
        n_e_ui.value,
        delta_cpor_ui.value,
        review_lift_ui.value,
        _adr_c,
        _adr_e,
    )
    _marker_color = "#065F46" if _current > 0 else "#7F1D1D"
    _ax.scatter(
        [lambda_c.value],
        [lambda_e.value],
        s=260,
        color="white",
        edgecolor=_marker_color,
        linewidth=2.8,
        zorder=4,
    )
    _ax.annotate(
        f"You are here\nΔEV = {_current:+.1f} EUR",
        xy=(lambda_c.value, lambda_e.value),
        xytext=(lambda_c.value + 0.6, lambda_e.value + 0.6),
        ha="left",
        va="bottom",
        fontsize=11,
        fontweight="bold",
        color=_marker_color,
        bbox=dict(
            facecolor="white",
            edgecolor=_marker_color,
            boxstyle="round,pad=0.3",
            alpha=0.95,
        ),
        arrowprops=dict(arrowstyle="->", color=_marker_color, lw=1.3),
        zorder=5,
    )

    _cb = plt.colorbar(_mesh, ax=_ax, pad=0.02)
    _cb.set_label("ΔEV of upgrading (EUR)", fontsize=12)

    _ax.set_xlabel("λ_c — expected cheap arrivals ahead")
    _ax.set_ylabel("λ_e — expected expensive arrivals ahead")
    _ax.set_title(
        "When to upgrade: decision surface",
        fontweight="bold",
        pad=14,
    )
    _ax.text(
        0.5,
        -0.14,
        "Green = upgrade. Red = don't. Black line is the break-even frontier.",
        transform=_ax.transAxes,
        ha="center",
        va="top",
        fontsize=10,
        color="#475569",
        style="italic",
    )

    _ax.legend(
        handles=[
            mpatches.Patch(color=PAL["opened"], label="ΔEV > 0 → upgrade"),
            mpatches.Patch(color=PAL["lost"], label="ΔEV < 0 → don't upgrade"),
        ],
        loc="upper left",
        frameon=True,
    )

    for _spine in ["top", "right"]:
        _ax.spines[_spine].set_visible(False)
    plt.tight_layout()
    plt.gca()
    return


@app.cell(hide_code=True)
def _(
    DEFAULT_ADR,
    delta_cpor_ui,
    lambda_c,
    lambda_e,
    mo,
    n_c_ui,
    n_e_ui,
    review_lift_ui,
):
    _adr_c = DEFAULT_ADR["Standard"]
    _adr_e = DEFAULT_ADR["Deluxe"]
    _cheap_saved = min(
        1.0,
        max(0.0, lambda_c.value - (n_c_ui.value - 1))
        - max(0.0, lambda_c.value - n_c_ui.value),
    )
    _exp_lost = min(
        1.0,
        max(0.0, lambda_e.value - (n_e_ui.value - 1))
        - max(0.0, lambda_e.value - n_e_ui.value),
    )
    _dev = (
        _cheap_saved * _adr_c
        - _exp_lost * _adr_e
        - delta_cpor_ui.value
        + review_lift_ui.value
    )

    if _dev > 1:
        _kind = "success"
        _msg = (
            f"**Upgrade.** ΔEV = **+EUR {_dev:,.1f}** per guest.\n\n"
            f"Cheap demand is tight enough (λ_c = {lambda_c.value:.1f} against "
            f"{n_c_ui.value} free rooms) that preserving a Standard is worth "
            f"roughly **EUR {_cheap_saved * _adr_c:,.0f}** in expected future revenue. "
            f"Giving up a Deluxe costs about **EUR {_exp_lost * _adr_e:,.0f}**. "
            f"Net, after the EUR {delta_cpor_ui.value:.0f} extra cost and EUR "
            f"{review_lift_ui.value:.1f} review lift, you come out ahead."
        )
    elif _dev < -1:
        _kind = "warn"
        _msg = (
            f"**Don't upgrade.** ΔEV = **EUR {_dev:,.1f}** per guest.\n\n"
            f"Either the cheap tier isn't tight enough to matter "
            f"(λ_c = {lambda_c.value:.1f}, N_c = {n_c_ui.value}), "
            f"the expensive tier is (λ_e = {lambda_e.value:.1f}, N_e = {n_e_ui.value}), "
            f"or the extra service cost swamps the review lift. "
            f"Leaving the guest in Standard is the higher-EV move."
        )
    else:
        _kind = "info"
        _msg = (
            f"**Close call.** ΔEV = **EUR {_dev:,.1f}** — effectively zero. "
            f"Small shifts in any input flip the decision. In real operations "
            f"you'd decide by policy (e.g. always upgrade loyalty members) "
            f"rather than by math at this margin."
        )

    mo.callout(mo.md(_msg), kind=_kind)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Putting both pieces together over a month

    The calculator above is one decision. A hotel makes hundreds of them every week.
    The simulation below runs a full month of bookings through three policies:

    1. **Baseline** — first-come-first-served, no reshuffle, no upgrades.
    2. **+ Tetris** — same bookings, but reshuffled inside each room type to
       close gaps.
    3. **+ Tetris + Upgrade** — plus the expected-value upgrade rule applied
       to every booking.

    Pick a preset or tune the sliders. The Gantt pair and waterfall below
    re-draw reactively.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    preset = mo.ui.radio(
        options=[
            "Boutique (20 rooms)",
            "City hotel (60 rooms)",
            "Resort (120 rooms)",
            "Custom",
        ],
        value="City hotel (60 rooms)",
        label="Scenario preset",
    )
    mo.vstack(
        [
            mo.md(r"### Full-month simulation"),
            preset,
        ]
    )
    return (preset,)


@app.cell(hide_code=True)
def _(mo, preset):
    _presets = {
        "Boutique (20 rooms)": (20, 30, 0.85, 2.8, 42),
        "City hotel (60 rooms)": (60, 30, 0.85, 2.8, 42),
        "Resort (120 rooms)": (120, 30, 0.82, 3.5, 42),
        "Custom": (60, 30, 0.85, 2.8, 42),
    }
    _cfg = _presets[preset.value]

    n_rooms_ui = mo.ui.slider(
        10, 150, step=2, value=_cfg[0], label="Total rooms", full_width=True,
    )
    days_ui = mo.ui.slider(
        14, 45, step=1, value=_cfg[1], label="Simulation horizon (days)", full_width=True,
    )
    occupancy_ui = mo.ui.slider(
        0.5, 1.0, step=0.01, value=_cfg[2], label="Target occupancy", full_width=True,
    )
    avg_stay_ui = mo.ui.slider(
        1.5, 5.0, step=0.1, value=_cfg[3], label="Average length of stay (nights)", full_width=True,
    )
    seed_ui = mo.ui.number(
        start=0, stop=9999, step=1, value=_cfg[4], label="Random seed",
    )

    mo.vstack([n_rooms_ui, days_ui, occupancy_ui, avg_stay_ui, seed_ui])
    return avg_stay_ui, days_ui, n_rooms_ui, occupancy_ui, seed_ui


@app.cell(hide_code=True)
def _(mo):
    mix_std = mo.ui.slider(
        0.30, 0.80, step=0.01, value=0.55, label="Demand share: Standard", full_width=True,
    )
    mix_dlx = mo.ui.slider(
        0.10, 0.50, step=0.01, value=0.30, label="Demand share: Deluxe", full_width=True,
    )
    adr_std = mo.ui.number(
        start=60, stop=300, step=5, value=120, label="ADR Standard (EUR)",
    )
    adr_dlx = mo.ui.number(
        start=80, stop=400, step=5, value=170, label="ADR Deluxe (EUR)",
    )
    adr_ste = mo.ui.number(
        start=120, stop=600, step=10, value=260, label="ADR Suite (EUR)",
    )
    window_k = mo.ui.slider(
        2, 5, step=1, value=3, label="Window length k (for phantom metric)", full_width=True,
    )
    sim_review_lift = mo.ui.slider(
        0.0, 20.0, step=0.5, value=5.0, label="Review lift (EUR per upgrade)", full_width=True,
    )

    mo.accordion(
        {
            "Advanced tuning": mo.vstack(
                [
                    mo.md("**Demand mix** (Suite share is the remainder)"),
                    mix_std,
                    mix_dlx,
                    mo.md("**Rates**"),
                    mo.hstack([adr_std, adr_dlx, adr_ste]),
                    mo.md("**Metrics & policy**"),
                    window_k,
                    sim_review_lift,
                    mo.md(
                        "_Room split across tiers is fixed: 60% Standard, 30% Deluxe, "
                        "10% Suite (rounded). Per-tier CPOR is fixed at 30 / 42 / 58 EUR._"
                    ),
                ]
            )
        }
    )
    return (
        adr_dlx,
        adr_std,
        adr_ste,
        mix_dlx,
        mix_std,
        sim_review_lift,
        window_k,
    )


@app.cell
def _(TIERS, np):
    def rooms_by_tier(total_rooms):
        n_std = max(1, round(total_rooms * 0.60))
        n_ste = max(1, round(total_rooms * 0.10))
        n_dlx = max(1, total_rooms - n_std - n_ste)
        return {"Standard": n_std, "Deluxe": n_dlx, "Suite": n_ste}

    def generate_bookings(n_rooms, days, occupancy, avg_stay, mix, seed):
        rng = np.random.default_rng(int(seed))
        target = n_rooms * days * occupancy
        booked = 0.0
        bookings = []
        tiers_arr = np.array(TIERS)
        probs = np.array([mix["Standard"], mix["Deluxe"], mix["Suite"]])
        probs = probs / probs.sum()
        bid = 0
        while booked < target:
            tier = tiers_arr[rng.choice(3, p=probs)]
            los = int(max(1, min(days, 1 + rng.poisson(max(0.5, avg_stay - 1)))))
            start = int(rng.integers(0, days - los + 1))
            bookings.append(
                {
                    "id": bid,
                    "tier": tier,
                    "start": start,
                    "length": los,
                    "assigned_tier": None,
                    "assigned_room": None,
                    "status": "pending",
                }
            )
            booked += los
            bid += 1
        bookings.sort(key=lambda b: (b["start"], -b["length"]))
        return bookings

    def assign_fcfs(bookings, rooms_per_tier, days):
        calendars = {
            t: np.zeros((rooms_per_tier[t], days), dtype=int) for t in rooms_per_tier
        }
        for b in bookings:
            t = b["tier"]
            placed = False
            for r in range(rooms_per_tier[t]):
                if calendars[t][r, b["start"] : b["start"] + b["length"]].sum() == 0:
                    calendars[t][r, b["start"] : b["start"] + b["length"]] = b["id"] + 1
                    b["assigned_tier"] = t
                    b["assigned_room"] = r
                    b["status"] = "accepted"
                    placed = True
                    break
            if not placed:
                b["status"] = "rejected_baseline"
        return calendars

    def tetris_reshuffle(bookings, rooms_per_tier, days):
        calendars = {
            t: np.zeros((rooms_per_tier[t], days), dtype=int) for t in rooms_per_tier
        }
        bk_by_tier = {t: [] for t in rooms_per_tier}
        for b in bookings:
            b["assigned_tier"] = None
            b["assigned_room"] = None
            b["status"] = "pending"
            bk_by_tier[b["tier"]].append(b)
        for t, bks in bk_by_tier.items():
            order = sorted(bks, key=lambda x: (-x["length"], x["start"]))
            n_r = rooms_per_tier[t]
            for b in order:
                s, l = b["start"], b["length"]
                best_room = None
                best_slack = 10**9
                for r in range(n_r):
                    if calendars[t][r, s : s + l].sum() != 0:
                        continue
                    left_gap = s
                    for j in range(s - 1, -1, -1):
                        if calendars[t][r, j] != 0:
                            left_gap = s - 1 - j
                            break
                    right_gap = days - (s + l)
                    for j in range(s + l, days):
                        if calendars[t][r, j] != 0:
                            right_gap = j - (s + l)
                            break
                    slack = min(left_gap, right_gap)
                    if slack < best_slack:
                        best_slack = slack
                        best_room = r
                if best_room is not None:
                    calendars[t][best_room, s : s + l] = b["id"] + 1
                    b["assigned_tier"] = t
                    b["assigned_room"] = best_room
                    b["status"] = "accepted"
                else:
                    b["status"] = "rejected_real"
        return calendars

    def ev_upgrade_decision(
        lambda_c, lambda_e, n_c, n_e, adr_c, adr_e, cpor_c, cpor_e, review_lift
    ):
        cheap_saved = min(
            1.0, max(0.0, lambda_c - (n_c - 1)) - max(0.0, lambda_c - n_c)
        )
        exp_lost = min(
            1.0, max(0.0, lambda_e - (n_e - 1)) - max(0.0, lambda_e - n_e)
        )
        delta_cpor = cpor_e - cpor_c
        return cheap_saved * adr_c - exp_lost * adr_e - delta_cpor + review_lift

    def apply_upgrade_policy(
        bookings, calendars_tetris, rooms_per_tier, days, adrs, cpors, review_lift
    ):
        tier_up = {"Standard": "Deluxe", "Deluxe": "Suite", "Suite": None}
        arrivals_remaining = {t: 0 for t in rooms_per_tier}
        for b in bookings:
            arrivals_remaining[b["tier"]] += 1
        upgrades = 0
        for b in bookings:
            if b["status"] != "accepted":
                continue
            t_up = tier_up[b["tier"]]
            if t_up is None:
                continue
            arrivals_remaining[b["tier"]] -= 1
            s, l = b["start"], b["length"]
            free_c = sum(
                1
                for r in range(rooms_per_tier[b["tier"]])
                if calendars_tetris[b["tier"]][r, s : s + l].sum() == 0
            )
            free_c += 1
            free_e = sum(
                1
                for r in range(rooms_per_tier[t_up])
                if calendars_tetris[t_up][r, s : s + l].sum() == 0
            )
            remaining_days = max(1, days - s)
            total_remaining = max(1, sum(arrivals_remaining.values()))
            lam_c = arrivals_remaining[b["tier"]] * (l / remaining_days)
            lam_e = arrivals_remaining[t_up] * (l / remaining_days)
            dev = ev_upgrade_decision(
                lam_c,
                lam_e,
                max(1, free_c),
                max(1, free_e),
                adrs[b["tier"]],
                adrs[t_up],
                cpors[b["tier"]],
                cpors[t_up],
                review_lift,
            )
            if dev > 0 and free_e > 0:
                cur_t, cur_r = b["assigned_tier"], b["assigned_room"]
                calendars_tetris[cur_t][cur_r, s : s + l] = 0
                target_r = None
                for r in range(rooms_per_tier[t_up]):
                    if calendars_tetris[t_up][r, s : s + l].sum() == 0:
                        target_r = r
                        break
                if target_r is None:
                    calendars_tetris[cur_t][cur_r, s : s + l] = b["id"] + 1
                    continue
                calendars_tetris[t_up][target_r, s : s + l] = b["id"] + 1
                b["assigned_tier"] = t_up
                b["assigned_room"] = target_r
                b["status"] = "upgraded"
                upgrades += 1
        return calendars_tetris, upgrades

    def count_windows(calendar, k):
        count = 0
        for r in range(calendar.shape[0]):
            run = 0
            for d in range(calendar.shape[1]):
                if calendar[r, d] == 0:
                    run += 1
                    if run == k:
                        count += 1
                else:
                    run = 0
        return count

    def score_policy(bookings, calendars, adrs, cpors, rooms_per_tier, k):
        revenue = 0.0
        var_cost = 0.0
        n_accepted = 0
        n_upgraded = 0
        n_rejected = 0
        for b in bookings:
            if b["status"] == "accepted":
                revenue += adrs[b["tier"]] * b["length"]
                var_cost += cpors[b["tier"]] * b["length"]
                n_accepted += 1
            elif b["status"] == "upgraded":
                revenue += adrs[b["tier"]] * b["length"]
                var_cost += cpors[b["assigned_tier"]] * b["length"]
                n_accepted += 1
                n_upgraded += 1
            else:
                n_rejected += 1
        windows_by_tier = {
            t: count_windows(calendars[t], k) for t in rooms_per_tier
        }
        return {
            "revenue": revenue,
            "var_cost": var_cost,
            "profit": revenue - var_cost,
            "accepted": n_accepted,
            "upgraded": n_upgraded,
            "rejected": n_rejected,
            "windows": windows_by_tier,
        }

    def euro(x):
        return f"EUR {x:,.0f}"

    import copy as _copy

    def deep_clone_bookings(bks):
        return _copy.deepcopy(bks)

    return (
        apply_upgrade_policy,
        assign_fcfs,
        count_windows,
        deep_clone_bookings,
        euro,
        generate_bookings,
        rooms_by_tier,
        score_policy,
        tetris_reshuffle,
    )


@app.cell
def _(
    DEFAULT_CPOR,
    adr_dlx,
    adr_std,
    adr_ste,
    apply_upgrade_policy,
    assign_fcfs,
    avg_stay_ui,
    days_ui,
    deep_clone_bookings,
    generate_bookings,
    mix_dlx,
    mix_std,
    n_rooms_ui,
    occupancy_ui,
    rooms_by_tier,
    score_policy,
    seed_ui,
    sim_review_lift,
    tetris_reshuffle,
    window_k,
):
    _mix_ste = max(0.05, 1.0 - mix_std.value - mix_dlx.value)
    mix = {"Standard": mix_std.value, "Deluxe": mix_dlx.value, "Suite": _mix_ste}
    adrs = {"Standard": adr_std.value, "Deluxe": adr_dlx.value, "Suite": adr_ste.value}
    cpors = DEFAULT_CPOR

    rpt = rooms_by_tier(int(n_rooms_ui.value))
    days = int(days_ui.value)
    bookings_master = generate_bookings(
        int(n_rooms_ui.value),
        days,
        float(occupancy_ui.value),
        float(avg_stay_ui.value),
        mix,
        int(seed_ui.value),
    )

    bks_a = deep_clone_bookings(bookings_master)
    cal_a = assign_fcfs(bks_a, rpt, days)
    score_a = score_policy(bks_a, cal_a, adrs, cpors, rpt, int(window_k.value))

    bks_b = deep_clone_bookings(bookings_master)
    cal_b = tetris_reshuffle(bks_b, rpt, days)
    score_b = score_policy(bks_b, cal_b, adrs, cpors, rpt, int(window_k.value))

    bks_c = deep_clone_bookings(bookings_master)
    cal_c = tetris_reshuffle(bks_c, rpt, days)
    cal_c, _n_up = apply_upgrade_policy(
        bks_c, cal_c, rpt, days, adrs, cpors, float(sim_review_lift.value)
    )
    score_c = score_policy(bks_c, cal_c, adrs, cpors, rpt, int(window_k.value))
    return bks_a, bks_c, cal_a, cal_c, days, rpt, score_a, score_b, score_c


@app.cell(hide_code=True)
def _(euro, mo, score_a, score_b, score_c):
    _total_a = score_a["accepted"] + score_a["rejected"]
    _total_b = score_b["accepted"] + score_b["rejected"]
    _total_c = score_c["accepted"] + score_c["rejected"]

    def _pct(acc, total):
        return f"{acc / total * 100:.1f}%" if total else "—"

    def _sum_windows(w):
        return sum(w.values())

    mo.md(
        f"""
    | | Baseline | + Tetris | + Tetris + Upgrade |
    |---|---:|---:|---:|
    | **Revenue** | {euro(score_a['revenue'])} | {euro(score_b['revenue'])} | {euro(score_c['revenue'])} |
    | **Variable cost** | {euro(score_a['var_cost'])} | {euro(score_b['var_cost'])} | {euro(score_c['var_cost'])} |
    | **Profit** | **{euro(score_a['profit'])}** | **{euro(score_b['profit'])}** | **{euro(score_c['profit'])}** |
    | Accepted bookings | {score_a['accepted']} | {score_b['accepted']} | {score_c['accepted']} |
    | Upgraded | — | — | {score_c['upgraded']} |
    | Rejected | {score_a['rejected']} | {score_b['rejected']} | {score_c['rejected']} |
    | Acceptance rate | {_pct(score_a['accepted'], _total_a)} | {_pct(score_b['accepted'], _total_b)} | {_pct(score_c['accepted'], _total_c)} |
    | Bookable {3}-night windows | {_sum_windows(score_a['windows'])} | {_sum_windows(score_b['windows'])} | {_sum_windows(score_c['windows'])} |
    """
    )
    return


@app.cell(hide_code=True)
def _(
    PAL,
    TIERS,
    bks_a,
    bks_c,
    cal_a,
    cal_c,
    count_windows,
    days,
    mpatches,
    plt,
    rpt,
):
    _tier_colors = {
        "Standard": PAL["tier1"],
        "Deluxe": PAL["tier2"],
        "Suite": PAL["tier3"],
    }

    def _row_offsets(_rpt):
        _offs = {}
        _cur = 0
        for _t in TIERS:
            _offs[_t] = _cur
            _cur += _rpt[_t]
        return _offs, _cur

    _offs, _total_rows = _row_offsets(rpt)

    def _draw_board(_ax, _bks, _cal, _title, _subtitle, _mark_upgrades=False):
        for _b in _bks:
            if _b["status"] not in ("accepted", "upgraded"):
                continue
            _t = _b["assigned_tier"]
            _r = _b["assigned_room"]
            _y = _offs[_t] + _r
            _is_up = _b["status"] == "upgraded"
            _color = _tier_colors[_t]
            _edge = PAL["upgrade"] if (_is_up and _mark_upgrades) else "#0F172A"
            _lw = 2.2 if (_is_up and _mark_upgrades) else 0.6
            _ax.barh(
                _y,
                _b["length"],
                left=_b["start"],
                height=0.86,
                color=_color,
                edgecolor=_edge,
                linewidth=_lw,
                zorder=3,
            )
        _ax.set_xlim(-0.5, days - 0.5)
        _ax.set_ylim(-0.8, _total_rows - 0.2)
        _ax.invert_yaxis()
        _step = max(1, days // 15)
        _ax.set_xticks(range(0, days, _step))
        _ax.set_xticklabels([str(_d + 1) for _d in range(0, days, _step)], fontsize=9)
        _ax.set_yticks([])
        for _t in TIERS:
            _ax.axhline(
                _offs[_t] - 0.5, color="#CBD5E1", lw=0.8, zorder=1
            )
            _ax.text(
                -0.4,
                _offs[_t] + rpt[_t] / 2 - 0.5,
                _t,
                ha="right",
                va="center",
                fontsize=10,
                fontweight="bold",
                color="#334155",
                rotation=90,
            )
        _ax.set_xlabel("Day")
        _ax.set_title(_title, fontweight="bold", pad=8)
        _ax.text(
            0.5,
            1.02,
            _subtitle,
            transform=_ax.transAxes,
            ha="center",
            va="bottom",
            fontsize=11,
            color="#475569",
        )
        _ax.grid(axis="x", color="#F8FAFC", linewidth=0.4, zorder=1)
        _ax.grid(axis="y", visible=False)
        for _spine in ["top", "right", "left"]:
            _ax.spines[_spine].set_visible(False)

    _wins_a = sum(count_windows(cal_a[_t], 3) for _t in TIERS)
    _wins_c = sum(count_windows(cal_c[_t], 3) for _t in TIERS)
    _fig, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(15, 7.5), sharey=True)
    _draw_board(
        _ax1,
        bks_a,
        cal_a,
        "Baseline — first-come-first-served",
        f"{_wins_a} bookable 3-night windows",
    )
    _draw_board(
        _ax2,
        bks_c,
        cal_c,
        "After Tetris + Upgrade",
        f"{_wins_c} bookable 3-night windows ({_wins_c - _wins_a:+d})",
        _mark_upgrades=True,
    )

    _legend = [
        mpatches.Patch(color=PAL["tier1"], label="Standard"),
        mpatches.Patch(color=PAL["tier2"], label="Deluxe"),
        mpatches.Patch(color=PAL["tier3"], label="Suite"),
        mpatches.Patch(
            facecolor="white", edgecolor=PAL["upgrade"], linewidth=2, label="Upgraded booking"
        ),
    ]
    _fig.legend(handles=_legend, loc="lower center", ncol=5, frameon=False, fontsize=11)
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.gca()
    return


@app.cell(hide_code=True)
def _(PAL, euro, mticker, np, plt, score_a, score_b, score_c):
    _baseline_rev = score_a["revenue"]
    _tetris_gain = score_b["revenue"] - score_a["revenue"]
    _upgrade_gain = score_c["revenue"] - score_b["revenue"]
    _final = score_c["revenue"]

    _labels = [
        "Baseline\nrevenue",
        "+ Tetris\nreshuffle",
        "+ Upgrade\npolicy",
        "Final\nrevenue",
    ]
    _values = [_baseline_rev, _tetris_gain, _upgrade_gain, _final]

    _bottoms = [0, _baseline_rev, _baseline_rev + _tetris_gain, 0]
    _heights = [_baseline_rev, _tetris_gain, _upgrade_gain, _final]
    _colors = [
        PAL["fixed"],
        PAL["opened"] if _tetris_gain >= 0 else PAL["lost"],
        PAL["upgrade"] if _upgrade_gain >= 0 else PAL["lost"],
        PAL["profit"],
    ]

    _fig, _ax = plt.subplots(figsize=(13, 7))
    _x = np.arange(len(_labels))
    _w = 0.55

    _ax.bar(
        _x,
        _heights,
        bottom=_bottoms,
        width=_w,
        color=_colors,
        edgecolor="white",
        linewidth=1.6,
        zorder=3,
    )

    _cum = [_baseline_rev, _baseline_rev + _tetris_gain, _final]
    for _i in range(3):
        _ax.plot(
            [_x[_i] + _w / 2, _x[_i + 1] - _w / 2],
            [_cum[_i], _cum[_i]],
            color="#94A3B8",
            ls="--",
            lw=1.3,
            zorder=4,
        )

    for _i, (_xi, _bot, _h) in enumerate(zip(_x, _bottoms, _heights)):
        _label = euro(_h) if _i == 0 or _i == 3 else (f"+{euro(_h)}" if _h >= 0 else f"-{euro(abs(_h))}")
        _txtc = "white" if _i in (0, 3) else "#111827"
        _ax.text(
            _xi,
            _bot + _h / 2,
            _label,
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold",
            color=_txtc,
        )

    _ax.set_xticks(_x)
    _ax.set_xticklabels(_labels, fontsize=11)
    _ax.set_ylabel("EUR")
    _ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _p: f"{v / 1000:.0f}k")
    )
    _ax.set_title(
        "Where the recovered revenue comes from",
        fontweight="bold",
        pad=14,
    )
    _ax.axhline(0, color="black", lw=0.8)
    for _spine in ["top", "right", "left"]:
        _ax.spines[_spine].set_visible(False)
    plt.tight_layout()
    plt.gca()
    return


@app.cell(hide_code=True)
def _(euro, mo, score_a, score_b, score_c):
    _tetris_gain = score_b["revenue"] - score_a["revenue"]
    _upgrade_gain = score_c["revenue"] - score_b["revenue"]
    _total_gain = score_c["revenue"] - score_a["revenue"]
    _base = max(score_a["revenue"], 1.0)
    _pct = _total_gain / _base * 100

    if _total_gain > 100:
        _kind = "success"
        _msg = (
            f"In this configuration, reshuffling plus smart upgrades recovers "
            f"**{euro(_total_gain)}** over a month — about **{_pct:.1f}%** on top of baseline revenue.\n\n"
            f"The Tetris reshuffle alone is worth {euro(_tetris_gain)} "
            f"({_tetris_gain / _base * 100:.1f}%); the upgrade policy adds another "
            f"{euro(_upgrade_gain)} ({_upgrade_gain / _base * 100:.1f}%).\n\n"
            f"That's money the hotel already earned — it just wasn't being collected because "
            f"the PMS couldn't see past its own fragmentation."
        )
    elif _total_gain < -100:
        _kind = "warn"
        _msg = (
            f"At these parameters, the policies **cost** {euro(abs(_total_gain))} — unusual and worth "
            f"a closer look. Likely cause: demand is so slack that reshuffles don't open "
            f"anything useful and upgrades just burn extra variable cost. Try raising occupancy "
            f"or tightening inventory."
        )
    else:
        _kind = "info"
        _msg = (
            f"At these parameters the three policies produce nearly identical revenue "
            f"({euro(score_c['revenue'])}). Most hotels spend a lot of time here — the gains only "
            f"show up when occupancy is high enough that fragmentation starts costing real nights. "
            f"Try raising the target occupancy or shortening the average stay."
        )

    mo.callout(mo.md(_msg), kind=_kind)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Stop losing nights you already earned

    Phantom availability and under-used upgrade logic are two of the quietest revenue
    leaks in hotel operations. Neither is about pricing. Both compound every week the
    PMS is left to assign rooms on its own.

    **Revenue Tales Smart Allocator** is the production version of what this notebook
    demonstrates: it reshuffles bookings inside each room type to close single-night
    gaps, respects locked reservations, and runs in seconds against live PMS inventory.

    **Two ways to get started:**

    **See the product** — walkthrough, screenshots, and how it plugs into your PMS:

    [revenuetales.com/smart-allocator](https://revenuetales.com/smart-allocator/)

    **Book a free call** to discuss your property's allocation and revenue setup:

    [Schedule a conversation](https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ2syk0Pi9fSaSg7ee_0Ifha38X9eRwfVqVSn0vl8ojxuJKKgkxwmzF9agli7gHC1fvfiFTGTmxu)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "Methodology & Assumptions": mo.md(
                r"""
    **Bookings.** Arrival times are uniform over the horizon; length of stay is
    1 + Poisson(avg_stay − 1), capped at the horizon. Tier is drawn from the demand
    mix (Standard / Deluxe / Suite share). The generator keeps producing requests
    until target room-nights are reached.

    **Baseline (FCFS).** Bookings are sorted by arrival date and assigned to the
    first free room of the requested tier. This is a deterministic stand-in for how
    many PMSs allocate rooms when staff don't intervene.

    **Tetris reshuffle.** Per tier, bookings are re-ordered longest-first and placed
    using a best-fit rule: pick the room where the booking leaves the smallest gap
    to its nearest neighbour. This is a transparent greedy heuristic, not an
    optimal solution (the general problem is NP-hard). Production Smart Allocator
    uses a more sophisticated solver.

    **Upgrade policy.** For every accepted booking that is not already in the top
    tier, we estimate expected remaining arrivals in the current and next tier,
    scaled by the booking's length relative to days remaining. We compute
    ΔEV = (expected cheap bookings saved) × ADR_c − (expected expensive bookings lost) ×
    ADR_e − ΔCPOR + review_lift, and upgrade iff ΔEV > 0. The 1-node bounded
    marginal (cheap_saved, exp_lost ∈ [0, 1]) reflects the fact that one upgrade
    moves at most one unit of demand between tiers.

    **Windows metric.** A "bookable k-night window" is a contiguous stretch of k or
    more free nights on a single room. We report the k=3 count; the slider exposes
    other k values.

    **What this simulation is NOT.** Not a forecast. Not a substitute for your RMS.
    No seasonality, no weekday/weekend skew, no cancellations, no loyalty-tier
    upgrade entitlements, no channel costs, no fixed overhead. Figures are directional
    and meant to build intuition.
    """
            )
        }
    )
    return


if __name__ == "__main__":
    app.run()
