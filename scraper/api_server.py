# Project: Swing
# Agent 0: The Local Architect
# Path: scraper/api_server.py

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import time
import json
import os
import asyncio

app = FastAPI(title="Swing Trading Local API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 시스템
DB_FILE = "recommendations.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "recommendations": {},
        "last_full_scan": 0,
        "is_scanning": False
    }

def save_db():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except:
        pass

db = load_db()

class StockData(BaseModel):
    code: str
    name: str
    market: str
    current_price: float
    volume: float
    sentiment_score: float
    news_summary: str
    tech_reason: Optional[str] = ""
    ext_reason: Optional[str] = ""
    grade: str
    targets: Dict[str, float]
    server_time: Optional[float] = 0

@app.get("/")
async def root():
    return {
        "status": "running",
        "engine": "FastAPI On-Demand",
        "is_scanning": db.get("is_scanning", False),
        "last_scan_time": db.get("last_full_scan", 0),
        "count": len(db.get("recommendations", {}))
    }

@app.get("/recommendations")
async def get_recommendations():
    results = list(db["recommendations"].values())
    results.sort(key=lambda x: x.get("server_time", 0), reverse=True)
    return results

@app.post("/start-scan")
async def start_scan():
    db["is_scanning"] = True
    save_db()
    return {"status": "scanning_started"}

@app.post("/end-scan")
async def end_scan():
    db["is_scanning"] = False
    db["last_full_scan"] = time.time()
    save_db()
    return {"status": "scanning_ended"}

@app.post("/update")
async def update_stock(data: StockData):
    data_dict = data.dict()
    data_dict["server_time"] = time.time()
    db["recommendations"][data.code] = data_dict
    save_db()
    return {"status": "success"}

# 🚀 On-Demand 기능을 위해 스캐너를 백그라운드에서 실행하는 엔드포인트
@app.post("/trigger-scan")
async def trigger_scan(background_tasks: BackgroundTasks):
    if db.get("is_scanning"):
        return {"status": "already_scanning"}
    
    # 별도 프로세스로 실행하여 API 응답 지연 방지
    import subprocess
    import sys
    
    def run_scanner_process():
        # uv 환경을 고려하여 실행
        subprocess.Popen([sys.executable, "scanner.py"], cwd=os.path.dirname(__file__))

    background_tasks.add_task(run_scanner_process)
    return {"status": "scan_triggered"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
