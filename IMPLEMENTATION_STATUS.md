# MotoMap Implementation Status & Detailed Remaining Plan

*Last updated: 2026-04-06*
*Reference: docs/superpowers/plans/comprehensive/MOTOMAP_MASTER_TODO.md*

---

## LEGEND

- [x] = DONE (implemented, file exists, code compiles)
- [ ] = NOT DONE (missing or needs implementation)
- [~] = PARTIAL (file exists but incomplete / stub)

---

# PART 1: WHAT IS DONE (COMPLETED STATUS)

---

## MODULE 1: WEATHER INTEGRATION SYSTEM -- DONE

| Task | Status | File |
|------|--------|------|
| Weather data models | [x] | `motomap/weather/models.py` |
| OpenWeatherMap client | [x] | `motomap/weather/client.py` |
| Weather caching (Redis + memory) | [x] | `motomap/weather/cache.py` |
| Road condition assessment | [x] | `motomap/weather/assessment.py` |
| Lane splitting modifiers | [x] | `motomap/weather/assessment.py` |
| Turkish warning messages | [x] | `motomap/weather/assessment.py` |
| Config management | [x] | `motomap/weather/config.py` |
| API endpoints (2) | [x] | `api/routes/weather.py` |

---

## MODULE 2: VISUAL ROUTE SAFETY OVERLAY -- MOSTLY DONE

| Task | Status | File |
|------|--------|------|
| Segment safety scoring | [x] | `motomap/routing/segment_analyzer.py` |
| Color mapping (4 levels) | [x] | `motomap/routing/segment_analyzer.py` |
| ColoredRoute component | [x] | `app/mobile/components/ColoredRoute.tsx` |
| SafetyModeToggle | [x] | `app/mobile/components/SafetyModeToggle.tsx` |
| WeatherCard overlay | [x] | `app/mobile/components/WeatherCard.tsx` |
| Route info panel | [ ] | NOT CREATED |
| Map legend | [ ] | NOT CREATED |
| User location marker | [ ] | NOT CREATED |
| Map controls | [ ] | NOT CREATED |

---

## MODULE 3: USER AUTH & DATABASE -- DONE

| Task | Status | File |
|------|--------|------|
| Async SQLAlchemy setup | [x] | `api/database.py` |
| User model | [x] | `api/models/user.py` |
| bcrypt hashing | [x] | `api/core/security.py` |
| JWT access/refresh | [x] | `api/core/security.py` |
| Auth service (7 ops) | [x] | `api/services/auth.py` |
| Auth API (7 endpoints) | [x] | `api/routes/auth.py` |
| get_current_user dep | [x] | `api/routes/auth.py` |
| Email verification | [ ] | NOT CREATED |
| Password reset flow | [ ] | NOT CREATED |
| OAuth2 social login | [ ] | NOT CREATED |

---

## MODULE 4: PROFILE & GARAGE -- DONE

| Task | Status | File |
|------|--------|------|
| Motorcycle model (12 types) | [x] | `api/models/motorcycle.py` |
| Profile service | [x] | `api/services/profile.py` |
| Motorcycle CRUD | [x] | `api/services/motorcycle.py` |
| Profile API routes | [x] | `api/routes/profile.py` |
| User settings | [x] | `api/services/profile.py` |
| Photo upload wiring | [ ] | NOT WIRED |

---

## MODULE 5: COMMUNITY PLATFORM -- DONE

| Task | Status | File |
|------|--------|------|
| Models (Community, Membership, Post, Comment) | [x] | `api/models/community.py` |
| Service (full CRUD) | [x] | `api/services/community.py` |
| API (11 endpoints) | [x] | `api/routes/communities.py` |
| Migrations (4 files) | [x] | `migrations/004-007` |
| Seed 18 TR communities | [x] | `api/services/community.py` |
| Post/comment likes | [ ] | NOT CREATED |
| WebSocket chat | [ ] | NOT CREATED |
| Moderation tools | [ ] | NOT CREATED |
| Full-text search | [ ] | NOT CREATED |

---

## MODULE 6: ROAD REPORTS -- DONE

| Task | Status | File |
|------|--------|------|
| Model (20 types, 4 categories) | [x] | `api/models/road_report.py` |
| Service (geo queries, votes) | [x] | `api/services/road_reports.py` |
| API (5 endpoints) | [x] | `api/routes/road_reports.py` |
| Migration | [x] | `migrations/008` |
| Gamification wired | [x] | `api/routes/road_reports.py` |
| Report photo upload | [ ] | NOT WIRED |
| Report clustering | [ ] | NOT CREATED |
| Nearby push notifications | [ ] | NOT CREATED |
| My reports endpoint | [ ] | NOT CREATED |

---

## MODULE 7: GAMIFICATION -- DONE

| Task | Status | File |
|------|--------|------|
| Models (Points, Transaction, Badge, Challenge) | [x] | `api/models/gamification.py` |
| Service (full) | [x] | `api/services/gamification.py` |
| API (5 endpoints) | [x] | `api/routes/gamification.py` |
| Migration | [x] | `migrations/009` |
| Points wired (reports +5, posts +3/+25, routes +10) | [x] | routes/road_reports, communities, history |
| Badge auto-award | [ ] | NOT CREATED |
| Challenge progress tracking | [ ] | NOT CREATED |
| Level-up notifications | [ ] | NOT CREATED |

---

## MODULE 8: BACKEND EXTENSIONS -- DONE

| Task | Status | File |
|------|--------|------|
| Redis cache layer | [x] | `api/core/cache.py` |
| Rate limiting | [x] | `api/middleware/rate_limit.py` |
| Request logging | [x] | `api/middleware/logging.py` |
| Route history (6 endpoints) | [x] | `api/routes/history.py` |
| Notifications (6 endpoints) | [x] | `api/routes/notifications.py` |
| File upload (2 endpoints) | [x] | `api/routes/upload.py` |
| Dynamic route generation | [ ] | NOT CREATED |
| Prometheus metrics | [ ] | NOT CREATED |
| Enhanced health check | [ ] | NOT CREATED |

---

## MODULE 9: MOBILE SCREENS -- MOSTLY DONE

### Screens Done (18)
| Screen | File |
|--------|------|
| Dashboard/Home | `app/(tabs)/index.tsx` |
| Map (weather+safety+reports) | `app/(tabs)/map.tsx` |
| Map Web fallback | `app/(tabs)/map.web.tsx` |
| Route planning | `app/(tabs)/route.tsx` |
| Garage | `app/(tabs)/garage.tsx` |
| Communities list | `app/(tabs)/communities.tsx` |
| Profile | `app/(tabs)/profile.tsx` |
| Login | `app/auth/login.tsx` |
| Register | `app/auth/register.tsx` |
| Forgot password | `app/auth/forgot-password.tsx` |
| Onboarding | `app/onboarding.tsx` |
| Add motorcycle | `app/add-motorcycle.tsx` |
| Saved routes | `app/saved-routes.tsx` |
| Report create | `app/report/create.tsx` |
| Achievements | `app/achievements/index.tsx` |
| Settings | `app/settings/index.tsx` |
| Community detail | `app/communities/[slug].tsx` |
| Leaderboard | `app/leaderboard/index.tsx` |

### Screens NOT Done (15)
- Reset password, Route detail, Navigation mode, Post detail, Chat, Report detail, My reports, Challenges, Motorcycle edit, Motorcycle stats, Account settings, Notification settings, Privacy settings, About

### Components Done (14)
GlassCard, AppButton, ScreenHeader, StatCard, ModeSelector, ColoredRoute, ReportMarker, SafetyModeToggle, WeatherCard, WeatherBadge, MotorcycleCard, RouteCompareCard, LoadingScreen, EmptyState

### Components NOT Done (16)
InputField, SelectField, DatePicker, ImagePicker, Toast/Snackbar, ErrorBoundary, PostCard, CommentCard, LeaderboardRow, BadgeCard, ChallengeCard, UserLocationMarker, RouteInfoPanel, MapControls, MapLegend, CommunityCard

---

## MODULE 10: TESTING -- NOT STARTED

All tasks pending.

