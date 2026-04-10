DO $$ BEGIN
    CREATE TYPE community_type AS ENUM (
        'brand', 'style', 'region', 'interest', 'event'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS communities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    type community_type NOT NULL,
    icon_url TEXT,
    banner_url TEXT,
    color VARCHAR(7),
    is_public BOOLEAN DEFAULT TRUE,
    is_official BOOLEAN DEFAULT FALSE,
    requires_approval BOOLEAN DEFAULT FALSE,
    member_count INTEGER DEFAULT 0,
    post_count INTEGER DEFAULT 0,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    brand_name VARCHAR(100),
    region_country VARCHAR(100),
    region_city VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_communities_type ON communities(type);
CREATE INDEX IF NOT EXISTS idx_communities_slug ON communities(slug);
CREATE INDEX IF NOT EXISTS idx_communities_brand ON communities(brand_name);
