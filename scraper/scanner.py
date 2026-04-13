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
        print("🚨 [AISync] API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        'models/gemini-flash-lite-latest',
        tools=[{"google_search_retrieval": {}}]
    )

class DeepScanner:
    def __init__(self):
        self.kis = KISClient()
        self.ai_model = init_ai()
        self.macro_context = ""
        self.last_macro_update = 0
        # 서버 URL을 환경 변수에서 가져오거나 기본값(localhost) 사용
        self.api_url = os.getenv("SWING_API_URL", "http://localhost:8000")
        self.target_stocks = []
        print(f"🔍 [Scanner] 엔진 가동 중... (Target API: {self.api_url})")

    def update_macro_context(self):
        print("🌍 글로벌 매크로 경제 스캔 중...")
        try:
            search_prompt = (
                "오늘 한국 및 글로벌 주식 시장에 영향을 미칠 수 있는 실시간 긴급 뉴스 3가지를 요약하세요. "
                "반드시 현재 시각(2026년 4월 13일) 기준의 팩트를 기반으로 하세요."
            )
            response = self.ai_model.generate_content(search_prompt)
            self.macro_context = response.text
            print(f"📊 매크로 상황 업데이트 완료: {self.macro_context[:100]}...")
        except Exception as e:
            print(f"⚠️ 매크로 스캔 실패: {e}")
            self.macro_context = "최신 데이터 연동 지연"

    def run_full_scan(self):
        print("\n⚡ 시장 전수 분석 시퀀스 시작...")
        
        # 0. 서버에 스캔 시작 알림
        try:
            requests.post(f"{self.api_url}/start-scan", timeout=5)
        except Exception as e:
            print(f"⚠️ 서버 연결 실패 ({self.api_url}): {e}")
            # 서버가 없으면 로컬 테스트 모드로 진행하거나 중단 가능

        # 1. 매크로 업데이트 (1시간 주기)
        current_time = time.time()
        if current_time - self.last_macro_update > 3600:
            self.update_macro_context()
            self.last_macro_update = current_time
        
        markets = [("0001", "KOSPI"), ("1001", "KOSDAQ")]
        self.target_stocks = []

        # 주도주 판단 기준 (기존 500억 -> 테스트를 위해 300억으로 완화 가능)
        VOLUME_THRESHOLD = 30_000_000_000 

        for m_code, m_name in markets:
            print(f"📡 {m_name} 실시간 랭킹 데이터 수집 중...")
            raw_stocks = self.kis.get_market_rankings(m_code)
            
            if not raw_stocks:
                print(f"❌ {m_name} 데이터를 가져오지 못했습니다.")
                continue

            # 상위 15개 종목만 정밀 분석
            analysis_targets = raw_stocks[:15]
            print(f"🎯 분석 후보군 {len(analysis_targets)}개 추출 완료.")
            
            for s in analysis_targets:
                name = s.get('hts_kor_isnm')
                code = s.get('mksc_shrn_iscd')
                price = float(s.get('stck_prpr', 0))
                volume_money = float(s.get('acml_tr_pbmn', 0))
                
                # 거래대금 필터링
                if volume_money < VOLUME_THRESHOLD:
                    # print(f"⏩ 스킵: {name} (거래대금 {volume_money/1e8:.1f}억 < {VOLUME_THRESHOLD/1e8:.1f}억)")
                    continue

                print(f"💎 AI 심층 분석 중: {name} ({volume_money/1e8:.1f}억)")
                try:
                    analysis = self.analyze_deep_with_ai(name, price, volume_money, m_name)
                    
                    if analysis and analysis.get("score", 0) > 0.35: # 기준 점수 살짝 완화 (0.4 -> 0.35)
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
                        print(f"✅ 추천 종목 전송 완료: {name} (Score: {analysis['score']})")
                    else:
                        print(f"⚠️ 점수 미달로 제외: {name} (Score: {analysis.get('score') if analysis else 'N/A'})")
                except Exception as e:
                    print(f"🚨 {name} 분석 중 에러: {e}")
                
                # Gemini API 레이트 리밋 방지 (Free tier 고려)
                time.sleep(10.0)

        try:
            requests.post(f"{self.api_url}/end-scan", timeout=5)
            print(f"\n✅ 스캔 완료. 총 {len(self.target_stocks)}개 종목 포착.")
        except:
            pass

    def analyze_deep_with_ai(self, stock_name, price, volume, market):
        try:
            prompt = (
                f"종목: {stock_name}\n"
                f"데이터: 가격 {price}원, 거래대금 {volume}원, 시장 {market}\n"
                f"환경 상황: {self.macro_context}\n"
                "분석 지침: 소수점 3자리 정밀 점수(-1.000 ~ 1.000)를 포함한 JSON 형식으로 응답하세요.\n"
                "형식: {\"score\": 0.718, \"summary\": \"요약\", \"tech\": \"기술적\", \"ext\": \"대외적\"}"
            )
            response = self.ai_model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text.strip())
        except Exception as e:
            print(f"AI 호출 에러: {e}")
            return None

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
        try: 
            requests.post(f"{self.api_url}/update", json=payload, timeout=5)
        except Exception as e: 
            print(f"전송 실패: {e}")

    def live_update_loop(self):
        while True:
            try:
                self.run_full_scan()
                print("💤 다음 스캔까지 대기 중 (10분)...")
                time.sleep(600)
            except Exception as e:
                print(f"🚨 루프 에러: {e}")
                time.sleep(60)

if __name__ == "__main__":
    scanner = DeepScanner()
    scanner.run_full_scan()
    scanner.live_update_loop()
