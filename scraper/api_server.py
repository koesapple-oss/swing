# Project: Swing
# Agent 0: The Local Architect
# Path: scraper/api_server.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import time
import json
import os

app = FastAPI(title="Swing Trading Local API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 시스템 (파일 기반 영속성 추가)
DB_FILE = "recommendations.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading DB: {e}")
    return {
        "recommendations": {},
        "last_full_scan": 0,
        "is_scanning": False
    }

def save_db():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving DB: {e}")

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
        "engine": "FastAPI Local", # Proxmox 서버 응답 형식과 일치 시킴
        "is_scanning": db.get("is_scanning", False),
        "last_scan_time": db.get("last_full_scan", 0),
        "count": len(db.get("recommendations", {}))
    }

@app.post("/start-scan")
async def start_scan():
    db["is_scanning"] = True
    # db["recommendations"] = {} # 기존 데이터를 지우지 않고 업데이트 방식으로 변경 (안정성)
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

@app.get("/recommendations")
async def get_recommendations():
    results = list(db["recommendations"].values())
    # 최신 수신 순 정렬
    results.sort(key=lambda x: x.get("server_time", 0), reverse=True)
    return results

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
