"""Visual layer: CSS and small HTML builders. No business logic lives here."""
import html

import streamlit as st

from .diet_engine import format_time

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Hind+Madurai:wght@400;500;600&display=swap');
:root{--leaf:#1F7A4D;--leaf-deep:#17402F;--turmeric:#F2B01E;--chilli:#C8402B;--tamarind:#8A4B2A;--rice:#F4F8F3;--ink:#1B3A2D;--muted:#566B5F;--line:#D3E0D1;--wash:#E6EFE4;}
.stApp{background:var(--rice);color:var(--ink);font-family:'Hind Madurai','Segoe UI',system-ui,sans-serif;font-size:1.02rem;}
.stApp input,.stApp textarea,.stApp select,.stApp button{font-family:inherit;}
h1,h2,h3,.display{font-family:'Bricolage Grotesque','Segoe UI',system-ui,sans-serif!important;letter-spacing:-0.01em;color:var(--leaf-deep);}
h2{font-size:1.7rem!important;margin-top:.4rem;}
h3{font-size:1.2rem!important;}
.block-container{max-width:1040px;padding-top:2rem;padding-bottom:4rem;}
#MainMenu,footer{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent;}
.stApp p,.stApp li{line-height:1.6;}
.stApp .stMarkdown p,.stApp .stMarkdown li{max-width:72ch;}
.stApp .stMarkdown .meals li{max-width:none;}
.stApp [data-testid="stCaptionContainer"],.stApp [data-testid="stCaptionContainer"] *{color:var(--muted)!important;opacity:1!important;}

/* tabs */
.stTabs [data-baseweb="tab-list"]{gap:.25rem;border-bottom:1px solid var(--line);overflow-x:auto;}
.stTabs button[data-baseweb="tab"]{height:3rem;padding:0 1rem;color:var(--muted);font-weight:500;}
.stTabs button[data-baseweb="tab"][aria-selected="true"]{color:var(--leaf-deep);font-weight:600;}
.stTabs [data-baseweb="tab-highlight"]{background:var(--leaf);height:3px;}
.stTabs [data-baseweb="tab-panel"]{padding-top:1.6rem;}

/* form + inputs */
[data-testid="stForm"]{background:#fff;border:1px solid var(--line);border-radius:16px;padding:1.6rem 1.6rem 1.2rem;}
[data-testid="stForm"] h3{margin-top:1.2rem;padding-top:1rem;border-top:1px solid var(--line);}
[data-testid="stForm"] h3:first-of-type{border-top:0;margin-top:0;padding-top:0;}
.stApp label p{font-weight:500;color:var(--ink);}
.stApp [data-baseweb="input"],.stApp [data-baseweb="select"]>div{border-radius:10px;}

/* buttons */
.stButton button,.stDownloadButton button,[data-testid="stFormSubmitButton"] button{background:var(--leaf);color:#fff;border:0;border-radius:10px;padding:.65rem 1.4rem;font-weight:600;}
.stButton button:hover,.stDownloadButton button:hover,[data-testid="stFormSubmitButton"] button:hover{background:var(--leaf-deep);color:#fff;}
.stApp button:focus-visible{outline:3px solid var(--turmeric);outline-offset:2px;}

/* expanders */
[data-testid="stExpander"]{background:#fff;border:1px solid var(--line)!important;border-radius:12px;}

/* hero */
.hero{display:grid;grid-template-columns:1.5fr 1fr;gap:2rem;align-items:center;background:var(--leaf-deep);color:#fff;border-radius:22px;padding:2.6rem 2.4rem;margin-bottom:1.8rem;}
.hero h1{font-size:2.5rem!important;line-height:1.1;color:#fff!important;margin:0 0 1rem;padding:0;}
.hero p{color:#DCE9DE;font-size:1.1rem;margin:0 0 .8rem;max-width:44ch;}
.hero .hint{color:var(--turmeric);font-weight:600;margin:1.2rem 0 0;}
.hero-art svg{width:100%;max-width:260px;display:block;margin:0 auto;}
.plain-list{margin:.4rem 0 1.2rem;padding-left:1.2rem;}
.plain-list li{margin-bottom:.5rem;}

/* target panel and range track */
.target{background:#fff;border:1px solid var(--line);border-radius:18px;padding:1.8rem 2rem 1.4rem;margin-bottom:1.4rem;}
.target .label{color:var(--muted);margin:0;}
.target .big{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-weight:700;font-size:3.1rem;line-height:1.05;color:var(--leaf-deep);margin:.2rem 0 .3rem;}
.target .big small{font-size:1.2rem;font-weight:500;color:var(--muted);margin-left:.4rem;}
.target .sub{margin:0 0 1.4rem;color:var(--ink);}
.track-wrap{padding:0 .5rem;}
.track-top,.track-bottom{position:relative;height:1.5rem;font-size:.88rem;color:var(--muted);}
.track-top span,.track-bottom span{position:absolute;transform:translateX(-50%);white-space:nowrap;}
.track-top span{color:var(--leaf-deep);font-weight:600;}
.track{position:relative;height:14px;background:var(--wash);border-radius:99px;}
.track-band{position:absolute;top:0;bottom:0;background:var(--leaf);border-radius:99px;}
.track-mark{position:absolute;top:-5px;width:4px;height:24px;margin-left:-2px;background:var(--turmeric);border:1px solid var(--leaf-deep);border-radius:3px;}

/* stats separated by hairlines */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin:0 0 1.6rem;}
.stat{padding:1.1rem 1.2rem;border-left:1px solid var(--line);}
.stat:first-child{border-left:0;padding-left:0;}
.stat .k{color:var(--muted);font-size:.92rem;margin:0;}
.stat .v{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-weight:700;font-size:1.7rem;color:var(--leaf-deep);margin:.1rem 0 0;}
.stat .n{font-size:.88rem;color:var(--muted);margin:0;}
.chip{display:inline-block;padding:.05rem .6rem;border-radius:99px;font-size:.85rem;font-weight:600;background:var(--wash);color:var(--leaf-deep);}
.chip.warn{background:#FBE3DD;color:#8E2A19;}
.chip.mid{background:#FCEFC8;color:#6B4A00;}

/* macro bar */
.macro-bar{display:flex;height:22px;border-radius:99px;overflow:hidden;margin:.4rem 0 .8rem;}
.macro-bar span{display:block;height:100%;}
.macro-legend{display:flex;flex-wrap:wrap;gap:.4rem 1.6rem;}
.macro-legend div{display:flex;align-items:center;gap:.5rem;}
.swatch{width:12px;height:12px;border-radius:3px;display:inline-block;}

/* meal timeline */
.day-note{background:var(--wash);border-radius:12px;padding:.9rem 1.2rem;margin:0 0 1.4rem;}
.day-note p{margin:0;}
.meals{list-style:none;margin:0;padding:0;}
.meal{display:grid;grid-template-columns:5.5rem 1fr;gap:1rem;}
.meal-time{text-align:right;font-weight:600;color:var(--leaf-deep);padding-top:.05rem;}
.meal-body{position:relative;padding:0 0 1.6rem 1.5rem;border-left:2px solid var(--line);}
.meal:last-child .meal-body{border-left-color:transparent;padding-bottom:.4rem;}
.meal-body::before{content:"";position:absolute;left:-8px;top:.3rem;width:14px;height:14px;border-radius:50%;background:var(--turmeric);border:2px solid var(--leaf-deep);}
.meal-head{display:flex;flex-wrap:wrap;justify-content:space-between;gap:.2rem 1rem;}
.meal-head strong{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:1.1rem;color:var(--leaf-deep);}
.meal-kcal{color:var(--muted);font-size:.92rem;}
.meal-body p{margin:.2rem 0 .6rem;}
.kcal-bar{height:6px;background:var(--wash);border-radius:99px;max-width:420px;}
.kcal-bar span{display:block;height:100%;background:var(--leaf);border-radius:99px;}
.tag-warn{display:inline-block;margin-top:.5rem;padding:.1rem .6rem;border-radius:8px;background:#FBE3DD;color:#8E2A19;font-size:.85rem;font-weight:600;}

/* workout rows */
.sched{border-top:1px solid var(--line);margin:1rem 0 1.4rem;}
.sched div{display:grid;grid-template-columns:6rem 1fr;gap:1rem;padding:.8rem 0;border-bottom:1px solid var(--line);}
.sched b{font-family:'Bricolage Grotesque',system-ui,sans-serif;color:var(--leaf-deep);}

/* callouts */
.callout{border-radius:12px;padding:.9rem 1.2rem;margin:.8rem 0;border-left:5px solid var(--leaf);background:#fff;}
.callout.warn{border-left-color:var(--chilli);background:#FFF5F2;}
.callout.note{border-left-color:var(--turmeric);background:#FFFBEF;}
.callout p,.callout ul{margin:0;}
.callout ul{padding-left:1.1rem;margin-top:.4rem;}
.callout strong{color:var(--leaf-deep);}

@media (max-width:720px){
.hero{grid-template-columns:1fr;padding:1.8rem 1.4rem;}
.hero h1{font-size:1.9rem!important;}
.hero-art{display:none;}
.target{padding:1.3rem 1.2rem;}
.target .big{font-size:2.3rem;}
.meal{grid-template-columns:4.2rem 1fr;gap:.6rem;}
.stats{grid-template-columns:1fr 1fr;}
.stat{border-left:0;border-top:1px solid var(--line);padding-left:0;}
.stat:nth-child(-n+2){border-top:0;}
.stat .v{font-size:1.35rem;}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important;}}
</style>"""

THALI_SVG = (
    '<svg viewBox="0 0 200 200" role="img" aria-label="Illustration of a thali plate" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="100" cy="100" r="96" fill="#F4F8F3"/>'
    '<circle cx="100" cy="100" r="88" fill="none" stroke="#D3E0D1" stroke-width="3"/>'
    '<circle cx="100" cy="48" r="23" fill="#F2B01E"/><circle cx="100" cy="48" r="15" fill="#F8CF6B"/>'
    '<circle cx="149.5" cy="84" r="23" fill="#1F7A4D"/><circle cx="149.5" cy="84" r="15" fill="#4FA77A"/>'
    '<circle cx="130.6" cy="142" r="23" fill="#C8402B"/><circle cx="130.6" cy="142" r="15" fill="#E0725F"/>'
    '<circle cx="69.4" cy="142" r="23" fill="#8A4B2A"/><circle cx="69.4" cy="142" r="15" fill="#B57A57"/>'
    '<circle cx="50.5" cy="84" r="23" fill="#DDE8D8"/><circle cx="50.5" cy="84" r="15" fill="#FFFFFF"/>'
    '<circle cx="100" cy="100" r="17" fill="#fff" stroke="#D3E0D1" stroke-width="2"/>'
    '</svg>'
)


def _e(value):
    return html.escape(str(value))


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def show(markup):
    st.markdown(markup, unsafe_allow_html=True)


def hero():
    return (
        '<section class="hero"><div>'
        '<h1>Eat for your goal with food you already cook</h1>'
        '<p>Share a few details and get calorie and protein targets, a full day of Indian home meals, '
        'and a workout split you can download as a PDF.</p>'
        '<p class="hint">Open the Profile tab to begin.</p></div>'
        f'<div class="hero-art">{THALI_SVG}</div></section>'
    )


def callout(text, kind="info", title=None, items=None):
    cls = {"info": "callout", "warn": "callout warn", "note": "callout note"}[kind]
    head = f"<p><strong>{_e(title)}</strong></p>" if title else ""
    body = f"<p>{_e(text)}</p>" if text else ""
    lis = "<ul>" + "".join(f"<li>{_e(i)}</li>" for i in items) + "</ul>" if items else ""
    return f'<div class="{cls}">{head}{body}{lis}</div>'


def target_panel(goal, low, high, tdee, weekly_change):
    span_lo = min(low, tdee) - 250
    span_hi = max(high, tdee) + 250
    span = span_hi - span_lo

    def pos(v):
        return (v - span_lo) / span * 100

    band_left, band_w = pos(low), pos(high) - pos(low)
    band_mid = min(88, max(12, band_left + band_w / 2))
    mark = pos(tdee)
    mark_lab = min(88, max(12, mark))
    return (
        '<div class="target">'
        '<p class="label">Your daily calorie target</p>'
        f'<p class="big">{low:,} to {high:,}<small>kcal a day</small></p>'
        f'<p class="sub">For {_e(goal.lower())}, the chart expects {_e(weekly_change)} a week. '
        'Treat it as a starting point and adjust after two to three weeks.</p>'
        '<div class="track-wrap">'
        f'<div class="track-top"><span style="left:{band_mid:.1f}%">Target range</span></div>'
        '<div class="track">'
        f'<div class="track-band" style="left:{band_left:.1f}%;width:{band_w:.1f}%"></div>'
        f'<div class="track-mark" style="left:{mark:.1f}%"></div></div>'
        f'<div class="track-bottom"><span style="left:{mark_lab:.1f}%">Maintenance {tdee:,}</span></div>'
        '</div></div>'
    )


def stat_row(stats):
    """stats: list of (label, value, note_html)."""
    cells = "".join(
        f'<div class="stat"><p class="k">{_e(k)}</p><p class="v">{_e(v)}</p><p class="n">{n}</p></div>'
        for k, v, n in stats
    )
    return f'<div class="stats">{cells}</div>'


def bmi_chip(category):
    cls = {"Normal": "chip", "Overweight": "chip mid", "Underweight": "chip mid"}.get(category, "chip warn")
    return f'<span class="{cls}">{_e(category)}</span>'


def macro_bar(macros):
    parts = [
        ("Protein", macros["protein_g"], macros["protein_g"] * 4, "#1F7A4D"),
        ("Carbs", macros["carbs_g"], macros["carbs_g"] * 4, "#F2B01E"),
        ("Fat", macros["fat_g"], macros["fat_g"] * 9, "#8A4B2A"),
    ]
    total = sum(p[2] for p in parts) or 1
    bar = "".join(
        f'<span style="width:{kcal / total * 100:.1f}%;background:{color}" title="{name}"></span>'
        for name, _, kcal, color in parts
    )
    legend = "".join(
        f'<div><span class="swatch" style="background:{color}"></span>'
        f'<span><strong>{name}</strong> {grams} g ({kcal / total * 100:.0f}% of calories)</span></div>'
        for name, grams, kcal, color in parts
    )
    return f'<div class="macro-bar">{bar}</div><div class="macro-legend">{legend}</div>'


def meal_timeline(meals):
    peak = max(int(meals["source_kcal"].max()), 1)
    items = []
    for _, m in meals.iterrows():
        kcal = int(m["source_kcal"])
        width = max(2, round(kcal / peak * 100))
        note = m.get("note", "")
        tag = f'<span class="tag-warn">{_e(note)}</span>' if note else ""
        items.append(
            '<li class="meal">'
            f'<div class="meal-time">{_e(format_time(m["meal_time"]))}</div>'
            '<div class="meal-body">'
            f'<div class="meal-head"><strong>{_e(m["meal_name"])}</strong>'
            f'<span class="meal-kcal">about {kcal} kcal</span></div>'
            f'<p>{_e(m["food_description"])}</p>'
            f'<div class="kcal-bar"><span style="width:{width}%"></span></div>{tag}'
            '</div></li>'
        )
    return f'<ol class="meals">{"".join(items)}</ol>'


def schedule(days):
    rows = ""
    for entry in days:
        day, _, focus = entry.partition(": ")
        rows += f"<div><b>{_e(day)}</b><span>{_e(focus)}</span></div>"
    return f'<div class="sched">{rows}</div>'
