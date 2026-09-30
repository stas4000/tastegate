"""Each rule gets a clean page with exactly one defect injected; the clean page itself must pass.

Run: python3 -m pytest tests -q   (needs playwright + chromium)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tastegate" / "scripts"))
import gate  # noqa: E402

CLEAN = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Harbor</title>
<style>
  body {{ margin: 0; font: 17px/1.6 Georgia, serif; color: #1d232b; background: #f4f6f8; }}
  h1, h2, h3 {{ font-family: "Courier Prime", Georgia, serif; line-height: 1.15; }}
  main {{ max-width: 960px; margin: 0 auto; padding: 32px 20px; }}
  .cta {{ display: inline-block; padding: 14px 22px; background: #0b5d4b; color: #fff; border-radius: 10px; text-decoration: none; }}
  nav a {{ display: inline-block; padding: 12px 8px; color: #1d232b; }}
  {extra_css}
</style></head><body>
<a href="#plans" style="position:absolute;left:-9999px;top:8px">Skip to plans</a>
<label style="position:absolute;left:-9999px;top:8px">Email address label</label>
<header><nav><a href="#plans">Plans</a> <a href="#faq">Questions</a></nav></header>
<main>
  <section><span style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">Screen reader note over the heading</span><h1>Tide tables for small harbors</h1>
  <p>Forecasts for 212 harbors, updated every hour from the national gauges.</p>
  <a class="cta" href="#plans">See the plans</a></section>
  <section id="plans"><h2>Plans</h2><p>One harbor is free. Every harbor is eight dollars a month.</p></section>
  <section id="faq"><h2>Questions</h2><p>Data comes from public tide gauges, checked against the last 30 days.</p></section>
  {extra_html}
</main></body></html>"""

CARD = '<div class="card"><svg width="24" height="24"><circle cx="12" cy="12" r="10"/></svg><h3>{t}</h3><p>Short supporting copy that explains this feature in a sentence.</p></div>'

DEFECTS = {
    "sideways_scroll": ("", '<div style="width:1600px;height:20px;background:#ddd"></div>'),
    "text_overlap": (".over { position: relative; } .over span { position: absolute; left: 0; top: 0; }",
                     '<p class="over">Harbor pilots read this first<span>Overlapping badge text here</span></p>'),
    "low_contrast": ("", '<p style="color:#b9c0c7">This caption is far too faint to read on the page.</p>'),
    "tiny_text": ("", '<p style="font-size:10px">Fine print nobody on a phone can read.</p>'),
    "small_tap_target": ("", '<button style="padding:2px 6px;font-size:13px">Go</button>'),
    "no_viewport_meta": ("", ""),
    "hero_below_fold": ("section:first-child { padding-top: 1100px; }", ""),
    "broken_image": ("", '<img src="missing-file.png" alt="harbor map" width="200" height="100">'),
    "image_without_alt": ("", '<img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" width="120" height="60">'),
    "ai_purple_gradient": (".glow { height: 120px; background: linear-gradient(135deg, #7c3aed, #4f46e5); }", '<div class="glow"></div>'),
    "gradient_text": (".gt { background: linear-gradient(90deg, #0b5d4b, #1d232b); -webkit-background-clip: text; background-clip: text; color: transparent; }",
                      '<h2 class="gt">Gradient headline</h2>'),
    "emoji_icon": ("", "<ul><li>\U0001F680 Fast updates every hour</li></ul>"),
    "eyebrow_labels": (".eb { font-size: 12px; text-transform: uppercase; letter-spacing: 0.2em; }",
                       '<div><p class="eb">Coverage</p><h2>Every harbor</h2></div><div><p class="eb">Speed</p><h2>Hourly</h2></div>'
                       '<div><p class="eb">Trust</p><h2>Public data</h2></div>'),
    "equal_icon_cards": (".grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; } .card { background: #fff; border: 1px solid #d5dbe1; padding: 16px; }",
                         '<div class="grid">' + CARD.format(t="Hourly") + CARD.format(t="Accurate") + CARD.format(t="Offline") + "</div>"),
    "default_display_font": ("h1, h2, h3 { font-family: Inter, sans-serif; }", ""),
    "placeholder_copy": ("", "<p>Lorem ipsum dolor sit amet, consectetur adipiscing.</p>"),
    "em_dash": ("", "<p>Tides move twice a day — sometimes more.</p>"),
}


def page(tmp_path: Path, extra_css: str = "", extra_html: str = "", drop_viewport: bool = False) -> Path:
    html = CLEAN.format(extra_css=extra_css, extra_html=extra_html)
    if drop_viewport:
        html = html.replace('<meta name="viewport" content="width=device-width, initial-scale=1">', "")
    p = tmp_path / "index.html"
    p.write_text(html)
    return p


def test_clean_page_passes(tmp_path):
    report = gate.run(str(page(tmp_path)), tmp_path / "out", wait_ms=100)
    assert report["fail"] == 0, report["findings"]
    assert Path(report["screenshots"]["mobile"]).stat().st_size > 1000
    assert gate.main([str(tmp_path / "index.html"), "--out", str(tmp_path / "o2"), "--wait", "50"]) == 0


@pytest.mark.parametrize("rule", sorted(DEFECTS))
def test_each_defect_is_caught(tmp_path, rule):
    css, html = DEFECTS[rule]
    target = page(tmp_path, css, html, drop_viewport=(rule == "no_viewport_meta"))
    report = gate.run(str(target), tmp_path / "out", wait_ms=100)
    assert rule in report["rules_failed"], report["findings"]
    assert gate.main([str(target), "--out", str(tmp_path / "o2"), "--wait", "50"]) == 1


def test_unrenderable_target_exits_2(tmp_path):
    assert gate.main([str(tmp_path / "nope.html")]) == 2


def test_reveal_on_scroll_content_is_judged_on_smooth_scroll_pages(tmp_path):
    """Content that fades in on scroll must be revealed before judging, even with scroll-behavior: smooth."""
    css = "html { scroll-behavior: smooth; } .rv { opacity: 0; } .rv.in { opacity: 1; }"
    html = ('<div style="height:3000px"></div><p class="rv" style="color:#c3c9cf">Faint caption far down the page.</p>'
            "<script>const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) e.target.classList.add('in'); }));"
            "document.querySelectorAll('.rv').forEach(el => io.observe(el));</script>")
    report = gate.run(str(page(tmp_path, css, html)), tmp_path / "out", wait_ms=300)
    assert "low_contrast" in report["rules_failed"], report["findings"]


def test_fading_container_does_not_fake_low_contrast(tmp_path):
    """White on teal inside a half-faded card is still about 4.6:1; opacity fades text and background together."""
    html = '<div style="opacity:0.5"><span style="display:inline-block;padding:12px;background:#3b7d8c;color:#fff">MR</span></div>'
    report = gate.run(str(page(tmp_path, "", html)), tmp_path / "out", wait_ms=100)
    assert "low_contrast" not in report["rules_failed"], report["findings"]
