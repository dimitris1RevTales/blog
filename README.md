marimo export html-wasm interactive_simulation.py -o docs/occupancy-vanity-metric --mode run -f

# to test locally:
python -m http.server --directory docs/occupancy-vanity-metric 8080
-- then go to http://localhost:8080/

if it does not work, fix with: `touch docs/.nojekyll`

commit to github with:
git add <the pytho file> docs/.
git commit -m 'some comment'
git push origin main

deployed at:
https://dimitris1revtales.github.io/blog/occupancy-vanity-metric/