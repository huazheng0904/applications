#!/usr/bin/env python3
"""Build the application-plan site.

Edit the data in schools.py, then run:  python3 build.py
Every school gets its own page; the overview (index.html) and the U.S.
comparison page (us.html) are generated from the same data.
"""
from html import escape as e
from schools import CANADA, EARLY, US, TOOLS, TIMELINE, NEXT_UP, REUSE

ALL = CANADA + EARLY + US
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">')

CHECK_JS = """<script>
(function () {
  var KEY = 'check-' + location.pathname;
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (x) {}
  document.querySelectorAll('ul.todo input').forEach(function (box) {
    box.checked = !!saved[box.id];
    box.parentElement.classList.toggle('done', box.checked);
    box.addEventListener('change', function () {
      saved[box.id] = box.checked;
      box.parentElement.classList.toggle('done', box.checked);
      try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch (x) {}
    });
  });
})();
</script>"""


def head(title, desc):
    return (f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{e(title)}</title>\n<meta name="description" content="{e(desc)}">\n'
            f'{FONTS}\n<link rel="stylesheet" href="style.css">\n</head>\n<body>\n<div class="wrap">\n')


def topbar(current):
    links = [('index.html', 'Overview'), ('index.html#canada', 'Canada'), ('us.html', 'U.S. schools'), ('euclid.html', 'Euclid prep')]
    items = ''.join(f'<a href="{h}"' + (' aria-current="page"' if h == current else '') + f'>{t}</a>' for h, t in links)
    return (f'<header class="topbar"><a class="brand" href="index.html">Fall 2027 applications</a>'
            f'<nav class="topnav" aria-label="Site">{items}</nav></header>\n')


def table(t):
    keys = set(t.get('key', []))
    out = '<div class="tablewrap"><table>\n<thead><tr>' + ''.join(f'<th>{e(h)}</th>' for h in t['head']) + '</tr></thead>\n<tbody>\n'
    for i, row in enumerate(t['rows']):
        cls = ' class="key"' if i in keys else ''
        cells = ''.join((f'<td class="when">{e(c)}</td>' if j == 0 and t.get('first_bold') else f'<td>{e(c)}</td>') for j, c in enumerate(row))
        out += f'<tr{cls}>{cells}</tr>\n'
    return out + '</tbody></table></div>\n'


def section(s, slug, n):
    out = f'<section class="block"><h2>{e(s["h"])}</h2>\n'
    for p in s.get('p', []):
        out += f'<p>{e(p)}</p>\n'
    if 'table' in s:
        out += table(s['table'])
    if 'list' in s:
        out += '<ul class="plain">' + ''.join(f'<li>{e(x)}</li>' for x in s['list']) + '</ul>\n'
    if 'check' in s:
        out += '<ul class="todo">' + ''.join(
            f'<li><input type="checkbox" id="{slug}-{n}-{i}"><label for="{slug}-{n}-{i}">{e(x)}</label></li>'
            for i, x in enumerate(s['check'])) + '</ul>\n<p class="note">Ticks are saved in this browser only.</p>\n'
    if 'warn' in s:
        out += f'<p class="warn">{e(s["warn"])}</p>\n'
    if 'note' in s:
        out += f'<p class="note">{e(s["note"])}</p>\n'
    return out + '</section>\n'


def more(current):
    def lst(group, cls):
        return f'<ul class="{cls}">' + ''.join(
            f'<li><a href="{s["slug"]}.html"' + (' aria-current="page"' if s['slug'] == current else '') + f'>{e(s["short"])}</a></li>'
            for group_item in [group] for s in group_item) + '</ul>'
    return ('<nav class="more" aria-label="All schools">'
            f'<div><h2>Canada</h2>{lst(CANADA, "ca")}</div>'
            f'<div><h2>United States</h2>{lst(EARLY + US, "us")}</div></nav>\n')


