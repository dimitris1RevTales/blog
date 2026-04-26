import marimo

__generated_with = "0.23.3"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # The Tetris of Hotel Rooms

    Some empty rooms are a pricing problem. Some are a demand problem. And some are
    a quieter problem: **rooms that look sold out but aren't**, because the PMS can't
    see across how bookings are scattered inside each room type.

    This notebook shows how a small reshuffle can recover nights the hotel already
    earned — without changing demand, prices, or inventory.
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
        "tier1": "#93C5FD",
        "tier2": "#3B82F6",
        "tier3": "#1E3A8A",
        "opened": "#10B981",
        "lost": "#DC2626",
        "upgrade": "#F59E0B",
    }
    return PAL, np, plt


@app.cell
def _():
    TIERS = ("Standard", "Deluxe", "Suite")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Some hotels are not losing rooms to demand. They are losing them to calendar geometry.

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
    _rooms = 3
    _days = 14
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
        _ax.set_title(_title, fontweight="bold", pad=0, y=1.13)
        _ax.text(
            0.5,
            1.035,
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
        _w_a,
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

    plt.tight_layout(rect=[0, 0, 1, 0.9])
    plt.gca()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Why the reshuffle creates revenue options

    This section has two separate stories.

    First, compare **Baseline vs tetris**. Same rooms, same existing bookings,
    same prices. The only difference is how the calendar is packed. tetris creates
    more clean 3-day windows, so it creates more opportunities for a future guest to
    book a 3-night stay.

    Second, compare **Tetris vs Tetris Plus Upgrade**. That is not deterministic.
    Upgrading can free cheaper rooms, which may sell more often in soft demand, but
    it also consumes higher-priced rooms that might have sold. So the result is a
    distribution, not one guaranteed number.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    room_adr = mo.ui.number(start=80, stop=300, step=10, value=140, label="ADR for an extra 3-night booking (EUR)")
    window_pickup = mo.ui.slider(0.10, 1.00, step=0.05, value=0.65, label="Chance each extra 3-day window gets booked", full_width=True)
    mo.vstack([mo.md("### 1. Baseline vs tetris"), room_adr, window_pickup])
    return room_adr, window_pickup


@app.cell
def _(room_adr, window_pickup):
    comparison_days = 10
    confirmed_room_nights = 38
    baseline_windows = 1
    tetris_windows = 4
    extra_tetris_windows = tetris_windows - baseline_windows
    baseline_revenue = confirmed_room_nights * room_adr.value
    tetris_expected_revenue = baseline_revenue + (
        extra_tetris_windows * 3 * room_adr.value * window_pickup.value
    )
    tetris_extra_revenue = tetris_expected_revenue - baseline_revenue
    return (
        baseline_revenue,
        baseline_windows,
        comparison_days,
        extra_tetris_windows,
        tetris_expected_revenue,
        tetris_extra_revenue,
        tetris_windows,
    )


@app.cell(hide_code=True)
def _(
    baseline_revenue,
    baseline_windows,
    extra_tetris_windows,
    mo,
    room_adr,
    tetris_expected_revenue,
    tetris_extra_revenue,
    tetris_windows,
    window_pickup,
):
    _uplift = tetris_extra_revenue / baseline_revenue * 100
    mo.md(
        f"""
    <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:14px; margin: 0.5rem 0 1rem;">
      <div style="border:1px solid #E5E7EB; border-radius:16px; padding:18px; background:#F8FAFC;">
        <div style="font-size:14px; color:#475569; font-weight:700; text-transform:uppercase; letter-spacing:0.03em;">Baseline</div>
        <div style="font-size:32px; font-weight:850; color:#0F172A; margin-top:6px;">EUR {baseline_revenue:,.0f}</div>
        <div style="font-size:13px; color:#64748B; margin-top:4px;">confirmed revenue from existing bookings</div>
        <div style="margin-top:14px; padding-top:12px; border-top:1px solid #E2E8F0; display:flex; justify-content:space-between; gap:12px;">
          <span style="font-size:13px; color:#475569;">3-day windows</span>
          <strong style="font-size:18px; color:#0F172A;">{baseline_windows}</strong>
        </div>
        <div style="font-size:12px; color:#64748B; margin-top:4px;">few future 3-night stays can fit</div>
      </div>
      <div style="border:1px solid #BBF7D0; border-radius:16px; padding:18px; background:#F0FDF4;">
        <div style="font-size:14px; color:#166534; font-weight:700; text-transform:uppercase; letter-spacing:0.03em;">Tetris</div>
        <div style="font-size:32px; font-weight:850; color:#166534; margin-top:6px;">EUR {tetris_expected_revenue:,.0f}</div>
        <div style="font-size:13px; color:#64748B; margin-top:4px;">expected revenue after opening more 3-day windows</div>
        <div style="margin-top:14px; padding-top:12px; border-top:1px solid #BBF7D0; display:flex; justify-content:space-between; gap:12px;">
          <span style="font-size:13px; color:#475569;">3-day windows</span>
          <strong style="font-size:18px; color:#166534;">{tetris_windows} ({extra_tetris_windows:+d})</strong>
        </div>
        <div style="font-size:12px; color:#64748B; margin-top:4px;">+EUR {tetris_extra_revenue:,.0f} expected revenue, +{_uplift:.1f}% vs baseline</div>
        <div style="font-size:12px; color:#64748B; margin-top:4px;">{window_pickup.value:.0%} pickup x {extra_tetris_windows} windows x 3 nights x EUR {room_adr.value}</div>
      </div>
    </div>
    """
    )
    return


@app.cell(hide_code=True)
def _(
    PAL,
    baseline_revenue,
    baseline_windows,
    comparison_days,
    np,
    plt,
    tetris_expected_revenue,
    tetris_extra_revenue,
    tetris_windows,
):
    _fig, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(14, 6))
    _labels = ["Baseline", "tetris"]
    _revenues = [baseline_revenue, tetris_expected_revenue]
    _windows = [baseline_windows, tetris_windows]

    _ax1.bar(_labels, _revenues, color=["#94A3B8", PAL["opened"]], width=0.58)
    _ax1.set_title("Revenue rises because more 3-day stays can fit", fontweight="bold", pad=12)
    _ax1.set_ylabel("Expected revenue (EUR)")
    for _i, _value in enumerate(_revenues):
        _ax1.text(_i, _value * 0.52, f"EUR {_value:,.0f}", ha="center", va="center", color="white", fontweight="bold")
    _ax1.annotate(
        f"+EUR {tetris_extra_revenue:,.0f}",
        xy=(0.5, sum(_revenues) / 2),
        xytext=(0.5, max(_revenues) * 1.08),
        ha="center",
        fontweight="bold",
        color="#166534",
        arrowprops=dict(arrowstyle="->", color="#94A3B8", lw=1.2),
    )

    _x = np.arange(comparison_days)
    for _row, _n_windows in enumerate(_windows):
        _ax2.barh(_row, comparison_days, left=0, height=0.55, color="#E5E7EB")
        for _j in range(_n_windows):
            _start = min(comparison_days - 3, _j * 2)
            _ax2.barh(_row, 3, left=_start, height=0.55, color=PAL["opened"], edgecolor="#065F46", hatch="///")
    _ax2.set_yticks([0, 1])
    _ax2.set_yticklabels(_labels)
    _ax2.set_xticks(_x)
    _ax2.set_xticklabels([str(_d + 1) for _d in _x], fontsize=9)
    _ax2.set_xlim(0, comparison_days)
    _ax2.set_title("Available 3-day windows", fontweight="bold", pad=12)
    _ax2.set_xlabel("Day")

    for _ax in (_ax1, _ax2):
        for _spine in ["top", "right", "left"]:
            _ax.spines[_spine].set_visible(False)
    plt.tight_layout()
    plt.gca()
    return


