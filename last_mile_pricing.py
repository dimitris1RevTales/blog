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
    # The Cost of Waiting Too Long

    Every unsold room disappears at midnight. The question is not *whether* to drop
    the rate in the final hours — it's **how fast**.

    This interactive simulation compares three last-mile pricing strategies:
    **hold** (keep the rate), **stepped discount** (drop every hour until inventory
    moves), and **crash** (go to the floor immediately). Adjust the sliders to see
    when patience pays, and when it just leaves rooms empty.
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
        "hold": "#94A3B8",
        "stepped": "#2A9D8F",
        "crash": "#E76F51",
        "floor": "#CBD5E1",
        "booked": "#264653",
    }
    return PAL, mticker, np, plt


@app.cell
def _():
    HOURS = 12
    return (HOURS,)


@app.cell(hide_code=True)
def _(mo):
    preset = mo.ui.radio(
        options=[
            "Balanced (-10% / hour)",
            "Aggressive (-15% / hour)",
            "Conservative (-5% / hour)",
            "Custom",
        ],
        value="Balanced (-10% / hour)",
        label="Strategy preset",
    )
    mo.vstack(
        [
            mo.md(r"""
            ---

            ## Pick a Last-Mile Strategy

            Your hotel has unsold rooms and a finite window. Choose a preset or
            go **Custom** to dial in your own discount curve.
            """),
            preset,
        ]
    )
    return (preset,)


@app.cell(hide_code=True)
def _(mo, preset):
    # (start_price, floor_price, step_pct, interval, rooms_left)
    _presets = {
        "Balanced (-10% / hour)": (150, 80, 10, 1, 8),
        "Aggressive (-15% / hour)": (150, 80, 15, 1, 8),
        "Conservative (-5% / hour)": (150, 80, 5, 1, 8),
        "Custom": (150, 80, 10, 1, 8),
    }
    _cfg = _presets[preset.value]

    start_price = mo.ui.number(
        start=50, stop=500, step=5, value=_cfg[0], label="Starting price (EUR)"
    )
    floor_price = mo.ui.number(
        start=30, stop=400, step=5, value=_cfg[1], label="Floor price (EUR)"
    )
    step_pct = mo.ui.number(
        start=1, stop=30, step=1, value=_cfg[2], label="Price drop per step (%)"
    )
    interval_hours = mo.ui.number(
        start=1, stop=6, step=1, value=_cfg[3], label="Hours between drops"
    )
    rooms_left = mo.ui.number(
        start=1, stop=20, step=1, value=_cfg[4], label="Unsold rooms"
    )

    mo.hstack(
        [
            mo.vstack(
                [
                    mo.md("### Pricing strategy"),
                    start_price,
                    floor_price,
                    step_pct,
                    interval_hours,
                ]
            ),
            mo.vstack([mo.md("### Inventory"), rooms_left]),
        ],
        widths=[1, 1],
    )
    return floor_price, interval_hours, rooms_left, start_price, step_pct


@app.cell(hide_code=True)
def _(mo):
    hold_prob = mo.ui.slider(
        0.01,
        1.0,
        step=0.01,
        value=0.25,
        full_width=True,
        label="Probability to sell per hour at the HOLD price (start price)",
    )
    elasticity = mo.ui.slider(
        0.5,
        5.0,
        step=0.1,
        value=2.0,
        full_width=True,
        label="Price elasticity (how much demand rises when you drop price)",
    )

    mo.vstack(
        [
            mo.md(
                r"""
            ---

            ## How Much Demand Is Out There?

            One number anchors the model: the per-hour chance of selling a room at
            your **hold** price. The elasticity slider controls how much that chance
            grows when you drop the price.
            """
            ),
            hold_prob,
            elasticity,
            mo.md(
                r"_At any price `p`, per-hour sell probability is "
                r"`min(1, hold_prob × (start / p)^elasticity)`. "
                r"**Hold** stays at `hold_prob` every hour. **Crash** uses the "
                r"probability implied at the floor. **Stepped** walks the curve._"
            ),
        ]
    )
    return elasticity, hold_prob


