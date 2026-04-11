# Project: Swing
# Agent 2: The Scanner & Analyzer
# Path: scraper/generate_dummy.py

import json
import datetime
import random

def generate_dummy_data():
    stocks = [
        {"code": "005930", "name": "삼성전자", "grade": "S", "sentiment": 0.88},
        {"code": "000660", "name": "SK하이닉스", "grade": "S", "sentiment": 0.92},
        {"code": "035420", "name": "NAVER", "grade": "A", "sentiment": 0.65},
        {"code": "035720", "name": "카카오", "grade": "A", "sentiment": 0.42},
        {"code": "005380", "name": "현대차", "grade": "S", "sentiment": 0.81},
    ]
    
    recommendations = []
    
    for s in stocks:
        current_price = random.randint(50000, 200000)
        data = {
            "code": s["code"],
            "name": s["name"],
            "market": "KOSPI",
            "current_price": current_price,
            "volume": random.randint(1000, 10000),
            "ma_trend": "up",
            "sentiment_score": s["sentiment"],
            "news_summary": f"{s['name']}: AI 및 반도체 업적 호조로 인해 강력한 매수 신호 포착.",
            "grade": s["grade"],
            "targets": {
                "buy": round(current_price * 0.99, -2),
                "take_profit": round(current_price * 1.12, -2),
                "stop_loss": round(current_price * 0.97, -2)
            },
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }
        recommendations.append(data)
    
    # Standard JSON Header 부합하게 패키징
    standard_json = {
        "header": {
            "status": "success",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0"
        },
        "payload": {
            "data": recommendations,
            "metadata": {"count": len(recommendations)}
        }
    }
    
    with open("dummy_data.json", "w", encoding="utf-8") as f:
        json.dump(standard_json, f, ensure_ascii=False, indent=2)
    
    print(f"Generated {len(recommendations)} dummy recommendations in dummy_data.json")

if __name__ == "__main__":
    generate_dummy_data()
