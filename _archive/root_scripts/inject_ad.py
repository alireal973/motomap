import re

with open('docs/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

ad_section = '''
<!-- ============ APP PREVIEW AD ============ -->
<section class="sec sec-alt shots" id="app">
  <div class="c">
    <div class="sec-h r"><div class="sec-e">Mobile App</div><h2 class="sec-t">Your <em class="em">Digital Twin</em> Command Center</h2><p class="sec-d">The complete routing intelligence system directly in your pocket. Control your ride styles, track live routing, manage your garage, and coordinate with communities.</p></div>
    
    <div class="shots-grid" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:32px; align-items:start; margin-top:56px;">
      
      <article class="shot-card r" style="display:flex; flex-direction:column; align-items:center; text-align:center;">
        <div style="border-radius:44px; padding:12px; background:linear-gradient(135deg, rgba(255,255,255,0.06), transparent); box-shadow:0 24px 64px rgba(0,0,0,0.4); margin-bottom:24px;">
          <img src="assets/app_mockups/dashboard_masked.png" alt="Dashboard" style="width:100%; max-width:280px; border-radius:36px; border:2px solid rgba(255,255,255,0.03); display:block;"/>
        </div>
        <h3 style="font-size:18px; color:var(--t); margin-bottom:8px;">Control Dashboard</h3>
        <p style="font-size:14px; color:var(--t2); line-height:1.6;">Live weather, route history, and rapid access to MotoMap tools.</p>
      </article>

      <article class="shot-card r" style="display:flex; flex-direction:column; align-items:center; text-align:center;">
        <div style="border-radius:44px; padding:12px; background:linear-gradient(135deg, rgba(255,255,255,0.06), transparent); box-shadow:0 24px 64px rgba(0,0,0,0.4); margin-bottom:24px;">
          <img src="assets/app_mockups/map_navigation_masked.png" alt="Map Navigation" style="width:100%; max-width:280px; border-radius:36px; border:2px solid rgba(255,255,255,0.03); display:block;"/>
        </div>
        <h3 style="font-size:18px; color:var(--t); margin-bottom:8px;">Route Navigation</h3>
        <p style="font-size:14px; color:var(--t2); line-height:1.6;">Uncluttered layer rendering with live traffic and hazard overlays.</p>
      </article>

      <article class="shot-card r" style="display:flex; flex-direction:column; align-items:center; text-align:center;">
        <div style="border-radius:44px; padding:12px; background:linear-gradient(135deg, rgba(255,255,255,0.06), transparent); box-shadow:0 24px 64px rgba(0,0,0,0.4); margin-bottom:24px;">
          <img src="assets/app_mockups/garage_masked.png" alt="Digital Garage" style="width:100%; max-width:280px; border-radius:36px; border:2px solid rgba(255,255,255,0.03); display:block;"/>
        </div>
        <h3 style="font-size:18px; color:var(--t); margin-bottom:8px;">Digital Garage</h3>
        <p style="font-size:14px; color:var(--t2); line-height:1.6;">Adjust cc, weight, torque, and tires to alter algorithm outputs.</p>
      </article>

      <article class="shot-card r" style="display:flex; flex-direction:column; align-items:center; text-align:center;">
        <div style="border-radius:44px; padding:12px; background:linear-gradient(135deg, rgba(255,255,255,0.06), transparent); box-shadow:0 24px 64px rgba(0,0,0,0.4); margin-bottom:24px;">
          <img src="assets/app_mockups/communities_masked.png" alt="Communities" style="width:100%; max-width:280px; border-radius:36px; border:2px solid rgba(255,255,255,0.03); display:block;"/>
        </div>
        <h3 style="font-size:18px; color:var(--t); margin-bottom:8px;">Rider Communities</h3>
        <p style="font-size:14px; color:var(--t2); line-height:1.6;">Coordinate group rides and track real-time club telemetry.</p>
      </article>
      
    </div>
  </div>
</section>
'''

# Inject before RIDER PERSONAS
if '<!-- ============ APP PREVIEW AD ============ -->' not in html:
    html = html.replace('<!-- ============ RIDER PERSONAS ============ -->', ad_section + '\n<!-- ============ RIDER PERSONAS ============ -->')

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Injected UI section.")