@app.cell
def _(HOURS, np):
    def p_sell(price, start_price, hold_prob, elasticity):
        """Per-hour sell probability using a price-elasticity curve.

        p(price) = min(1, hold_prob × (start_price / price)^elasticity).
        At price = start_price, probability = hold_prob.
        At any lower price, probability rises per the elasticity exponent,
        capped at 1.0.
        """
        if price <= 0:
            return 0.0
        ratio = start_price / price
        return min(1.0, hold_prob * (ratio ** elasticity))

    def simulate(price_fn, rooms_left, start_price, hold_prob, elasticity):
        """Simulate bookings hour-by-hour under a given price strategy."""
        hours = np.arange(HOURS)
        prices = np.array([price_fn(h) for h in hours], dtype=float)
        probs = np.array(
            [p_sell(p, start_price, hold_prob, elasticity) for p in prices]
        )

        bookings = np.zeros(HOURS)
        revenue = np.zeros(HOURS)
        rooms = float(rooms_left)

        for h in range(HOURS):
            if rooms <= 0 or prices[h] <= 0:
                continue
            sold = min(rooms, probs[h])
            bookings[h] = sold
            revenue[h] = sold * prices[h]
            rooms -= sold

        return {
            "prices": prices,
            "probs": probs,
            "bookings": bookings,
            "revenue": revenue,
            "cum_bookings": np.cumsum(bookings),
            "cum_revenue": np.cumsum(revenue),
            "total_bookings": float(bookings.sum()),
            "total_revenue": float(revenue.sum()),
            "rooms_unsold": float(rooms),
            "avg_adr": float(revenue.sum() / bookings.sum()) if bookings.sum() > 0 else 0.0,
        }

    def hold_fn(start_price):
        return lambda h: start_price

    def stepped_fn(start_price, floor_price, step_pct, interval_hours):
        step = step_pct / 100
        iv = max(int(interval_hours), 1)

        def _fn(h):
            steps = h // iv
            price = start_price * ((1 - step) ** steps)
            return max(price, floor_price)

        return _fn

    def crash_fn(floor_price):
        return lambda h: floor_price

    def euro(x):
        return f"EUR {x:,.0f}"

    return crash_fn, euro, hold_fn, simulate, stepped_fn


@app.cell
def _(
    crash_fn,
    elasticity,
    floor_price,
    hold_fn,
    hold_prob,
    interval_hours,
    rooms_left,
    simulate,
    start_price,
    step_pct,
    stepped_fn,
):
    _common = dict(
        rooms_left=rooms_left.value,
        start_price=start_price.value,
        hold_prob=hold_prob.value,
        elasticity=elasticity.value,
    )
    result_hold = simulate(hold_fn(start_price.value), **_common)
    result_stepped = simulate(
        stepped_fn(
            start_price.value,
            floor_price.value,
            step_pct.value,
            interval_hours.value,
        ),
        **_common,
    )
    result_crash = simulate(crash_fn(floor_price.value), **_common)
    return result_crash, result_hold, result_stepped


@app.cell(hide_code=True)
def _(euro, mo, result_crash, result_hold, result_stepped):
    def _row(label, r):
        return (
            f"| **{label}** | "
            f"{r['total_bookings']:.1f} | "
            f"{euro(r['avg_adr']) if r['total_bookings'] > 0 else '—'} | "
            f"**{euro(r['total_revenue'])}** |"
        )

    mo.md(
        f"""
    | Strategy | Rooms sold | Avg ADR | Total revenue |
    |---|---:|---:|---:|
    {_row("Hold at start price", result_hold)}
    {_row("Stepped discount", result_stepped)}
    {_row("Crash to floor", result_crash)}
    """
    )
    return


