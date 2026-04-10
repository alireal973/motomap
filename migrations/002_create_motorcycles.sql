DO $$ BEGIN
    CREATE TYPE motorcycle_type AS ENUM (
        'naked', 'sport', 'touring', 'adventure',
        'cruiser', 'scooter', 'classic', 'dual_sport',
        'enduro', 'supermoto', 'cafe_racer', 'bobber'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS motorcycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INTEGER,
    cc INTEGER NOT NULL,
    type motorcycle_type NOT NULL,
    color VARCHAR(50),
    nickname VARCHAR(100),
    vin VARCHAR(17),
    license_plate VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    is_primary BOOLEAN DEFAULT FALSE,
    total_km INTEGER DEFAULT 0,
    total_routes INTEGER DEFAULT 0,
    photo_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_motorcycles_user_id ON motorcycles(user_id);
CREATE INDEX IF NOT EXISTS idx_motorcycles_brand ON motorcycles(brand);
CREATE INDEX IF NOT EXISTS idx_motorcycles_type ON motorcycles(type);
