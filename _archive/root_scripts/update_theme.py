import re

with open('docs/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Update the core background colors to deep indigo/black
text = re.sub(r'--bg:#130B1A;', '--bg:#09090E;', text)
text = re.sub(r'--bg2:#1A0F24;', '--bg2:#111118;', text)
text = re.sub(r'--bg3:#241530;', '--bg3:#181822;', text)

# Keep accent yellow/gold as it's the core MotoMap color, but maybe adjust the glow/warm slightly to match indigo
text = re.sub(r'rgba\(19,11,26,([^)]+)\)', r'rgba(9,9,14,\1)', text) # Update nav backgrounds

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Theme updated to dark indigo/black")
