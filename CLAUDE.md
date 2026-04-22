# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A small publishing platform for **interactive marimo notebooks accompanying LinkedIn posts**. Each notebook lives at the repo root, gets exported to WASM, and is served as a static site under `blog.revenuetales.com`. The first/canonical example is `interactive_simulation.py` — a hotel revenue simulation showing that lower occupancy with higher ADR can outperform high-occupancy discounting. New notebooks should follow the same shape: edit a `.py` marimo notebook locally, export to `docs/<slug>/`, push to `main`, and GitHub Pages publishes.

## Repository Structure

- `interactive_simulation.py` — **Example notebook.** Reactive marimo notebook with `mo.ui` controls, preset scenarios, and matplotlib charts. No `plt.savefig()` calls (WASM-compatible). Copy its structure when adding new notebooks.
- `docs/<slug>/` — One folder per published notebook, holding the marimo-WASM-exported static site (treat as a build artifact: `index.html` + bundled `assets/` + favicons/manifest). Current slugs: `docs/occupancy-vanity-metric/`, `docs/last-mile-pricing/`, `docs/smart-allocator/`.
- `docs/index.html` — Hand-maintained blog home page (cards link to each published slug). Update when publishing a new notebook.
- `docs/CNAME` — Custom-domain config for GitHub Pages (`blog.revenuetales.com`).
- `scripts/inject_ga.py` — Idempotent injector that stamps the GA4 tag (`G-P32PX685T9`) into a given `index.html` before `</head>`. Must be re-run after every `marimo export html-wasm` (marimo overwrites `index.html` and strips the tag). See "Google Analytics (GA4)" below.
- `scripts/hide_marimo_badge.py` — Idempotent injector that stamps a CSS + MutationObserver block before `</body>` to suppress the "Made with Marimo" badge marimo renders in the bottom-right corner. Must be re-run after every `marimo export html-wasm` (marimo overwrites `index.html` and the badge returns). See "Post-export checklist" below.
- `scripts/update_favicon.py` — Idempotent injector that rewrites the three default marimo favicon `<link>` tags in `index.html` to point at the `revenuetales.com`-hosted 32x32 / 192x192 / 270x270 PNGs, so browser tabs on `blog.revenuetales.com` match the main site's branding. Must be re-run after every `marimo export html-wasm`. See "Post-export checklist" below.
- `.agents/skills/` and `.claude/skills/` — Skill definitions (`brainstorming`, `linkedin-post-maker`, `marimo-pair`, `writing-linkedin-posts`). Pinned via `skills-lock.json`.
- `README.md` — Short command cheat sheet for the export-and-deploy loop.

## Build, Run, Deploy

Dependencies: `numpy`, `matplotlib`, `marimo`. No `requirements.txt` / `pyproject.toml` — install manually:

```bash
pip install numpy matplotlib marimo
```

Edit the notebook:
```bash
marimo edit interactive_simulation.py
```

Rebuild the WASM site (replace `<notebook>.py` and `<slug>` when publishing a new notebook):
```bash
marimo export html-wasm <notebook>.py -o docs/<slug> --mode run -f
python scripts/inject_ga.py docs/<slug>/index.html
python scripts/hide_marimo_badge.py docs/<slug>/index.html
python scripts/update_favicon.py docs/<slug>/index.html
```
`--mode run` hides the code and shows only outputs/UI (the LinkedIn-reader view). Use `--mode edit` if you want the reader to see and tweak code in the browser. The three post-export scripts each mutate `index.html` and are all **required after every re-export**, because marimo overwrites `index.html` and strips their changes:
- `inject_ga.py` adds the GA4 tag (`G-P32PX685T9`, shared with `revenuetales.com`).
- `hide_marimo_badge.py` injects CSS + a MutationObserver that suppresses the "Made with Marimo" badge marimo renders at runtime.
- `update_favicon.py` swaps the default marimo favicon `<link>` tags for the `revenuetales.com`-hosted branded PNGs, so tabs on `blog.revenuetales.com` match the main site.

All three scripts are idempotent (marker-guarded); safe to re-run.

Test the exported site locally:
```bash
python -m http.server --directory docs/occupancy-vanity-metric 8080
# open http://localhost:8080/
```

