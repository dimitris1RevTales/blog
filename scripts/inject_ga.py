"""Idempotently inject the GA4 snippet into one or more HTML files.

Usage:
    python scripts/inject_ga.py <path> [<path> ...]

Examples:
    # After a marimo re-export, reapply GA to the exported index.html
    python scripts/inject_ga.py docs/last-mile-pricing/index.html

    # Inject (or re-check) every tracked page
    python scripts/inject_ga.py \\
        docs/index.html \\
        docs/occupancy-vanity-metric/index.html \\
        docs/last-mile-pricing/index.html

The script is safe to run repeatedly. It detects a marker comment and skips
files that already have the snippet.
"""

import pathlib
import sys

GA_MEASUREMENT_ID = "G-P32PX685T9"
GA_MARKER = "<!-- GA4 (gtag.js) -->"

SNIPPET = f"""    {GA_MARKER}
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_MEASUREMENT_ID}');
    </script>
  """


def inject(path: str) -> int:
    p = pathlib.Path(path)
    if not p.exists():
        print(f"  missing: {path}")
        return 1
    content = p.read_text(encoding="utf-8")
    if GA_MARKER in content:
        print(f"  skip  (already injected): {path}")
        return 0
    if "</head>" not in content:
        print(f"  error (no </head>):       {path}")
        return 1
    new = content.replace("</head>", SNIPPET + "</head>", 1)
    p.write_text(new, encoding="utf-8")
    print(f"  inject: {path}")
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    rc = 0
    for path in argv:
        rc |= inject(path)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
