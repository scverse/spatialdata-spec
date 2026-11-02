#!/usr/bin/env python3
"""Render the figure of the RFC process in the contributing guide (hard-coded layout, no Graphviz).

Writes rfc-process-light.svg and rfc-process-dark.svg next to this script; the website shows one or
the other with its theme toggle (classes only-light / only-dark). Edit the steps and statuses or the
LIGHT/DARK colours here, never the SVG files.
Usage: python pages/img/rfc_process.py
"""

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent

# Compact layout with 10 actions. Status changes at the exact center of an action.
# Everything derives from these few spacing knobs.
ORDER = ["idea", "plan", "propose", "publish", "discuss", "revise", "decide", "prepare", "merge", "release"]
h, gap = 51, 12  # box height, vertical gap between boxes (arrow room)
loop = 12  # x of the dashed loopback gutter
x, w = loop + 18, 212  # step boxes
fb = x + w + 10  # solid discuss -> decide line
rx, rw = fb + 12, 64  # status rail
endw, endh = 66, 32
endx = rx + rw + 7 - endw  # terminal outcomes overlap the rail, poking out 7px on the right
W = endx + endw + 4
head = 26  # header band height
top = head + 8  # rail / first box top
cy = {k: top + h / 2 + i * (h + gap) for i, k in enumerate(ORDER)}
H = round(cy["release"] + h / 2 + 8)
by = [top, cy["plan"], cy["propose"], cy["publish"], cy["decide"], cy["merge"], cy["release"], H - 4]
statuses = ["idea", "planned", "draft", "under\nreview", "accepted", "specified", "released"]
steps = [
    ("idea", "Pitch", "Float an idea; no full RFC yet.", "community"),
    ("plan", "Plan", "Agree to write up the proposal.", "authors"),
    ("propose", "Propose", "Open an RFC PR using the template.", "authors"),
    ("publish", "Announce", "Merge the RFC PR; call for comments.", "developers"),
    ("discuss", "Discuss", "Feedback via GitHub, Zulip, calls, etc.", "community"),
    ("revise", "Revise", "Update the RFC via follow-up PRs.", "authors"),
    ("decide", "Decide", "Weigh RFC and feedback; record why.", "developers"),
    ("prepare", "Specify", "Open PRs for the accepted design.", "authors"),
    ("merge", "Review", "Check consistency; merge.", "developers"),
    ("release", "Release", "Publish with an implementation.", "developers"),
]
ACTOR = {"community": "COMMUNITY", "authors": "RFC AUTHORS", "developers": "DEVELOPERS"}
# Per-role colours: (box fill, box stroke / accent, tag fill, tag ink) for light and dark mode.
LIGHT = {
    "community": ("#fff7df", "#dcb33b", "#e4bf55", "#493c15"),
    "authors": ("#e8f5fc", "#3598ca", "#3598ca", "#ffffff"),
    "developers": ("#f2edfd", "#8462d5", "#8462d5", "#ffffff"),
}
DARK = {
    "community": ("#3d3520", "#dfba50", "#dfba50", "#2a2312"),
    "authors": ("#1b3548", "#6fc3ed", "#3d9fd4", "#ffffff"),
    "developers": ("#2e2648", "#b59df3", "#8a6be0", "#ffffff"),
}


def role_css(pal):
    return "".join(
        f".box-{r}{{fill:{f};stroke:{s}}}.acc-{r}{{stroke:{s}}}.tagbg-{r}{{fill:{tf}}}.tagtx-{r}{{fill:{ti}}}"
        for r, (f, s, tf, ti) in pal.items()
    )


