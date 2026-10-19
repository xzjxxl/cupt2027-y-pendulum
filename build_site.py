#!/usr/bin/env python3
"""Build the static gallery for the Y-pendulum animation collection.

Usage: python build_site.py

Reads catalog.json from the folder that contains this script and writes
index.html, one g-<code>.html page per group, and a shared style.css into
that same folder (works from any working directory). Every user-facing
string comes from catalog.json; this script's own literals are ASCII-only.
Python 3.11, standard library only, deterministic and idempotent: running
it twice produces identical files.
"""

import html
import json
import pathlib
import sys
from urllib.parse import quote

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
CATALOG_PATH = SCRIPT_DIR / "catalog.json"

VIEWPORT_TAG = (
    '<meta name="viewport" '
    'content="width=device-width, initial-scale=1, viewport-fit=cover">'
)

FULLSCREEN_ICON = (
    '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">'
    '<path d="M4 9V5h5M15 5h5v5M20 15v4h-5M9 19H4v-5" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round"></path>'
    "</svg>"
)

PAGE_JS = """<script>
(function () {
  "use strict";
  // 移动端一次只加载一段：WKWebView / X5 对并发视频有限制，
  // 一次挂 4~5 个 src 会让后几个直接失败。
  var wide = false;
  try { wide = window.matchMedia("(min-width: 721px)").matches; } catch (e) {}

  function attach(v) {
    if (!v.getAttribute("src") && v.dataset.src) {
      v.setAttribute("src", v.dataset.src);
      v.load();
    }
  }
  function play(v) {
    v.muted = true;
    v.loop = true;
    try {
      var pr = v.play();
      if (pr && typeof pr.catch === "function") { pr.catch(function () {}); }
    } catch (e) {}
  }
  function pauseOthers(keep) {
    document.querySelectorAll("video").forEach(function (v) {
      if (v !== keep) { try { v.pause(); } catch (e) {} }
    });
  }
  function showOverlay(card, on) {
    var b = card.querySelector(".playbtn");
    if (b) { b.hidden = !on; }
  }
  function markBad(card, text) {
    var lab = card.querySelector(".placeholder-label");
    if (lab) { lab.textContent = text; }
    card.classList.add("missing");
  }

  var cards = document.querySelectorAll(".card");
  cards.forEach(function (card, idx) {
    var video = card.querySelector("video");
    if (!video) { return; }
    var tries = 0;

    function fail() {
      // 先重试；两次都失败再判断到底是不是"文件不存在"
      if (tries < 2) {
        tries += 1;
        window.setTimeout(function () {
          video.removeAttribute("src");
          attach(video);
          play(video);
        }, 700 * tries);
        return;
      }
      var src = video.dataset.src || "";
      if (!src) { markBad(card, "MEDIA NOT FOUND"); return; }
      fetch(src, { method: "HEAD" }).then(function (r) {
        markBad(card, r.ok ? "加载失败 · 点我看重试" : "MEDIA NOT FOUND");
      }).catch(function () {
        markBad(card, "加载失败 · 点我看重试");
      });
    }

    video.addEventListener("error", fail);
    // 点占位块 = 重试
    var ph = card.querySelector(".placeholder");
    if (ph) {
      ph.addEventListener("click", function () {
        card.classList.remove("missing");
        tries = 0;
        video.removeAttribute("src");
        attach(video);
        play(video);
      });
    }
    // 点播放按钮 = 播这一段，其余暂停
    var btn = card.querySelector(".playbtn");
    if (btn) {
      btn.addEventListener("click", function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        pauseOthers(video);
        attach(video);
        play(video);
        showOverlay(card, false);
      });
    }
    video.addEventListener("playing", function () { showOverlay(card, false); });
    // 还没挂 src 时原生控件是死的，整块画面点一下就该开始播
    video.addEventListener("click", function (ev) {
      if (video.getAttribute("src")) { return; }
      ev.preventDefault();
      pauseOthers(video);
      attach(video);
      play(video);
      showOverlay(card, false);
    });

    if (wide || idx === 0) {
      video.autoplay = true;      // 宽屏走原生自动播放，比脚本 play() 稳
      attach(video);
      play(video);
    } else {
      showOverlay(card, true);
    }
  });

  // 兜底：微信/X5 拦自动播放时，一次点击把能播的都开起来
  function playAll() {
    document.querySelectorAll(".card").forEach(function (card, idx) {
      var v = card.querySelector("video");
      if (!v) { return; }
      if (!wide && idx > 0) { pauseOthers(v); }
      v.autoplay = true;
      attach(v);
      play(v);
      showOverlay(card, false);
    });
  }
  var allBtn = document.getElementById("playall");
  if (allBtn) {
    if (!wide) { allBtn.hidden = false; }
    allBtn.addEventListener("click", function () {
      playAll();
      allBtn.classList.add("done");
    });
  }

  // 只检查"一个都没播起来"，不再用 readyState 判缺失
  window.setTimeout(function () {
    var paused = 0, total = 0;
    document.querySelectorAll("video").forEach(function (v) {
      total += 1;
      if (v.paused) { paused += 1; }
    });
    if (allBtn && total > 0 && paused === total) { allBtn.hidden = false; }
  }, 3000);
})();
</script>"""

