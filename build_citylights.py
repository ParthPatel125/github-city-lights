#!/usr/bin/env python3
"""Draw the contribution grid as "city lights": cells pop in with a staggered
spring, active days glow and gently pulse. Ported from the GithubCalendar
city-lights variant on parth's personal website.

Usage: build_citylights.py <contrib.json> <out_dir>
contrib.json is the GraphQL contributionsCollection response.
"""

import json
import sys

CELL = 12
GAP = 3
PITCH = CELL + GAP
PAD = 4
CAPTION_H = 26

# emerald scale, matching the website component's "green" colorSchema
THEMES = {
    "dark": {
        "empty": "#161b22",
        "levels": {
            "FIRST_QUARTILE": "#064e3b",
            "SECOND_QUARTILE": "#047857",
            "THIRD_QUARTILE": "#10b981",
            "FOURTH_QUARTILE": "#34d399",
        },
        "halo": 0.7,
        "caption": "#8b949e",
        "accent": "#34d399",
    },
    "light": {
        "empty": "#f0f1f3",
        "levels": {
            "FIRST_QUARTILE": "#a7f3d0",
            "SECOND_QUARTILE": "#6ee7b7",
            "THIRD_QUARTILE": "#34d399",
            "FOURTH_QUARTILE": "#10b981",
        },
        "halo": 0.45,
        "caption": "#59636e",
        "accent": "#10b981",
    },
}

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def build(cal, theme):
    c = THEMES[theme]
    weeks = cal["weeks"]
    width = PAD * 2 + len(weeks) * PITCH - GAP
    height = PAD * 2 + 7 * PITCH - GAP + CAPTION_H

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="{cal["totalContributions"]} contributions in the last year, drawn as glowing city lights">',
        '<defs>',
        '<filter id="b" x="-120%" y="-120%" width="340%" height="340%">'
        '<feGaussianBlur stdDeviation="4"/></filter>',
        '<style>',
        '.p { animation: pop 0.45s cubic-bezier(0.34, 1.56, 0.64, 1) both; '
        'transform-box: fill-box; transform-origin: center; }',
        '@keyframes pop { from { opacity: 0; transform: scale(0); } '
        'to { opacity: 1; transform: scale(1); } }',
        '</style>',
        '</defs>',
    ]

    for wi, week in enumerate(weeks):
        for day in week["contributionDays"]:
            di = _dow(day["date"])
            x = PAD + wi * PITCH
            y = PAD + di * PITCH
            delay = round(wi * 0.012 + di * 0.012, 3)
            level = day["contributionLevel"]
            if level == "NONE":
                parts.append(
                    f'<rect class="p" style="animation-delay:{delay}s" '
                    f'x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{c["empty"]}"/>'
                )
            else:
                fill = c["levels"].get(level, c["levels"]["FOURTH_QUARTILE"])
                # halo underneath + lit cell on top; the halo breathes
                pulse_delay = round((wi * 7 + di) % 10 * 0.3, 2)
                parts.append(f'<g class="p" style="animation-delay:{delay}s">')
                parts.append(
                    f'<rect x="{x - 1}" y="{y - 1}" width="{CELL + 2}" height="{CELL + 2}" rx="4" '
                    f'fill="{fill}" filter="url(#b)" opacity="{c["halo"]}">'
                    f'<animate attributeName="opacity" values="{c["halo"]};{round(c["halo"] * 0.35, 2)};{c["halo"]}" '
                    f'dur="3.2s" begin="{pulse_delay}s" repeatCount="indefinite"/></rect>'
                )
                parts.append(
                    f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{fill}"/>'
                )
                parts.append('</g>')

    total = cal["totalContributions"]
    cap_y = height - 8
    parts.append(
        f'<circle cx="{PAD + 5}" cy="{cap_y - 4}" r="4" fill="{c["accent"]}">'
        f'<animate attributeName="opacity" values="1;0.35;1" dur="3.2s" repeatCount="indefinite"/></circle>'
    )
    parts.append(
        f'<text x="{PAD + 16}" y="{cap_y}" font-family="{MONO}" font-size="12" '
        f'fill="{c["caption"]}">{total} contributions in the last year</text>'
    )
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def _dow(date_str):
    import datetime
    d = datetime.date.fromisoformat(date_str)
    return (d.weekday() + 1) % 7  # GitHub weeks start on Sunday


if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    out = sys.argv[2]
    for theme in THEMES:
        path = f"{out}/citylights-{theme}.svg"
        with open(path, "w") as f:
            f.write(build(cal, theme))
        print("wrote", path)
