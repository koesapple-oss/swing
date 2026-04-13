# Project: Swing
# Agent 2: The Scanner (Hyper-Deep Analysis Mode)
# Path: scraper/scanner.py

import os
import requests
import time
import re
import google.generativeai as genai
import json
from dotenv import load_dotenv
from kis_client import KISClient

load_dotenv()

def init_ai():
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('models/gemini-flash-lite-latest')

class DeepScanner:
    def __init__(self):
        self.kis = KISClient()
        self.ai_model = init_ai()
        self.macro_context = "실시간 주도주 데이터 분석 중"
        self.api_url = os.getenv("SWING_API_URL", "http://localhost:8000")
        print(f"🚀 [Scanner] On-Demand 분석을 시작합니다... (API: {self.api_url})")

    def update_macro_context(self):
        print("🌍 매크로 테마 스캔 중...")
        try:
            search_prompt = "현재 한국 주식 시장에서 거래대금이 가장 쏠리고 있는 3대 주도주 테마/섹터를 키워드 위주로 분석하세요."
            response = self.ai_model.generate_content(search_prompt)
            self.macro_context = response.text
        except:
            self.macro_context = "주도주 수급 중심 분석"

    def run_full_scan(self):
        # 0. 서버에 스캔 시작 알림
        try: requests.post(f"{self.api_url}/start-scan", timeout=5)
        except: pass

        self.update_macro_context()
        
        markets = [("0001", "KOSPI"), ("1001", "KOSDAQ")]
        self.target_stocks = []
        VOLUME_THRESHOLD = 5_000_000_000 # On-Demand이므로 필터를 50억으로 더 완화

        for m_code, m_name in markets:
            print(f"📡 {m_name} 정밀 스캔 중...")
            raw_stocks = self.kis.get_market_rankings(m_code)
            if not raw_stocks: continue

            # 정예 10개 종목으로 집중 분석 (속도 향상)
            analysis_targets = raw_stocks[:10]
            
            for index, s in enumerate(analysis_targets):
                name = s.get('hts_kor_isnm', 'Unknown')
                code = s.get('mksc_shrn_iscd', '')
                price = float(s.get('stck_prpr', 0))
                volume_money = float(s.get('acml_tr_pbmn', 0))
                
                if volume_money < VOLUME_THRESHOLD:
                    continue

                print(f"💎 AI 심층 분석 ({index+1}/10): {name} ({volume_money/1e8:.1f}억)")
                try:
                    analysis = self.analyze_deep_with_ai(name, price, volume_money, m_name)
                    if analysis and analysis.get("score", 0) > 0.35:
                        stock_data = {
                            "code": code, "name": name, "price": price, "market": m_name,
                            "volume": volume_money, "sentiment": analysis["score"],
                            "summary": analysis["summary"],
                            "tech_reason": analysis["tech"],
                            "ext_reason": analysis["ext"],
                            "grade": "S" if analysis["score"] > 0.7 else "A"
                        }
                        self.push_one_to_server(stock_data)
                        print(f"✅ 포착: {name} (점수: {analysis['score']})")
                except Exception as e:
                    print(f"🚨 {name} 에러: {e}")
                
                time.sleep(10.0) # 429 방지

        # 9. 서버에 스캔 종료 알림
        try: 
            requests.post(f"{self.api_url}/end-scan", timeout=5)
            print("✅ 분석 루프 정상 종료.")
        except: 
            pass

    def analyze_deep_with_ai(self, stock_name, price, volume, market):
        prompt = (
            f"종목: {stock_name}\n"
            f"데이터: 가격 {price}원, 거래대금 {volume}원, 시장 {market}\n"
            f"매크로: {self.macro_context}\n"
            "JSON 형식으로 응답: {\"score\": 점수, \"summary\": \"요약\", \"tech\": \"분석\", \"ext\": \"전망\"}"
        )
        response = self.ai_model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text.strip())

    def push_one_to_server(self, s):
        payload = {
            "code": s["code"], "name": s["name"], "market": s["market"],
            "current_price": s["price"], "volume": int(s["volume"] / 1_000_000),
            "sentiment_score": s["sentiment"], "news_summary": s["summary"],
            "tech_reason": s["tech_reason"], "ext_reason": s["ext_reason"],
            "grade": s["grade"], "targets": {
                "buy": s["price"] * 0.99, "take_profit": s["price"] * 1.15, "stop_loss": s["price"] * 0.97
            }
        }
        requests.post(f"{self.api_url}/update", json=payload, timeout=5)

if __name__ == "__main__":
    # 수동 실행 시 단 한 번만 스캔하고 종료
    scanner = DeepScanner()
    scanner.run_full_scan()
