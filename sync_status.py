import sqlite3
from pathlib import Path

DB = Path("sync_state.db")

def conn():
    c = sqlite3.connect(DB)
    c.execute("""
        CREATE TABLE IF NOT EXISTS ChannelSyncState(
            TeamId TEXT,
            ChannelId TEXT,
            DeltaLink TEXT,
            LastSyncedAt TEXT,
            PRIMARY KEY (TeamId, ChannelId)
        )
    """)
    return c

def get_state(team, channel):
    c = conn()
    cur = c.execute(
        "SELECT DeltaLink, LastSyncedAt FROM ChannelSyncState WHERE TeamId=? AND ChannelId=?",
        (team, channel),
    )
    row = cur.fetchone()
    c.close()
    return row if row else (None, None)

def upsert_state(team, channel, link, ts):
    c = conn()
    c.execute("""
        INSERT INTO ChannelSyncState (TeamId, ChannelId, DeltaLink, LastSyncedAt)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(TeamId, ChannelId) DO UPDATE SET
            DeltaLink=excluded.DeltaLink,
            LastSyncedAt=excluded.LastSyncedAt
    """, (team, channel, link, ts))
    c.commit()
    c.close()