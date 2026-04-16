import re

with open('docs/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# First, let's remove any old App Card 3D Tilt Effect JS blocks entirely.
# They usually end after the cards.forEach block. Let's do a hard clean based on matching the comment.
text = re.sub(r'// ── App Card 3D Tilt Effect ──[\s\S]*?\}\);\s*\}\);', '', text)

# Now remove the block of old css inside style dealing with app-shot
text = re.sub(r'\.app-shots-grid\s*\{[\s\S]*?\.app-shot-desc\s*\{.*?\}', '', text)


css_add = '''
.app-shots-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 32px; align-items: start; margin-top: 56px; }
.app-shot-card { position: relative; display: flex; flex-direction: column; align-items: center; text-align: center; cursor: pointer; padding: 24px; border-radius: 36px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); overflow: hidden; transition: transform 0.3s ease, border-color 0.3s ease; }
.app-shot-card:hover { transform: translateY(-8px); border-color: rgba(250,204,21,0.3); }
.app-shot-card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; background: radial-gradient(circle 400px at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(250,204,21,0.1), transparent 40%); opacity: 0; transition: opacity 0.3s ease; z-index:0;}
.app-shot-card:hover::before { opacity: 1; }
.app-shot-bezels { position: relative; border-radius: 44px; padding: 8px; background: rgba(0,0,0,0.4); box-shadow: 0 14px 44px rgba(0,0,0,0.4), inset 0 1px 1px rgba(255,255,255,0.1); margin-bottom: 24px; z-index: 1;}
.app-shot-img { width: 100%; max-width: 280px; border-radius: 36px; border: 2px solid rgba(255,255,255,0.03); display: block; z-index: 2; position: relative;}
.app-shot-title { position: relative; font-size: 18px; color: var(--t, #fff); margin-bottom: 8px; font-weight: 600; z-index: 1;}
.app-shot-desc { position: relative; font-size: 14px; color: var(--t2, #a1a1aa); line-height: 1.6; z-index: 1;}
.app-particle { position: absolute; width: 4px; height: 4px; background: #FACC15; border-radius: 50%; pointer-events: none; z-index:0; filter: blur(1px); }
'''

# Put it before </style>
text = text.replace('</style>', css_add + '\n</style>')

js_add = '''
// ── App Card Glow & Particle Effect ──
document.querySelectorAll('.app-shot-card').forEach(card => {
  card.addEventListener('mousemove', e => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Set variables for the glow backdrop
    card.style.setProperty('--mouse-x', x + 'px');
    card.style.setProperty('--mouse-y', y + 'px');
    
    // Occasionally spawn a particle when moving
    if(Math.random() > 0.85) {
      let p = document.createElement('div');
      p.className = 'app-particle';
      p.style.left = x + 'px';
      p.style.top = y + 'px';
      card.appendChild(p);
      
      let animX = (Math.random() - 0.5) * 50;
      let animY = (Math.random() - 0.5) * 50 - 20; // Slight upward bias
      
      let anim = p.animate([
        { transform: 'translate(0,0) scale(1)', opacity: 0.8 },
        { transform: 	ranslate(px, px) scale(0), opacity: 0 }
      ], { duration: 800 + Math.random()*500, easing: 'ease-out' });
      
      anim.onfinish = () => p.remove();
    }
  });
});
'''

# Put it before closing script if we can, or just append it before '</body>'
text = text.replace('</body>', '<script>\n' + js_add + '\n</script>\n</body>')

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated animation on index")
