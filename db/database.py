import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bot.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        with open(SCHEMA_PATH) as f:
            await db.executescript(f.read())
        await db.commit()


def get_db():
    return aiosqlite.connect(DB_PATH)


async def get_guild_channel(guild_id: str) -> str | None:
    async with get_db() as db:
        async with db.execute(
            "SELECT updates_channel_id FROM guild_config WHERE guild_id = ?", (guild_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def set_guild_channel(guild_id: str, channel_id: str):
    async with get_db() as db:
        await db.execute(
            "INSERT INTO guild_config (guild_id, updates_channel_id) VALUES (?, ?)"
            " ON CONFLICT(guild_id) DO UPDATE SET updates_channel_id = excluded.updates_channel_id",
            (guild_id, channel_id),
        )
        await db.commit()


async def add_follow(user_id: str, guild_id: str, league: str, team: str) -> bool:
    async with get_db() as db:
        try:
            await db.execute(
                "INSERT INTO follows (user_id, guild_id, league, team) VALUES (?, ?, ?, ?)",
                (user_id, guild_id, league, team),
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False  # already following


async def remove_follow(user_id: str, guild_id: str, league: str, team: str) -> bool:
    async with get_db() as db:
        cursor = await db.execute(
            "DELETE FROM follows WHERE user_id = ? AND guild_id = ? AND league = ? AND team = ?",
            (user_id, guild_id, league, team),
        )
        await db.commit()
        return cursor.rowcount > 0


async def get_follows(user_id: str, guild_id: str) -> list[dict]:
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT league, team FROM follows WHERE user_id = ? AND guild_id = ?",
            (user_id, guild_id),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def get_followers_for_teams(guild_id: str, league: str, home: str, away: str) -> list[str]:
    async with get_db() as db:
        async with db.execute(
            "SELECT DISTINCT user_id FROM follows"
            " WHERE guild_id = ? AND league = ? AND (team = ? OR team = ?)",
            (guild_id, league, home, away),
        ) as cursor:
            rows = await cursor.fetchall()
            return [r[0] for r in rows]


async def upsert_tracked_game(game_id: str, league: str, status: str, score: str, channel_id: str):
    async with get_db() as db:
        await db.execute(
            "INSERT INTO tracked_games (game_id, league, last_status, last_score, channel_id)"
            " VALUES (?, ?, ?, ?, ?)"
            " ON CONFLICT(game_id) DO UPDATE SET"
            "  last_status = excluded.last_status,"
            "  last_score = excluded.last_score",
            (game_id, league, status, score, channel_id),
        )
        await db.commit()


async def get_tracked_game(game_id: str) -> dict | None:
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM tracked_games WHERE game_id = ?", (game_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def delete_tracked_game(game_id: str):
    async with get_db() as db:
        await db.execute("DELETE FROM tracked_games WHERE game_id = ?", (game_id,))
        await db.commit()
