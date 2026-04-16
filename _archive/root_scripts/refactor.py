import re

with open('docs/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

clean_ad = '''<!-- ============ APP PREVIEW AD ============ -->
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
</section>'''

text = re.sub(r'<!-- ============ APP PREVIEW AD ============ -->.*?</section>', clean_ad, text, flags=re.DOTALL)

# Also adding the matching CSS rules into an external block - assuming the project uses global styles somewhere, appending to <head> for now
css_block = '''<style>
.app-shots-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 32px; align-items: start; margin-top: 56px; }
.app-shot-card { display: flex; flex-direction: column; align-items: center; text-align: center; }
.app-shot-bezels { border-radius: 44px; padding: 12px; background: linear-gradient(135deg, rgba(255,255,255,0.06), transparent); box-shadow: 0 24px 64px rgba(0,0,0,0.4); margin-bottom: 24px; display: inline-block; }
.app-shot-img { width: 100%; max-width: 280px; border-radius: 36px; border: 2px solid rgba(255,255,255,0.03); display: block; }
.app-shot-title { font-size: 18px; color: var(--t, #fff); margin-bottom: 8px; }
.app-shot-desc { font-size: 14px; color: var(--t2, #a1a1aa); line-height: 1.6; }
</style>'''

text = text.replace('</head>', f'{css_block}\n</head>')

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(text)