ROLE_LIGHT, ROLE_DARK = role_css(LIGHT), role_css(DARK)
a = []
a.append(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">SpatialData RFC process</title><desc id="d">Compact action-flow diagram with community, RFC author and developer responsibilities. Solid discussion to decision; dashed optional revision and rework arrows. Withdrawn and rejected outcomes on the right. Status boundaries correspond to action centers.</desc>
<defs><style><![CDATA[
.bg{{fill:#fff}} .ink{{fill:#293341}} .secondary{{fill:#6a7585}}
.h{{font:700 13.4px system-ui,-apple-system,'Segoe UI',sans-serif}} .body{{font:10.6px system-ui,-apple-system,'Segoe UI',sans-serif}}
.tag{{font:700 7.1px system-ui,-apple-system,'Segoe UI',sans-serif;letter-spacing:.1px}}
.small{{font:10.5px system-ui,-apple-system,'Segoe UI',sans-serif}}
.statustxt{{font:700 11.5px system-ui,-apple-system,'Segoe UI',sans-serif;fill:#536277}}
.line{{stroke:#8c98aa;stroke-width:1.65;fill:none;stroke-linecap:round;stroke-linejoin:round}}
.optional{{stroke-dasharray:4.5 4.5}}
.rail{{fill:#f4f6f9;stroke:#d5dbe5;stroke-width:1}}
.rule{{stroke:#d5dbe5;stroke-width:1}} .terminal{{fill:#f4f6f9;stroke:#aab4c3;stroke-width:1}}
.arrowhead{{fill:#8c98aa}}
{ROLE_LIGHT}
@media(prefers-color-scheme:dark){{.bg{{fill:#141a26}}.ink{{fill:#eff3fa}}.secondary{{fill:#c4ccda}}.statustxt{{fill:#d8e1ef}}.line{{stroke:#b2bed0}}.arrowhead{{fill:#b2bed0}}.rail,.terminal{{fill:#252e3d;stroke:#526075}}.rule{{stroke:#526075}}
{ROLE_DARK}}}
]]></style><marker id="arrow" markerWidth="7" markerHeight="7" refX="6.3" refY="3.5" orient="auto" markerUnits="userSpaceOnUse"><path class="arrowhead" d="M0 0 L7 3.5 L0 7 Z"/></marker></defs>
<rect class="bg" width="{W}" height="{H}"/>
<text class="small secondary" x="{x + 17}" y="{head - 9}">Step</text><text class="small secondary" x="{rx + rw / 2}" y="{head - 9}" text-anchor="middle">Status</text>
<path class="rule" d="M4 {head} H{W - 4}"/>
''')

# Continuous status rail and separators.
a.append(f'<rect class="rail" x="{rx}" y="{by[0]}" width="{rw}" height="{by[-1] - by[0]}" rx="9"/>')
for i, s in enumerate(statuses):
    y0, y1 = by[i : i + 2]
    if i:
        a.append(f'<path class="rule" d="M{rx} {y0} H{rx + rw}"/>')
    mid = (y0 + y1) / 2
    if "\n" in s:
        p, q = s.split("\n")
        a.extend(
            (
                f'<text class="statustxt" x="{rx + rw / 2}" y="{mid - 5:.1f}" text-anchor="middle">{p}</text>',
                f'<text class="statustxt" x="{rx + rw / 2}" y="{mid + 9:.1f}" text-anchor="middle">{q}</text>',
            )
        )
    else:
        a.append(f'<text class="statustxt" x="{rx + rw / 2}" y="{mid + 4:.1f}" text-anchor="middle">{s}</text>')


def edge(d, dashed=False):
    a.append(f'<path class="line{" optional" if dashed else ""}" d="{d}" marker-end="url(#arrow)"/>')


# Main spine excluding the alternative feedback-to-revision branch.
for u, v in [
    ("idea", "plan"),
    ("plan", "propose"),
    ("propose", "publish"),
    ("publish", "discuss"),
    ("decide", "prepare"),
    ("prepare", "merge"),
    ("merge", "release"),
]:
    edge(f"M{x + w / 2:.1f} {cy[u] + h / 2:.1f} V{cy[v] - h / 2 - 2:.1f}")
# Discuss -> decide is the primary solid path, to the right of the nodes.
edge(f"M{x + w} {cy['discuss']} H{fb} V{cy['decide']} H{x + w + 2}")
# Optional feedback -> RFC revision.
edge(f"M{x + w / 2:.1f} {cy['discuss'] + h / 2:.1f} V{cy['revise'] - h / 2 - 2:.1f}", True)
# Loopbacks, parallel from an aligned left margin: revision -> public review; specification -> RFC revision.
edge(f"M{x} {cy['revise'] - 9} H{loop} V{cy['publish']} H{x - 2}", True)
edge(f"M{x} {cy['prepare'] + 9} H{loop} V{cy['revise'] + 9} H{x - 2}", True)
# Optional merge review -> back to specification (changes requested); right gutter is free below decide.
edge(f"M{x + w} {cy['merge'] - 9} H{fb} V{cy['prepare'] + 9} H{x + w + 2}", True)
# Terminal branches overlap status rail. They are optional outcomes.
for action, label in [("revise", "Withdrawn"), ("decide", "Rejected")]:
    yy = cy[action] + 9
    edge(f"M{x + w} {yy} H{endx - 2}", True)
    a.append(f'<rect class="terminal" x="{endx}" y="{yy - endh / 2}" width="{endw}" height="{endh}" rx="8"/>')
    a.append(f'<text class="small ink" x="{endx + endw / 2}" y="{yy + 4}" text-anchor="middle">{label}</text>')

for key, title, detail, role in steps:
    actor = ACTOR[role]
    yy = cy[key] - h / 2
    a.append(
        f'<g id="{key}"><rect class="box-{role}" x="{x}" y="{yy:.1f}" width="{w}" height="{h}" rx="9" stroke-width="1.2"/>'
    )
    a.append(
        f'<path class="acc-{role}" d="M{x + 3} {yy + 7:.1f} V{yy + h - 7:.1f}" stroke-width="5" stroke-linecap="round"/>'
    )
    a.append(f'<text x="{x + 17}" y="{yy + 22:.1f}" class="h ink">{escape(title)}</text>')
    a.append(f'<text x="{x + 17}" y="{yy + 39:.1f}" class="body secondary">{escape(detail)}</text>')
    # Identically sized role labels, close to the main heading but not touching.
    tagw = 62
    a.append(
        f'<rect class="tagbg-{role}" x="{x + w - tagw - 9}" y="{yy + 8:.1f}" width="{tagw}" height="17" rx="8.5"/>'
    )
    a.append(
        f'<text class="tag tagtx-{role}" x="{x + w - tagw / 2 - 9}" y="{yy + 19.5:.1f}" text-anchor="middle">{actor}</text></g>'
    )
a.append("</svg>")
sv = "".join(a)
# One file per theme: the website switches them with its own theme toggle, not with the operating
# system's colour scheme, so the dark rules apply unconditionally in the dark file.
MQ = "@media(prefers-color-scheme:dark){"
i = sv.index(MQ)
j = sv.index("]]>", i)
dark_rules = sv[i + len(MQ) : j].rstrip()[:-1]  # without the media query's closing brace
for mode, css in [("light", ""), ("dark", dark_rules)]:
    q = OUT / f"rfc-process-{mode}.svg"
    q.write_text(sv[:i] + css + "\n" + sv[j:] + "\n", encoding="utf-8", newline="\n")
    print(q, W, H)