def pager(idx):
    prev_s = ALL[idx - 1] if idx > 0 else None
    next_s = ALL[idx + 1] if idx < len(ALL) - 1 else None
    left = f'<a href="{prev_s["slug"]}.html">Previous: {e(prev_s["short"])}</a>' if prev_s else '<span></span>'
    right = f'<a href="{next_s["slug"]}.html">Next: {e(next_s["short"])}</a>' if next_s else '<span></span>'
    return f'<div class="pager">{left}{right}</div>\n'


def sources(src):
    return ('<section class="sources"><p>Sources, checked Nov 1, 2026. Confirm in each applicant portal before submitting.</p><ul>'
            + ''.join(f'<li><a href="{e(u)}">{e(t)}</a></li>' for t, u in src) + '</ul></section>\n')


def school_page(s, idx):
    is_ca = s in CANADA
    country = 'Canada' if is_ca else 'United States'
    cls = 'ca-page' if is_ca else 'us-page'
    out = head(f'{s["name"]} plan', s['summary'])
    out += topbar('index.html#canada' if is_ca else 'us.html')
    out += f'<main class="{cls}">\n'
    crumb_mid = '<a href="index.html#canada">Canada</a>' if is_ca else '<a href="us.html">U.S. schools</a>'
    out += f'<p class="crumbs"><a href="index.html">Overview</a> / {crumb_mid} / {e(s["short"])}</p>\n'
    out += f'<div class="school-hero"><span class="country">{country}</span><h1>{e(s["name"])}</h1><p class="summary">{e(s["summary"])}</p></div>\n'
    out += '<dl class="facts">' + ''.join(
        f'<div><dt>{e(k)}</dt><dd{" class=\"big\"" if i == 0 else ""}>{e(v)}</dd></div>' for i, (k, v) in enumerate(s['facts'])) + '</dl>\n'
    for n, sec in enumerate(s['sections']):
        out += section(sec, s['slug'], n)
    out += sources(s['sources'])
    out += more(s['slug']) + pager(idx)
    out += '</main>\n<footer class="site"><p>Built from build.py. Dates checked Nov 1, 2026.</p></footer>\n</div>\n' + CHECK_JS + '\n</body>\n</html>\n'
    return out


def tool_page(t):
    out = head(t['name'], t['summary']) + topbar(f'{t["slug"]}.html') + '<main class="tool-page">\n'
    out += f'<p class="crumbs"><a href="index.html">Overview</a> / {e(t["short"])}</p>\n'
    out += f'<div class="school-hero"><span class="country">Tool</span><h1>{e(t["name"])}</h1><p class="summary">{e(t["summary"])}</p></div>\n'
    out += '<dl class="facts">' + ''.join(
        f'<div><dt>{e(k)}</dt><dd{" class=\"big\"" if i == 0 else ""}>{e(v)}</dd></div>' for i, (k, v) in enumerate(t['facts'])) + '</dl>\n'
    for n, sec in enumerate(t['sections']):
        out += section(sec, t['slug'], n)
    out += sources(t['sources']) + more('') + '</main>\n<footer class="site"><p>Built from build.py.</p></footer>\n</div>\n' + CHECK_JS + '\n</body>\n</html>\n'
    return out


def early_table():
    out = '<div class="tablewrap"><table class="us-table early-table"><thead><tr><th>Plan</th><th>School</th><th>Submitted</th><th>Decision</th><th>Status</th></tr></thead><tbody>\n'
    for s in EARLY:
        out += (f'<tr><td class="d">{e(s["plan"])}</td><td><a href="{s["slug"]}.html">{e(s["short"])}</a></td><td>{e(s["submitted"])}</td>'
                f'<td>{e(s["decision"])}</td><td><span class="status">{e(s["status"])}</span></td></tr>\n')
    return out + '</tbody></table></div>\n'


