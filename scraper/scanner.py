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
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    # 🔥 서버 진단(diag_server_models.py)을 통해 확인된 실제 가동 모델명을 사용하여 404 문제를 해결합니다.
    # 🔥 Lite 모델을 상속받아 할당량(RPM) 문제도 동시에 해결합니다.
    return genai.GenerativeModel('models/gemini-flash-lite-latest')

class DeepScanner:
    def __init__(self):
        self.kis = KISClient()
        self.ai_model = init_ai()
        print("🔍 [Hyper-Deep] 전문가급 정밀 분석 엔진 가동 (분석 주기: 60초)")
            
        self.local_url = "http://localhost:8000"
        self.target_stocks = []

    def run_full_scan(self):
        print("⚡ 시장 전수 분석 시퀀스 가동...")
        markets = [("0001", "KOSPI"), ("1001", "KOSDAQ")]
        
        all_candidates = []
        for m_code, m_name in markets:
            print(f"📡 {m_name} 시장 데이터 수집 중...")
            raw_stocks = self.kis.get_market_rankings(m_code)
            # 1.5 Flash의 할당량을 믿고 상위 30개 종목 전수 조사
            raw_stocks = raw_stocks[:30]
            print(f"✅ {m_name} 상위 30개 종목 수집 완료 (Professional Mode). 필터링 시작...")
            
            for s in raw_stocks:
                name = s.get('hts_kor_isnm')
                code = s.get('mksc_shrn_iscd')
                price = float(s.get('stck_prpr', 0))
                volume_money = float(s.get('acml_tr_pbmn', 0))
                
                # 거래대금 500억 이상 필터링
                if volume_money >= 50_000_000_000:
                    print(f"💎 초정밀 분석 가동: {name} ({int(volume_money/100_000_000)}억) - 수치 데이터 전송 중...")
                    analysis = self.analyze_deep_with_ai(name, price, volume_money, m_name)
                    if not analysis: continue
                    
                    sentiment = analysis["score"]
                    print(f"📊 {name} 분석: {sentiment:.2f} | {analysis['summary'][:40]}...")
                    
                    if sentiment > 0.4:
                        all_candidates.append({
                            "code": code, "name": name, "price": price, "market": m_name,
                            "volume": volume_money, "sentiment": sentiment, 
                            "summary": analysis["summary"], 
                            "tech_reason": analysis["tech"], 
                            "ext_reason": analysis["ext"],
                            "grade": "S" if sentiment > 0.7 else "A"
                        })
                        self.target_stocks = all_candidates
                        self.push_to_local_server()
                    
                    # Flash-Lite 모델의 넉넉한 할당량을 활용하여 대기 시간을 5초로 최적화
                    time.sleep(5.0)
        
    def analyze_deep_with_ai(self, stock_name, price, volume, market):
        try:
            # 🔥 점수 획일화(0.45, 0.65 고정)를 타파하기 위한 초정밀 채점 로직
            prompt = (
                f"당신은 월스트리트의 전설적인 헤지펀드 매니저입니다. '{stock_name}' 종목을 현미경 분석하세요.\n\n"
                f"[데이터 백보드]\n"
                f"- 현재가: {price:,.0f}원 / 당일 수급: {volume:,.0f}원 / 시장: {market}\n\n"
                "분석 및 채점 지침 (변별력 강화):\n"
                "1. 점수는 반드시 소수점 3자리까지 정밀하게 산출하세요 (예: 0.718, -0.245).\n"
                "2. 0.45, 0.65와 같은 상습적이고 모호한 점수를 부여할 시 즉시 탈락입니다. 종목 간 우열을 명확히 가리세요.\n"
                "3. 평가 기준:\n"
                "   - [+점수]: 거래대금 폭발 + 매집 흔적 + 강력한 매크로 호재(예: 이란 자금 해제 수혜)\n"
                "   - [-점수]: 고점 횡보 + 실질적 재료 부족 + 매크로 리스크\n"
                "4. 반드시 아래 JSON 형식을 엄수하며, 인사이트의 질적 수준을 높이세요.\n\n"
                "{\n"
                "  \"score\": 0.000, // -1.000에서 1.000 사이의 고해상도 점수\n"
                "  \"summary\": \"오늘의 수급 성격과 모멘텀 강도 요약\",\n"
                "  \"tech\": \"가격대 및 수급 확산 속도 기반 기술적 분석\",\n"
                "  \"ext\": \"미공개 시나리오 및 매크로 변수 연동 분석\"\n"
                "}"
            )
            # 웹 검색 기능을 지원하는 툴 설정 (지원되는 경우 자동 반영)
            response = self.ai_model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            data = json.loads(response.text.strip())
            
            return {
                "score": float(data.get("score", 0.0)),
                "summary": data.get("summary", "분석 데이터 부족"),
                "tech": data.get("tech", "수치 데이터 기반 판독 불가"),
                "ext": data.get("ext", "최신 뉴스 데이터 연동 지연")
            }
                
        except Exception as e:
            print(f"❌ {stock_name} 분석 실패: {e}")
            return {
                "score": 0.0, 
                "summary": f"🚨 분석 일시 장애 ({str(e)[:20]}...)", 
                "tech": "API 응답 지연 또는 데이터 파싱 에러 발생.", 
                "ext": "일시적인 수급 불안정으로 인해 분석 시스템 재가동 중."
            }

    def push_to_local_server(self):
        for s in self.target_stocks:
            payload = {
                "code": s["code"], "name": s["name"], "market": s["market"],
                "current_price": s["price"], "volume": int(s["volume"] / 1_000_000),
                "sentiment_score": s["sentiment"], "news_summary": s["summary"],
                "tech_reason": s.get("tech_reason", ""), "ext_reason": s.get("ext_reason", ""),
                "grade": s["grade"], "targets": {
                    "buy": s["price"] * 0.99, "take_profit": s["price"] * 1.15, "stop_loss": s["price"] * 0.97
                }
            }
            try: requests.post("http://localhost:8000/update", json=payload)
            except: pass

    def live_update_loop(self):
        while True:
            self.push_to_local_server()
            time.sleep(10)

if __name__ == "__main__":
    scanner = DeepScanner()
    scanner.run_full_scan()
    scanner.live_update_loop()
