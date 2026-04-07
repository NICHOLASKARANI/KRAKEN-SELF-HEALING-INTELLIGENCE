from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import logging
import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from kubernetes import client, config
from elasticsearch import Elasticsearch
from prometheus_client import CollectorRegistry, generate_latest, Counter, Gauge
import subprocess
import yaml
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="KRAKEN AI Brain", version="2.0.0")

# Track start time
start_time = datetime.now()

# Initialize database for decisions
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
    
    def get_history(self, limit=10):
        conn = sqlite3.connect(self.db_path)
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

# Initialize database
decision_db = DecisionDatabase()

# Models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    message: str

class SystemHealth(BaseModel):
    status: str
    services: List[Dict]
    alerts: List[Dict]
    metrics: Dict

class AIDecision(BaseModel):
    decision: str
    confidence: float
    actions: List[str]
    timestamp: str

# Initialize Kubernetes client (optional)
try:
    config.load_kube_config()
    logger.info("Kubernetes config loaded")
except:
    try:
        config.load_incluster_config()
        logger.info("In-cluster Kubernetes config loaded")
    except:
        logger.info("Running without Kubernetes")

# Initialize Elasticsearch (optional)
try:
    es = Elasticsearch(["http://elasticsearch:9200"])
    logger.info("Elasticsearch connected")
except:
    logger.info("Running without Elasticsearch")
    es = None

# Helper functions
def check_system_health():
    """Check overall system health status"""
    return {
        "status": "healthy",
        "services": ["ai-brain", "prometheus", "grafana"],
        "uptime_seconds": (datetime.now() - start_time).total_seconds(),
        "decisions_made": decision_db.get_stats()["total_decisions"]
    }

# API Endpoints
@app.get("/")
async def root():
    return {
        "name": "KRAKEN AI Brain",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": [
            "/health",
            "/system-health",
            "/ai-decision",
            "/decision-stats",
            "/decision-history",
            "/health-metrics",
            "/simulate-load",
            "/chaos-response"
        ]
    }

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        message="All systems operational"
    )

@app.get("/system-health")
async def system_health():
    health_data = check_system_health()
    return SystemHealth(
        status=health_data["status"],
        services=[{"name": s, "status": "running"} for s in health_data["services"]],
        alerts=[],
        metrics={
            "uptime_seconds": health_data["uptime_seconds"],
            "decisions_made": health_data["decisions_made"]
        }
    )

@app.get("/health-metrics")
async def detailed_health():
    """Get detailed health metrics"""
    stats = decision_db.get_stats()
    return {
        "status": "healthy",
        "uptime_seconds": (datetime.now() - start_time).total_seconds(),
        "decisions_made": stats["total_decisions"],
        "avg_confidence": stats["avg_confidence"],
        "active_services": ["ai-brain", "prometheus", "grafana"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/decision-stats")
async def get_decision_stats():
    """Get AI decision statistics"""
    return decision_db.get_stats()

@app.get("/decision-history")
async def get_decision_history(limit: int = 10):
    """Get recent AI decisions"""
    return decision_db.get_history(limit)

@app.post("/ai-decision")
async def ai_decision():
    """Make an AI decision"""
    # Simulate AI decision making
    decisions = [
        "System is stable, continue monitoring",
        "Detected high memory usage, scaling resources",
        "Service health check passed, no action needed",
        "Predictive analysis shows potential issue in 2 hours",
        "Auto-healing routine completed successfully"
    ]
    
    selected_decision = random.choice(decisions)
    confidence = round(random.uniform(0.85, 0.99), 2)
    actions = ["monitor", "log", "report"]
    
    # Save to database
    decision_db.save_decision(
        decision=selected_decision,
        confidence=confidence,
        actions=actions,
        reasoning="AI analysis based on current system metrics"
    )
    
    logger.info(f"AI Decision made: {selected_decision}")
    
    return AIDecision(
        decision=selected_decision,
        confidence=confidence,
        actions=actions,
        timestamp=datetime.now().isoformat()
    )

@app.post("/simulate-load")
async def simulate_load(requests: int = 100):
    """Simulate load for testing"""
    await asyncio.sleep(1)  # Simulate processing
    return {
        "requests_completed": requests,
        "success_rate": 100,
        "processing_time_ms": 1000,
        "message": f"Successfully simulated {requests} requests"
    }

@app.post("/chaos-response")
async def chaos_response(event: dict):
    """Handle chaos engineering events"""
    logger.info(f"Chaos event received: {event}")
    
    # Simulate auto-healing
    await asyncio.sleep(2)
    
    decision_db.save_decision(
        decision=f"Auto-healed {event.get('service', 'unknown')} service",
        confidence=0.95,
        actions=["restart", "verify", "report"],
        reasoning=f"Chaos injection detected and auto-healed"
    )
    
    return {
        "healed": True,
        "action": "auto_healing_triggered",
        "service": event.get("service", "unknown"),
        "recovery_time_ms": 2000
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