## MODULE 11: DEVOPS -- PARTIAL

| Task | Status |
|------|--------|
| Dockerfile | [x] |
| docker-compose.yml | [x] |
| Alembic config files | [x] |
| .env.example | [x] |
| GitHub Actions CI | [ ] |
| Kubernetes | [ ] |
| Env files | [ ] |
| Monitoring | [ ] |
| Mobile build pipeline | [ ] |

## MODULE 12: DOCUMENTATION -- NOT STARTED

All tasks pending.

---

## CURRENT TOTALS

| Category | Count |
|----------|-------|
| API Endpoints | 54 |
| Database Tables | 18 |
| SQL Migrations | 11 |
| Mobile Screens | 18 |
| Mobile Components | 14 |
| Backend Services | 8 |
| Middleware | 3 |

---

---

# PART 2: DETAILED REMAINING IMPLEMENTATION PLAN

---

## INTENTION & VISION

MotoMap is a **motorcycle-first** navigation and community app for Turkey. The core value proposition:
1. **Weather-aware routing** -- riders see real-time road safety based on weather, not just traffic
2. **Lane-splitting intelligence** -- the only app that calculates lane-split-eligible segments
3. **Community safety** -- crowdsourced road reports (potholes, oil spills, police) keep riders safe
4. **Gamification** -- keeps riders engaged, reporting hazards, and helping each other

The remaining work focuses on: (a) making the app truly end-to-end functional (dynamic routing, badge awards), (b) testing to ensure production quality, (c) DevOps for deployment, (d) the remaining mobile screens.

---

## ARCHITECTURE REFERENCE

```
Backend Stack:
  Python 3.13 / FastAPI / async SQLAlchemy / asyncpg / PostgreSQL 16 / Redis 7

Mobile Stack:
  React Native 0.81 / Expo 54 / TypeScript / Expo Router v6

Routing Engine:
  motomap/ package -- uses NetworkX + OSMnx for graph-based routing
  3 modes: standart (fastest), viraj_keyfi (curvy fun), guvenli (safest)

Weather:
  motomap/weather/ -- OpenWeatherMap API, Redis-cached, road condition assessment
```

---

## CODE CONVENTIONS (MUST FOLLOW)

### Backend Python Conventions

**Import order:** stdlib -> third-party (fastapi, sqlalchemy, pydantic) -> internal (api.database, api.models, api.services, api.routes, api.core)

**Model file template:**
```python
"""Description database model."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, Float, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from api.database import Base

class MyModel(Base):
    __tablename__ = "my_models"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
```

**Service file template:**
```python
"""Description service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from api.models.my_model import MyModel

class MyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, name: str) -> MyModel:
        entity = MyModel(user_id=user_id, name=name)
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def get_by_id(self, id: UUID) -> Optional[MyModel]:
        result = await self.db.execute(select(MyModel).where(MyModel.id == id))
        return result.scalar_one_or_none()
```

**Route file template:**
```python
"""Description API endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.routes.auth import get_current_user
from api.services.my_service import MyService

router = APIRouter(prefix="/api/my-resource", tags=["my-resource"])

class MyResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    model_config = {"from_attributes": True}

class CreateRequest(BaseModel):
    name: str = Field(..., max_length=200)

@router.get("", response_model=List[MyResponse])
async def list_items(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = MyService(db)
    items = await svc.list_for_user(user.id, limit, offset)
    return [MyResponse.model_validate(i) for i in items]

@router.post("", response_model=MyResponse, status_code=status.HTTP_201_CREATED)
async def create_item(request: CreateRequest, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = MyService(db)
    item = await svc.create(user_id=user.id, name=request.name)
    return MyResponse.model_validate(item)
```

**Gamification wiring pattern (fire-and-forget, NEVER block main operation):**
```python
try:
    gam = GamificationService(db)
    await gam.award_points(user.id, 5, "reason_string", "category", "reference_type", reference_id)
except Exception:
    pass
```

**Registration steps for a new module:**
1. Create model in `api/models/my_model.py`
2. Add import to `api/models/__init__.py` and add to `__all__`
3. Create service in `api/services/my_service.py`
4. Create routes in `api/routes/my_routes.py`
5. In `api/main.py`: import router and add `app.include_router(my_router)`
6. Create SQL migration in `migrations/NNN_create_my_table.sql`

### Mobile React Native Conventions

**Import order:** react -> react-native -> expo -> local components -> local utils/context -> theme

**Screen template:**
```tsx
import { useCallback, useEffect, useState } from "react";
import { ActivityIndicator, FlatList, StyleSheet, Text, View } from "react-native";
import ScreenHeader from "../../components/ScreenHeader";
import GlassCard from "../../components/GlassCard";
import { colors, spacing, radius } from "../../theme";
import { apiRequest } from "../../utils/api";
import { useAuth } from "../../context/AuthContext";

type ItemType = { id: string; name: string };

export default function MyScreen() {
  const { token } = useAuth();
  const [items, setItems] = useState<ItemType[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiRequest<ItemType[]>("/api/my-resource", { token });
      setItems(data);
    } catch {}
    setLoading(false);
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (loading) {
    return (
      <View style={styles.container}>
        <ScreenHeader title="My Screen" />
        <ActivityIndicator size="large" color={colors.accentBlue} style={{ marginTop: spacing.xl }} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScreenHeader title="My Screen" />
      <FlatList
        data={items}
        keyExtractor={(i) => i.id}
        contentContainerStyle={styles.list}
        renderItem={({ item }) => (
          <GlassCard style={styles.card}>
            <Text style={styles.name}>{item.name}</Text>
          </GlassCard>
        )}
        ListEmptyComponent={<Text style={styles.empty}>No items</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  list: { padding: spacing.md, paddingBottom: 100 },
  card: { marginBottom: spacing.sm, padding: spacing.md },
  name: { fontSize: 14, fontWeight: "600", color: colors.textPrimary },
  empty: { fontSize: 14, color: colors.textSecondary, textAlign: "center", marginTop: spacing.xl },
});
```

**Theme tokens available:**
```
colors: bgPrimary (#081C50), bgSecondary (#0A2461), bgTertiary (#0D2D6B),
  accentBlue (#3D8BFF), accentBlueDark (#2D6FE8), accentBlueGlow (rgba),
  success (#22C55E), warning (#F59E0B), danger (#EF4444), info (#A78BFA),
  textPrimary (#FFF), textSecondary (rgba 0.7), textTertiary (rgba 0.45),
  surfaceGlass (rgba 0.08), surfaceBorder (rgba 0.15), googleBlue (#4285F4)

spacing: xs=4, sm=8, md=14, lg=20, xl=28, xxl=40, screenPadding=20, topSafeArea=56
radius: sm=8, md=14, lg=18, xl=22, pill=50
typography: heroLarge, heroMedium, h1, h2, h3, body, bodyBold, caption, label, stat
shadows: card, panel; glowShadow(color) function
```

**API call pattern:**
```ts
const data = await apiRequest<ResponseType>("/api/endpoint", {
  method: "POST",
  token,
  body: { key: value },
});
```

**Navigation:**
```ts
import { router } from "expo-router";
router.push("/communities/my-slug");
router.replace("/auth/login" as never);
router.back();

// For dynamic routes, use useLocalSearchParams:
import { useLocalSearchParams } from "expo-router";
const { slug } = useLocalSearchParams<{ slug: string }>();
```

**Component export:** Always `export default function ComponentName()` (not named export)

**No icon libraries used.** All icons are emoji strings: "\uD83D\uDCAC", "\uD83D\uDCF8", etc.

---

---

# REMAINING TASKS -- EXHAUSTIVE DETAIL

---

## TASK R1: DYNAMIC ROUTE GENERATION API
**Priority:** HIGH
**Why:** Without this, the app can only show pre-computed demo routes. This is THE core feature -- users need to enter origin/destination and get a live route.

### What exists today
- `motomap/algorithm.py` contains the full routing engine with `ucret_opsiyonlu_rota_hesapla()` as the main entry point
- `website/generate_route.py` and `app/api/demo_route.py` show how the algorithm is called today
- The algorithm works on a NetworkX MultiDiGraph built from OSM data via `motomap_graf_olustur(place)`
- It requires: graph (pre-built), source node ID, target node ID, driving mode, toll preference, motorcycle CC