PAGE_CSS = """/* Y-pendulum gallery - shared stylesheet (generated by build_site.py) */

:root {
  --bg: #000000;
  --panel: #070A0F;
  --text: #F2F5F9;
  --muted: #9AA6B8;
  --accent-a: #35C7D8;
  --accent-b: #F2C14E;
  --line: #232A36;
}

* { box-sizing: border-box; }

html { -webkit-text-size-adjust: 100%; overflow-x: hidden; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, "PingFang SC", "Hiragino Sans GB",
    "Microsoft YaHei", sans-serif;
  line-height: 1.55;
  overflow-x: hidden;
}

img, video { max-width: 100%; }

.wrap {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 16px 24px;
  padding-bottom: calc(24px + env(safe-area-inset-bottom, 0px));
}

a { color: var(--accent-a); }

a:focus-visible, button:focus-visible {
  outline: 2px solid var(--accent-a);
  outline-offset: 2px;
}

.back, .fs, .group-card { touch-action: manipulation; }

/* home masthead */
.masthead { margin: 6px 0 18px; }
.masthead h1 {
  margin: 0 0 6px;
  font-size: 30px;
  line-height: 1.25;
  overflow-wrap: anywhere;
}
.masthead .sub { margin: 0; color: var(--muted); font-size: 15px; }
.masthead .note { margin: 8px 0 0; color: #7f8a99; font-size: 13px;
  line-height: 1.5; border-left: 2px solid #2b3542; padding-left: 10px; }

/* group page header */
.topnav { margin: 0 0 14px; }
.back {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 48px;
  padding: 0 18px;
  border: 1px solid var(--line);
  border-radius: 24px;
  font-size: 15px;
  letter-spacing: 1px;
  text-decoration: none;
}
.page-head { margin: 6px 0 20px; }
.page-head h1 { margin: 0 0 6px; font-size: 26px; line-height: 1.3; }
.page-head .sub { margin: 0 0 10px; color: var(--muted); font-size: 15px; }
.page-head .intro { margin: 0; color: var(--muted); overflow-wrap: anywhere; }

/* responsive grid: 1 column by default, 2 from 720px, 3 from 1100px */
.grid { display: grid; grid-template-columns: 1fr; gap: 16px; }
@media (min-width: 720px) {
  .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (min-width: 1100px) {
  .grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}

/* home: group cards */
.group-card {
  display: flex;
  align-items: center;
  gap: 14px;
  min-height: 88px;
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: var(--panel);
  color: var(--text);
  text-decoration: none;
}
.badge {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: var(--accent-a);
  color: #001016;
  font-size: 26px;
  font-weight: 700;
}
.group-card:nth-child(2n) .badge { background: var(--accent-b); color: #1A1200; }
.group-info { flex: 1 1 auto; min-width: 0; }
.group-title { display: block; font-size: 17px; font-weight: 600; }
.group-sub { display: block; margin-top: 2px; color: var(--muted); font-size: 13px; }
.count {
  flex: 0 0 auto;
  min-width: 36px;
  padding: 4px 10px;
  border: 1px solid var(--line);
  border-radius: 18px;
  color: var(--muted);
  font-size: 14px;
  text-align: center;
}

/* group page: clip cards */
.clip-card {
  border: 1px solid var(--line);
  border-radius: 14px;
  background: var(--panel);
  overflow: hidden;
}
.player { position: relative; background: #000000; }
.player video {
  display: block;
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  background: #000000;
}
.card.missing video { display: none; }
.card.missing .fs { display: none; }
.fs {
  position: absolute;
  right: 10px;
  bottom: 10px;
  width: 48px;
  height: 48px;
  padding: 0;
  border: 1px solid var(--line);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.55);
  color: var(--text);
  cursor: pointer;
}
.fs svg { display: block; }
.placeholder { display: none; }
.card.missing .placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  aspect-ratio: 16 / 9;
  padding: 18px;
  text-align: center;
  overflow-wrap: anywhere;
}
.placeholder-label {
  margin: 0;
  color: var(--muted);
  font-size: 11px;
  letter-spacing: 2px;
}
.placeholder-note { margin: 0; font-size: 14px; }
.card.missing .placeholder { cursor: pointer; }
.playbtn {
  position: absolute; inset: 0; margin: auto;
  width: 74px; height: 74px; border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.34);
  background: rgba(0,0,0,0.46);
  color: #fff; font-size: 26px; line-height: 1;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; z-index: 3;
}
.playbtn[hidden] { display: none; }
.playbtn span { transform: translateX(3px); }
.clip-text { padding: 12px 14px 16px; overflow-wrap: anywhere; }
.clip-text h3 { margin: 0 0 4px; font-size: 16px; line-height: 1.4; }
.clip-text p { margin: 0; color: var(--muted); font-size: 14px; }

/* footer */
.site-footer {  margin-top: 26px;
  padding-top: 16px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 13px;
}
.site-footer p { margin: 0; }

/* one-tap play-all (in-app browsers may block autoplay) */
.playall {
  display: block;
  width: 100%;
  min-height: 48px;
  margin: 4px 0 18px;
  padding: 12px 16px;
  font: inherit;
  font-size: 15px;
  letter-spacing: 1px;
  color: #0b0d10;
  background: var(--accent-a);
  border: 0;
  border-radius: 12px;
  cursor: pointer;
}
.playall[hidden] { display: none; }

/* 首页 hero：交互实验台 */
.hero {
  display: block;
  margin: 0 0 22px;
  padding: 26px 24px 22px;
  border: 1px solid var(--accent-a);
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(53,199,216,0.10), rgba(53,199,216,0.02));
  text-decoration: none;
  color: var(--text);
}
.hero-kicker {
  display: inline-block; margin-bottom: 8px; padding: 2px 9px;
  border-radius: 999px; background: var(--accent-a); color: #08111a;
  font-size: 12.5px; font-weight: 700; letter-spacing: .04em;
}
.hero-title { display: block; font-size: 27px; font-weight: 800; }
.hero-sub { display: block; margin-top: 8px; color: var(--muted);
  font-size: 14.5px; line-height: 1.6; }
.hero-cta { display: inline-block; margin-top: 16px; color: var(--accent-a);
  font-size: 16px; font-weight: 700; }

/* 交互实验台入口卡片 */
.labcard { border-color: var(--accent-a); }
.labcard .badge { background: var(--accent-a); color: #08111a; }
.labcard .count { color: var(--accent-a); font-size: 20px; }
.playall.done { background: #2a323d; color: var(--text); }
.fallback { margin: -8px 0 16px; color: #7f8a99; font-size: 12.5px;
  line-height: 1.5; }
"""


