# Motomap Stitch-Style Next.js App Plan

## 1. Overview & Theme Concept
We are rebuilding the entire application from scratch using Next.js (App Router), leveraging a unified "Stitch-style" UI.
The "Stitch style" focuses on playful, soft, and textured aesthetics:
- **Colors:** Deep denim blues, vibrant tropical teal/cyan, and energetic accents (coral/orange).
- **Textures/Borders:** Heavy use of dashed/dotted borders resembling fabric stitching (`border-dashed`, `border-dotted`).
- **Shapes:** Bubbly, heavily rounded corners (`rounded-2xl`, `rounded-full`) for buttons, cards, and input fields.
- **Typography:** Friendly, rounded sans-serif fonts (e.g., Nunito or Quicksand).
- **Animations:** Bouncy, spring-like interactions (using Framer Motion).

## 2. Tech Stack
- **Framework:** Next.js 14+ (App Router)
- **Styling:** Tailwind CSS (extended with custom dashed borders and stitch patterns)
- **Components:** Radix UI primitives or Headless UI (fully unstyled to support heavy theming)
- **Icons:** Lucide-React (with thicker stroke widths to match the theme)
- **State & Data:** Zustand (global state) & SWR / React Query
- **Auth & DB:** Supabase SSR (Database, Auth, Edge Functions)

## 3. Screen Flow & Architecture (Web & Mobile PWA)

### A. Authentication (Supabase)
- **`/login`**: Sign in with Google / Email. 
  - *UI:* Large stitched card centered on screen, tropical gradient background, thick dashed borders on inputs.
- **`/register`**: Simple sign up. 

### B. Core Screens
- **`/dashboard` (Home)**
  - *UI:* A grid of rounded "patches" (cards). Each patch has a different pastel/blue background with a stitched border footprint.
  - *Content:* Quick actions (Start ride, view routes), recent activity, weather snippet.
- **`/map` (Live Navigation/Routes)**
  - *UI:* Full-bleed Mapbox/MapLibre GL map.
  - *Overlay:* Floating action buttons (FABs) with heavy dropshadows and dashed rings. Drawer pulling up from the bottom with route details.
- **`/routes` (Saved & Shared)**
  - *UI:* Vertical list of route cards. Hover effects that "pull" the stitch tight (CSS transform/border transitions).
- **`/profile`**
  - *UI:* Circular avatar with a woven-border appearance. Stats on trips, saved locations, and user settings.

## 4. Design System Tokens (Tailwind Config Prep)
```js
// tailwind.config.js concept
module.exports = {
  theme: {
    extend: {
      colors: {
        stitch: {
          dark: '#0e1f3b',   // Deep space blue
          base: '#2a5a9c',   // Classic stitch blue
          light: '#6db4d8',  // Cyan/teal belly
          accent: '#ff5c5c', // Coral/red accent
          thread: '#f1f5f9', // White/silver thread color
        }
      },
      borderWidth: {
        '3': '3px',
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
        '3xl': '2rem',
      }
    }
  }
}
```

## 5. Implementation Phases 
1. **Clean Slate execution:** Delete old client/app folders (`app/mobile`, `app/website`, `web/`, etc.) that hold the legacy project.
2. **Next.js Initialization:** Scaffold the fresh Next.js project with Tailwind and TypeScript.
3. **Establish Design System:** Integrate the Tailwind config mapping the "Stitch" colors, global CSS for the `.stitch-border` utility classes.
4. **Layout & Navigation:** Create the bottom navigation (for mobile views) and sidebars (for desktop views).
5. **Supabase Integration:** Reinstall the Supabase SSR setup inside the new App Router structure.
6. **Screen Build-Out:** Construct the Dashboard, Map, Routes, and Profile scenes.

---
*Ready to tear down the old code and initialize the new Next.js environment.*