@app.cell(hide_code=True)
def _(HOURS, PAL, mticker, np, plt, result_crash, result_hold, result_stepped):
    _fig, (_axp, _axr) = plt.subplots(1, 2, figsize=(15, 6.5))

    _hours = np.arange(HOURS)
    _series = [
        ("Hold", result_hold, PAL["hold"], "-"),
        ("Stepped", result_stepped, PAL["stepped"], "-"),
        ("Crash", result_crash, PAL["crash"], "-"),
    ]

    for _name, _r, _c, _ls in _series:
        _axp.plot(
            _hours,
            _r["prices"],
            drawstyle="steps-post",
            color=_c,
            lw=3,
            label=_name,
        )

    _axp.set_title("Price trajectory (by hour)", fontweight="bold", pad=14)
    _axp.set_xlabel("Hours elapsed")
    _axp.set_ylabel("Price (EUR)")
    _axp.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _p: f"{v:.0f}")
    )
    _axp.legend(loc="upper right", frameon=True)
    for _spine in ["top", "right"]:
        _axp.spines[_spine].set_visible(False)

    _labels_r = ["Hold", "Stepped", "Crash"]
    _revs = [
        result_hold["total_revenue"],
        result_stepped["total_revenue"],
        result_crash["total_revenue"],
    ]
    _colors_r = [PAL["hold"], PAL["stepped"], PAL["crash"]]
    _bars = _axr.bar(_labels_r, _revs, color=_colors_r, edgecolor="white", linewidth=2)

    _max_r = max(_revs) if max(_revs) > 0 else 1
    for _b, _v, _r in zip(_bars, _revs, [result_hold, result_stepped, result_crash]):
        _axr.text(
            _b.get_x() + _b.get_width() / 2,
            _v + _max_r * 0.03,
            f"EUR {_v:,.0f}\n{_r['total_bookings']:.1f} rooms",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
            color="#111827",
        )

    _axr.set_title("Total revenue by strategy", fontweight="bold", pad=14)
    _axr.set_ylabel("EUR")
    _axr.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _p: f"{v / 1000:.1f}k")
    )
    _axr.set_ylim(0, _max_r * 1.25)
    for _spine in ["top", "right"]:
        _axr.spines[_spine].set_visible(False)

    plt.tight_layout()
    plt.gca()
    return


