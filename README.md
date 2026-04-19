marimo export html-wasm interactive_simulation.py -o docs/occupancy-vanity-metric --mode run -f

# to test locally:
python -m http.server --directory docs/occupancy-vanity-metric 8080
-- then go to http://localhost:8080/

if it does not work, fix with: `touch docs/.nojekyll`

commit to github with:<br>
`git add .`<br>
`git commit -m 'some comment'`<br>
`git push origin main`<br>

deployed at:
https://dimitris1revtales.github.io/blog/occupancy-vanity-metric/

Official url:
https://blog.revenuetales.com/occupancy-vanity-metric/