# Project: Swing
# Agent 0: The Local Architect
# Path: scraper/api_server.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import time
import uvicorn

app = FastAPI(title="Swing Trading Local API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db = {
    "recommendations": {},
    "last_full_scan": 0
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
    return {"status": "running", "engine": "FastAPI Local", "last_scan": db["last_full_scan"]}

@app.post("/update")
async def update_stock(data: StockData):
    data_dict = data.dict()
    data_dict["server_time"] = time.time() # 서버 수신 시각 기록
    db["recommendations"][data.code] = data_dict
    return {"status": "success"}

@app.delete("/clear")
async def clear_recommendations():
    """새로운 전체 스캔 시작 전 기존 데이터를 비웁니다."""
    db["recommendations"] = {}
    db["last_full_scan"] = time.time()
    return {"status": "cleared"}

@app.get("/recommendations")
async def get_recommendations():
    # 최신 순(업데이트 시각 순)으로 정렬하여 반환
    results = list(db["recommendations"].values())
    results.sort(key=lambda x: x.get("server_time", 0), reverse=True)
    return results

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