@app.cell(hide_code=True)
def _(extra_tetris_windows, mo, tetris_extra_revenue, window_pickup):
    mo.callout(
        mo.md(
            f"tetris is higher because it creates **{extra_tetris_windows} additional 3-day windows**. "
            f"If each has a **{window_pickup.value:.0%}** chance of being booked, those windows are worth "
            f"**EUR {tetris_extra_revenue:,.0f}** in expected revenue. The algorithm is not inventing demand; "
            f"it is making room for demand that the baseline calendar cannot accept."
        ),
        kind="success",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    upgrade_mode = mo.ui.radio(
        options=["Off-season cheap demand", "Balanced", "High expensive demand"],
        value="Off-season cheap demand",
        label="Demand context",
    )
    upgrade_adr = mo.ui.number(start=80, stop=300, step=10, value=140, label="Cheap-room ADR (EUR)")
    premium_adr = mo.ui.number(start=120, stop=500, step=10, value=220, label="Expensive-room ADR (EUR)")
    mo.vstack([mo.md("### 2. Tetris vs Tetris + Upgrade"), upgrade_mode, mo.hstack([upgrade_adr, premium_adr])])
    return premium_adr, upgrade_adr, upgrade_mode


@app.cell
def _(premium_adr, tetris_expected_revenue, upgrade_adr, upgrade_mode):
    _profiles = {
        "Off-season cheap demand": (0.75, 0.25, 2, 1),
        "Balanced": (0.55, 0.45, 1, 1),
        "High expensive demand": (0.40, 0.75, 1, 1),
    }
    cheap_pickup_rate, expensive_pickup_rate, cheap_windows_freed, expensive_windows_used = _profiles[upgrade_mode.value]
    tetris_revenue = tetris_expected_revenue
    upgrade_ev = (
        cheap_pickup_rate * cheap_windows_freed * 3 * upgrade_adr.value
        - expensive_pickup_rate * expensive_windows_used * 3 * premium_adr.value
    )
    upgrade_mean_revenue = tetris_revenue + upgrade_ev
    return (
        cheap_pickup_rate,
        cheap_windows_freed,
        expensive_pickup_rate,
        expensive_windows_used,
        tetris_revenue,
        upgrade_ev,
        upgrade_mean_revenue,
    )


@app.cell(hide_code=True)
def _(
    PAL,
    cheap_windows_freed,
    expensive_windows_used,
    np,
    plt,
    premium_adr,
    tetris_revenue,
    upgrade_adr,
    upgrade_mean_revenue,
):
    _left = tetris_revenue - max(1, expensive_windows_used) * 3 * premium_adr.value * 0.9
    _right = tetris_revenue + max(1, cheap_windows_freed) * 3 * upgrade_adr.value * 1.4
    _x = np.linspace(_left, _right, 300)
    _z = (_x - _left) / (_right - _left)
    _alpha, _beta = 4.0, 2.2
    _density = (_z ** (_alpha - 1)) * ((1 - _z) ** (_beta - 1))
    _density = _density / np.trapezoid(_density, _x)
    _share_right = np.trapezoid(_density[_x > tetris_revenue], _x[_x > tetris_revenue])

    _fig, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(14, 6))
    _ax1.bar(
        ["Tetris", "Tetris Plus\nUpgrade mean"],
        [tetris_revenue, upgrade_mean_revenue],
        color=["#94A3B8", PAL["upgrade"]],
        width=0.58,
    )
    _ax1.set_title("Upgrade is an expected-value decision", fontweight="bold", pad=12)
    _ax1.set_ylabel("Revenue (EUR)")
    for _i, _value in enumerate([tetris_revenue, upgrade_mean_revenue]):
        _ax1.text(_i, _value * 0.52, f"EUR {_value:,.0f}", ha="center", va="center", color="white", fontweight="bold")

    _ax2.fill_between(_x, _density, color=PAL["tier2"], alpha=0.28)
    _ax2.plot(_x, _density, color=PAL["tier2"], lw=2.4)
    _ax2.axvline(tetris_revenue, color="#0F172A", lw=2, label="Tetris revenue")
    _ax2.axvline(upgrade_mean_revenue, color=PAL["upgrade"], lw=2, label="Plus Upgrade mean")
    _ax2.set_title(f"Tetris Plus Upgrade distribution ({_share_right:.0%} to the right)", fontweight="bold", pad=12)
    _ax2.set_xlabel("Revenue (EUR)")
    _ax2.set_ylabel("Probability")
    _ax2.legend(frameon=False)

    for _ax in (_ax1, _ax2):
        for _spine in ["top", "right", "left"]:
            _ax.spines[_spine].set_visible(False)
    plt.tight_layout()
    plt.gca()
    return


