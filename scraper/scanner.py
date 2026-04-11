# Project: Swing
# Agent 2: The Scanner (Hyper-Deep Analysis Mode)
# Path: scraper/scanner.py

import os
import requests
import time
import re
import google.generativeai as genai
from dotenv import load_dotenv
from kis_client import KISClient

load_dotenv()

def init_ai():
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    # 🔥 차단을 피하기 위해 가장 검증된 1.5-flash 모델을 기본으로 사용합니다.
    return genai.GenerativeModel('gemini-1.5-flash')

class DeepScanner:
    def __init__(self):
        self.kis = KISClient()
        self.ai_model = init_ai()
        print("🔍 [Hyper-Deep] 정밀 분석 엔진 가동 (분석 주기: 60초)")
            
        self.local_url = "http://localhost:8000"
        self.target_stocks = []

    def run_full_scan(self):
        print("⚡ 시장 전수 분석 시퀀스 가동...")
        markets = [("0001", "KOSPI"), ("1001", "KOSDAQ")]
        
        all_candidates = []
        for m_code, m_name in markets:
            raw_stocks = self.kis.get_market_rankings(m_code)
            for s in raw_stocks:
                name = s.get('hts_kor_isnm')
                code = s.get('mksc_shrn_iscd')
                price = float(s.get('stck_prpr', 0))
                volume_money = float(s.get('acml_tr_pbmn', 0))
                
                if volume_money >= 50_000_000_000:
                    analysis = self.analyze_deep_with_ai(name)
                    sentiment = analysis["score"]
                    
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
                    time.sleep(60.0)
        
    def analyze_deep_with_ai(self, stock_name):
        try:
            # 🔥 성의 없는 답변을 방지하기 위해 구체적인 '전문가적 의견'을 요구하는 프롬프트
            prompt = (
                f"당신은 20년 경력의 수석 애널리스트입니다. 주식 '{stock_name}'을 분석하세요. "
                "반드시 아래 형식을 지키되, 각 항목은 30자 이상의 전문적인 통찰을 담으세요.\n"
                "점수|요약|기술적분석|대외적요인\n"
                "- 점수: -1.00에서 1.00 사이의 실수.\n"
                "- 요약: 현재 시장에서의 핵심 위치와 평가.\n"
                "- 기술적분석: 이평선, 거래량, 캔들 패턴 기반의 향후 전망.\n"
                "- 대외적요인: 산업 트렌드, 거시 경제, 개별 뉴스 호재/악재 분석."
            )
            response = self.ai_model.generate_content(prompt)
            content = response.text.replace('`', '').strip()
            
            parts = content.split('|')
            if len(parts) >= 4:
                score_str = re.findall(r"[-+]?\d*\.\d+|\d+", parts[0])
                score = float(score_str[0]) if score_str else 0.5
                return {
                    "score": score, "summary": parts[1].strip(),
                    "tech": parts[2].strip(), "ext": parts[3].strip()
                }
            raise Exception("AI 응답 형식이 올바르지 않습니다.")
                
        except Exception as e:
            # 🔥 에러가 났음을 사용자가 알 수 있도록 문구를 수정
            print(f"❌ {stock_name} 분석 실패: {e}")
            return {
                "score": 0.0, 
                "summary": "🚨 AI 분석 일시적 차단 (구글 할당량 초과)", 
                "tech": "서버 IP가 구글로부터 일시적 제한을 받고 있습니다. 잠시 후 재개됩니다.", 
                "ext": "이 메시지가 지속되면 API 키의 유료 티어 전환을 검토하세요."
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
