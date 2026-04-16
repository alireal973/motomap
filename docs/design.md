# MotoMap Website & App Design Guidelines

## 1. Color Palette

MotoMap utilizes a dark, modern, and high-contrast theme, blending deep space blacks/purples with vibrant, energetic neon highlights that signify premium routing technology.

### Backgrounds (Deep Dark / Purple-Blacks)
- **Base Background (`--bg`)**: `#130B1A` - Core background color, extremely dark purple-black.
- **Surface Level 1 (`--bg2`)**: `#1A0F24` - Secondary background for cards, slight elevation.
- **Surface Level 2 (`--bg3`)**: `#241530` - Highest elevation surface for active elements or hovers.

### Text & Typography
- **Primary Text (`--t`)**: `#F5F0F8` - Off-white with a hint of purple/warmth for readability.
- **Secondary Text (`--t2`)**: `rgba(245,240,248,0.62)` - Muted text for descriptions, sub-labels.
- **Tertiary Text (`--t3`)**: `rgba(245,240,248,0.34)` - Disabled or highly subtle text.

### Accents & Highlights
- **Primary Accent (MotoMap Yellow/Gold)**:
  - Base (`--accent`): `#FACC15`
  - High (`--accent-hi`): `#FDE047`
  - Low (`--accent-lo`): `#F59E0B`
- **Secondary / Data Accents**:
  - Pink (`--pink`): `#E879F9`
  - Orange (`--orange`): `#FB923C`
  - Green (`--green`): `#86EFAC` - Used for "safe/good" states or highlights.
  - Purple (`--purple`): `#C084FC`
  - Warm/Red (`--warm`): `#F472B6`

### Release / Special Pages Theme
For auxiliary pages like the **Releases** page (`releases.html`), the theme pivots slightly to incorporate:
- **Deep Blues / Midnight Blues**: Moving towards a tech-focused `#0B132B` to `#1C2541` aesthetic integrated with the core black.
- **Cyber Blue Accents**: `#00F0FF` or `#3B82F6` for version tags, badges, and technical release notes.

## 2. Typography

The font stack provides a blend of high-legibility UI sans-serif fonts, elegant serif headers, and technical monospace.

- **Primary UI (Sans-Serif)**: `Inter`, `-apple-system`, `BlinkMacSystemFont`, `system-ui`, `sans-serif`
  - Used for body text, navigation, buttons, and general UI.
- **Display / Headers (Serif)**: `Instrument Serif`, `Playfair Display`, `Georgia`, `serif`
  - Used for large, impactful headlines (e.g., Hero sections).
- **Code / Technical (Monospace)**: `JetBrains Mono`, `Fira Code`, `monospace`
  - Used for numbers, stats, versioning, and technical data.

## 3. Core UI Components

### Cards & Surfaces
- **Borders (`--bdr`)**: `rgba(255,255,255,0.06)`
- **Hover Borders (`--bdr-h`)**: `rgba(255,255,255,0.14)`
- **Glassmorphism**: Cards typically use subtle white tinting (`rgba(255,255,255,0.025)`) with blurred backdrops to create depth without relying on harsh lines.

### Navigation (Top Bar)
- **Height**: `80px` standard, collapses to `56px` on scroll.
- **Background**: Frosted glass effect `rgba(19, 11, 26, 0.55)` with `backdrop-filter: blur(24px)`.
- **Behavior**: Sticks to the top, gains a shadow and becomes more opaque on scroll.

### Animations & Interactions
- Smooth easing curves (`cubic-bezier(0.16, 1, 0.3, 1)`) for all transform and opacity shifts.
- Uses particle effects, ambient orbs, and glows rather than harsh 3D tilts for professional, high-end feel.

## 4. Page Structure

### Landing Page (`index.html`)
- **Hero**: Orbs/Glows background, clear H1, App mockups.
- **Features / Services**: Grid layouts with glass cards.
- **App Preview**: Sleek cards showcasing the mobile app interface.

### Release Notes (`releases.html`)
- Clean, technical layout. 
- Timeline or changelog format based in deep blues and blacks.
- Focus strictly on content (versions, features, bug fixes) rather than heavy marketing visuals.
