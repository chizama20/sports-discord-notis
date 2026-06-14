CREATE TABLE IF NOT EXISTS follows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    guild_id TEXT NOT NULL,
    league TEXT NOT NULL,
    team TEXT NOT NULL,
    UNIQUE(user_id, guild_id, league, team)
);

CREATE TABLE IF NOT EXISTS tracked_games (
    game_id TEXT PRIMARY KEY,
    league TEXT NOT NULL,
    last_status TEXT,
    last_score TEXT,
    channel_id TEXT
);

CREATE TABLE IF NOT EXISTS guild_config (
    guild_id TEXT PRIMARY KEY,
    updates_channel_id TEXT
);
