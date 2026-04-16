with open('docs/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Since we injected <script> and </script> directly inside an existing script block, let's clean it.
import re

# look exactly for the block we injected
pattern = r'<script>\s*(document\.querySelectorAll\(\'\.app-shot-card\'\).*?)\s*</script>\s*// ── Animated count-up ──'

def replace(m):
    return m.group(1) + '\n// ── Animated count-up ──'

text = re.sub(pattern, replace, text, flags=re.DOTALL)

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("Removed nested <script> tags!")
