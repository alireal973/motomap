import re

with open('docs/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Update the hero button 'btn-p' from standard orange back to cyber and green styles
text = text.replace('background:linear-gradient(135deg,#FDE047,var(--accent) 50%,#F59E0B)', 'background:linear-gradient(135deg,#86EFAC,var(--accent) 50%,#00F0FF)')

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated hero button gradient")
