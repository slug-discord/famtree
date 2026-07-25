# famtree

Readable, themeable family-tree rendering for Python 3.11+. Generation-tiered layout, HTML/CSS node cards with avatars, rasterized to PNG with Playwright. Built for Discord bots where a giant graphviz strip is unreadable.

---

## Install

```bash
pip install famtree
playwright install chromium   # one-time, for PNG rendering
```

Local dev:

```bash
git clone https://github.com/slug-discord/famtree
cd famtree
pip install -e ".[render,dev]"
```

---

## Quick start

```python
import asyncio
from famtree import Tree, Person, Theme, render_png

people = {
    1: Person(1, "Alex", avatar_url="https://.../a.png", gender="male"),
    2: Person(2, "Sam",  avatar_url="https://.../s.png", gender="female"),
    3: Person(3, "Kid",  gender="female"),
}
tree = Tree(
    root=1,
    people=people,
    parent_edges=[(1, 3), (2, 3)],   # (parent, child)
    partner_edges=[(1, 2)],          # (a, b)
)

async def main():
    png = await render_png(tree, Theme.named("dark"))
    open("tree.png", "wb").write(png)

asyncio.run(main())
```

---

## Theming

`Theme` is a frozen dataclass of CSS-ready strings — swap any of them, or use a preset:

```python
Theme.named("dark")    # default
Theme.named("light")
Theme.named("sunset")

Theme(background="#000", node_bg="#111", root_accent="#f0f")  # fully custom
```

Node borders auto-accent by gender (`male_accent` / `female_accent`); the root gets `root_accent`.

---

## How it works

- `assign_generations(tree)` — BFS from the root; parents are one generation up, children one down, partners share a row.
- `build_rows(tree)` — ordered rows, oldest generation first, couples kept adjacent.
- `build_html(tree, theme)` — self-contained HTML; parent→child and partner links are drawn as SVG connectors measured from the laid-out DOM.
- `render_png(tree, theme)` — Playwright screenshots the `#stage` element.

Layout and HTML generation have no dependencies; only `render_png` needs Playwright (`pip install famtree[render]`).

---

## License

[MIT](LICENSE)