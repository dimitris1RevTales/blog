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
    # Occupancy Is a Vanity Metric

    95% occupancy sounds impressive — until you see the hotel at 80% making more profit.

    This interactive simulation lets you explore why **fewer rooms at a higher rate**
    often beats a **full house at a discount**. Adjust the sliders, pick a preset,
    and watch the math change in real time.
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
    }
    return PAL, mpatches, mticker, np, plt


@app.cell
def _():
    TOTAL_ROOMS = 100
    DAYS = 30
    return DAYS, TOTAL_ROOMS


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## How Hotel Revenue Becomes Profit

    Revenue is only the starting line. Every room sold carries variable costs —
    housekeeping, laundry, amenities, breakfast. Then channel costs (OTA commissions
    and booking fees) take their cut. Fixed costs hit regardless of occupancy.
    What survives all three layers is your actual profit.
    """)
    return


@app.cell(hide_code=True)
def _(DAYS, PAL, TOTAL_ROOMS, mticker, np, plt):
    from matplotlib.transforms import blended_transform_factory as _btf

    _occ, _adr = 0.80, 120
    _cpor, _fixed, _chan = 35, 2000, 0.10

    _rooms = TOTAL_ROOMS * _occ * DAYS
    _revenue = _rooms * _adr
    _var = _rooms * _cpor
    _channel = _revenue * _chan
    _fix = _fixed * DAYS
    _profit = _revenue - _var - _channel - _fix


    def _efmt(x):
        return f"EUR {x:,.0f}"


    _labels = [
        "Revenue",
        "Variable\nCosts",
        "Channel\nCosts",
        "Fixed\nCosts",
        "Net Profit",
    ]
    _bottoms = [0, _revenue, _revenue - _var, _revenue - _var - _channel, 0]
    _heights = [_revenue, -_var, -_channel, -_fix, _profit]
    _colors = [
        PAL["revenue"],
        PAL["variable"],
        PAL["channel"],
        PAL["fixed"],
        PAL["profit"],
    ]
    _txtc = ["white", "#111827", "white", "#111827", "white"]

    _fig, _ax = plt.subplots(figsize=(14, 7))
    _x = np.arange(len(_labels))
    _w = 0.52

    _ax.bar(
        _x,
        _heights,
        bottom=_bottoms,
        width=_w,
        color=_colors,
        edgecolor="white",
        linewidth=1.8,
        zorder=3,
    )

    _cum = [_revenue, _revenue - _var, _revenue - _var - _channel, _profit]
    for _i in range(len(_cum)):
        _ax.plot(
            [_x[_i] + _w / 2, _x[_i + 1] - _w / 2],
            [_cum[_i], _cum[_i]],
            color="#94A3B8",
            ls="--",
            lw=1.3,
            zorder=4,
        )

    for _i, (_xi, _bot, _h) in enumerate(zip(_x, _bottoms, _heights)):
        _ax.text(
            _xi,
            _bot + _h / 2,
            _efmt(abs(_h)),
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold",
            color=_txtc[_i],
        )

    _descs = [
        f"{_rooms:,.0f} rooms \u00d7 {_efmt(_adr)}/night",
        "housekeeping, laundry,\namenities, breakfast",
        "OTA commissions\n& booking fees",
        "staff, mortgage,\nutilities",
        f"{_profit / _revenue * 100:.0f}% margin",
    ]
    _trans = _btf(_ax.transData, _ax.transAxes)
    for _i, _xi in enumerate(_x):
        _ax.text(
            _xi,
            -0.10,
            _descs[_i],
            transform=_trans,
            ha="center",
            va="top",
            fontsize=9,
            color="#6B7280",
            style="italic",
            linespacing=1.3,
        )

    _ax.set_xticks(_x)
    _ax.set_xticklabels(_labels, fontsize=11)
    _ax.set_ylabel("EUR", fontsize=12)
    _ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _p: f"{v / 1000:.0f}k")
    )
    _ax.set_title(
        "How Hotel Revenue Becomes Profit",
        fontweight="bold",
        fontsize=16,
        pad=18,
    )
    _ax.axhline(0, color="black", lw=0.8)
    for _spine in ["top", "right", "left"]:
        _ax.spines[_spine].set_visible(False)
    plt.tight_layout()
    plt.gca()
    return


@app.cell(hide_code=True)
def _(mo):
    preset = mo.ui.radio(
        options=["95% vs 80% occupancy", "98% vs 70% occupancy", "Custom"],
        value="95% vs 80% occupancy",
        label="Scenario preset",
    )
    mo.vstack(
        [
            mo.md(
                r"""
            ---

            ## Compare Two Strategies

            Pick a preset matching the LinkedIn posts, or choose **Custom** to experiment.
            """
            ),
            preset,
        ]
    )
    return (preset,)


@app.cell(hide_code=True)
def _(mo, preset):
    _presets = {
        "95% vs 80% occupancy": (95, 100, 80, 114),
        "98% vs 70% occupancy": (98, 100, 70, 130),
        "Custom": (90, 110, 75, 130),
    }
    _cfg = _presets[preset.value]

    occ_a = mo.ui.number(
        start=30,
        stop=100,
        value=_cfg[0],
        step=1,
        label="Occupancy (%)",
    )
    adr_a = mo.ui.number(
        start=50,
        stop=300,
        value=_cfg[1],
        step=1,
        label="ADR (EUR)",
    )
    occ_b = mo.ui.number(
        start=30,
        stop=100,
        value=_cfg[2],
        step=1,
        label="Occupancy (%)",
    )
    adr_b = mo.ui.number(
        start=50,
        stop=300,
        value=_cfg[3],
        step=1,
        label="ADR (EUR)",
    )

    mo.hstack(
        [
            mo.vstack([mo.md("### Hotel A — High Volume"), occ_a, adr_a]),
            mo.vstack([mo.md("### Hotel B — Higher Rate"), occ_b, adr_b]),
        ],
        widths=[1, 1],
    )
    return adr_a, adr_b, occ_a, occ_b


@app.cell(hide_code=True)
def _(mo):
    fixed_daily = mo.ui.number(
        start=500, stop=10000, step=100, value=2000, label="Fixed daily cost (EUR)",
    )
    base_cpor = mo.ui.number(
        start=10, stop=100, step=1, value=35, label="Variable cost per room (EUR)",
    )
    surge_threshold = mo.ui.slider(
        0.50, 1.0, step=0.05, value=0.90, label="Surge threshold", full_width=True,
    )
    surge_rate = mo.ui.slider(
        0.0, 0.50, step=0.05, value=0.10, label="Surge rate", full_width=True,
    )
    channel_rate = mo.ui.slider(
        0.0, 0.30, step=0.01, value=0.10, label="Channel cost rate", full_width=True,
    )

    mo.accordion({
        "Cost Parameters (advanced)": mo.vstack([
            fixed_daily,
            base_cpor,
            surge_threshold,
            surge_rate,
            channel_rate,
            mo.md(
                "_Defaults: EUR 2,000 fixed/day, EUR 35/room variable, "
                "10% surge above 90% occupancy, 10% channel costs._"
            ),
        ])
    })
    return base_cpor, channel_rate, fixed_daily, surge_rate, surge_threshold


@app.cell
def _(
    DAYS,
    TOTAL_ROOMS,
    base_cpor,
    channel_rate,
    fixed_daily,
    surge_rate,
    surge_threshold,
):
    def cpor(occupancy):
        """Variable cost per occupied room, with surge above threshold."""
        if occupancy > surge_threshold.value:
            return base_cpor.value * (1 + surge_rate.value)
        return base_cpor.value

    def simulate(name, occupancy, adr):
        """Run a single monthly simulation."""
        rooms_sold = TOTAL_ROOMS * occupancy * DAYS
        revenue = rooms_sold * adr
        variable_costs = rooms_sold * cpor(occupancy)
        channel_costs = revenue * channel_rate.value
        fixed_costs = fixed_daily.value * DAYS
        net_profit = revenue - variable_costs - channel_costs - fixed_costs
        margin_pct = (net_profit / revenue * 100) if revenue else 0
        return {
            "Scenario": name,
            "Occupancy": occupancy,
            "ADR": adr,
            "Rooms Sold": rooms_sold,
            "Revenue": revenue,
            "Variable Costs": variable_costs,
            "Channel Costs": channel_costs,
            "Fixed Costs": fixed_costs,
            "Net Profit": net_profit,
            "Margin %": margin_pct,
        }

    def euro(x):
        return f"EUR {x:,.0f}"

    return euro, simulate


@app.cell
def _(adr_a, adr_b, occ_a, occ_b, simulate):
    result_a = simulate("Hotel A", occ_a.value / 100, adr_a.value)
    result_b = simulate("Hotel B", occ_b.value / 100, adr_b.value)
    return result_a, result_b


@app.cell(hide_code=True)
def _(euro, mo, result_a, result_b):
    def _fd(val):
        """Format difference with sign."""
        return f"+{euro(val)}" if val >= 0 else euro(val)

    mo.md(
        f"""
    | | Hotel A | Hotel B | Difference |
    |---|---:|---:|---:|
    | **Occupancy** | {result_a['Occupancy'] * 100:.0f}% | {result_b['Occupancy'] * 100:.0f}% | {(result_b['Occupancy'] - result_a['Occupancy']) * 100:+.0f} pp |
    | **ADR** | {euro(result_a['ADR'])} | {euro(result_b['ADR'])} | {_fd(result_b['ADR'] - result_a['ADR'])} |
    | **Rooms Sold** | {result_a['Rooms Sold']:,.0f} | {result_b['Rooms Sold']:,.0f} | {result_b['Rooms Sold'] - result_a['Rooms Sold']:+,.0f} |
    | **Revenue** | {euro(result_a['Revenue'])} | {euro(result_b['Revenue'])} | {_fd(result_b['Revenue'] - result_a['Revenue'])} |
    | **Variable Costs** | {euro(result_a['Variable Costs'])} | {euro(result_b['Variable Costs'])} | {_fd(result_b['Variable Costs'] - result_a['Variable Costs'])} |
    | **Channel Costs** | {euro(result_a['Channel Costs'])} | {euro(result_b['Channel Costs'])} | {_fd(result_b['Channel Costs'] - result_a['Channel Costs'])} |
    | **Net Profit** | **{euro(result_a['Net Profit'])}** | **{euro(result_b['Net Profit'])}** | **{_fd(result_b['Net Profit'] - result_a['Net Profit'])}** |
    | **Margin** | {result_a['Margin %']:.1f}% | {result_b['Margin %']:.1f}% | {result_b['Margin %'] - result_a['Margin %']:+.1f} pp |
    """
    )
    return


@app.cell(hide_code=True)
def _(euro, mpatches, mticker, np, plt, result_a, result_b):
    def _wf(row):
        _r, _v = row["Revenue"], row["Variable Costs"]
        _c, _f, _n = row["Channel Costs"], row["Fixed Costs"], row["Net Profit"]
        return [0, _r, _r - _v, _r - _v - _c, 0], [_r, -_v, -_c, -_f, _n]


    _labels = [
        "Revenue",
        "Variable\nCosts",
        "Channel\nCosts",
        "Fixed\nCosts",
        "Net\nProfit",
    ]
    _nn = len(_labels)
    _x = np.arange(_nn)
    _wb, _wc = 0.42, 0.34
    _xb, _xc = _x - 0.20, _x + 0.20

    _b_bot, _b_ht = _wf(result_a)
    _c_bot, _c_ht = _wf(result_b)

    _fig, _ax = plt.subplots(figsize=(14, 7.4))

    # Hotel A bars (gray, wider)
    for _i, (_xi, _bot, _h) in enumerate(zip(_xb, _b_bot, _b_ht)):
        _cost = _i in [1, 2, 3]
        _ax.bar(
            _xi,
            _h,
            bottom=_bot,
            width=_wb,
            color="#64748B",
            alpha=0.72,
            edgecolor="#DC2626" if _cost else "#334155",
            linewidth=2.0 if _cost else 1.2,
            zorder=2,
        )

    # Hotel B bars (blue, narrower)
    _cc = "#0EA5E9"
    for _i, (_xi, _bot, _h) in enumerate(zip(_xc, _c_bot, _c_ht)):
        _cost = _i in [1, 2, 3]
        _ax.bar(
            _xi,
            _h,
            bottom=_bot,
            width=_wc,
            color=_cc,
            alpha=0.88,
            edgecolor="#DC2626" if _cost else "#1F2937",
            linewidth=2.0 if _cost else 1.2,
            zorder=3,
        )

    # Connectors — Hotel B
    _cum_c = [
        result_b["Revenue"],
        result_b["Revenue"] - result_b["Variable Costs"],
        result_b["Revenue"]
        - result_b["Variable Costs"]
        - result_b["Channel Costs"],
        result_b["Revenue"]
        - result_b["Variable Costs"]
        - result_b["Channel Costs"]
        - result_b["Fixed Costs"],
    ]
    for _i in range(_nn - 1):
        _ax.plot(
            [_xc[_i] + _wc / 2, _xc[_i + 1] - _wc / 2],
            [_cum_c[_i], _cum_c[_i]],
            color="#334155",
            ls="--",
            lw=1.4,
            alpha=0.95,
            zorder=4,
        )

    # Connectors — Hotel A
    _cum_b = [
        result_a["Revenue"],
        result_a["Revenue"] - result_a["Variable Costs"],
        result_a["Revenue"]
        - result_a["Variable Costs"]
        - result_a["Channel Costs"],
        result_a["Revenue"]
        - result_a["Variable Costs"]
        - result_a["Channel Costs"]
        - result_a["Fixed Costs"],
    ]
    for _i in range(_nn - 1):
        _ax.plot(
            [_xb[_i] + _wb / 2, _xb[_i + 1] - _wb / 2],
            [_cum_b[_i], _cum_b[_i]],
            color="#475569",
            ls=":",
            lw=1.3,
            alpha=0.9,
            zorder=3,
        )

    # Value labels for both series
    for _xi, _bot, _h in zip(_xb, _b_bot, _b_ht):
        _ax.text(
            _xi,
            _bot + _h + (5000 if _h > 0 else -5000),
            euro(_h),
            ha="center",
            va="bottom" if _h > 0 else "top",
            fontsize=10,
            fontweight="bold",
            color="#111827",
            bbox=dict(
                facecolor="white",
                edgecolor="none",
                alpha=0.78,
                boxstyle="round,pad=0.18",
            ),
        )
    for _xi, _bot, _h in zip(_xc, _c_bot, _c_ht):
        _ax.text(
            _xi,
            _bot + _h + (5000 if _h > 0 else -5000),
            euro(_h),
            ha="center",
            va="bottom" if _h > 0 else "top",
            fontsize=10,
            fontweight="bold",
            color="#111827",
            bbox=dict(
                facecolor="white",
                edgecolor="none",
                alpha=0.78,
                boxstyle="round,pad=0.18",
            ),
        )

    # Profit difference annotation
    _diff = result_b["Net Profit"] - result_a["Net Profit"]
    _dc = "#166534" if _diff > 0 else "#991B1B"
    _dl = f"{'+' if _diff > 0 else ''}{euro(_diff)}"
    _top = max(result_b["Net Profit"], result_a["Net Profit"])
    _ax.annotate(
        f"Profit difference:\n{_dl}",
        xy=(4, _top),
        xytext=(4, _top + 34000),
        ha="center",
        color=_dc,
        fontweight="bold",
        fontsize=11,
        arrowprops=dict(arrowstyle="->", color=_dc, lw=1.5),
    )

    # Context box
    _ctx = (
        f"Hotel A: Occ {result_a['Occupancy'] * 100:.0f}% | ADR {euro(result_a['ADR'])}\n"
        f"Hotel B: Occ {result_b['Occupancy'] * 100:.0f}% | ADR {euro(result_b['ADR'])}"
    )
    _ax.text(
        -0.06,
        1.08,
        _ctx,
        transform=_ax.transAxes,
        va="bottom",
        ha="left",
        fontsize=16,
        fontweight="bold",
        color="#111827",
        bbox=dict(
            facecolor="white",
            edgecolor="#CBD5E1",
            boxstyle="round,pad=0.35",
            alpha=0.95,
        ),
    )

    _ax.set_xticks(_x)
    _ax.set_xticklabels(_labels)
    _ax.set_ylabel("EUR")
    _ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _p: f"{v / 1000:.0f}k")
    )
    _ax.set_title(
        "Revenue vs Profit: Two Strategies Compared",
        fontweight="bold",
        pad=40,
    )
    _ax.axhline(0, color="black", lw=1)

    _ax.legend(
        handles=[
            mpatches.Patch(
                facecolor="#64748B",
                edgecolor="#334155",
                alpha=0.72,
                label="Hotel A",
            ),
            mpatches.Patch(
                facecolor=_cc,
                edgecolor="#1F2937",
                alpha=0.88,
                label="Hotel B",
            ),
            mpatches.Patch(
                facecolor="white",
                edgecolor="#DC2626",
                linewidth=2,
                label="Cost bars (red outline)",
            ),
        ],
        loc="upper right",
        frameon=True,
    )

    for _spine in ["top", "right", "left"]:
        _ax.spines[_spine].set_visible(False)
    plt.tight_layout()
    plt.gca()
    return


@app.cell(hide_code=True)
def _(euro, mo, result_a, result_b):
    _pa = result_a["Net Profit"]
    _pb = result_b["Net Profit"]
    _diff = _pb - _pa

    if _diff > 1:
        _text = (
            f"**Hotel A** fills {result_a['Occupancy'] * 100:.0f}% of rooms at "
            f"{euro(result_a['ADR'])} per night \u2014 {result_a['Rooms Sold']:,.0f} rooms sold, "
            f"{euro(result_a['Revenue'])} revenue, **{euro(_pa)} profit** "
            f"({result_a['Margin %']:.0f}% margin).\n\n"
            f"**Hotel B** at {result_b['Occupancy'] * 100:.0f}% occupancy and "
            f"{euro(result_b['ADR'])} ADR \u2014 {result_b['Rooms Sold']:,.0f} rooms sold, "
            f"{euro(result_b['Revenue'])} revenue, **{euro(_pb)} profit** "
            f"({result_b['Margin %']:.0f}% margin).\n\n"
            f"**Hotel B makes {euro(_diff)} more profit.** "
            f"A {result_b['Margin %']:.0f}% margin vs {result_a['Margin %']:.0f}% \u2014 "
            f"that gap compounds every month."
        )
        _kind = "success"
    elif _diff < -1:
        _text = (
            f"In this configuration, **Hotel A** ({result_a['Occupancy'] * 100:.0f}% occ, "
            f"{euro(result_a['ADR'])} ADR) generates **{euro(abs(_diff))} more profit** "
            f"than Hotel B ({result_b['Occupancy'] * 100:.0f}% occ, "
            f"{euro(result_b['ADR'])} ADR).\n\n"
            f"Not every higher-rate strategy wins. The relationship between occupancy, rate, "
            f"and costs creates a sweet spot \u2014 try adjusting the sliders to find where "
            f"the crossover happens."
        )
        _kind = "warn"
    else:
        _text = (
            f"Both strategies produce effectively the same profit: **{euro(_pa)}**. "
            f"Hotel A achieves a {result_a['Margin %']:.0f}% margin while "
            f"Hotel B achieves {result_b['Margin %']:.0f}%. "
            f"Try adjusting the sliders to see how small changes tip the balance."
        )
        _kind = "info"

    mo.callout(mo.md(_text), kind=_kind)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    **Occupancy tells you how busy you are. It says nothing about how profitable you are.**

    Fewer rooms at a higher rate means lower variable costs, lower channel costs,
    and often a fatter bottom line. The math is surprisingly forgiving —
    you can afford to leave rooms empty when the rate is right.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Want to Stop Leaving Money on the Table?

    We help hotels move beyond vanity metrics and build pricing strategies that actually grow profit.

    **Two ways to get started:**

    **Visit our website** to explore how we work with hotels and hotel Revenue Management firms on revenue strategy:

    [revenuetales.com](https://revenuetales.com/)

    **Book a free call** to discuss your property's RMS and Cost Tracking with our team:

    [Schedule a conversation](https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ2syk0Pi9fSaSg7ee_0Ifha38X9eRwfVqVSn0vl8ojxuJKKgkxwmzF9agli7gHC1fvfiFTGTmxu)
    """)
    return


