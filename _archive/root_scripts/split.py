import re

with open('docs/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

def extr(name, h):
    pattern = r'<!-- ============ ' + name + r' ============ -->[\s\S]*?(?=<!-- ============)'
    m = re.search(pattern, h)
    if m:
        sec = m.group(0)
        h = h.replace(sec, '')
        return sec, h
    return '', h

s1, html = extr('FEATURES: 5-LAYER MAP SHOWCASE', html)
s2, html = extr('APP PREVIEW', html)
s3, html = extr('LIVE LOCAL MAP', html)
s4, html = extr('LIVE LAB', html)

# Remove SVG hero route
hero = re.search(r'<svg class="hero-route[\s\S]*?</svg>', html)
if hero:
    html = html.replace(hero.group(0), '')

# Write the maps section string out
with open('extracted.html', 'w', encoding='utf-8') as f:
    f.write(s1 + '\n' + s2 + '\n' + s3 + '\n' + s4)

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Extraction sizes: {len(s1)}, {len(s2)}, {len(s3)}, {len(s4)}")