@app.cell(hide_code=True)
def _(
    cheap_pickup_rate,
    cheap_windows_freed,
    expensive_pickup_rate,
    expensive_windows_used,
    mo,
    upgrade_ev,
    upgrade_mode,
):
    _kind = "success" if upgrade_ev > 0 else "warn"
    mo.callout(
        mo.md(
            f"In the **{upgrade_mode.value}** context, upgrade mostly helps when cheap-room demand is more likely "
            f"than expensive-room demand. Here it frees **{cheap_windows_freed}** cheap 3-day window(s) with "
            f"a **{cheap_pickup_rate:.0%}** pickup probability, while consuming **{expensive_windows_used}** expensive "
            f"3-day window(s) with a **{expensive_pickup_rate:.0%}** pickup probability. The expected impact is "
            f"**EUR {upgrade_ev:,.0f}**."
        ),
        kind=_kind,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    **Revenue Tales `Smart Allocator`** is the production version of what this notebook
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
    **Baseline vs tetris.** This is a deliberately fixed, simplified example.
    Baseline and tetris start from the same confirmed booking revenue. tetris
    gets higher expected revenue only because it creates more 3-day windows that a
    future guest may book.

    **Window value.** Extra revenue is computed as: extra 3-day windows × pickup
    probability × 3 nights × ADR. The pickup slider is bounded above zero, so the
    tetris expected revenue is always higher in this example.

    **Tetris Plus Upgrade.** The upgrade section is not an operational booking
    simulation. It is an expected-value distribution: freed cheap-room windows can
    add revenue, while consumed expensive-room windows can subtract revenue.

    **What this is NOT.** Not a forecast. Not a substitute for your RMS. No
    seasonality, weekday/weekend skew, cancellations, loyalty rules, or channel mix.
    Figures are directional and meant to build intuition.
    """
            )
        }
    )
    return


if __name__ == "__main__":
    app.run()
