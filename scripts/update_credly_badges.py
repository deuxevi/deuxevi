"""Met à jour la section des badges Credly du README à partir du profil public Credly."""

import json
import os
import re
import sys
import urllib.request
from html import escape
from pathlib import Path

CREDLY_USER = os.environ.get("CREDLY_USER", "marcel-deuxevi")
README = Path(__file__).resolve().parent.parent / "README.md"
START = "<!--START_SECTION:badges-->"
END = "<!--END_SECTION:badges-->"
BADGE_WIDTH = 80


def fetch_badges(user):
    badges = []
    url = f"https://www.credly.com/users/{user}/badges.json"
    while url:
        request = urllib.request.Request(
            url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
        badges.extend(payload["data"])
        url = payload.get("metadata", {}).get("next_page_url")
    return badges


def render(badges):
    visible = [b for b in badges if b.get("public") and b.get("state") == "accepted"]
    visible.sort(key=lambda b: b["issued_at_date"], reverse=True)
    lines = ['<div align="center">']
    for badge in visible:
        name = escape(badge["badge_template"]["name"], quote=True)
        image = badge["badge_template"]["image_url"]
        link = f"https://www.credly.com/badges/{badge['id']}"
        lines.append(
            f'  <a href="{link}" target="_blank">'
            f'<img src="{image}" width="{BADGE_WIDTH}" title="{name}" alt="{name}"></a>'
        )
    lines.append("</div>")
    return "\n".join(lines)


def main():
    badges = fetch_badges(CREDLY_USER)
    if not badges:
        sys.exit(f"Aucun badge trouvé pour {CREDLY_USER} : README laissé intact.")

    readme = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    if not pattern.search(readme):
        sys.exit(f"Marqueurs {START} / {END} introuvables dans {README}.")

    section = f"{START}\n{render(badges)}\n{END}"
    updated = pattern.sub(lambda _: section, readme)
    if updated == readme:
        print("Badges déjà à jour.")
        return
    README.write_text(updated, encoding="utf-8", newline="\n")
    print(f"README mis à jour avec {len(badges)} badges.")


if __name__ == "__main__":
    main()
