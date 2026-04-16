import re

with open('docs/maps.html', 'r', encoding='utf-8') as f:
    text = f.read()

new_preview = '''<section class="sec sec-alt shots" id="preview"><div class="c">
  <div class="sec-h r"><div class="sec-e">Preview</div><h2 class="sec-t">A cleaner look at the <em class="em">product</em></h2><p class="sec-d">Real screen captures from the live MotoMap experience, framed as premium product previews for the site.</p></div>
  <div class="shots-grid" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:32px; align-items:start; margin-top:56px;">
    
    <article class="shot-card r" style="display:flex; flex-direction:column; align-items:center; text-align:center;">
        <div style="border-radius:44px; padding:12px; background:linear-gradient(135deg, rgba(255,255,255,0.06), transparent); box-shadow:0 24px 64px rgba(0,0,0,0.4); margin-bottom:24px;">
          <img src="assets/app_mockups/dashboard_masked.png" alt="Dashboard" style="width:100%; max-width:280px; border-radius:36px; border:2px solid rgba(255,255,255,0.03); display:block;"/>
        </div>
        <div class="shot-copy">
            <span class="shot-kicker">Live Feed</span>
            <h3 style="font-size:18px; color:var(--t); margin-bottom:8px;">Control Dashboard</h3>
            <p style="font-size:14px; color:var(--t2); line-height:1.6;">Live weather, route history, and rapid access to MotoMap tools.</p>
        </div>
    </article>

    <article class="shot-card r" style="display:flex; flex-direction:column; align-items:center; text-align:center;">
        <div style="border-radius:44px; padding:12px; background:linear-gradient(135deg, rgba(255,255,255,0.06), transparent); box-shadow:0 24px 64px rgba(0,0,0,0.4); margin-bottom:24px;">
          <img src="assets/app_mockups/map_navigation_masked.png" alt="Map Navigation" style="width:100%; max-width:280px; border-radius:36px; border:2px solid rgba(255,255,255,0.03); display:block;"/>
        </div>
        <div class="shot-copy">
            <span class="shot-kicker">Navigation</span>
            <h3 style="font-size:18px; color:var(--t); margin-bottom:8px;">Route Navigation</h3>
            <p style="font-size:14px; color:var(--t2); line-height:1.6;">Uncluttered layer rendering with live traffic and hazard overlays.</p>
        </div>
    </article>

    <article class="shot-card r" style="display:flex; flex-direction:column; align-items:center; text-align:center;">
        <div style="border-radius:44px; padding:12px; background:linear-gradient(135deg, rgba(255,255,255,0.06), transparent); box-shadow:0 24px 64px rgba(0,0,0,0.4); margin-bottom:24px;">
          <img src="assets/app_mockups/garage_masked.png" alt="Digital Garage" style="width:100%; max-width:280px; border-radius:36px; border:2px solid rgba(255,255,255,0.03); display:block;"/>
        </div>
        <div class="shot-copy">
            <span class="shot-kicker">Physics Config</span>
            <h3 style="font-size:18px; color:var(--t); margin-bottom:8px;">Digital Garage</h3>
            <p style="font-size:14px; color:var(--t2); line-height:1.6;">Adjust cc, weight, torque, and tires to alter algorithm outputs.</p>
        </div>
    </article>

    <article class="shot-card r" style="display:flex; flex-direction:column; align-items:center; text-align:center;">
        <div style="border-radius:44px; padding:12px; background:linear-gradient(135deg, rgba(255,255,255,0.06), transparent); box-shadow:0 24px 64px rgba(0,0,0,0.4); margin-bottom:24px;">
          <img src="assets/app_mockups/communities_masked.png" alt="Communities" style="width:100%; max-width:280px; border-radius:36px; border:2px solid rgba(255,255,255,0.03); display:block;"/>
        </div>
        <div class="shot-copy">
            <span class="shot-kicker">Social Features</span>
            <h3 style="font-size:18px; color:var(--t); margin-bottom:8px;">Rider Communities</h3>
            <p style="font-size:14px; color:var(--t2); line-height:1.6;">Coordinate group rides and track real-time club telemetry.</p>
        </div>
    </article>

  </div>
</div></section>'''

text = re.sub(r'<section class="sec sec-alt shots" id="preview">.*?</section>', new_preview, text, flags=re.DOTALL)

with open('docs/maps.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated maps.html')