### What needs to be built

**File to create: `api/routes/routing.py`**

```python
# Endpoint: POST /api/route/generate
# 
# Request body:
#   origin_lat: float (-90..90)
#   origin_lng: float (-180..180)  
#   destination_lat: float (-90..90)
#   destination_lng: float (-180..180)
#   mode: str = "standart"  -- one of: "standart", "viraj_keyfi", "guvenli"
#   toll_preference: str = "ucretli_serbest"  -- one of: "ucretli_serbest", "ucretsiz"
#   motor_cc: Optional[int] = None  -- engine displacement in cc (affects slope penalties)
#   include_weather: bool = True  -- whether to fetch weather and apply safety overlay
#   include_alternatives: bool = True  -- whether to include toll-free alternative
#
# Response:
#   RouteResponse {
#     selected_route: {
#       coordinates: List[{lat, lng}],  -- polyline points from graph nodes
#       total_distance_m: int,
#       total_duration_s: int,
#       fun_curves: int,
#       dangerous_curves: int,
#       high_risk_segments: int,
#       lane_split_m: int,
#       avg_grade: float,
#       includes_toll: bool,
#       includes_ferry: bool,
#     },
#     alternative_route: Optional[same structure],  -- toll-free alternative if available
#     segments: List[SegmentResponse],  -- per-segment safety data for ColoredRoute component
#     weather: Optional[{
#       condition: str,
#       temperature_celsius: float,
#       overall_safety_score: float,
#       lane_splitting_modifier: float,
#       warnings: List[str],
#     }],
#     mode: str,
#     toll_preference: str,
#   }
```

### Implementation steps in detail

1. **Graph management:** The graph build (`motomap_graf_olustur`) is expensive (downloads OSM data, adds elevation, computes grades). It must be built ONCE at app startup and cached in a module-level variable. Use a startup event or the lifespan context in `main.py`.

```python
# In api/routes/routing.py:
import osmnx as ox
from motomap import motomap_graf_olustur
from motomap.algorithm import add_travel_time_to_graph, ucret_opsiyonlu_rota_hesapla

_graph = None  # Module-level cache

async def get_graph():
    """Get or build the routing graph. Called once, cached forever."""
    global _graph
    if _graph is None:
        # CRITICAL: This blocks for 30-120 seconds on first call.
        # In production, pre-build and serialize to disk (pickle).
        # The place string determines the coverage area.
        _graph = motomap_graf_olustur("Istanbul, Turkey")
        _graph = add_travel_time_to_graph(_graph)
    return _graph
```

2. **Coordinate-to-node mapping:** Use `osmnx.nearest_nodes()` to find the closest graph node to the user's lat/lng. This is fast (milliseconds).

```python
origin_node = ox.nearest_nodes(graph, origin_lng, origin_lat)  # NOTE: lng first, lat second
dest_node = ox.nearest_nodes(graph, dest_lng, dest_lat)
```

3. **Route computation:** Call `ucret_opsiyonlu_rota_hesapla()`. This returns a dict with `secilen_rota` (selected route) containing node IDs and stats.

4. **Node-to-coordinate conversion:** Convert the node ID list to lat/lng pairs:
```python
nodes = result["secilen_rota"]["nodes"]
coordinates = [{"lat": graph.nodes[n]["y"], "lng": graph.nodes[n]["x"]} for n in nodes]
```

5. **Edge extraction for segment analysis:** For each consecutive pair of nodes, get the edge data:
```python
edges = []
for i in range(len(nodes) - 1):
    u, v = nodes[i], nodes[i+1]
    edge_data = graph[u][v][0]  # first edge in multigraph
    edges.append(edge_data)
```

6. **Weather integration (optional):** If `include_weather=True`, fetch weather along route and apply segment analysis:
```python
from motomap.weather import WeatherService, RoadConditionAssessor
from motomap.routing import RouteSegmentAnalyzer

coord_tuples = [(c["lat"], c["lng"]) for c in coordinates]
async with WeatherService() as ws:
    worst_weather = await ws.get_worst_weather_along_route(coord_tuples)

assessor = RoadConditionAssessor()
assessment = assessor.assess(worst_weather)

analyzer = RouteSegmentAnalyzer(assessor)
segments = analyzer.analyze_route(edges, weather=worst_weather)
```

7. **Register in main.py:**
```python
from api.routes.routing import router as routing_router
app.include_router(routing_router)
```

### Critical dependency
- `osmnx` and `networkx` must be in `requirements.txt` (check if already present)
- Graph build requires internet access on first run (OSM download)
- For production: pre-build the graph and serialize to disk, load at startup

### Error cases to handle
- Origin/destination outside graph coverage area -> 400 "Location outside coverage area"
- No route found between points -> 404 "No route found"
- Graph not yet loaded -> 503 "Routing engine initializing"
- Weather API failure -> return route without weather data (degrade gracefully)

---

## TASK R2: PASSWORD RESET FLOW
**Priority:** HIGH
**Why:** Users who forget passwords are permanently locked out.

### Backend changes

**Update `api/services/auth.py`:**

Add two new methods to `AuthService`:

```python
async def request_password_reset(self, email: str) -> str:
    """
    Generate a password reset token and store it.
    
    Logic:
    1. Find user by email (case-insensitive, stripped)
    2. If user not found, STILL return success (don't leak email existence)
    3. Generate a 6-digit numeric code: secrets.randbelow(900000) + 100000
    4. Store in Redis: key="password_reset:{email}", value=str(code), TTL=900 seconds (15 min)
       - If Redis unavailable, store in a module-level dict with timestamp
    5. In production: send email via SendGrid/SES
       - For now: log.info(f"Password reset code for {email}: {code}")
    6. Return the code (for testing only; in production, never return it)
    """
    
async def reset_password(self, email: str, code: str, new_password: str) -> bool:
    """
    Validate reset code and update password.
    
    Logic:
    1. Look up Redis key "password_reset:{email}"
    2. If not found or expired -> raise InvalidTokenError("Invalid or expired code")
    3. If code doesn't match -> raise InvalidTokenError
    4. Validate new password (min 8 chars, same rules as register)
    5. Hash new password with bcrypt
    6. Update user.password_hash
    7. Delete the Redis key
    8. Delete ALL user sessions (force re-login everywhere)
    9. Return True
    """
```

**Update `api/routes/auth.py`:**

Add two new endpoints:

```python
# POST /api/auth/forgot-password
# Body: { "email": "user@example.com" }
# Response: { "message": "If an account with that email exists, a reset code has been sent." }
# ALWAYS returns 200 (never reveal if email exists)

# POST /api/auth/reset-password
# Body: { "email": "user@example.com", "code": "123456", "new_password": "newpass123" }
# Response: { "message": "Password has been reset successfully." }
# Returns 400 if code invalid/expired
```

**Pydantic models:**
```python
class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., max_length=255)

class ResetPasswordRequest(BaseModel):
    email: str = Field(..., max_length=255)
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, max_length=100)
```

### Mobile changes

**Update `app/mobile/app/auth/forgot-password.tsx`:**
- Currently simulates success with setTimeout. Replace with actual API call:
```ts
await apiRequest("/api/auth/forgot-password", { method: "POST", body: { email } });
```
- Add a code input field after success (6-digit OTP input)
- Add "Verify Code" button that calls `/api/auth/reset-password`

**Create `app/mobile/app/auth/reset-password.tsx`:**
- Or: extend the forgot-password screen with a second step (code + new password)

---

## TASK R3: BADGE AUTO-AWARD SYSTEM
**Priority:** HIGH
**Why:** Badges are seeded but never awarded. Users complete actions but never see badges appear.

### What the `award_badge()` method already does
It exists in `api/services/gamification.py` -- takes `user_id` and `badge_id`, checks if already earned, creates `UserBadge`, awards bonus points. It works correctly.

### What's missing: the CHECK that triggers badge awards

**Update `api/services/gamification.py`, add method:**

