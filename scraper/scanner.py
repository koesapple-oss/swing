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
        self.macro_context = "장 개시 전 시장 주도 섹터 분석 중"
        self.api_url = os.getenv("SWING_API_URL", "http://localhost:8000")
        print(f"🚀 [Scanner] 분석 엔진 가동 (Target: {self.api_url})")

    def run_full_scan(self):
        try: requests.post(f"{self.api_url}/start-scan", timeout=5)
        except: pass

        markets = [("0001", "KOSPI"), ("1001", "KOSDAQ")]
        self.target_stocks = []
        
        for m_code, m_name in markets:
            print(f"📡 {m_name} 데이터 수집 중...")
            raw_stocks = self.kis.get_market_rankings(m_code)
            
            # 장전(0.0억) 상황이면 테스트를 위해 상위 3개 종목을 강제로 분석 대상으로 편입
            is_pre_market = all(float(s.get('acml_tr_pbmn', 0)) == 0 for s in raw_stocks[:5])
            
            if is_pre_market:
                print(f"⚠️ 장전(새벽) 모드 감지: {m_name} 상위 종목 강제 분석 시뮬레이션 시작")
                analysis_targets = raw_stocks[:3] # 각 시장별 상위 3개 강제 분석
            else:
                # 실시간 거래대금이 있을 경우 10억 이상만 필터링
                analysis_targets = [s for s in raw_stocks[:15] if float(s.get('acml_tr_pbmn', 0)) >= 10_000_000_000]

            for index, s in enumerate(analysis_targets):
                name = s.get('hts_kor_isnm', 'Unknown')
                code = s.get('mksc_shrn_iscd', '')
                price = float(s.get('stck_prpr', 0))
                volume_money = float(s.get('acml_tr_pbmn', 0))
                
                # 가상 거래대금 부여 (시뮬레이션용)
                if volume_money == 0:
                    volume_money = (1000 - (index * 100)) * 100_000_000 # 1000억~800억 가상 부여

                print(f"💎 AI 분석 ({index+1}/{len(analysis_targets)}): {name} ({volume_money/1e8:.1f}억 추정)")
                try:
                    analysis = self.analyze_deep_with_ai(name, price, volume_money, m_name)
                    if analysis:
                        stock_data = {
                            "code": code, "name": name, "price": price, "market": m_name,
                            "volume": volume_money, "sentiment": analysis["score"],
                            "summary": analysis["summary"],
                            "tech_reason": analysis["tech"],
                            "ext_reason": analysis["ext"],
                            "grade": "S" if analysis["score"] > 0.7 else "A"
                        }
                        self.push_one_to_server(stock_data)
                        print(f"✅ 분석 완료: {name} (점수: {analysis['score']})")
                except Exception as e:
                    print(f"🚨 {name} 에러: {e}")
                
                time.sleep(10.0)

        try: 
            requests.post(f"{self.api_url}/end-scan", timeout=5)
            print("✅ 시뮬레이션 완료. 이제 앱에서 결과를 확인하세요!")
        except: 
            pass

    def analyze_deep_with_ai(self, stock_name, price, volume, market):
        prompt = (
            f"종목: {stock_name}\n"
            f"데이터: 가격 {price}원, 거래대금 {volume}원, 시장 {market}\n"
            f"매크로: {self.macro_context}\n"
            "JSON 형식으로 응답: {\"score\": 0.75, \"summary\": \"요약\", \"tech\": \"기술적분석\", \"ext\": \"대외전망\"}\n"
            "주의: 점수는 반드시 -1.0 ~ 1.0 사이의 소수점으로만 응답하세요."
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
    scanner = DeepScanner()
    scanner.run_full_scan()
