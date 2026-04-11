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
    # 🔥 1.5 Flash의 압도적 할당량과 전문가용 프롬프트를 조합하여 24/7 고성능 분석을 구현합니다.
    return genai.GenerativeModel('gemini-1.5-flash-latest')

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
                    print(f"💎 전문가 분석 대상: {name} ({int(volume_money/100_000_000)}억) - 심층 분석 가동...")
                    analysis = self.analyze_deep_with_ai(name)
                    if not analysis: continue
                    
                    sentiment = analysis["score"]
                    print(f"📊 {name} 인사이트: {sentiment:.2f} | {analysis['summary'][:40]}...")
                    
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
                    
                    # 1.5 Flash는 10초 대기면 매우 안정적입니다.
                    time.sleep(10.0)
        
    def analyze_deep_with_ai(self, stock_name):
        try:
            # 🔥 1.5 모델의 한계를 넘는 30년 경력 수석 애널리스트 페르소나 주입
            prompt = (
                f"당신은 월스트리트 출신의 30년 경력 수석 퀀트 애널리스트이자 기술적 분석 전문가입니다. "
                f"주식 '{stock_name}'에 대해 기관 투자자 수준의 심층 보고서를 작성하세요.\n\n"
                "분석 지침:\n"
                "1. 시장의 노이즈를 배제하고 거래량의 질적 변화와 세력 매집 흔적을 추적하세요.\n"
                "2. 글로벌 매크로 트렌드와 해당 기업의 비즈니스 모델 간의 상관관계를 명확히 하세요.\n"
                "3. 반드시 아래 JSON 형식을 엄수하며, 각 필드는 최소 50자 이상의 밀도 높은 인사이트를 담으세요.\n\n"
                "{\n"
                "  \"score\": 0.00, // 기술적/기본적 분석을 종합한 투자 신뢰 점수 (-1.00 ~ 1.00)\n"
                "  \"summary\": \"핵심 투자 하이라이트 및 잠재적 리스트 요약\",\n"
                "  \"tech\": \"차트 패턴, 주요 이평선 이격도, 거래량 수급 기반의 정밀 추세 분석\",\n"
                "  \"ext\": \"글로벌 산업 사이클, 거시 경제 지표, 지정학적 요소 등 대외 분석\"\n"
                "}"
            )
            response = self.ai_model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            data = json.loads(response.text.strip())
            
            return {
                "score": float(data.get("score", 0.0)),
                "summary": data.get("summary", "분석 데이터 부족"),
                "tech": data.get("tech", "기술적 추세 분석 불가"),
                "ext": data.get("ext", "대외적 변수 데이터 부족")
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