```python
async def check_and_award_badges(self, user_id: UUID) -> List[str]:
    """
    Check all unearned badges and award any where requirements are met.
    Called automatically after award_points().
    
    Returns list of newly awarded badge IDs.

    Logic:
    1. Get all badges the user does NOT have:
       SELECT b.* FROM badges b
       WHERE b.id NOT IN (SELECT badge_id FROM user_badges WHERE user_id = :user_id)
       AND b.is_secret = FALSE

    2. Get user stats (need to query from multiple tables):
       - routes_completed: COUNT from route_history WHERE user_id AND completed=true
       - unique_routes: COUNT DISTINCT (origin_label, destination_label) from route_history
       - total_km: SUM(distance_m)/1000 from route_history WHERE completed=true
       - reports_submitted: COUNT from road_reports WHERE reporter_id
       - posts_created: COUNT from community_posts WHERE author_id
       - help_given: COUNT from community_posts WHERE author_id AND type IN ('help_offer')
       - streak_days: user_points.current_streak_days

    3. For each unearned badge, compare requirement_type and requirement_value:
       badge.requirement_type == "routes_completed" -> check routes_completed >= badge.requirement_value
       badge.requirement_type == "unique_routes" -> check unique_routes >= badge.requirement_value
       badge.requirement_type == "total_km" -> check total_km >= badge.requirement_value
       badge.requirement_type == "reports_submitted" -> check reports_submitted >= badge.requirement_value
       badge.requirement_type == "posts_created" -> check posts_created >= badge.requirement_value
       badge.requirement_type == "help_given" -> check help_given >= badge.requirement_value
       badge.requirement_type == "streak_days" -> check streak_days >= badge.requirement_value

    4. For each met badge, call self.award_badge(user_id, badge.id)
    
    5. For each awarded badge, create a notification:
       NotificationService(self.db).create(
           user_id, NotificationType.BADGE_EARNED,
           title=f"Yeni Rozet: {badge.name_tr}",
           body=badge.description_tr,
           data={"badge_id": badge.id}
       )

    6. Return list of awarded badge IDs
    """
```

**Update `award_points()` method:**
At the end, after level calculation, add:
```python
# Check for level-up notification
old_level = ... # save before update
if user_points.level > old_level:
    try:
        from api.services.notifications import NotificationService
        ns = NotificationService(self.db)
        level_names = {1: "Caylak", 2: "Gezgin", 3: "Deneyimli", 4: "Usta", 5: "Efsane", 6: "Tanri"}
        await ns.create(user_id, NotificationType.LEVEL_UP,
            title=f"Seviye Atladin: {level_names.get(user_points.level, '')}",
            body=f"Artik seviye {user_points.level} suruculerdensin!",
            data={"level": user_points.level}
        )
    except Exception:
        pass

# Check for new badge awards
try:
    await self.check_and_award_badges(user_id)
except Exception:
    pass
```

### Import needed
```python
from api.models.route_history import RouteHistory
from api.models.road_report import RoadReport
from api.models.community import CommunityPost, PostType
from api.models.notification import NotificationType
```

---

## TASK R4: PYTHON TEST INFRASTRUCTURE
**Priority:** HIGH
**Why:** Zero tests = zero confidence for deployment

### Files to create

**`pytest.ini`:**
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

**`tests/__init__.py`:** Empty file

**`tests/conftest.py`:**
```python
"""
Shared test fixtures for the entire test suite.

KEY DECISIONS:
- Use SQLite for unit tests (fast, no external deps)
- Use PostgreSQL service container for integration tests
- Each test gets its own transaction that rolls back (clean isolation)
- A test user + auth token fixture is provided for authenticated endpoint tests

FIXTURES:
  db_session -- async SQLAlchemy session with auto-rollback
  client -- httpx AsyncClient bound to FastAPI app with overridden get_db
  auth_headers -- dict with {"Authorization": "Bearer <token>"} for a test user
  test_user -- User ORM instance for the authenticated test user
"""

import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from api.database import Base, get_db
from api.main import app
from api.core.security import hash_password, create_access_token
from api.models.user import User

# Use SQLite for fast unit tests
TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()

@pytest.fixture
async def db_session(engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        async with session.begin():
            yield session
            await session.rollback()

@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(db_session):
    user = User(email="test@motomap.dev", password_hash=hash_password("TestPass123"), display_name="Test Rider")
    db_session.add(user)
    await db_session.flush()
    return user

@pytest.fixture
async def auth_headers(test_user):
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}
```

**`tests/unit/__init__.py`:** Empty

**`tests/unit/test_security.py`:**
```python
"""
Tests for api/core/security.py

Test cases:
  test_hash_and_verify_password -- hash a password, verify it matches
  test_verify_wrong_password -- verify returns False for wrong password  
  test_create_access_token -- create token, decode it, check sub and type
  test_create_refresh_token -- create refresh token, check type is "refresh"
  test_decode_expired_token -- create token with past expiry, decode returns None
  test_decode_invalid_token -- decode garbage string returns None
"""
```

**`tests/unit/test_weather_assessment.py`:**
```python
"""
Tests for motomap/weather/assessment.py

Test cases:
  test_clear_dry_conditions -- WeatherData with clear sky -> safety_score near 1.0, surface=DRY
  test_heavy_rain -- precipitation_mm=20 -> safety_score < 0.5, surface=FLOODED, has warnings
  test_fog_low_visibility -- visibility_meters=200 -> visibility_factor < 0.3, has fog warning  
  test_strong_wind -- wind_speed_ms=18 -> wind_risk_factor < 0.4, has wind warning
  test_freezing_rain -- temp=-2, precipitation -> surface=ICY, grip_factor very low
  test_lane_splitting_rain -- lane_splitting_modifier should be < 0.5 in rain
  test_lane_splitting_dry -- lane_splitting_modifier should be > 0.8 in dry/clear
  test_segment_assessment_tunnel -- has_tunnel=True should give min 0.8 safety
"""
```

**`tests/integration/__init__.py`:** Empty

**`tests/integration/test_auth_flow.py`:**
```python
"""
Tests for the complete auth flow via HTTP endpoints.

Test flow:
  1. POST /api/auth/register -> 201, returns user + tokens
  2. GET /api/auth/me with access token -> 200, returns user data
  3. POST /api/auth/refresh with refresh token -> 200, returns new tokens
  4. POST /api/auth/change-password -> 200
  5. POST /api/auth/login with new password -> 200
  6. POST /api/auth/logout -> 200
  7. GET /api/auth/me with old token -> 401

Edge cases:
  - Register with existing email -> 400
  - Login with wrong password -> 401
  - Register with short password -> 422
  - Refresh with access token (not refresh) -> 401
"""
```

**`tests/integration/test_communities.py`:**
```python
"""
Test community lifecycle.

Test flow:
  1. POST /api/communities (create) -> 201
  2. GET /api/communities/{slug} -> 200
  3. POST /api/communities/{slug}/join -> 200
  4. POST /api/communities/{slug}/posts (create post) -> 201
  5. GET /api/communities/{slug}/posts -> 200, contains the post
  6. POST /api/communities/{slug}/posts/{id}/comments -> 201
  7. GET /api/communities/{slug}/posts/{id}/comments -> 200, contains the comment
  8. DELETE /api/communities/{slug}/leave -> 200
  9. POST /api/communities/{slug}/posts (after leave) -> 400 "Not a member"
"""
```

**`tests/integration/test_reports.py`:**
```python
"""
Test road report lifecycle.

Test flow:
  1. POST /api/reports (create report) -> 201
  2. GET /api/reports?lat=X&lng=Y&radius_km=5 -> 200, contains the report
  3. POST /api/reports/{id}/vote (upvote) -> 200
  4. Verify vote_count increased
  5. POST /api/reports/{id}/vote (duplicate) -> 400
  6. POST /api/reports/{id}/resolve -> 200
"""
```

**`tests/integration/test_gamification.py`:**
```python
"""
Test gamification integration.

Test flow:
  1. POST /api/reports (create) -> verify points increased by 5
  2. POST /api/communities/{slug}/posts (create post) -> verify points increased by 3
  3. POST /api/history (record route) -> POST /api/history/{id}/complete -> verify points increased by 10
  4. GET /api/gamification/points -> verify total_points = 18
  5. GET /api/gamification/leaderboard -> user appears
"""
```

