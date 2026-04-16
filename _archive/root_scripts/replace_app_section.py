import re

with open('docs/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Strip out the old AD section HTML
old_html_regex = r'<div class="app-shots-grid">.*?</div>\s*</div>\s*</section>'
new_html = '''
    <div class="app-showcase-modern c r">
      <!-- Anti-gravity canvas as background -->
      <canvas id="ag-canvas" class="ag-canvas"></canvas>
      
      <div class="app-sc-content">
          <div class="app-sc-left">
            <div class="app-sc-item active" data-target="img-dash">
              <div class="app-sc-icon"><i data-lucide="layout-dashboard"></i></div>
              <h3 class="app-shot-title">Control Dashboard</h3>
              <p class="app-shot-desc">Live weather, route history, and rapid access to MotoMap tools directly from one screen.</p>
            </div>

            <div class="app-sc-item" data-target="img-map">
              <div class="app-sc-icon"><i data-lucide="map"></i></div>
              <h3 class="app-shot-title">Route Navigation</h3>
              <p class="app-shot-desc">Uncluttered layer rendering with live traffic and hazard overlays for perfect cornering.</p>
            </div>

            <div class="app-sc-item" data-target="img-garage">
              <div class="app-sc-icon"><i data-lucide="tool"></i></div>
              <h3 class="app-shot-title">Digital Garage</h3>
              <p class="app-shot-desc">Adjust cc, weight, torque, and tires to alter algorithm outputs specifically for your bike.</p>
            </div>

            <div class="app-sc-item" data-target="img-comm">
              <div class="app-sc-icon"><i data-lucide="users"></i></div>
              <h3 class="app-shot-title">Rider Communities</h3>
              <p class="app-shot-desc">Coordinate group rides and track real-time club telemetry with your riding crew.</p>
            </div>
          </div>
          
          <div class="app-sc-right">
            <div class="app-phone-frame">
              <div class="app-phone-glare"></div>
              <img src="assets/app_mockups/dashboard_masked.png" id="img-dash" class="app-sc-img active" loading="lazy" />
              <img src="assets/app_mockups/map_navigation_masked.png" id="img-map" class="app-sc-img" loading="lazy" />
              <img src="assets/app_mockups/garage_masked.png" id="img-garage" class="app-sc-img" loading="lazy" />
              <img src="assets/app_mockups/communities_masked.png" id="img-comm" class="app-sc-img" loading="lazy" />
            </div>
          </div>
      </div>
    </div>
  </div>
</section>
'''

text = re.sub(old_html_regex, new_html.strip(), text, flags=re.DOTALL)

# 2. Add the CSS for modern showcase
css_block = '''
/* Modern App Showcase */
.app-showcase-modern { position: relative; margin-top: 64px; border-radius: 40px; background: rgba(255,255,255,0.015); border: 1px solid rgba(255,255,255,0.04); overflow: hidden; padding: 40px 0; }
.ag-canvas { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; z-index: 0; opacity: 0.6; }
.app-sc-content { display: flex; flex-direction: column; gap: 48px; position: relative; z-index: 10; max-width: 1000px; margin: 0 auto; padding: 0 32px; align-items: center;}
@media(min-width: 900px){ .app-sc-content{ flex-direction: row; justify-content: space-between; } }
.app-sc-left { flex: 1; display: flex; flex-direction: column; gap: 16px; }
.app-sc-item { padding: 24px 32px; border-radius: 28px; cursor: pointer; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); border: 1px solid transparent; background: transparent; opacity: 0.5; }
.app-sc-item:hover { opacity: 0.8; background: rgba(255,255,255,0.03); }
.app-sc-item.active { opacity: 1; background: rgba(255,255,255,0.05); border-color: rgba(250,204,21,0.2); box-shadow: 0 12px 32px rgba(0,0,0,0.2); transform: translateX(8px); }
.app-sc-icon { width: 44px; height: 44px; border-radius: 12px; background: rgba(250,204,21,0.1); display: flex; align-items: center; justify-content: center; color: var(--accent); margin-bottom: 16px; transition: transform 0.3s; }
.app-sc-item.active .app-sc-icon { background: var(--accent); color: var(--bg); transform: scale(1.1); box-shadow: 0 4px 16px rgba(250,204,21,0.4); }
.app-sc-item .app-shot-title { margin-bottom: 8px;font-size:20px; }
.app-sc-item .app-shot-desc { margin:0; font-size:15px; }

.app-sc-right { flex: 1; display: flex; justify-content: center; position: relative; perspective: 1000px; }
.app-phone-frame { position: relative; width: 300px; height: 620px; background: #000; border-radius: 52px; padding: 12px; box-shadow: 0 32px 84px rgba(0,0,0,0.6), inset 0 0 0 2px rgba(255,255,255,0.1); transform-style: preserve-3d; transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1); }
.app-sc-right:hover .app-phone-frame { transform: translateY(-10px) rotateY(-5deg) rotateX(2deg); }
.app-phone-glare { position: absolute; inset: 0; border-radius: 52px; background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, transparent 40%, transparent 100%); pointer-events: none; z-index: 5; }
.app-sc-img { position: absolute; top: 12px; left: 12px; width: calc(100% - 24px); height: calc(100% - 24px); border-radius: 40px; object-fit: cover; opacity: 0; transform: scale(0.95) translateY(20px); transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1); pointer-events: none; }
.app-sc-img.active { opacity: 1; transform: scale(1) translateY(0); pointer-events: auto; }
'''

text = text.replace('</style>', css_block + '\n</style>')

# 3. Clean previous glow particle script
text = re.sub(r'// ── App Card Glow & Particle Effect ──[\s\S]*?\}\);\s*\}\);', '', text)

# 4. Insert modern JS logic (tab switcher + anti-gravity particles)
js_block = '''
// ── App Modern Tab Switcher ──
const appItems = document.querySelectorAll('.app-sc-item');
const appImgs = document.querySelectorAll('.app-sc-img');

appItems.forEach(item => {
  item.addEventListener('click', () => {
    // Reset all
    appItems.forEach(i => i.classList.remove('active'));
    appImgs.forEach(img => img.classList.remove('active'));
    
    // Activate target
    item.classList.add('active');
    const targetId = item.getAttribute('data-target');
    const targetImg = document.getElementById(targetId);
    if(targetImg) targetImg.classList.add('active');
  });
});

// ── Anti-Gravity Particle Physics (Google style) ──
const agCanvas = document.getElementById('ag-canvas');
if (agCanvas) {
  const ctx = agCanvas.getContext('2d');
  let ps = [];
  let w = agCanvas.width = agCanvas.offsetWidth;
  let h = agCanvas.height = agCanvas.offsetHeight;
  let mx = w/2, my = h/2, mActive = false;

  window.addEventListener('resize', () => {
    w = agCanvas.width = agCanvas.offsetWidth;
    h = agCanvas.height = agCanvas.offsetHeight;
  });

  agCanvas.addEventListener('mousemove', e => {
    const rect = agCanvas.getBoundingClientRect();
    mx = e.clientX - rect.left;
    my = e.clientY - rect.top;
    mActive = true;
  });
  agCanvas.addEventListener('mouseleave', () => mActive = false);

  // Initialize anti-gravity orbs/shapes
  const colors = ['#FACC15', '#F59E0B', '#86EFAC', '#E879F9'];
  for(let i=0; i<35; i++) {
    ps.push({
      x: Math.random()*w, y: Math.random()*h,
      vx: (Math.random() - 0.5) * 1.5,
      vy: (Math.random() - 0.5) * 1.5,
      r: Math.random() * 8 + 3,
      c: colors[Math.floor(Math.random() * colors.length)]
    });
  }

  function loop() {
    ctx.clearRect(0,0,w,h);
    
    for(let i=0; i<ps.length; i++) {
      let p = ps[i];
      p.x += p.vx;
      p.y += p.vy;

      // Bounce off walls
      if(p.x < p.r || p.x > w - p.r) p.vx *= -1;
      if(p.y < p.r || p.y > h - p.r) p.vy *= -1;

      // Mouse repulsion (anti-gravity repulsion field)
      if (mActive) {
        let dx = p.x - mx;
        let dy = p.y - my;
        let dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < 120) {
          let force = (120 - dist) / 120;
          p.vx += (dx / dist) * force * 0.4;
          p.vy += (dy / dist) * force * 0.4;
        }
      }
      
      // Dampen velocity limits
      let speed = Math.sqrt(p.vx*p.vx + p.vy*p.vy);
      if (speed > 2.5) {
        p.vx = (p.vx/speed) * 2.5;
        p.vy = (p.vy/speed) * 2.5;
      }
      if (speed < 0.2) {
          p.vx *= 1.05;
          p.vy *= 1.05;
      }

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
      ctx.fillStyle = p.c;
      ctx.globalAlpha = 0.5;
      ctx.fill();
    }
    requestAnimationFrame(loop);
  }
  loop();
}
'''

text = text.replace('</body>', '<script>\n' + js_block + '\n</script>\n</body>')

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Modern Showcase and Anti-Gravity physics executed.")
