CREATE TABLE IF NOT EXISTS route_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    motorcycle_id UUID REFERENCES motorcycles(id) ON DELETE SET NULL,

    origin_lat FLOAT NOT NULL,
    origin_lng FLOAT NOT NULL,
    origin_label VARCHAR(200),
    destination_lat FLOAT NOT NULL,
    destination_lng FLOAT NOT NULL,
    destination_label VARCHAR(200),

    mode VARCHAR(50) NOT NULL,
    distance_m INTEGER NOT NULL,
    duration_s INTEGER NOT NULL,

    lane_split_m INTEGER DEFAULT 0,
    fun_curves INTEGER DEFAULT 0,
    dangerous_curves INTEGER DEFAULT 0,
    avg_grade FLOAT DEFAULT 0,
    safety_score FLOAT,

    weather_condition VARCHAR(50),
    road_surface VARCHAR(50),
    weather_modifier FLOAT,

    is_favorite BOOLEAN DEFAULT FALSE,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_route_history_user ON route_history(user_id);
CREATE INDEX IF NOT EXISTS idx_route_history_created ON route_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_route_history_favorite ON route_history(user_id, is_favorite) WHERE is_favorite = TRUE;
