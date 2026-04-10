DO $$ BEGIN
    CREATE TYPE post_type AS ENUM (
        'discussion', 'question', 'help_request', 'help_offer',
        'ride_invite', 'event', 'photo', 'route_share'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS community_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    community_id UUID NOT NULL REFERENCES communities(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type post_type DEFAULT 'discussion',
    title VARCHAR(200),
    content TEXT NOT NULL,
    image_urls TEXT[],
    route_id UUID,
    location_lat FLOAT,
    location_lng FLOAT,
    location_name VARCHAR(200),
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_locked BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_posts_community ON community_posts(community_id);
CREATE INDEX IF NOT EXISTS idx_posts_author ON community_posts(author_id);
CREATE INDEX IF NOT EXISTS idx_posts_type ON community_posts(type);
CREATE INDEX IF NOT EXISTS idx_posts_created ON community_posts(created_at DESC);
