"""Idempotently replace the default marimo favicons with revenuetales.com ones.

Usage:
    python scripts/update_favicon.py <path> [<path> ...]

Examples:
    # After a marimo re-export, reapply the branded favicons
    python scripts/update_favicon.py docs/last-mile-pricing/index.html

    # Reapply to every exported notebook
    python scripts/update_favicon.py \\
        docs/occupancy-vanity-metric/index.html \\
        docs/last-mile-pricing/index.html \\
        docs/smart-allocator/index.html

The script is safe to run repeatedly. It detects a marker comment and skips
files that already have the replacement. It rewrites the three default
<link> tags marimo emits (favicon.ico, apple-touch-icon, manifest.json)
with PNGs hosted under revenuetales.com, so the blog tabs match the main
site's branding. Marimo overwrites index.html on every re-export, so this
script has to be re-run each time.
"""

import pathlib
import sys

MARKER = "<!-- favicon: revenuetales -->"

OLD_ICON = '    <link rel="icon" href="./favicon.ico" />'
OLD_APPLE = '    <link rel="apple-touch-icon" href="./apple-touch-icon.png" />'
OLD_MANIFEST = '    <link rel="manifest" href="./manifest.json" />'

FAVICON_BASE = "https://revenuetales.com/wp-content/uploads/cropped-favicon-1"

NEW_BLOCK = f"""    {MARKER}
    <link rel="icon" type="image/png" sizes="32x32" href="{FAVICON_BASE}-32x32.png" />
    <link rel="icon" type="image/png" sizes="192x192" href="{FAVICON_BASE}-192x192.png" />
    <link rel="apple-touch-icon" sizes="270x270" href="{FAVICON_BASE}-270x270.png" />"""


def inject(path: str) -> int:
    p = pathlib.Path(path)
    if not p.exists():
        print(f"  missing: {path}")
        return 1
    content = p.read_text(encoding="utf-8")
    if MARKER in content:
        print(f"  skip  (already injected): {path}")
        return 0
    for needle in (OLD_ICON, OLD_APPLE, OLD_MANIFEST):
        if needle not in content:
            print(f"  error (missing tag '{needle.strip()}'): {path}")
            return 1
    # Swap the ./favicon.ico line for our branded block, then drop the
    # other two tags. Blank lines left behind are harmless in HTML.
    new = content.replace(OLD_ICON, NEW_BLOCK, 1)
    new = new.replace(OLD_APPLE, "", 1)
    new = new.replace(OLD_MANIFEST, "", 1)
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