If Jekyll swallows a file after push, `touch docs/.nojekyll` and recommit.

### Google Analytics (GA4)

**Every page under `blog.revenuetales.com` MUST carry the GA4 tag `G-P32PX685T9`** (same property as the main site, so GA sees one user journey across `revenuetales.com` ↔ `blog.revenuetales.com`). The Measurement ID is hardcoded inside `scripts/inject_ga.py` — do not change it without confirming with the user.

Currently tagged:

- `docs/index.html` — blog home (hand-maintained; the injected `<!-- GA4 (gtag.js) -->` block persists across edits).
- `docs/occupancy-vanity-metric/index.html` — marimo export; tag is **stripped on every re-export**.
- `docs/last-mile-pricing/index.html` — marimo export; tag is **stripped on every re-export**.
- `docs/smart-allocator/index.html` — marimo export; tag is **stripped on every re-export**.

#### Publishing a new marimo notebook — post-export checklist

Any new post `docs/<slug>/index.html` is also a marimo export and will ship untagged (no GA, with the Marimo badge, with default marimo favicons) unless you explicitly inject. So when adding a new post:

1. Export the notebook: `marimo export html-wasm <notebook>.py -o docs/<slug> --mode run -f`.
2. **Inject GA**: `python scripts/inject_ga.py docs/<slug>/index.html`.
3. **Hide the Marimo badge**: `python scripts/hide_marimo_badge.py docs/<slug>/index.html`.
4. **Swap in the branded favicon**: `python scripts/update_favicon.py docs/<slug>/index.html`.
5. Verify GA: `grep -c "G-P32PX685T9" docs/<slug>/index.html` should print `2` (once in the script `src`, once in the `gtag('config', ...)` call).
6. Verify badge-hide: `grep -c "hide marimo badge" docs/<slug>/index.html` should print `1`.
7. Verify favicon: `grep -c "favicon: revenuetales" docs/<slug>/index.html` should print `1`.
8. **Update CLAUDE.md's "Currently tagged" list above** to include the new path, so future LLMs see the full set.
9. **Update the bulk re-inject command below** to include the new path.

#### Re-inject after any marimo re-export

Single file (most common after editing one notebook):
```bash
python scripts/inject_ga.py docs/<slug>/index.html
python scripts/hide_marimo_badge.py docs/<slug>/index.html
python scripts/update_favicon.py docs/<slug>/index.html
```

Reapply to all tagged pages (use after any batch re-export; update this list when you publish a new slug):
```bash
python scripts/inject_ga.py \
  docs/index.html \
  docs/occupancy-vanity-metric/index.html \
  docs/last-mile-pricing/index.html \
  docs/smart-allocator/index.html

python scripts/hide_marimo_badge.py \
  docs/occupancy-vanity-metric/index.html \
  docs/last-mile-pricing/index.html \
  docs/smart-allocator/index.html

python scripts/update_favicon.py \
  docs/occupancy-vanity-metric/index.html \
  docs/last-mile-pricing/index.html \
  docs/smart-allocator/index.html
```

(`hide_marimo_badge.py` and `update_favicon.py` are not run against `docs/index.html` — the hand-maintained blog home has no Marimo badge and already uses its own favicon markup.)

All three scripts are idempotent — rerunning on an already-processed file prints `skip (already injected)` and is a no-op. They match on `<!-- GA4 (gtag.js) -->`, `<!-- hide marimo badge -->`, and `<!-- favicon: revenuetales -->` markers respectively, so never hand-edit those comments away.

#### Verification

- Devtools → Network tab on the deployed page: you should see a request to `googletagmanager.com/gtag/js?id=G-P32PX685T9` and one to `google-analytics.com/g/collect…`.
- `analytics.google.com` → property "Revenue Tales" → Reports → **Realtime** should show your session within ~30s of a visit.

#### Consent banner

None installed — analytics fires unconditionally. If an EU-compliance need arises, wire a banner that blocks `gtag('config', ...)` until the user accepts. Do not add a banner pre-emptively without the user asking; it degrades UX for the current (mostly LinkedIn-referred) audience.

