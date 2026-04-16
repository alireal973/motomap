import re

with open('docs/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update CSS to ensure images fit the display properly and modern showcase works perfectly
css_update_re = r'\.app-sc-right\s*\{\s*flex:\s*1;\s*display:\s*flex;\s*justify-content:\s*center;\s*position:\s*relative;\s*perspective:\s*1000px;\s*\}\s*\.app-phone-frame\s*\{.*?\}\s*\.app-sc-right:hover\s*\.app-phone-frame\s*\{.*?\}\s*\.app-phone-glare\s*\{.*?\}\s*\.app-sc-img\s*\{.*?\}\s*\.app-sc-img\.active\s*\{.*?\}'

new_css = '''
.app-sc-right { flex: 1; display: flex; justify-content: center; position: relative; perspective: 1200px; padding: 20px; }
.app-phone-frame { 
  position: relative; width: 320px; height: 660px; background: #000; border-radius: 56px; 
  box-shadow: 0 40px 100px rgba(0,0,0,0.8), inset 0 0 0 2px rgba(255,255,255,0.1), inset 0 0 8px rgba(0,240,255,0.3); 
  transform-style: preserve-3d; transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1); 
  display: flex; justify-content: center; align-items: center; overflow: hidden;
}
.app-sc-right:hover .app-phone-frame { transform: translateY(-12px) rotateY(-8deg) rotateX(4deg); }
.app-phone-glare { position: absolute; inset: 0; border-radius: 56px; background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, transparent 40%, rgba(255,255,255,0.05) 100%); pointer-events: none; z-index: 10; mix-blend-mode: overlay; }
.app-phone-screen { position: absolute; top: 12px; left: 12px; right: 12px; bottom: 12px; border-radius: 44px; background: #09090E; overflow: hidden; z-index: 1; }
.app-sc-img { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0; transform: scale(1.05) translateY(20px); transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1); pointer-events: none; }
.app-sc-img.active { opacity: 1; transform: scale(1) translateY(0); pointer-events: auto; }
'''

# We also need to update the HTML to match this new .app-phone-screen nesting
# Let's do that cleanly

html_regex = r'<div class="app-phone-frame">\s*<div class="app-phone-glare"></div>\s*<img.*?id="img-dash".*?>\s*<img.*?id="img-map".*?>\s*<img.*?id="img-garage".*?>\s*<img.*?id="img-comm".*?>\s*</div>'
new_html = '''
<div class="app-phone-frame">
  <div class="app-phone-glare"></div>
  <div class="app-phone-screen">
    <img src="assets/app_mockups/dashboard_masked.png" id="img-dash" class="app-sc-img active" loading="lazy" />
    <img src="assets/app_mockups/map_navigation_masked.png" id="img-map" class="app-sc-img" loading="lazy" />
    <img src="assets/app_mockups/garage_masked.png" id="img-garage" class="app-sc-img" loading="lazy" />
    <img src="assets/app_mockups/communities_masked.png" id="img-comm" class="app-sc-img" loading="lazy" />
  </div>
</div>
'''

text = re.sub(html_regex, new_html.strip(), text, flags=re.DOTALL)
text = re.sub(css_update_re, new_css.strip(), text, flags=re.DOTALL)

# 2. Update JS to auto-rotate + advanced particles
js_old = r'// ── App Modern Tab Switcher ──[\s\S]*?requestAnimationFrame\(loop\);\s*\}\s*loop\(\);\s*\}'

js_new = '''
// ── App Modern Tab Switcher (Auto Rotate) ──
const appItems = Array.from(document.querySelectorAll('.app-sc-item'));
const appImgs = Array.from(document.querySelectorAll('.app-sc-img'));
let currentAppIndex = 0;
let appInterval;

function setAppActive(index) {
  appItems.forEach(i => i.classList.remove('active'));
  appImgs.forEach(img => img.classList.remove('active'));
  
  if(appItems[index] && appImgs[index]) {
      appItems[index].classList.add('active');
      const targetId = appItems[index].getAttribute('data-target');
      const targetImg = document.getElementById(targetId);
      if(targetImg) targetImg.classList.add('active');
  }
  currentAppIndex = index;
}

function startAppRotation() {
  clearInterval(appInterval);
  appInterval = setInterval(() => {
    let nextIndex = (currentAppIndex + 1) % appItems.length;
    setAppActive(nextIndex);
  }, 4000);
}

appItems.forEach((item, idx) => {
  item.addEventListener('click', () => {
    setAppActive(idx);
    startAppRotation(); // Reset timer on manual click
  });
  item.addEventListener('mouseenter', () => {
    setAppActive(idx);
    startAppRotation(); // Reset timer on hover
  });
});

// Start rotation initially
startAppRotation();


// ── Advanced Google-style Anti-Gravity Particle Physics ──
const agCanvas = document.getElementById('ag-canvas');
if (agCanvas) {
  const ctx = agCanvas.getContext('2d');
  let ps = [];
  let connections = [];
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
  agCanvas.addEventListener('mouseleave', () => {
      mActive = false;
      // Gently pull to center when mouse leaves so they don't get stuck
      mx = w/2; my = h/2;
  });

  // Initialize advanced anti-gravity nodes
  const colors = ['#FACC15', '#F59E0B', '#86EFAC', '#00F0FF'];
  for(let i=0; i<45; i++) {
    ps.push({
      x: Math.random()*w, y: Math.random()*h,
      vx: (Math.random() - 0.5) * 1.2,
      vy: (Math.random() - 0.5) * 1.2,
      r: Math.random() * 5 + 2, // slightly smaller, more elegant
      c: colors[Math.floor(Math.random() * colors.length)],
      baseX: Math.random()*w,
      baseY: Math.random()*h
    });
  }

  function loop() {
    ctx.clearRect(0,0,w,h);
    
    for(let i=0; i<ps.length; i++) {
      let p = ps[i];
      p.x += p.vx;
      p.y += p.vy;

      // Soft borders (wrap around smoothly)
      if(p.x < -50) p.x = w + 50;
      if(p.x > w + 50) p.x = -50;
      if(p.y < -50) p.y = h + 50;
      if(p.y > h + 50) p.y = -50;

      // Mouse interaction (Anti-Gravity / Repulsion)
      if (mActive) {
        let dx = p.x - mx;
        let dy = p.y - my;
        let dist = Math.sqrt(dx*dx + dy*dy);
        
        // Repel strong within 150px
        if (dist < 150) {
          let force = (150 - dist) / 150;
          p.vx += (dx / dist) * force * 0.8; // Advanced push
          p.vy += (dy / dist) * force * 0.8;
          p.r = Math.min(p.r + 0.2, 8); // Grow slightly when pushed
        } else {
             p.r = Math.max(p.r - 0.1, 2);
        }
      }

      // Friction
      p.vx *= 0.98;
      p.vy *= 0.98;
      
      // Minimum drift speed so they don't stop completely
      let speed = Math.sqrt(p.vx*p.vx + p.vy*p.vy);
      if (speed < 0.3) {
          p.vx += (Math.random() - 0.5) * 0.1;
          p.vy += (Math.random() - 0.5) * 0.1;
      }

      // Draw particle
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
      ctx.fillStyle = p.c;
      ctx.globalAlpha = 0.6;
      ctx.fill();
    }
    
    // Draw constellation connections
    ctx.lineWidth = 0.5;
    for(let i=0; i<ps.length; i++) {
        for(let j=i+1; j<ps.length; j++) {
            let dx = ps[i].x - ps[j].x;
            let dy = ps[i].y - ps[j].y;
            let dist = Math.sqrt(dx*dx + dy*dy);
            if(dist < 100) {
                ctx.beginPath();
                ctx.moveTo(ps[i].x, ps[i].y);
                ctx.lineTo(ps[j].x, ps[j].y);
                // Line opacity fades out at distance 100
                ctx.strokeStyle = gba(255, 255, 255, );
                ctx.stroke();
            }
        }
    }
    
    requestAnimationFrame(loop);
  }
  loop();
}
'''

text = re.sub(js_old, js_new.strip(), text, flags=re.DOTALL)

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Advanced slider and particle system fully implemented.")
