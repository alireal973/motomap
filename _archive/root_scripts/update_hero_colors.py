import re

with open('docs/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Update orb 2 and 3 colors to match the cyber/neon theme
text = re.sub(r'\.orb-2\{bottom:-5%;left:20%;width:400px;height:400px;background:radial-gradient\(circle,rgba\(232,121,249,\.08\),transparent 70%\)', '.orb-2{bottom:-5%;left:20%;width:400px;height:400px;background:radial-gradient(circle,rgba(134,239,172,.08),transparent 70%)', text)
text = re.sub(r'\.orb-3\{top:40%;left:-10%;width:350px;height:350px;background:radial-gradient\(circle,rgba\(192,132,252,\.06\),transparent 70%\)', '.orb-3{top:40%;left:-10%;width:350px;height:350px;background:radial-gradient(circle,rgba(0,240,255,.06),transparent 70%)', text)

# Also let's update some hero pink texts to the theme
text = text.replace('rgba(232,121,249,.15)', 'rgba(134,239,172,.2)') # cyan/green border for badge
text = text.replace('rgba(232,121,249,.05)', 'rgba(134,239,172,.08)') # background for badge
text = text.replace('color:var(--cyan)', 'color:var(--green)') # cyan text to green text
text = text.replace('box-shadow:0 0 8px var(--cyan)', 'box-shadow:0 0 8px var(--green)')
text = text.replace('background:var(--cyan)', 'background:var(--green)')
text = text.replace('#F0ABFC', '#86EFAC') # grad text ending in pink -> ending in green

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Hero circle and badge colors updated")