Deployment is GitHub Pages off `main`: `git push origin main` publishes. URLs:
- `https://dimitris1revtales.github.io/blog/occupancy-vanity-metric/`
- Official: `https://blog.revenuetales.com/occupancy-vanity-metric/`

Lint (if ruff is installed):
```bash
ruff check interactive_simulation.py
```

## Authoring Marimo Notebooks

### Cell mechanics

Only edit code **inside** `@app.cell` decorators. Marimo auto-generates the function parameters and `return` statement — don't hand-edit them; they are overwritten on save.

- Variables cannot be redeclared across cells. Names prefixed with `_` are cell-local (used heavily in chart cells to avoid global pollution).
- Cells form a DAG; reactivity re-runs downstream cells when upstream values change.
- A UI element's `.value` cannot be read in the same cell where it's defined.
- Final expression of a cell is auto-displayed; use `plt.gca()` (not `plt.show()`) for matplotlib.
- `hide_code=True` on the `@app.cell` decorator hides the source on the published page — use it for prose, charts, and CTA cells; leave it off for cells whose code is the point.

### WASM constraints (every notebook here is exported to WASM)

Notebooks run client-side in Pyodide, not on a server. That changes what you can use:

- **Allowed**: `numpy`, `pandas`, `matplotlib`, `polars`, `altair`, `plotly`, `scipy`, `scikit-learn`, `duckdb`, standard library. These have Pyodide wheels and load cleanly.
- **Avoid**: `seaborn` (history of bundling/font issues in WASM — use matplotlib directly with custom `rcParams` for the same look), `tensorflow`, `pytorch`, `selenium`, anything needing a system compiler or native binary at runtime, anything with C extensions not built for `emscripten`.
- **Network**: `requests` doesn't work natively in Pyodide. Use `urllib`, `pyodide.http`, or `micropip` install + `httpx`/`aiohttp` async patterns. Prefer pre-loading data into the notebook over runtime fetches.
- **No filesystem writes** the user can keep: no `plt.savefig(...)`, no `pd.to_csv("file.csv")`, no `open("x", "w")`. The Pyodide FS is in-browser only and resets on reload.
- **No subprocess / no `os.system`** — Pyodide has no shell.
- **Fonts**: only the fonts marimo bundles are guaranteed. Don't reference system-only typefaces.
- **Bundle size matters**: every dependency adds to the user's first-load time. Keep the imports cell minimal.

### Recommended notebook shape (mirror `interactive_simulation.py`)

1. `import marimo as mo` (its own cell, by convention).
2. Title + intro markdown cell (`hide_code=True`).
3. Imports + global styling (`plt.rcParams`, palette dict).
4. Constants cell (e.g. `TOTAL_ROOMS`, `DAYS`).
5. `mo.ui` controls — sliders, numbers, radios, presets.
6. Pure-function logic cell (the simulation/calculation).
7. Reactive results cell that calls the logic with `.value` from the UI.
8. Visualization cells (`hide_code=True`, last expression `plt.gca()`).
9. Insight/callout cell that narrates the current result (`mo.callout`).
10. Closing markdown with CTA / external links.
11. Optional `mo.accordion` with methodology and assumptions.

### Quality checks before exporting

- Run `marimo check --fix <notebook>.py` to catch formatting and DAG issues.
- Click through every preset and exercise sliders at extremes — WASM will surface any divide-by-zero or unhandled edge case as an in-page traceback.
- Open the exported `docs/<slug>/index.html` via the local `http.server` command above and load it in a clean browser tab; first-time WASM bootstrap is what real readers will see.
- **Run `python scripts/inject_ga.py docs/<slug>/index.html`** after the export (marimo overwrites `index.html` and strips the GA tag). Then `grep -c "G-P32PX685T9" docs/<slug>/index.html` must return `2`. See "Google Analytics (GA4)" above.
- **Run `python scripts/hide_marimo_badge.py docs/<slug>/index.html`** after the export to suppress the "Made with Marimo" badge (marimo re-adds it on every re-export). Then `grep -c "hide marimo badge" docs/<slug>/index.html` must return `1`.
- **Run `python scripts/update_favicon.py docs/<slug>/index.html`** after the export to swap the default marimo favicons for the `revenuetales.com`-hosted branded PNGs (marimo re-emits its defaults on every re-export). Then `grep -c "favicon: revenuetales" docs/<slug>/index.html` must return `1`.