def us_page():
    out = head('U.S. schools', 'Deadlines, testing and essays for every U.S. school, with links to each school page.')
    out += topbar('us.html') + '<main class="us-page">\n<p class="crumbs"><a href="index.html">Overview</a> / U.S. schools</p>\n'
    out += ('<div class="school-hero"><span class="country">United States</span><h1>U.S. schools</h1>'
            f'<p class="summary">{len(EARLY)} early applications already in, plus {len(US)} Regular Decision schools: UC Berkeley is due Nov 30, the rest Jan 1–5. Each school has its own page.</p></div>\n')
    out += '<section class="block"><h2>Submitted early</h2>' + early_table() + '</section>\n'
    out += '<section class="block"><h2>Regular Decision</h2><div class="tablewrap"><table class="us-table"><thead><tr><th>Deadline</th><th>School</th><th>Testing</th><th>Supplements</th></tr></thead><tbody>\n'
    for s in US:
        early = ' class="early"' if s.get('early') else ''
        out += f'<tr{early}><td class="d">{e(s["deadline"])}</td><td><a href="{s["slug"]}.html">{e(s["short"])}</a></td><td>{e(s["testing"])}</td><td>{e(s["supp"])}</td></tr>\n'
    out += '</tbody></table></div></section>\n'
    out += section({'h': 'Write once, adapt everywhere', 'p': ['Most prompts ask for the same few stories. Write each one well once, then cut it to each school\'s limit.'],
                    'table': {'head': ['Core story', 'Where it is used'], 'rows': REUSE}}, 'us', 0)
    out += more('') + '</main>\n<footer class="site"><p>Built from build.py.</p></footer>\n</div>\n</body>\n</html>\n'
    return out


def index_page():
    out = head('Fall 2027 Applications', 'Deadlines, programs and plans for Fall 2027 university applications in Canada and the United States.')
    out += topbar('index.html') + '<main>\n'
    out += (f'<section class="hero"><h1>Fall 2027 applications</h1><p class="lede">{len(CANADA)} Canadian universities and {len(EARLY) + len(US)} in the U.S., {len(EARLY)} of them already submitted early. '
            'Every deadline from now to June on one line.</p></section>\n')
    out += '<p class="legend"><span class="tag ca">Canada</span> above the line <span class="tag us">U.S.</span> below</p>\n'
    out += ('<div class="river-wrap" role="img" aria-label="Timeline of application deadlines from November 2026 to June 2027, Canada above and U.S. below">'
            '<div class="river" id="river"><div class="channel"></div></div></div>\n'
            '<p class="river-note">Scroll sideways on a phone. The dark line marks today.</p>\n')
    out += '<div class="next"><h2>Next up</h2><ol id="next"></ol></div>\n'
    out += ('<section class="country-sec ca" id="canada" aria-labelledby="ca-h"><div class="country-head"><h2 id="ca-h">Canada</h2>'
            '<p>U of T and Waterloo share one OUAC application; McGill is separate. All three charge domestic tuition to Canadian citizens.</p></div>\n')
    for s in CANADA:
        out += (f'<article class="srow"><div><h3>{e(s["name"])}</h3><div class="route">{e(s["route"])}</div></div><dl>'
                + ''.join(f'<dt>{e(k)}</dt><dd>{e(v)}</dd>' for k, v in s['row'])
                + f'</dl><a class="go" href="{s["slug"]}.html">{e(s["short"])} plan</a></article>\n')
    out += '</section>\n'
    out += ('<section class="country-sec us" id="us" aria-labelledby="us-h"><div class="country-head"><h2 id="us-h">United States</h2>'
            f'<p>Columbia (ED) and Northeastern (EA) are in. Of the Regular Decision schools, UC Berkeley comes first on Nov 30; the other {len(US) - 1} are due Jan 1–5.</p></div>\n'
            '<h3 class="sub-h">Submitted early</h3>' + early_table() +
            '<h3 class="sub-h">Regular Decision</h3><div class="tablewrap"><table class="us-table"><thead><tr><th>Deadline</th><th>School</th><th>Testing</th><th>Applying to</th></tr></thead><tbody>\n')
    for s in US:
        early = ' class="early"' if s.get('early') else ''
        out += f'<tr{early}><td class="d">{e(s["deadline"])}</td><td><a href="{s["slug"]}.html">{e(s["short"])}</a></td><td>{e(s["testing"])}</td><td>{e(s["applying"])}</td></tr>\n'
    out += '</tbody></table></div></section>\n'
    for t in TOOLS:
        out += f'<aside class="tools"><div><h2>{e(t["name"])}</h2><p>{e(t["tagline"])}</p></div><a href="{t["slug"]}.html">Prep plan</a></aside>\n'
    out += '</main>\n<footer class="site"><p>Dates checked Nov 1, 2026 against each university\'s admissions pages. Confirm in each applicant portal before submitting.</p></footer>\n</div>\n'
    import json
    out += '<script>\nvar EVENTS = ' + json.dumps(TIMELINE) + ';\nvar NEXT = ' + json.dumps(NEXT_UP) + ';\n' + RIVER_JS + '</script>\n</body>\n</html>\n'
    return out


