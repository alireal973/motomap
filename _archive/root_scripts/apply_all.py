import re

with open('docs/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

ad_section = '''
<!-- ============ APP PREVIEW AD ============ -->
<section class="sec sec-alt shots" id="app">
  <div class="c">
    <div class="sec-h r"><div class="sec-e">Mobile App</div><h2 class="sec-t">Your <em class="em">Digital Twin</em> Command Center</h2><p class="sec-d">The complete routing intelligence system directly in your pocket. Control your ride styles, track live routing, manage your garage, and coordinate with communities.</p></div>
    
    <div class="app-shots-grid">
      
      <article class="app-shot-card r">
        <div class="app-shot-bezels">
          <img src="assets/app_mockups/dashboard_masked.png" alt="Dashboard" class="app-shot-img" loading="lazy"/>
        </div>
        <h3 class="app-shot-title">Control Dashboard</h3>
        <p class="app-shot-desc">Live weather, route history, and rapid access to MotoMap tools.</p>
      </article>

      <article class="app-shot-card r">
        <div class="app-shot-bezels">
          <img src="assets/app_mockups/map_navigation_masked.png" alt="Map Navigation" class="app-shot-img" loading="lazy"/>
        </div>
        <h3 class="app-shot-title">Route Navigation</h3>
        <p class="app-shot-desc">Uncluttered layer rendering with live traffic and hazard overlays.</p>
      </article>

      <article class="app-shot-card r">
        <div class="app-shot-bezels">
          <img src="assets/app_mockups/garage_masked.png" alt="Digital Garage" class="app-shot-img" loading="lazy"/>
        </div>
        <h3 class="app-shot-title">Digital Garage</h3>
        <p class="app-shot-desc">Adjust cc, weight, torque, and tires to alter algorithm outputs.</p>
      </article>

      <article class="app-shot-card r">
        <div class="app-shot-bezels">
          <img src="assets/app_mockups/communities_masked.png" alt="Communities" class="app-shot-img" loading="lazy"/>
        </div>
        <h3 class="app-shot-title">Rider Communities</h3>
        <p class="app-shot-desc">Coordinate group rides and track real-time club telemetry.</p>
      </article>
      
    </div>
  </div>
</section>
'''

# Inject HTML
if '<!-- ============ APP PREVIEW AD ============ -->' not in text:
    text = text.replace('<!-- ============ RIDER PERSONAS ============ -->', ad_section + '\n<!-- ============ RIDER PERSONAS ============ -->')

# Inject CSS exactly once
css_block = '''<style>
.app-shots-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 32px; align-items: start; margin-top: 56px; perspective: 1000px; }
.app-shot-card { display: flex; flex-direction: column; align-items: center; text-align: center; transition: transform 0.1s ease, box-shadow 0.3s ease; transform-style: preserve-3d; will-change: transform; cursor: pointer; }
.app-shot-bezels { border-radius: 44px; padding: 12px; background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.01)); box-shadow: 0 14px 44px rgba(0,0,0,0.4), inset 0 1px 1px rgba(255,255,255,0.1); margin-bottom: 24px; display: inline-block; transform: translateZ(50px); transition: transform 0.2s ease, box-shadow 0.2s ease; position: relative; }
.app-shot-bezels::after { content: ''; position: absolute; inset: 0; border-radius: 44px; box-shadow: 0 0 20px rgba(250, 204, 21, 0); transition: box-shadow 0.3s ease; pointer-events: none;}
.app-shot-img { width: 100%; max-width: 280px; border-radius: 36px; border: 2px solid rgba(255,255,255,0.03); display: block; transform: translateZ(20px); transition: transform 0.2s ease; pointer-events: none; }
.app-shot-title { font-size: 18px; color: var(--t, #fff); margin-bottom: 8px; transform: translateZ(30px); transition: transform 0.2s ease, color 0.3s ease; margin-top: 10px; }
.app-shot-desc { font-size: 14px; color: var(--t2, #a1a1aa); line-height: 1.6; transform: translateZ(10px); }
</style>'''

text = text.replace('</head>', css_block + '\n</head>')

# Inject JS exactly once
js_block = '''
// ── App Card 3D Tilt Effect ──
document.querySelectorAll('.app-shot-card').forEach(card => {
  card.addEventListener('mousemove', e => {
    const r = card.getBoundingClientRect();
    const cx = (e.clientX - r.left) / r.width - 0.5;
    const cy = (e.clientY - r.top) / r.height - 0.5;
    const tiltX = cy * -20;
    const tiltY = cx * 20;
    card.style.transform = perspective(1000px) rotateX(deg) rotateY(deg) scale3d(1.05, 1.05, 1.05);
    
    const bezels = card.querySelector('.app-shot-bezels');
    if (bezels) {
      bezels.style.boxShadow = '0 34px 64px rgba(0,0,0,0.6), inset 0 1px 1px rgba(255,255,255,0.2)';
      bezels.style.transform = 'translateZ(60px)';
    }
    const img = card.querySelector('.app-shot-img');
    if(img) img.style.transform = 'translateZ(40px)';
    const title = card.querySelector('.app-shot-title');
    if(title) {
        title.style.transform = 'translateZ(50px)';
        title.style.color = 'var(--accent, #FACC15)';
    }
  });
  
  card.addEventListener('mouseleave', () => {
    card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
    const bezels = card.querySelector('.app-shot-bezels');
    if (bezels) {
      bezels.style.boxShadow = '0 14px 44px rgba(0,0,0,0.4), inset 0 1px 1px rgba(255,255,255,0.1)';
      bezels.style.transform = 'translateZ(50px)';
    }
    const img = card.querySelector('.app-shot-img');
    if(img) img.style.transform = 'translateZ(20px)';
    const title = card.querySelector('.app-shot-title');
    if(title) {
        title.style.transform = 'translateZ(30px)';
        title.style.color = 'var(--t, #fff)';
    }
  });
  
  card.addEventListener('mouseenter', () => {
    card.style.transition = 'transform 0.15s ease-out';
  });
  card.addEventListener('mouseleave', () => {
    card.style.transition = 'transform 0.5s cubic-bezier(0.16, 1, 0.3, 1)';
  });
});
'''

# Use string replace for JS since it goes inside the bottom script block just before // ── Animated count-up ──
text = text.replace('// ── Animated count-up ──', js_block + '\n// ── Animated count-up ──')

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("Complete injection finished without duplicates.")
