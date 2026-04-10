DO $$ BEGIN
    CREATE TYPE report_category AS ENUM ('hazard', 'surface', 'traffic', 'poi');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE report_type AS ENUM (
        'oil_spill', 'debris', 'pothole', 'construction', 'traffic_light', 'electrical',
        'wet', 'ice', 'fog', 'sand', 'leaves',
        'heavy_traffic', 'accident', 'police', 'road_closure',
        'gas_station', 'moto_shop', 'parking', 'scenic', 'cafe'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE report_severity AS ENUM ('low', 'medium', 'high', 'critical');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS road_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporter_id UUID REFERENCES users(id) ON DELETE SET NULL,
    reporter_anonymous BOOLEAN DEFAULT FALSE,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    location_name VARCHAR(200),
    road_name VARCHAR(200),
    category report_category NOT NULL,
    type report_type NOT NULL,
    severity report_severity DEFAULT 'medium',
    title VARCHAR(200),
    description TEXT,
    photo_urls TEXT[],
    affects_direction VARCHAR(20) DEFAULT 'both',
    upvote_count INTEGER DEFAULT 0,
    downvote_count INTEGER DEFAULT 0,
    verification_score FLOAT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(id),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT valid_coordinates CHECK (latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180)
);

CREATE INDEX IF NOT EXISTS idx_reports_category ON road_reports(category);
CREATE INDEX IF NOT EXISTS idx_reports_type ON road_reports(type);
CREATE INDEX IF NOT EXISTS idx_reports_active ON road_reports(is_active);
CREATE INDEX IF NOT EXISTS idx_reports_expires ON road_reports(expires_at);

CREATE TABLE IF NOT EXISTS report_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID NOT NULL REFERENCES road_reports(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_upvote BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(report_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_votes_report ON report_votes(report_id);
CREATE INDEX IF NOT EXISTS idx_votes_user ON report_votes(user_id);
