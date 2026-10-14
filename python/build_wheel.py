"""Builds the skills wheel shapes for Tableau from the skills-by-project table.

Each slice is one skill. Its length is the number of portfolio projects (out of 5) that used the skill,
so the wheel is evidence from the projects rather than a self-rating.

Reads  data/skills_by_project.csv   one row per skill and project, used = 1 or 0
Writes data/skills_wheel.csv        polygon points for Tableau's Polygon mark, plus label positions

Run from the project root:  python3 python/build_wheel.py
"""
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
N_PROJECTS = 5
LABEL_RADIUS = 1.22      # labels sit just outside the full circle
ARC_STEPS = 16           # points per slice edge; enough for a smooth curve

ORDER = ["Data quality auditing", "SQL", "Python (pandas)", "Statistics and testing", "Machine learning",
         "Power BI (DAX)", "Tableau", "Excel", "Recommendations with impact estimates"]
SHORT = {"Recommendations with impact estimates": "Business recs", "Data quality auditing": "Data cleaning",
         "Statistics and testing": "Statistics", "Python (pandas)": "Python", "Power BI (DAX)": "Power BI"}

projects_using = {}
with open(ROOT / "data" / "skills_by_project.csv") as f:
    for row in csv.DictReader(f):
        projects_using[row["skill"]] = projects_using.get(row["skill"], 0) + int(row["used"])
missing = set(ORDER) - set(projects_using)
assert not missing, f"Skills in ORDER but not in the data: {missing}"


def point(radius, angle):
    """Clockwise from 12 o'clock, so the first skill starts at the top."""
    return round(radius * math.sin(angle), 4), round(radius * math.cos(angle), 4)


rows = []
for i in range(73):                                   # the pale full circle behind the slices
    rows.append(["Background", "disc", i, *point(1, 2 * math.pi * i / 72), "", ""])

step = 2 * math.pi / len(ORDER)
for i, skill in enumerate(ORDER):
    count = projects_using[skill]
    radius, a0, a1 = count / N_PROJECTS, i * step, (i + 1) * step
    name = SHORT.get(skill, skill)
    outline = [(0, 0)] + [point(radius, a0 + (a1 - a0) * j / ARC_STEPS) for j in range(ARC_STEPS + 1)]
    for order, (x, y) in enumerate(outline):
        rows.append([name, "wedge", order, x, y, count, f"{count} of {N_PROJECTS} projects"])
    rows.append([name, "label", 0, *point(LABEL_RADIUS, (a0 + a1) / 2), count, f"{count} of {N_PROJECTS} projects"])

with open(ROOT / "data" / "skills_wheel.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["skill", "part", "point_order", "x", "y", "projects", "projects_text"])
    writer.writerows(rows)

for skill in ORDER:
    print(f"{SHORT.get(skill, skill):<15} {projects_using[skill]} of {N_PROJECTS}")