RIVER_JS = """(function () {
  var START = Date.UTC(2026, 10, 1), END = Date.UTC(2027, 6, 10);
  var MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var t = function (s) { return Date.parse(s + 'T12:00:00Z'); };
  var pct = function (ms) { return Math.max(0, Math.min(100, (ms - START) / (END - START) * 100)); };
  var fmt = function (s) { var p = s.split('-'); return MONTHS[+p[1] - 1] + ' ' + (+p[2]); };
  var river = document.getElementById('river');
  for (var i = 1; i < 9; i++) {
    var ms = Date.UTC(2026, 10 + i, 1), d = new Date(ms), m = document.createElement('div');
    m.className = 'month'; m.style.left = pct(ms) + '%';
    m.textContent = MONTHS[d.getUTCMonth()] + (d.getUTCMonth() === 0 ? ' ' + d.getUTCFullYear() : '');
    river.appendChild(m);
  }
  EVENTS.forEach(function (ev) {
    var el = document.createElement('div');
    el.className = 'pin ' + ev.c;
    el.style.setProperty('--d', (ev.lvl === 3 ? 172 : ev.lvl === 1 ? 118 : 62) + 'px');
    el.style.left = pct(t(ev.d)) + '%';
    el.innerHTML = '<span class="dot"></span><div class="lbl"><b></b><span></span></div>';
    el.querySelector('b').textContent = fmt(ev.d) + ', ' + ev.t;
    el.querySelector('.lbl span').textContent = ev.s;
    river.appendChild(el);
  });
  var now = Date.now();
  if (now > START && now < END) {
    var td = document.createElement('div'); td.className = 'today'; td.style.left = pct(now) + '%';
    td.innerHTML = '<span>Today</span>'; river.appendChild(td);
  }
  var list = document.getElementById('next'), shown = 0;
  NEXT.forEach(function (n) {
    var due = t(n.d); if (due < now - 864e5 || shown >= 5) return; shown++;
    var days = Math.ceil((due - now) / 864e5);
    var li = document.createElement('li');
    var when = document.createElement('div'); when.className = 'when'; when.textContent = fmt(n.d);
    var inn = document.createElement('span'); inn.className = 'in'; inn.textContent = days <= 0 ? 'today' : 'in ' + days + ' day' + (days === 1 ? '' : 's');
    when.appendChild(inn);
    var what = document.createElement('div');
    var tag = document.createElement('span'); tag.className = 'tag ' + n.c; tag.textContent = n.c === 'ca' ? 'Canada' : 'U.S.';
    what.appendChild(tag);
    var a = document.createElement(n.href ? 'a' : 'span'); if (n.href) a.href = n.href; a.textContent = n.t;
    what.appendChild(a);
    li.appendChild(when); li.appendChild(what); list.appendChild(li);
  });
  if (!shown) list.innerHTML = '<li><div class="when">Done</div><div>All listed deadlines have passed.</div></li>';
})();
"""

if __name__ == '__main__':
    pages = {'index.html': index_page(), 'us.html': us_page()}
    for i, s in enumerate(ALL):
        pages[f'{s["slug"]}.html'] = school_page(s, i)
    for tl in TOOLS:
        pages[f'{tl["slug"]}.html'] = tool_page(tl)
    for name, html in pages.items():
        with open(name, 'w') as f:
            f.write(html)
    print(f'Wrote {len(pages)} pages: ' + ', '.join(sorted(pages)))