def esc(value) -> str:
    """HTML-escape any catalog-derived value before it enters markup."""
    return html.escape(str(value), quote=True)


def safe_code(code) -> str:
    """Turn a group code into a filesystem-safe page suffix."""
    text = str(code).strip()
    cleaned = "".join(
        ch if ch.isascii() and (ch.isalnum() or ch in "-_") else "-"
        for ch in text
    )
    return cleaned or "x"


def page(title: str, body: str, script: str = "") -> str:
    script_html = ("\n" + script + "\n") if script else "\n"
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
{VIEWPORT_TAG}
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#000000">
<meta name="robots" content="noindex, nofollow">
<title>{esc(title)}</title>
<link rel="icon" href="favicon.png" type="image/png">
<link rel="stylesheet" href="style.css">
</head>
<body>
{body}
{script_html}</body>
</html>
"""


def footer_html(project) -> str:
    return (
        '<footer class="site-footer">'
        "<p>" + esc(project) + " &middot; CUPT 2027 Problem 5</p>"
        "</footer>"
    )


def build_index(catalog: dict) -> str:
    project = str(catalog.get("project", ""))
    cards = []
    # 交互实验台放在最前面
    cards.append(
        '<a class="card group-card labcard" href="lab.html">'
        '<span class="badge" aria-hidden="true">&#9881;</span>'
        '<span class="group-info">'
        '<span class="group-title">交互实验台（可拖动旋转）</span>'
        '<span class="group-sub">拉滑块改 d、L、l 和初角，频率比与轨迹同步变</span>'
        '</span>'
        '<span class="count">&rarr;</span>'
        '</a>'
    )
    for group in catalog.get("groups", []):
        code = str(group.get("code", ""))
        code_file = safe_code(code)
        n_clips = len(group.get("clips", []))
        cards.append(
            f'<a class="card group-card" href="g-{esc(code_file)}.html">'
            f'<span class="badge" aria-hidden="true">{esc(code)}</span>'
            f'<span class="group-info">'
            f'<span class="group-title">{esc(group.get("title", ""))}</span>'
            f'<span class="group-sub">{esc(group.get("subtitle", ""))}</span>'
            f'</span>'
            f'<span class="count">{n_clips}</span>'
            f'</a>'
        )
    parts = [
        '<main class="wrap">',
        '<header class="masthead">',
        f'<h1>{esc(project)}</h1>',
        f'<p class="sub">{esc(catalog.get("subtitle", ""))}</p>',
        '<p class="note">画面与曲线都是报告 4.1 节给定输入下的条件设计值，'
        '不是实测结果；实测数据待补。</p>',
        '</header>',
        '<a class="hero" href="lab.html">',
        '<span class="hero-kicker">先玩这个</span>',
        '<span class="hero-title">交互实验台</span>',
        '<span class="hero-sub">拖动旋转三维装置，拉滑块改 d、L、l、'
        '初角和阻尼；频率比、两个周期、公共周期、两条上绳张力实时跟着变，'
        '球心轨迹当场画出来。</span>',
        '<span class="hero-cta">开始操作 →</span>',
        '</a>',
        '<nav class="grid groups">',
        "\n".join(cards),
        '</nav>',
        footer_html(project),
        '</main>',
    ]
    return page(project, "\n".join(parts) + "\n")


def clip_card_html(clip: dict) -> str:
    cid = quote(str(clip.get("id", "")))
    src = esc("video/" + cid + ".mp4")
    poster = esc("video/" + cid + ".jpg")
    title = esc(clip.get("title", ""))
    note = esc(clip.get("note", ""))
    return f'''<article class="card clip-card">
  <div class="player">
    <video poster="{poster}" muted loop controls playsinline webkit-playsinline x5-playsinline preload="none" data-src="{src}" aria-label="{title}"></video>
    <button class="playbtn" type="button" aria-label="Play" hidden><span aria-hidden="true">▶</span></button>
    <div class="placeholder">
      <p class="placeholder-label">MEDIA NOT FOUND</p>
      <p class="placeholder-note">{note}</p>
    </div>
  </div>
  <div class="clip-text">
    <h3>{title}</h3>
    <p>{note}</p>
  </div>
</article>'''


def build_group(catalog: dict, group: dict) -> str:
    project = str(catalog.get("project", ""))
    title = str(group.get("title", ""))
    clip_cards = [clip_card_html(clip) for clip in group.get("clips", [])]
    parts = [
        '<main class="wrap">',
        '<nav class="topnav">',
        '<a class="back" href="index.html">&#8592; HOME</a>',
        '</nav>',
        '<header class="page-head">',
        f'<h1>{esc(title)}</h1>',
        f'<p class="sub">{esc(group.get("subtitle", ""))}</p>',
        f'<p class="intro">{esc(group.get("intro", ""))}</p>',
        ('<button class="playall" id="playall" type="button" hidden>'
         'TAP TO PLAY ALL / \u5168\u90e8\u64ad\u653e</button>'),
        ('<p class="fallback">画面不动就点上面的按钮；仍不行，点微信右上角 '
         '\u00b7\u00b7\u00b7 \u7528\u6d4f\u89c8\u5668\u6253\u5f00\u3002</p>'),
        '</header>',
        '<section class="grid clips">',
        "\n".join(clip_cards),
        '</section>',
        footer_html(project),
        '</main>',
    ]
    return page(title + " - " + project, "\n".join(parts) + "\n", script=PAGE_JS)


def write_page(path: pathlib.Path, text: str) -> int:
    data = text.encode("utf-8")
    path.write_bytes(data)
    print(f"{path.name}  {len(data)} bytes")
    return 1


def main() -> int:
    try:
        catalog_text = CATALOG_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        print("cannot read catalog.json next to build_site.py: " + str(exc))
        return 1
    try:
        catalog = json.loads(catalog_text)
    except ValueError as exc:
        print("catalog.json is not valid JSON: " + str(exc))
        return 1

    groups = catalog.get("groups", [])
    n_clips_total = 0
    written = 0

    written += write_page(SCRIPT_DIR / "index.html", build_index(catalog))
    for group in groups:
        n_clips_total += len(group.get("clips", []))
        code = safe_code(group.get("code", ""))
        written += write_page(
            SCRIPT_DIR / ("g-" + code + ".html"), build_group(catalog, group)
        )
    written += write_page(SCRIPT_DIR / "style.css", PAGE_CSS)

    print(f"done: {written} files, {len(groups)} groups, {n_clips_total} clips")
    return 0


if __name__ == "__main__":
    sys.exit(main())
