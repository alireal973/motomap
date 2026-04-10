const fs = require('fs');
const path = require('path');
const p = 'C:/Users/lenovo/Desktop/motomap/docs/superpowers/plans/2026-04-04-mobile-ui-redesign.md';
const content = fs.readFileSync(p, 'utf8');

const codeBlocks = [...content.matchAll(/```typescript\n([\s\S]*?)\n```/g)];

for (const m of codeBlocks) {
  const code = m[1];
  const firstLine = code.split('\n')[0];
  if (firstLine.startsWith('// app/mobile/')) {
    const filename = firstLine.replace('// app/mobile/', '').trim();
    const dest = path.join('app/mobile', filename);
    const dir = path.dirname(dest);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(dest, code);
    console.log('Wrote', dest);
  }
}
