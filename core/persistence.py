import sqlite3
from datetime import datetime

conn = sqlite3.connect("agents.db", check_same_thread=False)

conn.executescript(
    """
CREATE TABLE IF NOT EXISTS agents (
    agent_id TEXT PRIMARY KEY,
    name TEXT,
    system_prompt TEXT,
    client_id TEXT DEFAULT 'default',
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS feedbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT,
    source TEXT,
    content TEXT,
    created_at TEXT
);
"""
)


def save_agent(agent_id, name, system_prompt, client_id="default"):
    conn.execute(
        "INSERT OR REPLACE INTO agents VALUES (?, ?, ?, ?, ?)",
        (agent_id, name, system_prompt, client_id, datetime.now().isoformat()),
    )
    conn.commit()


def add_feedback(agent_id, source, content):
    conn.execute(
        "INSERT INTO feedbacks (agent_id, source, content, created_at) VALUES (?, ?, ?, ?)",
        (agent_id, source, content, datetime.now().isoformat()),
    )
    conn.commit()


def get_feedbacks(agent_id):
    cursor = conn.execute(
        "SELECT source, content FROM feedbacks WHERE agent_id=? ORDER BY created_at DESC LIMIT 10",
        (agent_id,),
    )
    return [f"{source}: {content}" for source, content in cursor.fetchall()]


def get_recent_agents(limit=20):
    cursor = conn.execute(
        "SELECT agent_id, name, created_at FROM agents ORDER BY created_at DESC LIMIT ?",
        (limit,),
    )
    return [
        {"agent_id": row[0], "name": row[1] or row[0], "created_at": row[2]}
        for row in cursor.fetchall()
    ]


def get_feedback_counts(agent_id):
    cursor = conn.execute(
        "SELECT source, COUNT(*) FROM feedbacks WHERE agent_id=? GROUP BY source",
        (agent_id,),
    )
    counts = {"judge": 0, "human": 0, "peer": 0}
    for source, count in cursor.fetchall():
        counts[source] = count
    return counts
