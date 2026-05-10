import aiosqlite
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "netguardian.db"

async def init_db():
    """Initialize the SQLite database with required tables."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        # Incidents table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                node_id TEXT,
                severity TEXT,
                primary_metric TEXT,
                anomaly_score REAL,
                incident_state TEXT,
                assigned_to TEXT,
                resolution_note TEXT,
                payload TEXT,
                agents_data TEXT,
                experience_data TEXT,
                created_at TEXT
            )
        """)
        
        # Audit logs table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT,
                action TEXT,
                note TEXT,
                assigned_to TEXT,
                at TEXT,
                FOREIGN KEY (incident_id) REFERENCES incidents (id)
            )
        """)
        
        # Knowledge base entries (dynamic)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_base_custom (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                remedy TEXT,
                source_incident_id TEXT,
                created_at TEXT
            )
        """)
        
        await db.commit()
    logger.info(f"Database initialized at {DB_PATH}")

async def record_incident(event: dict):
    """Persist an incident to SQLite."""
    async with aiosqlite.connect(DB_PATH) as db:
        payload = {k: v for k, v in event.items() if k not in ["agents", "experience"]}
        await db.execute(
            """
            INSERT INTO incidents (
                id, timestamp, node_id, severity, primary_metric, 
                anomaly_score, incident_state, assigned_to, 
                payload, agents_data, experience_data, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.get("incident_id"),
                str(event.get("timestamp")),
                event.get("node_id"),
                event.get("severity"),
                event.get("primary_metric"),
                event.get("anomaly_score", event.get("score", 0)),
                event.get("incident_state", "open"),
                event.get("assigned_to"),
                json.dumps(payload, default=str),
                json.dumps(event.get("agents"), default=str),
                json.dumps(event.get("experience"), default=str),
                datetime.now(timezone.utc).isoformat()
            )
        )
        await db.commit()

async def update_incident_state(incident_id: str, state: str, note: str = None, assigned_to: str = None):
    """Update incident state and record audit log."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE incidents SET incident_state = ?, resolution_note = ?, assigned_to = COALESCE(?, assigned_to) WHERE id = ?",
            (state, note, assigned_to, incident_id)
        )
        await db.execute(
            "INSERT INTO audit_logs (incident_id, action, note, assigned_to, at) VALUES (?, ?, ?, ?, ?)",
            (incident_id, state, note, assigned_to, datetime.now(timezone.utc).isoformat())
        )
        await db.commit()

async def get_recent_incidents(limit: int = 50):
    """Fetch recent incidents from the DB."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM incidents ORDER BY created_at DESC LIMIT ?", (limit,)) as cursor:
            rows = await cursor.fetchall()
            incidents = []
            for row in rows:
                d = dict(row)
                # Reconstruct full object
                item = json.loads(d["payload"])
                item["incident_id"] = d["id"]
                item["incident_state"] = d["incident_state"]
                item["assigned_to"] = d["assigned_to"]
                item["resolution_note"] = d["resolution_note"]
                item["agents"] = json.loads(d["agents_data"]) if d["agents_data"] else None
                item["experience"] = json.loads(d["experience_data"]) if d["experience_data"] else None
                incidents.append(item)
            return incidents

async def get_db_summary():
    """Aggregate statistics for the summary dashboard."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        stats = {}
        async with db.execute("SELECT COUNT(*) as total FROM incidents") as cursor:
            stats["total_incidents"] = (await cursor.fetchone())["total"]
        
        async with db.execute("SELECT severity, COUNT(*) as count FROM incidents GROUP BY severity") as cursor:
            stats["severity_counts"] = {row["severity"]: row["count"] for row in await cursor.fetchall()}
            
        async with db.execute("SELECT primary_metric, COUNT(*) as count FROM incidents GROUP BY primary_metric") as cursor:
            stats["primary_metrics"] = {row["primary_metric"]: row["count"] for row in await cursor.fetchall()}
            
        async with db.execute("SELECT AVG(anomaly_score) as avg_score FROM incidents") as cursor:
            stats["average_score"] = round((await cursor.fetchone())["avg_score"] or 0, 4)
            
        return stats
