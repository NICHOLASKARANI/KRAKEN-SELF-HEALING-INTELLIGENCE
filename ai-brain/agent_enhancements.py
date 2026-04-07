# Add these imports at the top of agent.py (after existing imports)
import sqlite3
from datetime import datetime, timedelta
import json
from pathlib import Path

# Add this class before the app initialization
class DecisionDatabase:
    def __init__(self, db_path="decisions.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                decision TEXT,
                confidence REAL,
                actions TEXT,
                reasoning TEXT,
                success BOOLEAN
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                metric_name TEXT,
                metric_value REAL
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_decision(self, decision, confidence, actions, reasoning, success=True):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO decisions (timestamp, decision, confidence, actions, reasoning, success)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), decision, confidence, json.dumps(actions), reasoning, success))
        conn.commit()
        conn.close()
    
    def get_stats(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM decisions')
        total = cursor.fetchone()[0]
        cursor.execute('SELECT AVG(confidence) FROM decisions')
        avg_conf = cursor.fetchone()[0] or 0
        conn.close()
        return {"total_decisions": total, "avg_confidence": avg_conf}

# Initialize database
decision_db = DecisionDatabase()

# Add these new endpoints after existing ones
@app.get("/decision-stats")
async def get_decision_stats():
    \"\"\"Get AI decision statistics\"\"\"
    return decision_db.get_stats()

@app.get("/decision-history")
async def get_decision_history(limit: int = 10):
    \"\"\"Get recent AI decisions\"\"\"
    conn = sqlite3.connect("decisions.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, decision, confidence, reasoning 
        FROM decisions 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        "timestamp": row[0],
        "decision": row[1],
        "confidence": row[2],
        "reasoning": row[3]
    } for row in rows]

@app.post("/simulate-load")
async def simulate_load(requests: int = 100):
    \"\"\"Simulate load for testing\"\"\"
    import asyncio
    import random
    
    async def mock_request():
        await asyncio.sleep(random.uniform(0.01, 0.1))
        return {"status": "ok"}
    
    tasks = [mock_request() for _ in range(requests)]
    results = await asyncio.gather(*tasks)
    
    return {
        "requests_completed": len(results),
        "success_rate": 100,
        "message": f"Simulated {requests} requests"
    }

@app.get("/health-metrics")
async def detailed_health():
    \"\"\"Get detailed health metrics\"\"\"
    stats = decision_db.get_stats()
    return {
        "status": "healthy",
        "uptime_seconds": (datetime.now() - start_time).total_seconds() if 'start_time' in dir() else 0,
        "decisions_made": stats["total_decisions"],
        "avg_confidence": stats["avg_confidence"],
        "active_services": ["ai-brain", "prometheus", "grafana"],
        "timestamp": datetime.now().isoformat()
    }

# Add start_time tracking
from datetime import datetime
start_time = datetime.now()
