# Project: Swing
# Agent 0: The Local Architect
# Path: scraper/api_server.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn

app = FastAPI(title="Swing Trading Local API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db = {
    "recommendations": {}
}

class StockData(BaseModel):
    code: str
    name: str
    market: str
    current_price: float
    volume: float
    sentiment_score: float
    news_summary: str
    tech_reason: Optional[str] = "" # 기술적 분석 추가
    ext_reason: Optional[str] = ""  # 대외적 분석 추가
    grade: str
    targets: Dict[str, float]

@app.get("/")
async def root():
    return {"status": "running", "engine": "FastAPI Local"}

@app.post("/update")
async def update_stock(data: StockData):
    db["recommendations"][data.code] = data.dict()
    return {"status": "success"}

@app.get("/recommendations")
async def get_recommendations():
    return list(db["recommendations"].values())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
