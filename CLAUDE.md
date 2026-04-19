# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A hotel revenue management simulation proving that "Occupancy is a vanity metric." The project compares pricing strategies for a 100-room hotel over 30 days, demonstrating that lower occupancy with higher ADR yields more net operating profit than high-occupancy discount strategies.

## Repository Structure

- `occupancy_vanity_metric_simulation.py` — **Primary artifact.** A marimo notebook (Python file with `@app.cell` decorators) containing the simulation engine, comparison table, and all visualizations.
- `interactive_simulation.py` — **Interactive version.** A marimo notebook with `mo.ui` sliders, preset scenarios, and dynamic narrative. Designed for WASM export and LinkedIn sharing. No `plt.savefig()` calls (WASM-compatible).
- `notebooks/occupancy_vanity_metric_simulation.ipynb` — Legacy Jupyter notebook version. May lag behind the marimo version.
- `outputs/` — Exported PNG charts from the marimo notebook at 300 DPI.
- `notebooks/outputs/` — Exported PNG charts from the Jupyter notebook at 300 DPI.
- `docs/plans/` — Design documents capturing the financial model and visualization specifications.
- `docs/linkedin-posts/` — Drafted LinkedIn post content derived from simulation insights.
- `.agents/skills/` — Skill definitions (writing-linkedin-posts, linkedin-post-maker, marimo-pair, brainstorming).

## Running the Notebook

Dependencies: `numpy`, `pandas`, `matplotlib`, `seaborn`, `marimo`. No requirements.txt or pyproject.toml exists — install manually.

```bash
pip install numpy pandas matplotlib seaborn marimo
```

Marimo (primary — static chart generation):
```bash
marimo edit occupancy_vanity_metric_simulation.py
```

Marimo (interactive — for LinkedIn/WASM):
```bash
marimo edit interactive_simulation.py
```

WASM export (standalone HTML for hosting):
```bash
marimo export html-wasm interactive_simulation.py -o docs/wasm-app --mode run
```

Jupyter (legacy):
```bash
jupyter notebook notebooks/occupancy_vanity_metric_simulation.ipynb
```

## Linting

Ruff is configured (`.ruff_cache/` exists). Run with:

```bash
ruff check notebooks/
ruff check occupancy_vanity_metric_simulation.py
ruff check interactive_simulation.py
```

## Simulation Parameters

All inputs are editable constants defined in the notebook's "Simulation Parameters" cell.

### Hotel

| Parameter | Default | Meaning |
|---|---|---|
| `TOTAL_ROOMS` | 100 | Number of rooms in the hotel's inventory. All revenue and cost calculations scale from this. |
| `DAYS` | 30 | Length of the simulated period in days. Monthly totals are daily values × this number. |

### Cost Structure

| Parameter | Default | Meaning |
|---|---|---|
| `FIXED_DAILY_COST` | 2,000 EUR | Overhead the hotel pays every day regardless of how many rooms are sold (staff, mortgage, utilities, etc.). |
| `BASE_CPOR` | 35 EUR | Base variable cost per occupied room per night (housekeeping, laundry, amenities, breakfast). |
| `CPOR_SURGE_THRESHOLD` | 0.90 | Occupancy rate above which variable costs increase. Running near-full capacity strains operations. |
| `CPOR_SURGE_RATE` | 0.10 | How much variable costs increase above the surge threshold. At default, CPOR rises 10% (from 35 to 38.50 EUR). |
| `CHANNEL_COST_RATE` | 0.10 | Distribution cost as a flat percentage of revenue. Covers OTA commissions and direct booking costs blended together. |

### Scenarios

Each scenario represents a different pricing strategy defined by two inputs: occupancy rate and Average Daily Rate (ADR). The simulation compares them all against the baseline.

| Scenario | Occupancy | ADR | Role |
|---|---|---|---|
| Busy Fool (Baseline) | 98% | 100 EUR | The high-volume, low-price trap. Maximises occupancy but discounts heavily and relies on OTAs. |
| Higher Revenue | 85% | 130 EUR | Sells fewer rooms at a premium. Total revenue is actually higher than baseline, and profit is much higher. |
| Same Revenue | 80% | 122.50 EUR (Jupyter) / 130 EUR (marimo) | Prices near baseline revenue, proving that even at equal top-line, lower occupancy is more profitable. |
| Lower Revenue | 70% | 130 EUR | Accepts less revenue than baseline but still generates more profit, the strongest form of the argument. |

## Financial Model

Key functions:
- `cpor(occupancy)` — Returns variable cost per room with surge pricing above 90% occupancy.
- `simulate(name, occupancy, adr)` — Runs one monthly simulation, returns dict with all financial line items.
- `euro(x)` — Formats numbers as `EUR X,XXX`.

Cost flow: Revenue → minus Variable Costs (CPOR × rooms, with surge) → minus Channel Costs (flat % of revenue) → minus Fixed Costs → Net Profit.

## Visualization Conventions

- All charts use Seaborn `whitegrid` theme with `talk` context.
- Waterfall charts are manually constructed (no waterfall library) using `matplotlib.bar` with computed bottoms/heights.
- The `PAL` and `SCENARIO_COLORS` dicts define the project color palette.
- Charts are saved at `dpi=300` — to `outputs/` (marimo) or `notebooks/outputs/` (Jupyter).
- Styling targets LinkedIn readability: large fonts, high contrast, professional appearance.

## Design Process

New features or changes should follow the brainstorming skill workflow: explore context, ask clarifying questions, propose approaches, validate design, then write a design doc to `docs/plans/YYYY-MM-DD-<topic>-design.md` before implementing.

## LinkedIn Post Writing

The `writing-linkedin-posts` skill (`.agents/skills/writing-linkedin-posts/SKILL.md`) guides content creation from the simulation's insights. Key rules:

- **One idea per post**, 150-300 words, 3,000 chars max.
- **Hook** (lines 1-2): Honest admissions, specific observations, or direct challenges. No "I'm excited to announce..." or engagement bait.
- **Body**: Short paragraphs (1-3 sentences), generous whitespace, scannable. Storytelling follows: scene → tension → turning point → insight → reader application.
- **Close**: Genuine question or reflection. Never "Agree?" or "Follow me for more."
- **Formatting**: No inline hashtags (3-5 at the end after a line break). One emoji max. Use "I" not "we."
- **Tone**: Authentic, slightly casual, conversational — not corporate. Avoid humblebrags, performed vulnerability, and recycled viral formats.
- **Post formats**: Story, List, Contrarian, Observation — each has a template in the skill file.
- **Vulnerability test**: Share to help others, not to process feelings. Protect others involved. Only share with hindsight.
