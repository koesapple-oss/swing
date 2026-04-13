# Project: Swing
# Agent 0: The Local Architect
# Path: scraper/api_server.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import time

app = FastAPI(title="Swing Trading Local API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 시스템 (메모리)
db = {
    "recommendations": {},
    "last_full_scan": 0,
    "is_scanning": False
}

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
        "is_scanning": db["is_scanning"],
        "last_scan_time": db["last_full_scan"],
        "count": len(db["recommendations"])
    }

@app.post("/start-scan")
async def start_scan():
    db["is_scanning"] = True
    db["recommendations"] = {} # 새 스캔 시 이전 데이터 삭제
    return {"status": "scanning_started"}

@app.post("/end-scan")
async def end_scan():
    db["is_scanning"] = False
    db["last_full_scan"] = time.time()
    return {"status": "scanning_ended"}

@app.post("/update")
async def update_stock(data: StockData):
    data_dict = data.dict()
    data_dict["server_time"] = time.time()
    db["recommendations"][data.code] = data_dict
    return {"status": "success"}

@app.get("/recommendations")
async def get_recommendations():
    results = list(db["recommendations"].values())
    # 최신 수신 순 정렬
    results.sort(key=lambda x: x.get("server_time", 0), reverse=True)
    return results

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
