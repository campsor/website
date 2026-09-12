"""Render the track record into index.html at build time.

GitHub Pages serves static files, so the table is generated here, during the deploy, from the
same data/returns.json that the automation updates. The figures then exist in the HTML source:
search engines, AI assistants and browsers without JavaScript all see them. The page's own
script reads the rows back from the DOM to build the cumulative chart.
"""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent


def cell(value: float | None) -> str:
    if value is None:
        return "<td></td>"
    cls = ' class="neg"' if value < 0 else (' class="pos-strong"' if value >= 5 else "")
    return f"<td{cls}>{value:.1f}%</td>"


def main() -> None:
    data = json.loads((ROOT / "data" / "returns.json").read_text(encoding="utf-8"))
    rows = []
    for year in data["years"]:
        months = "".join(cell(m) for m in year["months"])
        annual = f"{year['annual']:.1f}%" if year.get("annual") is not None else ""
        ytd = '<span class="ytd">YTD</span>' if year.get("ytd") else ""
        rows.append(
            f'<tr><th scope="row">{year["year"]}</th>{months}'
            f'<td class="perf-table__annual">{annual}{ytd}</td></tr>'
        )

    path = ROOT / "index.html"
    html = path.read_text(encoding="utf-8")
    body = "\n            ".join(rows)
    html, n = re.subn(r"<tbody>.*?</tbody>",
                      f"<tbody>\n            {body}\n          </tbody>",
                      html, count=1, flags=re.S)
    if n != 1:
        raise SystemExit("tbody not found in index.html")
    path.write_text(html, encoding="utf-8")
    print(f"rendered {len(rows)} year rows into index.html")


if __name__ == "__main__":
    main()