@app.cell(hide_code=True)
def _(
    DAYS,
    TOTAL_ROOMS,
    base_cpor,
    channel_rate,
    fixed_daily,
    mo,
    surge_rate,
    surge_threshold,
):
    mo.accordion({
        "Methodology & Assumptions": mo.md(
            f"""
    This simulation models a **{TOTAL_ROOMS}-room hotel** over **{DAYS} days**.

    **Cost model:**
    - Fixed daily overhead: EUR {fixed_daily.value:,.0f} (staff, mortgage, utilities)
    - Variable cost per occupied room: EUR {base_cpor.value:,.0f} (housekeeping, laundry, amenities)
    - Variable cost surge: +{surge_rate.value * 100:.0f}% above {surge_threshold.value * 100:.0f}% occupancy
    - Channel costs: {channel_rate.value * 100:.0f}% of revenue (blended OTA + direct)

    **Simplifications:**
    - No seasonality or day-of-week variation
    - No price elasticity of demand (occupancy and ADR are independent inputs)
    - Channel cost is a flat percentage (no OTA vs. direct split)
    - No ancillary revenue (F&B, spa, parking)

    This is a scenario-based simulation under stated assumptions, not a forecast.
    """
        ),
    })
    return


if __name__ == "__main__":
    app.run()
