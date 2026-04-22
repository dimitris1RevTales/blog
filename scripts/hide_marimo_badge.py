"""Idempotently inject a CSS+JS block that hides the "Made with Marimo" badge.

Usage:
    python scripts/hide_marimo_badge.py <path> [<path> ...]

Examples:
    # After a marimo re-export, reapply the badge-hide snippet
    python scripts/hide_marimo_badge.py docs/last-mile-pricing/index.html

    # Reapply to every exported notebook
    python scripts/hide_marimo_badge.py \\
        docs/occupancy-vanity-metric/index.html \\
        docs/last-mile-pricing/index.html \\
        docs/smart-allocator/index.html

The script is safe to run repeatedly. It detects a marker comment and skips
files that already have the snippet. The snippet runs on DOMContentLoaded,
sets up a MutationObserver, and also fires a delayed sweep at 2s to catch
the badge that marimo renders late during WASM bootstrap.
"""

import pathlib
import sys

MARKER = "<!-- hide marimo badge -->"

SNIPPET = f"""    {MARKER}
    <style>
      a[href*="marimo.io"],
      a[href*="marimo.app"],
      [class*="marimo-badge"],
      [data-marimo-badge] {{
        display: none !important;
      }}
    </style>
    <script>
      (function () {{
        var TEXT_RE = /^\\s*made with\\s+marimo\\s*$/i;
        function hideIn(root) {{
          if (!root || !root.querySelectorAll) return;
          var links = root.querySelectorAll('a');
          for (var i = 0; i < links.length; i++) {{
            var a = links[i];
            var href = (a.getAttribute('href') || '').toLowerCase();
            var text = (a.textContent || '').trim();
            if (
              href.indexOf('marimo.io') !== -1 ||
              href.indexOf('marimo.app') !== -1 ||
              TEXT_RE.test(text)
            ) {{
              a.style.display = 'none';
            }}
          }}
          var all = root.querySelectorAll('*');
          for (var j = 0; j < all.length; j++) {{
            var el = all[j];
            if (el.shadowRoot) hideIn(el.shadowRoot);
          }}
        }}
        function sweep() {{ hideIn(document); }}
        if (document.readyState === 'loading') {{
          document.addEventListener('DOMContentLoaded', sweep);
        }} else {{
          sweep();
        }}
        setTimeout(sweep, 2000);
        try {{
          var mo = new MutationObserver(function () {{ sweep(); }});
          mo.observe(document.documentElement, {{ childList: true, subtree: true }});
        }} catch (e) {{}}
      }})();
    </script>
  """


def inject(path: str) -> int:
    p = pathlib.Path(path)
    if not p.exists():
        print(f"  missing: {path}")
        return 1
    content = p.read_text(encoding="utf-8")
    if MARKER in content:
        print(f"  skip  (already injected): {path}")
        return 0
    if "</body>" not in content:
        print(f"  error (no </body>):       {path}")
        return 1
    new = content.replace("</body>", SNIPPET + "</body>", 1)
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
