import re

with open('docs/maps.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace all occurrences of old mockup PNGs in maps.html
# Wait, I don't know the file names. Let me read maps.html
import re
match = re.search(r'(<section class="sec sec-alt shots" id="preview">.*?</section>)', text, re.DOTALL)
if match:
    print(match.group(1))

