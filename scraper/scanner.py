import os
import requests
import time
import json
import warnings
from dotenv import load_dotenv
from kis_client import KISClient

# 🤫 불필요한 경고 메시지 억제
warnings.filterwarnings("ignore", category=FutureWarning)

load_dotenv()

print("🚀 [Scanner] 로컬 전용 초고속 스캐너 가동...", flush=True)

class DeepScanner:
    def __init__(self):
        self.kis = KISClient()
        self.api_url = os.getenv("SWING_API_URL", "http://127.0.0.1:8000")
        print(f"🚀 [Scanner] 분석 엔진 가동 (Target: {self.api_url})", flush=True)

    def run_full_scan(self):
        print("📡 [Scanner] 전 종목 초고속 데이터 수집 시작...", flush=True)
        
        try: 
            requests.post(f"{self.api_url}/start-scan", timeout=5)
        except: pass

        markets = [("0001", "KOSPI"), ("1001", "KOSDAQ")]
        
        for m_code, m_name in markets:
            print(f"📡 [KIS] {m_name} 데이터 수집 중...", flush=True)
            try:
                raw_stocks = self.kis.get_market_rankings(m_code)
                if not raw_stocks: 
                    print(f"⚠️ {m_name} 데이터가 없습니다.", flush=True)
                    continue

                # 상위 20개 추출
                analysis_targets = raw_stocks[:20]
                print(f"DEBUG: {m_name} {len(analysis_targets)}개 종목 전송 시작...", flush=True)

                for index, s in enumerate(analysis_targets):
                    try:
                        name = s.get('hts_kor_isnm', 'Unknown')
                        code = s.get('mksc_shrn_iscd', '')
                        price = float(str(s.get('stck_prpr', 0)).replace(',', ''))
                        volume_money = float(str(s.get('acml_tr_pbmn', 0)).replace(',', ''))
                        
                        # AI 대신 수치 기반 점수 산출
                        score = 1.0 - (index / len(analysis_targets)) * 1.5
                        score = max(-1.0, min(1.0, round(score, 2)))

                        # 등급 부여
                        if index < 3: grade = "S"
                        elif index < 8: grade = "A"
                        else: grade = "B"

                        stock_data = {
                            "code": code,
                            "name": name,
                            "price": price,
                            "market": m_name,
                            "volume": volume_money,
                            "sentiment": score,
                            "summary": "로컬 Gemma 4 분석 대기 중...",
                            "tech_reason": "수급 상위 종목 포착",
                            "ext_reason": "실시간 거래량 모멘텀 분석 중",
                            "grade": grade
                        }
                        self.push_one_to_server(stock_data)
                    except: continue

            except Exception as outer_e:
                print(f"🚨 {m_name} 에러: {outer_e}", flush=True)

        try: 
            requests.post(f"{self.api_url}/end-scan", timeout=5)
            print("✅ 서버 데이터 업데이트 완료!", flush=True)
        except: pass

    def push_one_to_server(self, s):
        payload = {
            "code": s["code"], "name": s["name"], "market": s["market"],
            "current_price": s["price"], "volume": int(s["volume"] / 100_000_000),
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
