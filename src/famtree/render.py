from __future__ import annotations

import html
import json
from typing import Optional

from .layout import Layout
from .models import Theme, Tree


class Renderer:
    """Builds the HTML for a tree and rasterises it to PNG."""

    @staticmethod
    def _node(
        tree: Tree, 
        uid: int, 
        theme: Theme
    ) -> str:
        """Markup for a single person card."""
        p = tree.person(uid)
        is_root = uid == tree.root
        accent = theme.root_accent if is_root else (
            theme.male_accent if p.gender == "male"
            else theme.female_accent if p.gender == "female"
            else theme.node_border
        )
        avatar = (
            f'<img class="av" src="{html.escape(p.avatar_url)}" alt="">'
            if p.avatar_url
            else '<div class="av av-empty"></div>'
        )
        return (
            f'<div class="node{" root" if is_root else ""}" data-id="{uid}" '
            f'style="border-color:{accent}">'
            f'{avatar}<span class="nm">{html.escape(p.name)}</span></div>'
        )

    @staticmethod
    def build_html(
        tree: Tree, 
        theme: Optional[Theme] = None
    ) -> str:
        """Render the tree to a self-contained HTML document."""
        theme = theme or Theme()
        rows = Layout.build_rows(tree)
        rows_html = "".join(
            f'<div class="gen">{"".join(Renderer._node(tree, uid, theme) for uid in row)}</div>'
            for row in rows
        )
        edges = {
            "parents": [[a, b] for a, b in tree.parent_edges],
            "partners": [[a, b] for a, b in tree.partner_edges],
        }
        return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; background: {theme.background}; font-family: {theme.font_family}; }}
#stage {{ position: relative; display: inline-block; padding: 40px; }}
#lines {{ position: absolute; inset: 0; pointer-events: none; z-index: 0; }}
.gen {{ position: relative; z-index: 1; display: flex; gap: 26px; justify-content: center;
        flex-wrap: wrap; margin: 0 0 64px 0; }}
.gen:last-child {{ margin-bottom: 0; }}
.node {{ display: flex; flex-direction: column; align-items: center; gap: 8px;
         width: 118px; padding: 12px 8px; border-radius: 16px;
         background: {theme.node_bg}; border: 2px solid {theme.node_border};
         box-shadow: 0 6px 18px rgba(0,0,0,0.35); }}
.node.root {{ box-shadow: 0 0 0 3px {theme.root_accent}55, 0 6px 18px rgba(0,0,0,0.4); }}
.av {{ width: 64px; height: 64px; border-radius: 50%; object-fit: cover;
       border: 2px solid rgba(255,255,255,0.12); }}
.av-empty {{ width: 64px; height: 64px; border-radius: 50%;
             background: linear-gradient(135deg,#667eea,#764ba2); }}
.nm {{ color: {theme.text}; font-size: 13px; font-weight: 600; text-align: center;
       line-height: 1.2; max-width: 104px; overflow: hidden; text-overflow: ellipsis;
       display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
</style></head><body>
<div id="stage"><svg id="lines"></svg>{rows_html}</div>
<script>
const EDGES = {json.dumps(edges)};
function center(el){{const r=el.getBoundingClientRect();const s=document.getElementById('stage').getBoundingClientRect();
  return {{x:r.left-s.left+r.width/2, y:r.top-s.top, b:r.top-s.top+r.height, w:r.width}};}}
function draw(){{
  const svg=document.getElementById('lines');const stage=document.getElementById('stage');
  svg.setAttribute('width',stage.scrollWidth);svg.setAttribute('height',stage.scrollHeight);
  const map={{}};document.querySelectorAll('.node').forEach(n=>map[n.dataset.id]=n);
  let out='';
  for(const [a,b] of EDGES.parents){{const pa=map[a],ch=map[b];if(!pa||!ch)continue;
    const c1=center(pa),c2=center(ch);const my=(c1.b+c2.y)/2;
    out+='<path d="M '+c1.x+' '+c1.b+' C '+c1.x+' '+my+', '+c2.x+' '+my+', '+c2.x+' '+c2.y+'" stroke="{theme.edge}" stroke-width="2" fill="none"/>';}}
  for(const [a,b] of EDGES.partners){{const na=map[a],nb=map[b];if(!na||!nb)continue;
    const c1=center(na),c2=center(nb);const y=(c1.y+c1.b)/2;
    out+='<line x1="'+c1.x+'" y1="'+y+'" x2="'+c2.x+'" y2="'+y+'" stroke="{theme.partner_edge}" stroke-width="2.5" stroke-dasharray="4 4"/>';}}
  svg.innerHTML=out;
}}
draw();window.__ready=true;
</script>
</body></html>"""

    @staticmethod
    async def render_png(
        tree: Tree, 
        theme: Optional[Theme] = None, 
        *, 
        scale: int = 2
    ) -> bytes:
        """Screenshot the rendered tree to PNG bytes with Playwright."""
        from playwright.async_api import async_playwright

        markup = Renderer.build_html(tree, theme)
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(args=["--no-sandbox"])
            try:
                page = await browser.new_page(device_scale_factor=scale)
                await page.set_content(markup, wait_until="networkidle")
                await page.wait_for_function("window.__ready === true", timeout=5000)
                stage = await page.query_selector("#stage")
                png = await stage.screenshot(omit_background=False)
            finally:
                await browser.close()
        return png
