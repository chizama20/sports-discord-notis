CREATE TABLE IF NOT EXISTS follows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    guild_id TEXT NOT NULL,
    league TEXT NOT NULL,
    team TEXT NOT NULL,
    UNIQUE(user_id, guild_id, league, team)
);

-- stage: 0 = nothing sent, 1 = pregame reminder sent, 2 = halftime sent, 3 = final sent
CREATE TABLE IF NOT EXISTS tracked_games (
    game_id TEXT PRIMARY KEY,
    league TEXT NOT NULL,
    stage INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS guild_config (
    guild_id TEXT PRIMARY KEY,
    updates_channel_id TEXT
);
