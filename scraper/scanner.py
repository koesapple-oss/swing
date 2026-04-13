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
    if not api_key:
        print("🚨 [AISync] API 키가 설정되지 않았습니다.")
    genai.configure(api_key=api_key)
    # 429 에러 방지를 위해 검색 도구(google_search_retrieval) 일시 제외
    return genai.GenerativeModel('models/gemini-flash-lite-latest')

class DeepScanner:
    def __init__(self):
        self.kis = KISClient()
        self.ai_model = init_ai()
        self.macro_context = "시장 주도 테마 및 수급 중심의 데이터 분석"
        self.last_macro_update = 0
        self.api_url = os.getenv("SWING_API_URL", "http://localhost:8000")
        print(f"🔍 [Scanner] 엔진 가동 중... (Target API: {self.api_url})")

    def update_macro_context(self):
        print("🌍 글로벌 매크로 경제 스캔 중...")
        try:
            # 쿼터 절약을 위해 단순화된 프롬프트 사용
            search_prompt = "현재 한국 시장에서 가장 강한 섹터/테마 3가지를 핵심 키워드로만 나열하세요."
            response = self.ai_model.generate_content(search_prompt)
            self.macro_context = response.text
            print(f"📊 매크로 상황 업데이트 완료.")
        except Exception as e:
            print(f"⚠️ 매크로 스캔 실패 (기본값 사용): {e}")

    def run_full_scan(self):
        print("\n⚡ 시장 전수 분석 시퀀스 시작...")
        
        try:
            requests.post(f"{self.api_url}/start-scan", timeout=5)
        except:
            print(f"⚠️ 서버 연결 실패 ({self.api_url})")

        current_time = time.time()
        if current_time - self.last_macro_update > 3600:
            self.update_macro_context()
            self.last_macro_update = current_time
        
        markets = [("0001", "KOSPI"), ("1001", "KOSDAQ")]
        self.target_stocks = []

        # 필터 기준: 100억 원 (데이터 단위 확인을 위해 대폭 완화)
        VOLUME_THRESHOLD = 10_000_000_000 

        for m_code, m_name in markets:
            print(f"📡 {m_name} 랭킹 수집 중...")
            raw_stocks = self.kis.get_market_rankings(m_code)
            
            if not raw_stocks:
                print(f"❌ {m_name} 데이터를 가져오지 못했습니다.")
                continue

            analysis_targets = raw_stocks[:15]
            
            for index, s in enumerate(analysis_targets):
                name = s.get('hts_kor_isnm', 'Unknown')
                code = s.get('mksc_shrn_iscd', '')
                price = float(s.get('stck_prpr', 0))
                volume_raw = s.get('acml_tr_pbmn', '0')
                volume_money = float(volume_raw)
                
                # 첫 번째 종목만 로그로 거래대금 단위 확인
                if index == 0:
                    print(f"💡 [단위체크] {name}: {volume_money:,.0f} (RAW: {volume_raw})")

                if volume_money < VOLUME_THRESHOLD:
                    continue

                print(f"💎 AI 심층 분석 중: {name} ({volume_money/1e8:.1f}억)")
                try:
                    analysis = self.analyze_deep_with_ai(name, price, volume_money, m_name)
                    
                    if analysis and analysis.get("score", 0) > 0.3:
                        stock_data = {
                            "code": code, "name": name, "price": price, "market": m_name,
                            "volume": volume_money, "sentiment": analysis["score"],
                            "summary": analysis["summary"],
                            "tech_reason": analysis["tech"],
                            "ext_reason": analysis["ext"],
                            "grade": "S" if analysis["score"] > 0.7 else "A"
                        }
                        self.target_stocks.append(stock_data)
                        self.push_one_to_server(stock_data)
                        print(f"✅ 전송 완료: {name} (Score: {analysis['score']})")
                    else:
                        print(f"⚠️ 점수 미달: {name} ({analysis.get('score') if analysis else 'N/A'})")
                except Exception as e:
                    if "429" in str(e):
                        print("🚨 Gemini API 쿼터 초과. 잠시 대기합니다 (30초)...")
                        time.sleep(30)
                    else:
                        print(f"🚨 {name} 분석 중 에러: {e}")
                
                time.sleep(12.0) # RPM 수동 조절 (Flash 무료 티어는 분당 15건 전후 권장)

        try:
            requests.post(f"{self.api_url}/end-scan", timeout=5)
            print(f"\n✅ 스캔 완료. 포착: {len(self.target_stocks)}개")
        except:
            pass

    def analyze_deep_with_ai(self, stock_name, price, volume, market):
        prompt = (
            f"종목: {stock_name}\n상황: {self.macro_context}\n"
            f"데이터: 가격 {price}원, 거래대금 {volume}원, 시장 {market}\n"
            "분석 지침: 정밀 점수(-1.0 ~ 1.0)를 포함한 JSON 형식으로만 응답하세요.\n"
            "형식: {\"score\": 0.7, \"summary\": \"요약\", \"tech\": \"기술적\", \"ext\": \"대외적\"}"
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
        try: requests.post(f"{self.api_url}/update", json=payload, timeout=5)
        except: pass

    def live_update_loop(self):
        while True:
            try:
                self.run_full_scan()
                print("💤 대기 중 (10분)...")
                time.sleep(600)
            except Exception as e:
                print(f"🚨 에러: {e}")
                time.sleep(60)

if __name__ == "__main__":
    scanner = DeepScanner()
    scanner.run_full_scan()
    scanner.live_update_loop()
