# Objective
Redesign the MOTOMAP mobile app UI to match the provided screenshots exactly:
- Screen 1: Motorcycle background photo with dark blue overlay, large bold hero text "YOLUN / RUHUNU / KEŞFET.", frosted glass feature card, white "BAŞLAYALIM" pill button
- Screen 2: "Seni Daha İyi Tanıyalım." onboarding with İş/Kurye and Gezi/Hobi glass selection cards
- Map screen: Updated to match the same blue design language

Design language:
- Background: Motorcycle on road photo with deep blue tint overlay
- Primary color: Bright blue (#3D8BFF / #007AFF)
- Text: White (#FFF) + Blue accent for keywords
- Cards: Frosted glass effect (rgba(255,255,255,0.12) bg, rgba(255,255,255,0.25) border)
- CTA Button: White pill button with dark text
- Header: Globe icon in blue circle + "MOTOMAP" text

# Tasks

### T001: Generate Motorcycle Background Image
- **Blocked By**: []
- **Details**:
  - Use media generation skill to generate a motorcycle-on-road photo (cinematic, dark blue moody sky, coastal road)
  - Save to `mobile/assets/moto_bg.jpg`
  - This is the hero background used across all screens

### T002: Redesign Welcome Screen (index.tsx)
- **Blocked By**: [T001]
- **Details**:
  - Full-screen background image with deep blue overlay (ImageBackground + View overlay)
  - Top bar: Blue circle globe icon (🌐 or styled View) + "MOTOMAP" bold white text
  - Hero section: Very large bold text (fontSize 52+):
    - "YOLUN" — white
    - "RUHUNU" — blue (#3D8BFF)
    - "KEŞFET." — white
  - Subtitle: "Sadece en hızlı değil, en keyifli rotalar için tasarlandı." — gray/white, smaller
  - Feature card (frosted glass): Blue lightning icon in circle + "Akıllı Rotalar" title + "Virajlı ve manzaralı seçenekler." subtitle
  - White pill CTA button at bottom: "BAŞLAYALIM  ›" — navigates to /onboarding
  - Files: `mobile/app/index.tsx`

### T003: Create Onboarding Screen (onboarding.tsx)
- **Blocked By**: [T001]
- **Details**:
  - Same background image + blue overlay
  - Same top bar (globe + MOTOMAP)
  - Hero text: "Seni Daha İyi" (white, large bold) + "Tanıyalım." (blue, large bold)
  - Subtitle: "Uygulamayı genellikle hangi amaçla kullanacaksın?"
  - Two frosted glass selection cards (like in screenshot):
    1. Briefcase icon in blue circle + "İş / Kurye" bold + "Hızlı teslimat ve verimli rotalar." + arrow →
    2. Heart icon in blue circle + "Gezi / Hobi" bold + "Keyifli turlar ve virajlı yollar." + arrow →
  - Both cards navigate to /map when tapped
  - "GERİ DÖN" text button at very bottom
  - Files: `mobile/app/onboarding.tsx`

### T004: Update Map Screen Panel to Match Blue Theme
- **Blocked By**: []
- **Details**:
  - Keep all map functionality intact (polylines, circles, route data fetch)
  - Update back button style: blue circle globe icon + "MOTOMAP" text (matching header style)
  - Update bottom panel:
    - Background: deep blue (#0A1E3D) instead of #1a1a2e
    - Mode buttons: blue active state (#3D8BFF) instead of red
    - Stat cards: rgba glass style matching the new theme
    - Section titles: updated to new style
  - Files: `mobile/app/map.tsx`

### T005: Update Layout and Navigation
- **Blocked By**: [T002, T003, T004]
- **Details**:
  - Update `_layout.tsx` to use slide animation between screens
  - Update `mobile/app.json` splash backgroundColor if needed
  - Restart the Start Mobile workflow so Expo picks up all changes
  - Files: `mobile/app/_layout.tsx`