### Packages needed
Add to `requirements.txt`: `pytest`, `pytest-asyncio`, `httpx`, `aiosqlite`

---

## TASK R5: GITHUB ACTIONS CI PIPELINE
**Priority:** HIGH
**Why:** No automated checks = broken code can merge to main

### File to create: `.github/workflows/ci.yml`

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  python-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.13" }
      - run: pip install ruff
      - run: ruff check api/ motomap/ tests/

  python-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: motomap_test
        ports: ["5432:5432"]
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
      redis:
        image: redis:7
        ports: ["6379:6379"]
        options: --health-cmd "redis-cli ping" --health-interval 10s --health-timeout 5s --health-retries 5
    env:
      DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/motomap_test
      REDIS_URL: redis://localhost:6379
      JWT_SECRET_KEY: test-secret-key-for-ci
      OPENWEATHER_API_KEY: test-key
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.13" }
      - run: pip install -r requirements.txt pytest pytest-asyncio aiosqlite httpx
      - run: pytest tests/ -v --tb=short

  typescript-check:
    runs-on: ubuntu-latest
    defaults:
      run: { working-directory: app/mobile }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20", cache: "npm", cache-dependency-path: app/mobile/package-lock.json }
      - run: npm ci
      - run: npx tsc --noEmit

  docker-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t motomap-api .
```

---

## TASK R6: POST AND COMMENT LIKES
**Priority:** MEDIUM
**Why:** Community engagement needs likes. Posts show `like_count` but there's no way to increment it.

### Migration to create: `migrations/012_create_likes.sql`
```sql
CREATE TABLE IF NOT EXISTS post_likes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id UUID NOT NULL REFERENCES community_posts(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, post_id)
);

CREATE TABLE IF NOT EXISTS comment_likes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    comment_id UUID NOT NULL REFERENCES post_comments(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, comment_id)
);
```

### Model to create: `api/models/like.py`
```python
# PostLike: id, user_id, post_id, created_at
# CommentLike: id, user_id, comment_id, created_at
# Both with UniqueConstraint on (user_id, target_id)
```

### Service updates: `api/services/community.py`
Add methods:
```python
async def toggle_post_like(self, post_id: UUID, user_id: UUID) -> bool:
    """Toggle like. Returns True if liked, False if unliked.
    1. Check if PostLike exists for (user_id, post_id)
    2. If exists: delete it, decrement post.like_count
    3. If not exists: create it, increment post.like_count
    4. Commit and return new state
    """

async def toggle_comment_like(self, comment_id: UUID, user_id: UUID) -> bool:
    """Same pattern for comments."""
