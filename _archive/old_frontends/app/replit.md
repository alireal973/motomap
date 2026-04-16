# MOTOMAP

A motorcycle route optimization project that compares MOTOMAP routes against Google Maps routes. Includes a web frontend and a React Native mobile app (Expo).

## Project Structure

- `motomap/` — Python library for route analysis (curve risk, elevation, OSM validation, routing)
- `api/` — FastAPI REST API backend wrapping the motomap library
- `website/` — Vite/TypeScript web frontend for map visualization
- `mobile/` — Expo React Native mobile app (iOS + Android + Web preview)
- `scripts/` — Standalone scripts (demo, route generation, elevation plots)
- `tests/` — Python test suite
- `outputs/` — Generated map exports and elevation data
- `docs/` — Architecture docs, plans, and research

## Tech Stack

- **Mobile app:** Expo 52 + React Native + react-native-maps + expo-router
- **Backend API:** FastAPI + Uvicorn (Python 3.12)
- **Web frontend:** Vite 6 + TypeScript + Google Maps JS API
- **Route engine:** osmnx, networkx, geopandas, numpy
- **Node version:** 20

## Running the Project

### Workflows

| Workflow | Command | Port | Purpose |
|---|---|---|---|
| Start application | `cd mobile && npx expo start --web --port 5000` | 5000 | Expo web preview (Replit webview) |
| Backend API | `python -m uvicorn api.main:app --host localhost --port 8000 --reload` | 8000 | REST API |
| Start Mobile | `cd mobile && npx expo start --tunnel` | — | Expo dev server for phone (QR code) |

### Expo Mobile App (Phone)

1. Open the **Start Mobile** workflow console to see the QR code
2. Install **Expo Go** on your phone (App Store / Google Play)
3. Scan the QR code — the app will load on your phone
4. The app fetches route data via `EXPO_PUBLIC_API_URL` set in `mobile/.env`

### Web Preview (Replit)

The **Start application** workflow runs Expo for web on port 5000. This gives a browser-based preview of the mobile app UI directly in the Replit webview. `react-native-maps` is stubbed for web via `mobile/metro.config.js` and `mobile/stubs/react-native-maps.js`. The map screen on web uses `mobile/app/map.web.tsx` (platform-specific file), which shows route stats without the native map.

## Key Configuration

- `mobile/metro.config.js` — Stubs `react-native-maps` for web platform
- `mobile/stubs/react-native-maps.js` — Web stub returning no-op React components
- `mobile/app/map.web.tsx` — Web-specific map screen (route stats without native MapView)
- `mobile/assets/moto_bg.png` — AI-generated cinematic motorcycle road background image
- `api/main.py` — FastAPI with CORS allow_origins=["*"], serves demo route data
- `mobile/.env` — `EXPO_PUBLIC_API_URL` = Replit public domain for phone access
- `mobile/app.json` — Expo config, scheme "motomap", dark splash screen #081C50

## Mobile App Design

Deep blue theme matching Moto Navigator design language:
- Background: Motorcycle road photo (`moto_bg.png`) with `rgba(8,28,80,0.72)` overlay
- Primary: `#3D8BFF` (bright blue accent)
- Glass cards: `rgba(255,255,255,0.12)` bg + `rgba(255,255,255,0.22)` border
- CTA button: White pill with dark text
- Header: Globe icon in `#3D8BFF` circle + "MOTOMAP" bold text

## Screens

1. **Welcome** (`index.tsx`) — Hero text "YOLUN/RUHUNU/KEŞFET.", feature card, BAŞLAYALIM button
2. **Onboarding** (`onboarding.tsx`) — User type selection: İş/Kurye vs Gezi/Hobi
3. **Map** (`map.tsx` / `map.web.tsx`) — Google vs MOTOMAP route comparison with stats

## Route Data

Demo route: Kadıköy İskele → Kalamış Parkı (Istanbul).  
To generate real data: set `GOOGLE_MAPS_API_KEY` env variable then run `python website/generate_route.py`.

## Deployment

Configured as a static site deployment:
- Build: `npm --prefix website run build`
- Public dir: `website/dist`