@app.cell(hide_code=True)
def _(euro, mo, result_crash, result_hold, result_stepped):
    _r = [
        ("Hold", result_hold),
        ("Stepped", result_stepped),
        ("Crash", result_crash),
    ]
    _winner = max(_r, key=lambda x: x[1]["total_revenue"])
    _loser = min(_r, key=lambda x: x[1]["total_revenue"])
    _gap = _winner[1]["total_revenue"] - _loser[1]["total_revenue"]

    if _winner[0] == "Stepped":
        _msg = (
            f"**Stepped discount wins this round** at {euro(_winner[1]['total_revenue'])}, "
            f"vs {euro(_loser[1]['total_revenue'])} for **{_loser[0]}**. "
            f"That's **{euro(_gap)}** more revenue for the same inventory, same window. "
            f"Stepped sold {_winner[1]['total_bookings']:.1f} rooms at an average of "
            f"{euro(_winner[1]['avg_adr'])} — the gradual drop captures high-WTP "
            f"bookers early and price-sensitive ones later."
        )
        _kind = "success"
    elif _winner[0] == "Hold":
        _msg = (
            f"With this demand profile, **holding at the start price** is the winner — "
            f"{euro(_winner[1]['total_revenue'])} vs {euro(_loser[1]['total_revenue'])} "
            f"for {_loser[0]}. Demand is strong enough that you don't need to discount. "
            f"Try lowering the hold-prob slider to see when patience stops paying."
        )
        _kind = "info"
    else:
        _msg = (
            f"**Crashing to the floor early** wins here — {euro(_winner[1]['total_revenue'])}. "
            f"At this hold probability, demand is thin enough that full-price sales never "
            f"materialise — and holding out just means empty rooms. But watch: you sold "
            f"{_winner[1]['total_bookings']:.1f} rooms at only "
            f"{euro(_winner[1]['avg_adr'])} — if demand picks up tomorrow, the floor was too low."
        )
        _kind = "warn"

    mo.callout(mo.md(_msg), kind=_kind)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    **The last-mile question isn't "should I discount?" — it's "how fast?"**

    Hold too long and rooms expire empty. Crash too early and you give away
    margin you could have kept. A stepped discount splits the difference: you
    capture the guests who will pay more, and still catch the bargain-hunters
    before midnight.

    The right step size depends on how price-sensitive your remaining demand is.
    That's knowable — from your own booking data.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Reading the Sliders

    **As you raise elasticity, stepped revenue climbs — usually the fastest of the three.**

    Elasticity is how strongly guests respond to price. An elasticity of **1** is mild: halving the price doubles demand. An elasticity of **3** is sharp: halving the price multiplies demand eightfold. Leisure and OTA traffic tends toward higher elasticity; business, event-driven, and last-minute walk-ups toward lower.

    Stepped benefits most from higher elasticity because it is the only strategy that *samples intermediate prices*. **Hold** never leaves the start price — no price response, no extra demand. **Crash** is already at the floor, so extra elasticity just pushes its probability toward 1 (capped). But **stepped** walks through a gradient of prices, and as elasticity rises the *middle* of that gradient becomes a premium zone: near-certain sales at a rate well above the floor.

    **What the hold-probability slider tells you:**

    - **High hold_prob (0.5 – 1.0):** the headline rate is already clearing inventory. Every discount is pure margin loss. **Hold wins.**
    - **Medium hold_prob (0.25 – 0.40):** hold leaves rooms empty; crash becomes inventory-constrained at the floor (some hours wasted). Stepped distributes inventory across a gradient of prices — high rate early, floor late. **Stepped wins.**
    - **Low hold_prob (< 0.2):** demand is so thin that full-price hours contribute almost nothing. Crash captures the most nights at the floor. **Crash wins — but narrowly.** Stepped converges toward crash as step % grows, because a faster drop means more hours spent at the floor.

    **The practical takeaway:** stepped is almost never the worst option. In real operations — where you do not know tomorrow's demand — that *second-place-at-worst* profile is what makes stepped a robust default, not a perfect forecast.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Want Last-Mile Pricing That Runs Itself?

    **[LastMile Optimizer](https://revenuetales.com/last-mile-optimizer/)** automates stepped price reductions based on your inventory and
    demand signal — so you're not manually adjusting rates at 8pm the night before arrival.

    **Two ways to get started:**

    **Visit our website** to explore how our application suite helps hotels and
    hotel Revenue Management firms build better revenue strategy:

    [revenuetales.com](https://revenuetales.com/)

    **Book a free call** to discuss your property's last-mile strategy:

    [Schedule a conversation](https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ2syk0Pi9fSaSg7ee_0Ifha38X9eRwfVqVSn0vl8ojxuJKKgkxwmzF9agli7gHC1fvfiFTGTmxu)
    """)
    return


@app.cell(hide_code=True)
def _(HOURS, elasticity, floor_price, hold_prob, mo, start_price):
    _implied_crash = min(
        1.0,
        hold_prob.value * (start_price.value / max(floor_price.value, 1)) ** elasticity.value,
    )
    mo.accordion(
        {
            "Methodology & Assumptions": mo.md(
                f"""
    This simulation models the final **{HOURS} hours** before arrival for a block of unsold rooms.

    **Demand model (price-elasticity curve):**
    - Per-hour probability of selling at the **hold price** (start price): **{hold_prob.value * 100:.0f}%**.
    - Price elasticity of demand: **{elasticity.value:.1f}**.
    - For any price `p`: `p_sell(p) = min(1, hold_prob × (start_price / p) ^ elasticity)`.
    - Implied per-hour probability at the floor (**crash price**): **{_implied_crash * 100:.1f}%**.

    **Strategies:**
    - **Hold**: price held at the starting value for the full window → every hour uses `hold_prob`.
    - **Stepped**: price drops by the chosen step % every interval, floored at the minimum price → the curve walks from `hold_prob` toward the implied crash probability as the price falls.
    - **Crash**: price set to the floor immediately → every hour uses the implied crash probability.

    **Behaviour across the hold-probability sweep (with defaults otherwise):**
    - **Very high hold_prob** (you sell at headline rate almost every hour): **hold wins** — every discount is margin lost on inventory you'd have sold anyway.
    - **Medium hold_prob**: **stepped wins** — it captures the few high-rate bookers early and still clears the rest at the floor.
    - **Very low hold_prob**: **crash wins** — demand is so thin that only the floor moves rooms. The faster stepped reaches the floor (higher step %), the closer it gets to crash.

    **Simplifications:**
    - Deterministic demand (expected bookings = sell probability per hour — no Monte Carlo).
    - At most one room sold per hour; probability is capped at 1.0.
    - No competitor response or rate-parity constraints.
    - A booking is one room-night (no length-of-stay effects).
    - Channel and variable costs ignored — this is a top-line revenue view.

    This is a scenario-based simulation under stated assumptions, not a forecast.
    """
            ),
        }
    )
    return


if __name__ == "__main__":
    app.run()