```

### Route updates: `api/routes/communities.py`
```python
# POST /api/communities/{slug}/posts/{post_id}/like -> {"liked": true/false, "like_count": N}
# POST /api/communities/{slug}/posts/{post_id}/comments/{comment_id}/like -> same
```

### Mobile updates
- Add a heart/like button to PostCard in `communities/[slug].tsx`
- On tap: call API, toggle local state optimistically

---

## TASK R7: MISSING MOBILE SCREENS
**Priority:** MEDIUM

### R7a: Post Detail Screen `app/mobile/app/communities/post/[id].tsx`

**URL params:** `useLocalSearchParams<{ id: string }>()`

**What it shows:**
- Full post content (no truncation)
- Author info, post type icon, timestamp
- Like button with count
- FlatList of comments from `/api/communities/{slug}/posts/{post_id}/comments`
- Comment composer at bottom (TextInput + "Gonder" button)
- Each comment: content, author, timestamp, like button

**Problem:** The API routes comments under `/api/communities/{slug}/posts/{post_id}/comments` but this screen only has `post_id`, not `slug`. Two options:
1. Pass `slug` as a second param: `router.push({ pathname: "/communities/post/[id]", params: { id: post.id, slug } })`
2. Add a standalone endpoint: `GET /api/posts/{post_id}` that returns post + community slug

**Recommendation:** Option 1 (simpler, no backend change).

### R7b: Report Detail Screen `app/mobile/app/report/[id].tsx`

**URL params:** `useLocalSearchParams<{ id: string }>()`

**What it shows:**
- Map with a single marker at report location
- Report type icon + severity badge (color-coded: low=green, medium=yellow, high=orange, critical=red)
- Title, description, photos (if any)
- Vote section: upvote/downvote buttons with counts
- "Cozuldu" (Resolved) button if user is the reporter
- Status badge: "Aktif" / "Dogrulandi" / "Cozuldu" / "Suresi Doldu"

**API calls:**
```ts
GET /api/reports/{id}  -- load report
POST /api/reports/{id}/vote { vote: "up" | "down" }  -- vote
POST /api/reports/{id}/resolve  -- resolve
```

### R7c: My Reports Screen `app/mobile/app/my-reports.tsx`

**Needs new backend endpoint:** `GET /api/reports/my`

**Backend change in `api/routes/road_reports.py`:**
```python
@router.get("/my", response_model=List[ReportResponse])
async def get_my_reports(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # IMPORTANT: This route MUST be registered BEFORE /{report_id}
    # otherwise FastAPI interprets "my" as a report_id UUID and fails
    svc = RoadReportService(db)
    reports = await svc.get_user_reports(user.id, limit, offset)
    return [ReportResponse.model_validate(r) for r in reports]
```

**Service change in `api/services/road_reports.py`:**
```python
async def get_user_reports(self, user_id: UUID, limit: int = 20, offset: int = 0) -> List[RoadReport]:
    result = await self.db.execute(
        select(RoadReport)
        .where(RoadReport.reporter_id == user_id)
        .order_by(RoadReport.created_at.desc())
        .offset(offset).limit(limit)
    )
    return list(result.scalars().all())
```

**Mobile screen:** FlatList of user's reports with status badges and tap-to-detail navigation.

### R7d: Challenges Screen `app/mobile/app/challenges/index.tsx`

**Needs new backend endpoint:** `GET /api/gamification/challenges`

**Backend change in `api/routes/gamification.py`:**
```python
@router.get("/challenges", response_model=List[ChallengeResponse])
async def get_active_challenges(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = GamificationService(db)
    challenges = await svc.get_active_challenges(user.id)
    return challenges
```

**Service method to add:**
```python
async def get_active_challenges(self, user_id: UUID) -> List[dict]:
    """
    Get all active challenges with user's progress.
    Join challenges with user_challenges to get progress.
    Return: [{id, title, title_tr, description_tr, type, target_value, current_value, points_reward, 
              starts_at, ends_at, is_completed}]
    """
```

**Mobile screen:**
- List of challenge cards
- Each card: title, description, progress bar (current/target), points reward, deadline
- Completed challenges greyed out with checkmark

### R7e: Route Detail Screen `app/mobile/app/route/[id].tsx`

**URL params:** `useLocalSearchParams<{ id: string }>()`

**What it shows:**
- Map with ColoredRoute showing the route
- Stats panel: distance, duration, fun curves, dangerous curves, lane split km, safety score
- Weather section if available
- Favorite toggle (heart icon)
- "Tekrar Git" (Go Again) button -> navigates to navigation mode
- "Paylas" (Share) button

**API call:** `GET /api/history` then filter by ID, or add `GET /api/history/{route_id}`

**Backend: add to `api/routes/history.py`:**
```python
@router.get("/{route_id}", response_model=RouteHistoryResponse)
async def get_route(route_id: UUID, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = RouteHistoryService(db)
    # Need to add get_by_id method to service
    entry = await svc.get_by_id(route_id, user.id)
    if not entry:
        raise HTTPException(404, "Route not found")
    return RouteHistoryResponse.model_validate(entry)
```

**NOTE:** The `RouteHistory` model stores origin/destination lat/lng but NOT the full route polyline. To show the route on a map, either:
1. Store the polyline in RouteHistory (add `polyline TEXT` column) -- RECOMMENDED
2. Re-generate the route from origin/destination on demand

### R7f: Navigation Mode `app/mobile/app/route/navigation.tsx`

**This is the most complex screen.** Full-screen map with:
- ColoredRoute displayed
- User's live location (needs `expo-location` watch)
- Turn-by-turn instructions overlay at top
- Speed display, ETA, distance remaining at bottom
- "Navigasyonu Bitir" (End Navigation) button
- On end: call POST `/api/history/{id}/complete` -> award 10 points

**This screen requires:**
- `expo-location` foreground location permission + watchPositionAsync
- Route instructions data (currently not generated by backend -- would need turn-by-turn instruction generation added to the routing API)
- Map camera following user location

**Recommendation:** Implement as a simplified version first (map + live location + route + end button) without turn-by-turn instructions. Turn-by-turn requires significant backend work (instruction generation from OSM node/edge data).

### R7g-R7j: Settings Sub-screens

**`settings/account.tsx`:**
- Display name edit (PATCH /api/profile)
- Email display (read-only for now)
- Change password button -> call POST /api/auth/change-password
- Delete account button -> confirm dialog -> call DELETE /api/profile (needs new endpoint)

**`settings/notifications.tsx`:**
- Toggle switches for each notification type
- Call PATCH /api/profile/settings with notification preferences
- Push permission toggle (request Expo push permissions)

**`settings/privacy.tsx`:**
- Profile visibility toggle
- Activity visibility toggle
- "Verilerimi Indir" (Download Data) button
- "Hesabimi Sil" (Delete Account) button

**`settings/about.tsx`:**
- App name, version (from app.json)
- "Gizlilik Politikasi" link
- "Kullanim Kosullari" link
- "Iletisim" email link

---

## TASK R8: REUSABLE COMPONENTS
**Priority:** MEDIUM

### R8a: InputField Component

**File: `app/mobile/components/InputField.tsx`**

**Purpose:** Every form screen (login, register, report create, etc.) manually creates TextInput with identical styling. Extract into reusable component.

**Props:**
```ts
type Props = {
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  placeholder?: string;
  secureTextEntry?: boolean;  // password toggle
  keyboardType?: KeyboardTypeOptions;
  autoCapitalize?: "none" | "sentences" | "words" | "characters";
  error?: string | null;  // shows red error text below input
  icon?: string;  // emoji icon
  editable?: boolean;
  multiline?: boolean;
  maxLength?: number;
};
```

**Visual:** Label text above, glass-style input (surfaceGlass background, surfaceBorder), error text below in danger color.

### R8b: PostCard Component

**File: `app/mobile/components/PostCard.tsx`**

**Purpose:** Post rendering is duplicated in `communities/[slug].tsx`. Extract for reuse.

**Props:**
```ts
type Props = {
  post: Post;
  onPress?: () => void;  // navigate to detail
  onLike?: () => void;
  truncateContent?: boolean;  // default true, show first 4 lines
};
```

### R8c: Toast/Snackbar Component

**File: `app/mobile/components/Toast.tsx`**

**Purpose:** Show success/error/info messages to user. Currently no feedback mechanism exists.

**Implementation:** Use React Context + animated View that slides in from top. Methods: `showToast({ message, type: "success"|"error"|"info", duration?: number })`.

### R8d: ErrorBoundary Component

**File: `app/mobile/components/ErrorBoundary.tsx`**

**Purpose:** Catch JS errors and show recovery UI instead of white screen.

**Implementation:** Class component with `componentDidCatch`. Shows "Bir hata olustu. Tekrar dene." with retry button.

---

## TASK R9: ENHANCED HEALTH CHECK
**Priority:** MEDIUM

**Update `api/main.py`:**
```python
@app.get("/health")
async def health_check():
    """
    Check connectivity to all dependencies.
    Returns: { 
      status: "ok"|"degraded",
      api: "ok",
      database: "ok"|"error", 
      redis: "ok"|"error",
      version: "1.0.0",
    }
    """
    db_ok = False
    redis_ok = False
    
    # Check DB: execute "SELECT 1"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            db_ok = True
    except: pass
    
    # Check Redis: PING
    try:
        if cache._redis:
            await cache._redis.ping()
            redis_ok = True
    except: pass
    
    overall = "ok" if (db_ok and redis_ok) else "degraded"
    return {"status": overall, "api": "ok", "database": "ok" if db_ok else "error", 
            "redis": "ok" if redis_ok else "error", "version": "1.0.0"}
```

---

## TASK R10: REPORT CLUSTERING FOR MAP
**Priority:** MEDIUM

**Why:** When many reports exist in an area, the map becomes cluttered with overlapping markers.

**Update `app/mobile/app/(tabs)/map.tsx`:**

**Approach:** Grid-based clustering. When map zoom is below a threshold, group nearby reports into clusters.

```ts
function clusterReports(reports: Report[], zoomLevel: number): (Report | Cluster)[] {
  if (zoomLevel > 13) return reports;  // show individual markers at high zoom
  
  const gridSize = 0.01 * Math.pow(2, 15 - zoomLevel);  // adaptive grid
  const grid: Record<string, Report[]> = {};
  
  for (const r of reports) {
    const key = `${Math.floor(r.latitude / gridSize)}_${Math.floor(r.longitude / gridSize)}`;
    (grid[key] ||= []).push(r);
  }
  
  return Object.values(grid).map(group => {
    if (group.length === 1) return group[0];
    return {
      isCluster: true,
      count: group.length,
      latitude: group.reduce((s, r) => s + r.latitude, 0) / group.length,
      longitude: group.reduce((s, r) => s + r.longitude, 0) / group.length,
    };
  });
}
```

**Cluster marker:** Circle with count number. On tap: zoom into the cluster area.

---

## TASK R11: DOCKER PRODUCTION & DOCKERIGNORE
**Priority:** LOW

**`.dockerignore`:**
```
.git
.github
node_modules
app/mobile/node_modules
__pycache__
*.pyc
tests/
docs/
*.md
.env
.env.*
!.env.example
uploads/
```

**`docker-compose.prod.yml`:**
```yaml
# Differences from docker-compose.yml:
# - No volume mounts (baked into image)
# - restart: always on all services
# - Resource limits (mem_limit, cpus)
# - Production environment variables
# - No port exposure for postgres/redis (internal only)
# - Health checks on all services
```

---

## TASK R12: KUBERNETES MANIFESTS
**Priority:** LOW

**Files to create in `k8s/` directory:**
- `namespace.yaml` -- "motomap" namespace
- `configmap.yaml` -- non-secret config (REDIS_URL, LOG_LEVEL, etc.)
- `secrets.yaml` -- base64-encoded secrets (DB password, JWT key, API keys)
- `api-deployment.yaml` -- 2 replicas, resource limits (256Mi/500m), readiness/liveness probes on /health
- `api-service.yaml` -- ClusterIP service on port 8000
- `ingress.yaml` -- NGINX ingress with TLS, host: api.motomap.dev
- `redis-deployment.yaml` -- Single replica, 128Mi limit
- `postgres-statefulset.yaml` -- StatefulSet with PVC for data persistence

---

## TASK R13: MOBILE BUILD PIPELINE
**Priority:** LOW

**`.github/workflows/mobile-build.yml`:**
```yaml
# Triggers: push to main (with path filter: app/mobile/**)
# Jobs:
#   1. typecheck: npx tsc --noEmit
#   2. lint: npx eslint . (if configured)
#   3. test: npx jest --passWithNoTests
#   4. build: eas build --platform android --profile preview --non-interactive
```

**`eas.json`:**
```json
{
  "cli": { "version": ">= 12.0.0" },
  "build": {
    "development": { "distribution": "internal", "android": { "buildType": "apk" } },
    "preview": { "distribution": "internal", "android": { "buildType": "apk" } },
    "production": { "android": { "buildType": "app-bundle" } }
  }
}
```

---

## TASK R14: WEBSOCKET COMMUNITY CHAT
**Priority:** LOW
**Why:** Real-time chat is listed in TODO but is complex. Implement last.

**Backend: `api/routes/chat.py`**
```python
# WebSocket endpoint: /api/communities/{slug}/chat
# 
# Authentication: JWT token sent as first message or query param
# 
# Protocol:
#   Client -> Server: { "type": "message", "content": "text" }
#   Server -> Client: { "type": "message", "author_id": "...", "content": "text", "timestamp": "..." }
#   Server -> Client: { "type": "presence", "online_count": N }
#
# Backend pattern:
#   - Use FastAPI WebSocket endpoint
#   - Keep dict of active connections per community
#   - On message: broadcast to all connections in same community
#   - For multi-instance: use Redis pub/sub channel per community
```

**Mobile: `app/mobile/app/communities/chat/[id].tsx`**
```
- WebSocket connection to ws://API_URL/api/communities/{slug}/chat
- FlatList inverted for message display (newest at bottom)
- TextInput + Send button at bottom
- Auto-reconnect on disconnect
- Online user count display
```

---

## TASK R15: ALEMBIC AUTO-MIGRATIONS
**Priority:** LOW
**Why:** Currently using raw SQL migration files. Alembic provides auto-generation, versioning, and rollback.

**Steps:**
1. Start PostgreSQL (docker-compose up db)
2. Run all existing SQL migrations manually
3. Run `alembic revision --autogenerate -m "initial schema"` to generate an Alembic migration matching current state
4. Verify the generated migration matches all 18 tables
5. Add `alembic upgrade head` to docker-compose API entrypoint
6. Future: only use `alembic revision --autogenerate` for schema changes

---

## TASK R16: MONITORING (PROMETHEUS + SENTRY)
**Priority:** LOW

**`api/core/metrics.py`:**
```python
# Create Prometheus metrics:
#   REQUEST_COUNT = Counter("http_requests_total", "Total requests", ["method", "endpoint", "status"])
#   REQUEST_DURATION = Histogram("http_request_duration_seconds", "Request duration", ["method", "endpoint"])
#   ACTIVE_CONNECTIONS = Gauge("http_active_connections", "Active connections")
#   DB_POOL_SIZE = Gauge("db_pool_size", "DB connection pool size")

# Expose via /metrics endpoint (plaintext Prometheus format)
```

**Sentry integration in `api/main.py`:**
```python
import sentry_sdk
if os.getenv("SENTRY_DSN"):
    sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), traces_sample_rate=0.1)
```

---

## IMPLEMENTATION ORDER (RECOMMENDED)

```
Phase A (Critical Path -- enables core functionality):
  1. R1: Dynamic Route Generation API
  2. R2: Password Reset Flow
  3. R3: Badge Auto-Award System
  4. R4: Python Test Infrastructure
  5. R5: GitHub Actions CI

Phase B (Community & Engagement):
  6. R6: Post/Comment Likes
  7. R7a-R7c: Post Detail, Report Detail, My Reports screens
  8. R8a-R8d: InputField, PostCard, Toast, ErrorBoundary components
  9. R9: Enhanced Health Check

Phase C (Gamification & Navigation):
  10. R7d-R7f: Challenges, Route Detail, Navigation screens
  11. R10: Report Clustering

Phase D (Settings & Polish):
  12. R7g-R7j: Settings sub-screens
  13. R11: Docker production compose
  14. R12: Kubernetes manifests

Phase E (Scale & Monitor):
  15. R13: Mobile Build Pipeline
  16. R14: WebSocket Chat
  17. R15: Alembic Auto-Migrations
  18. R16: Monitoring

Total estimated: ~90 hours
```

---

## KNOWN INCONSISTENCIES TO FIX WHEN TOUCHING THESE FILES

1. `from __future__ import annotations` -- missing from `user.py`, `session.py`, `route_history.py` models (add when editing)
2. HTTPException status codes -- auth uses `status.HTTP_401_UNAUTHORIZED`, others use bare `401` (standardize to constants)
3. Service variable naming -- auth route uses `auth_service`, others use `svc` (keep `svc` as standard)
4. Seed endpoints `/api/communities/seed` and `/api/gamification/seed-badges` are unauthenticated (add admin-only guard or remove from production)
5. `RouteSegment` type is duplicated in `types/index.ts` AND `ColoredRoute.tsx` (remove from ColoredRoute, import from types)
6. `app/motomap/algorithm.py` is an identical copy of `motomap/algorithm.py` (remove the copy)
7. Typography tokens exist in theme but are almost never used in screens (adopt when creating new screens)

---

# PART 3: REPO-VERIFIED CURRENT STAGE (ADDENDUM)

**Added:** 2026-04-06  
**Purpose:** This section records the real product stage after reading the repository and comparing it against Part 1 and Part 2.  
**Rule:** If this addendum conflicts with older status labels above, treat this addendum as the more accurate current-state view.

---

## VERIFIED CURRENT STAGE

MotoMap is **not** in an early greenfield stage anymore. The project already has:
- A substantial FastAPI backend with auth, profile, communities, reports, gamification, history, notifications, uploads, and weather routes
- A substantial Expo/React Native mobile app shell with many screens and components already implemented
- A real routing engine in `motomap/algorithm.py`
- Database models and migrations for the main product domains

However, MotoMap is also **not yet a true end-to-end MVP** because the most important product promise is still not fully integrated into the primary app flow.

### Practical classification

**Current stage:** Feature-rich prototype / pre-MVP beta  
**More precise engineering label:** Integration-completion stage  
**Meaning:** Most domain modules exist, but the core user journey is not fully closed from mobile UI -> primary backend -> live route generation -> persistence -> follow-up UX.

### The single most important conclusion

MotoMap is currently **between Phase A0 and Phase A1** of the real execution path:
1. **A0: Architecture and integration alignment** is still incomplete
2. **A1: Live route MVP** is still incomplete

Until these are done, the app remains visually advanced but functionally short of the actual product promise.

---

## REPO-VERIFIED FINDINGS

### F1. Primary backend does not yet expose live route generation

- `api/main.py` includes routers for auth, profile, weather, communities, reports, gamification, history, notifications, and upload
- `motomap/algorithm.py` contains the actual routing engine
- There is still no primary production-facing route generation API wired into `api/main.py`

**Impact:** The core routing algorithm exists, but the main backend still does not expose it as a first-class product API.

### F2. Mobile map still depends on a legacy/demo route endpoint

- `app/mobile/utils/api.ts` uses `fetchRoute()` -> `GET /api/route`
- That endpoint exists in `app/api/main.py`, not in the main product backend
- `app/api/main.py` serves either a generated JSON file or the fallback `DEMO_ROUTE`
- `app/mobile/app/(tabs)/map.tsx` still calls `fetchRoute()`

**Impact:** The mobile route/map experience is still coupled to a legacy/demo API surface instead of the main backend stack.

### F3. Route selection flow is still mostly static

- `app/mobile/app/(tabs)/route.tsx` renders hardcoded mode cards and pushes the user to the map screen
- It does not yet collect a true origin/destination pair and submit a live route-generation request to the primary backend

**Impact:** The user can browse route UI, but the main route-planning loop is not end-to-end functional.

### F4. Password reset exists in UI only, not as a real product flow

- `app/mobile/app/auth/forgot-password.tsx` explicitly simulates success
- The file comments state that production would call `/api/auth/forgot-password`
- The corresponding backend flow is still absent

**Impact:** Auth looks broader than it really is; account recovery is not complete.

### F5. Testing status in Part 1 is outdated

Part 1 says **MODULE 10: TESTING -- NOT STARTED**, but the repository already contains meaningful Python test coverage, especially for the routing engine and data pipeline.

Examples already present:
- `tests/test_router.py`
- `tests/test_algorithm.py`
- `tests/test_data_loader.py`
- `tests/test_curve_risk.py`
- `app/tests/test_router.py`
- `app/tests/test_algorithm.py`

**More accurate statement:** Core Python tests exist. What is still missing is:
- Product/backend API integration testing
- Mobile UI/component testing
- End-to-end route flow testing
- CI enforcement for those tests

### F6. Gamification is implemented structurally, but the loop is not fully closed

- Points, badges, challenges, and leaderboard models/routes/services exist
- Points are already awarded from some flows
- Badge seeding and manual badge-award capability exist
- Automatic badge evaluation after user actions is still missing
- Challenge progress endpoints are still missing

**Impact:** The gamification foundation is real, but the user reward system is not fully reactive yet.

### F7. Route history is useful, but not yet enough for full route-detail/navigation UX

- `api/routes/history.py` and `api/services/route_history.py` support list, create, complete, favorite, analytics, and delete
- There is still no dedicated `get_by_id` route
- There is no stored polyline for replay/detail rendering

**Impact:** Saved-route and navigation follow-up screens cannot yet be implemented cleanly without expanding the history model/API.

### F8. Upload infrastructure exists but is not fully wired into product flows

- Upload endpoints exist in `api/routes/upload.py`
- Profile photo and report-photo flows are still not fully integrated

**Impact:** File storage capability exists, but key user workflows still do not consume it properly.

### F9. Two backend surfaces create architectural ambiguity

Current repo reality:
- `api/main.py` = main product backend
- `app/api/main.py` = legacy/demo route backend

**Impact:** This split increases confusion around which API the mobile client should trust and slows down completion of the core route workflow.

### F10. Some known inconsistencies are confirmed by the repo

Confirmed:
- `app/motomap/algorithm.py` is an identical copy of `motomap/algorithm.py`
- `RouteSegment` is duplicated in `app/mobile/types/index.ts` and `app/mobile/components/ColoredRoute.tsx`
- Seed endpoints remain unauthenticated in `api/routes/communities.py` and `api/routes/gamification.py`

Partially outdated:
- The note about `from __future__ import annotations` missing from `api/models/user.py` is no longer accurate; `user.py` already has it

---

## STATUS CORRECTIONS TO PART 1

These corrections should be read as the accurate interpretation of the earlier module labels.

### Module 2: Visual Route Safety Overlay

**Correct interpretation:** UI capability exists, but the route visualization is not yet backed by the final live routing pipeline.

### Module 3: User Auth & Database

**Correct interpretation:** Core auth is done; account recovery and email verification are still missing and materially affect product readiness.

### Module 7: Gamification

**Correct interpretation:** Data model and point-award plumbing are present; automatic badge/challenge completion is still incomplete.

### Module 8: Backend Extensions

**Correct interpretation:** Useful platform extensions exist, but the most important backend extension, dynamic route generation, is still missing from the primary backend.

### Module 9: Mobile Screens

**Correct interpretation:** Many screens exist visually, but several of them are still partial because backend integration is incomplete or mocked.

### Module 10: Testing

**Correct interpretation:** Not "not started."  
Better wording: **Core Python tests exist; product-level integration, mobile tests, and CI enforcement are still missing.**

---

## TRUE PRODUCT STAGE CHECKPOINT

MotoMap should be considered a **true MVP** only when all of the following are complete:
- Mobile route planning uses the main backend, not the legacy/demo route endpoint
- The main backend can generate a live route from user input and return route data for all supported modes
- The route can be persisted and reopened meaningfully
- Password reset works end-to-end
- Badge auto-award works for the main user actions
- A minimum automated quality gate exists in CI

Until then, MotoMap should be described as:

**"A substantial product prototype with real backend modules, but still missing final integration of the core route experience."**

---

## REVISED IMPLEMENTATION ORDER WITH SUB-PHASES

The original phase order is directionally correct, but the actual repo state suggests a more precise execution path.

### Phase A0: Architecture Alignment (NEW)
**Goal:** Collapse ambiguity before adding more product surface.

1. Standardize on **one primary backend entrypoint** for the mobile app
2. Add the real route-generation router to `api/main.py`
3. Migrate mobile route consumers away from `app/api/main.py`
4. Keep `app/api/main.py` only as a temporary compatibility/demo layer, or remove it after parity
5. Remove or quarantine duplicated routing code (`app/motomap/algorithm.py`)

**Exit criteria:**
- Mobile app talks to one backend base URL for production features
- `/api/route`-style demo dependency is no longer the main product path

### Phase A1: Live Route MVP
**Goal:** Make the core MotoMap promise real.

1. Create route-generation request/response contracts in the main backend
2. Snap origin/destination coordinates to graph nodes
3. Load/cache graphs efficiently enough for repeated route requests
4. Expose route generation for the supported riding modes
5. Return geometry, stats, and route metadata needed by the mobile map
6. Optionally include segment-level safety overlay data in the same response or a companion response
7. Wire mobile route selection screen to submit real route requests
8. Replace hardcoded route-selection placeholders with live backend results

**Exit criteria:**
- User can choose origin/destination and receive a live route from the main backend
- Mobile map renders that route without relying on demo JSON

### Phase A2: Account Recovery MVP
**Goal:** Close the auth system from a real-user perspective.

1. Add forgot-password token generation and persistence
2. Add reset-password confirmation endpoint
3. Add email sending abstraction/provider
4. Connect mobile forgot-password flow to the real backend
5. Add reset-password mobile screen if backend contract requires token entry/new password

**Exit criteria:**
- A real user can request a reset link/token and set a new password

### Phase A3: Gamification Completion
**Goal:** Make reward loops reactive instead of manual/semi-static.

1. Implement automatic badge eligibility checks after route/report/post actions
2. Add challenge progress tracking updates
3. Add active challenge query endpoints for the mobile app
4. Trigger badge/challenge notifications where appropriate
5. Guard or remove public seed endpoints for production safety

**Exit criteria:**
- Main user actions can automatically unlock badges and advance challenges

### Phase A4: Quality Gate
**Goal:** Convert the current codebase from "works locally" to "protected by automation."

1. Reclassify existing test assets instead of rebuilding from zero
2. Add API-level tests for the new route-generation flow
3. Add tests for password reset
4. Add tests for gamification auto-award
5. Add CI to run the important Python test set on every push/PR

**Exit criteria:**
- The critical product path is covered by automated tests and CI

### Phase B0: Community Completion
**Goal:** Complete the most visible remaining community interactions.

1. Post likes
2. Comment likes
3. Post detail screen
4. Report detail screen
5. My reports endpoint and screen

### Phase B1: Mobile Shared Infrastructure
**Goal:** Reduce duplication and unlock faster screen work.

1. InputField
2. PostCard
3. Toast/Snackbar
4. ErrorBoundary
5. Replace duplicated raw input/post rendering patterns where touched

### Phase B2: Operational Safety / Product Plumbing
**Goal:** Close smaller but important product gaps.

1. Enhanced `/health`
2. Upload wiring for profile/report photos
3. Route history expansion (`get_by_id`, optional polyline storage)
4. Basic admin/guard strategy for seed/debug endpoints

### Phase C0: Route Experience Expansion
**Goal:** Build on the live-route MVP once the backend contract is stable.

1. Route detail screen
2. Navigation mode (simplified version first)
3. Report clustering on map
4. User-location marker / map-control polish if still pending

### Phase D0: Settings and Account Management
**Goal:** Finish the remaining account-management surfaces.

1. Account settings
2. Notification settings
3. Privacy settings
4. About screen
5. Optional account deletion flow

### Phase E0: Deployment, Scale, and Observability
**Goal:** Productionize after the core loop is stable.

1. Docker production compose and `.dockerignore`
2. Mobile build pipeline
3. Kubernetes manifests
4. Monitoring (Prometheus/Sentry)
5. WebSocket community chat
6. Alembic auto-migration workflow

---

## WHAT TO TREAT AS THE CURRENT BLOCKER LIST

If work starts immediately, the real blocker order should be:

1. Phase A0
2. Phase A1
3. Phase A2
4. Phase A3
5. Phase A4

Only after these should the team spend serious effort on deeper polish, extra screens, chat, Kubernetes, or observability.

---

## BOTTOM-LINE SUMMARY

**What is already strong:**
- Core routing algorithm
- Domain backend breadth
- Mobile app breadth
- Data model breadth

**What is still blocking a real MVP:**
- Main-backend live routing integration
- Removal of legacy/demo route dependency
- Real password reset flow
- Automatic badge/challenge completion
- CI-backed testing of the critical path

**Therefore:** MotoMap is best understood as a **substantial but integration-incomplete product build**, not as an unfinished prototype and not yet as a completed MVP.
