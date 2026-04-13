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
    # 🔥 실시간 뉴스 데이터 반영을 위해 google_search_retrieval 툴을 활성화합니다.
    # 🔥 Lite 모델을 상속받아 할당량(RPM) 문제도 동시에 해결합니다.
    return genai.GenerativeModel(
        'models/gemini-flash-lite-latest',
        tools=[{"google_search_retrieval": {}}]
    )

class DeepScanner:
    def __init__(self):
        self.kis = KISClient()
        self.ai_model = init_ai()
        self.macro_context = ""
        self.last_macro_update = 0  # 마지막 매크로 업데이트 시간 추적
        print("🔍 [Hyper-Deep] 전문가급 정밀 분석 엔진 가동 (분석 주기: 60초)")
            
        self.local_url = "http://localhost:8000"
        self.target_stocks = []

    def update_macro_context(self):
        print("🌍 글로벌 매크로 경제 및 긴급 뉴스 스캔 중...")
        try:
            # 매크로 분석용 검색 프롬프트
            search_prompt = (
                "오늘 한국 및 글로벌 주식 시장에 강력한 영향을 미칠 수 있는 '최신' 긴급 뉴스 3가지를 브리핑하세요. "
                "특히 '미국-이란 협상', '유가 급등락', '미국 금리/물가' 관련 최신 뉴스를 우선적으로 찾으세요. "
                "반드시 현재 시각(2026년 4월 12일) 기준의 최신 팩트를 기반으로 요약하세요."
            )
            # 검색 도구를 활용하여 최신 정보 획득
            response = self.ai_model.generate_content(search_prompt)
            self.macro_context = response.text
            print(f"✅ 매크로 뉴스 업데이트 완료:\n{self.macro_context[:200]}...")
        except Exception as e:
            print(f"⚠️ 매크로 뉴스 스캔 실패: {e}")
            self.macro_context = "최신 매크로 데이터 연동 일시 장애 (검색 도구 확인 필요)"

    def run_full_scan(self):
        print("⚡ 시장 전수 분석 시퀀스 가동...")
        
        # 0. 기존 데이터 초기화 (Stale Data 방지)
        try:
            requests.delete(f"{self.local_url}/clear")
            print("🧹 이전 스캔 데이터 초기화 완료.")
        except:
            print("⚠️ 데이터 초기화 요청 실패 (서버 확인 필요)")

        # 1시간(3600초)에 한 번만 매크로 뉴스 업데이트 수행 (사용자 요청 반영)

        current_time = time.time()
        if current_time - self.last_macro_update > 3600:
            self.update_macro_context()
            self.last_macro_update = current_time
        else:
            print(f"ℹ️ 매크로 뉴스 생략 (마지막 업데이트: {int((current_time - self.last_macro_update)/60)}분 전)")
        
        markets = [("0001", "KOSPI"), ("1001", "KOSDAQ")]
        
        all_candidates = []
        for m_code, m_name in markets:
            print(f"📡 {m_name} 시장 데이터 수집 중...")
            raw_stocks = self.kis.get_market_rankings(m_code)
            # 429 에러 방지를 위해 상위 15개 종목으로 압축 분석 (Professional Focus)
            raw_stocks = raw_stocks[:15]
            print(f"✅ {m_name} 상위 15개 종목 수집 완료. 필터링 시작...")
            
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
                    
                    # 429 방지를 위해 대기 시간을 8초로 상향 조정
                    time.sleep(8.0)
        
    def analyze_deep_with_ai(self, stock_name, price, volume, market):
        try:
            # 🔥 점수 획일화(0.45, 0.65 고정)를 타파하기 위한 초정밀 채점 로직
            prompt = (
                f"당신은 월스트리트의 전설적인 헤지펀드 매니저입니다. '{stock_name}' 종목을 현미경 분석하세요.\n\n"
                f"[현재 거시 경제 상황]\n{self.macro_context}\n\n"
                f"[시장 데이터]\n"
                f"- 현재가: {price:,.0f}원 / 당일 수급: {volume:,.0f}원 / 시장: {market}\n\n"
                "분석 및 채점 지침 (변별력 강화):\n"
                "1. 점수는 반드시 소수점 3자리까지 정밀하게 산출하세요 (예: 0.718, -0.245).\n"
                "2. 0.45, 0.65와 같은 상습적이고 모호한 점수를 부여할 시 즉시 탈락입니다. 종목 간 우열을 명확히 가리세요.\n"
                "3. 최신 뉴스(거시 상황 포함)가 해당 종목의 섹터(에너지, 방산, 반도체 등)에 미칠 직간접적 영향을 결정적으로 반영하세요.\n"
                "4. 평가 기준:\n"
                "   - [+점수]: 거래대금 폭발 + 매집 흔적 + 강력한 매크로 호재\n"
                "   - [-점수]: 고점 횡보 + 실질적 재료 부족 + 매크로 리스크 (특히 이란 리스크 등)\n"
                "5. 반드시 아래 JSON 형식을 엄수하며, 인사이트의 질적 수준을 높이세요.\n\n"
                "{\n"
                "  \"score\": 0.000, // -1.000에서 1.000 사이의 고해상도 점수\n"
                "  \"summary\": \"오늘의 수급 성격과 모멘텀 강도 요약\",\n"
                "  \"tech\": \"가격대 및 수급 확산 속도 기반 기술적 분석\",\n"
                "  \"ext\": \"미공개 시나리오 및 매크로 변수 연동 분석 (실시간 뉴스 반영 필)\"\n"
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
        print("🔄 실시간 동적 분석 루프 진입...")
        while True:
            try:
                self.run_full_scan()
                print("💤 분석 완료. 10분간 시장 모니터링 후 재스캔(Deep Refresh)...")
                time.sleep(600) 
            except Exception as e:
                print(f"🚨 루프 실행 중 장애 발생: {e}")
                time.sleep(60)

if __name__ == "__main__":
    scanner = DeepScanner()
    scanner.run_full_scan()
    scanner.live_update_loop()