## Simulation Parameters

All tunables are defined in cells near the top of `interactive_simulation.py`. Hotel constants (`TOTAL_ROOMS=100`, `DAYS=30`) live in their own cell; cost structure is exposed through `mo.ui` controls (defaults in parentheses).

| Parameter | Default | Meaning |
|---|---|---|
| `TOTAL_ROOMS` | 100 | Rooms in inventory. All revenue and cost calculations scale from this. |
| `DAYS` | 30 | Length of the simulated period. Monthly totals are daily values × this. |
| Fixed daily cost | 2,000 EUR | Overhead paid regardless of rooms sold (staff, mortgage, utilities). |
| Base CPOR | 35 EUR | Variable cost per occupied room per night (housekeeping, laundry, amenities, breakfast). |
| Surge threshold | 0.90 | Occupancy above which variable costs spike (operations strain near full capacity). |
| Surge rate | 0.10 | How much CPOR rises above threshold. At default, 35 → 38.50 EUR. |
| Channel cost rate | 0.10 | Distribution cost as a flat % of revenue (OTA commissions + direct blended). |

### Scenarios

Two-hotel comparison with three presets: `95% vs 80% occupancy`, `98% vs 70% occupancy`, and `Custom`. Each hotel is defined by an (occupancy, ADR) pair. The comparison illustrates that the busy-fool baseline (high occupancy, discounted ADR) is beaten on profit by lower-occupancy, higher-ADR strategies.

## Financial Model

Key functions inside the simulation cell (around line 313 of `interactive_simulation.py`):
- `cpor(occupancy)` — Returns variable cost per room, applying the surge multiplier above the threshold.
- `simulate(name, occupancy, adr)` — Runs one monthly simulation, returns a dict with all line items.
- `euro(x)` — Formats numbers as `EUR X,XXX`.

Cost flow: Revenue → minus Variable Costs (CPOR × rooms, with surge) → minus Channel Costs (flat % of revenue) → minus Fixed Costs → Net Profit.

## Visualization Conventions

- Matplotlib is the default. Custom `plt.rcParams` in the imports cell set a white background + light grid — copy that block into new notebooks for visual consistency.
- The `PAL` dict in `interactive_simulation.py` defines the project palette (`revenue`, `variable`, `channel`, `fixed`, `profit`). Reuse it (or extend it) rather than introducing arbitrary new colors.
- Waterfall charts are hand-built with `matplotlib.bar` + computed bottoms/heights — there's no waterfall library dependency.
- Do NOT add `plt.savefig(...)` calls. Charts must render in the browser only.
- Styling targets readable embedded output (the exported site is shared on LinkedIn): large fonts, high contrast, generous padding around titles and legends.
- For more interactive charts, prefer `altair` (works well in WASM, supports tooltips, returns a chart object as the cell's final expression).

## Skills and Workflow

Installed skills (locked in `skills-lock.json`):
- `marimo-pair` — marimo authoring guidance (there's also a bundled copy at `docs/occupancy-vanity-metric/CLAUDE.md` — that file is the marimo SKILL contents, not project instructions).
- `writing-linkedin-posts`, `linkedin-post-maker` — post-authoring skills.
- `brainstorming` — design-exploration skill.

### LinkedIn Post Rules

When drafting posts tied to the simulation (consult `.agents/skills/writing-linkedin-posts/SKILL.md` for the full spec):

- **One idea per post**, 150–300 words, 3,000 chars max.
- **Hook** (lines 1–2): honest admission, specific observation, or direct challenge. No "I'm excited to announce…" or engagement bait.
- **Body**: short paragraphs (1–3 sentences), scannable. Follow scene → tension → turning point → insight → reader application.
- **Close**: genuine question or reflection. Never "Agree?" or "Follow me for more."
- **Formatting**: no inline hashtags (3–5 at the end after a line break). One emoji max. "I", not "we."
- **Tone**: authentic, slightly casual. Avoid humblebrags, performed vulnerability, recycled viral formats.
- **Vulnerability test**: share to help others, not to process feelings; protect others involved; only share with hindsight.
