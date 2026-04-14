import os
import requests
import time
import re
import warnings
import google.generativeai as genai
import json
from dotenv import load_dotenv
from kis_client import KISClient

# 🤫 불필요한 경고 메시지 억제
warnings.filterwarnings("ignore", category=FutureWarning)

load_dotenv()

print("🚀 [Scanner] 시스템 초기화 시작...", flush=True)

def init_ai():
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    # 🚀 무료 할당량이 가장 넉넉하고 빠른 2.5-flash-lite 모델 사용
    return genai.GenerativeModel('models/gemini-2.5-flash-lite')

def safe_float(val):
    try:
        if val is None or str(val).strip() == "": return 0.0
        # 콤마 제거 등 기본적인 정제 후 변환
        clean_val = str(val).replace(',', '').strip()
        return float(clean_val)
    except:
        return 0.0

class DeepScanner:
    def __init__(self):
        self.kis = KISClient()
        self.ai_model = init_ai()
        self.macro_context = "장 개시 전 시장 주도 섹터 분석 중"
        self.api_url = os.getenv("SWING_API_URL", "http://127.0.0.1:8000")
        print(f"🚀 [Scanner] 분석 엔진 가동 (Target: {self.api_url})", flush=True)

    def run_full_scan(self):
        print("📡 [Scanner] 전 종목 스캔 및 AI 분석 시작...", flush=True)
        
        print(f"DEBUG: [1] 서버({self.api_url})에 스캔 시작 신호 전송...", flush=True)
        try: 
            requests.post(f"{self.api_url}/start-scan", timeout=5)
            print("DEBUG: [2] 스캔 시작 신호 전송 성공", flush=True)
        except Exception as e: 
            print(f"DEBUG: [2] 스캔 시작 신호 전송 실패: {e}", flush=True)

        # 🚀 통신 확인용 초기 데이터 즉시 전송
        print("DEBUG: [3] 테스트 데이터 전송 시도...", flush=True)
        try:
            self.push_one_to_server({
                "code": "000000", "name": "AI 분석 가동됨", "price": 0, "market": "SYSTEM",
                "volume": 0, "sentiment": 0.99, "summary": "연결 성공! 시장 데이터를 분석하기 시작합니다.",
                "tech_reason": "연결 완료", "ext_reason": "분석 대기 중", "grade": "S"
            })
            print("DEBUG: [4] 테스트 데이터 전송 성공", flush=True)
        except Exception as e:
            print(f"DEBUG: [4] 테스트 데이터 전송 실패: {e}", flush=True)

        markets = [("0001", "KOSPI"), ("1001", "KOSDAQ")]
        
        for m_code, m_name in markets:
            print(f"📡 [KIS] {m_name} 데이터 수집 중...", flush=True)
            try:
                raw_stocks = self.kis.get_market_rankings(m_code)
                print(f"DEBUG: [5] {m_name} KIS 수집 완료 ({len(raw_stocks) if raw_stocks else 0}개)", flush=True)
                
                if not raw_stocks:
                    raw_stocks = []

                # 장전(새벽) 상황 감지 (안전한 숫자 변환 적용)
                is_pre_market = all(safe_float(s.get('acml_tr_pbmn', 0)) == 0 for s in raw_stocks[:5]) if raw_stocks else True
                
                if is_pre_market:
                    print(f"⚠️ 시뮬레이션 모드: {m_name} 분석 시작", flush=True)
                    analysis_targets = raw_stocks[:3] if raw_stocks else []
                else:
                    # 실시간 거래대금이 있을 경우 100억 이상만 필터링
                    analysis_targets = [s for s in raw_stocks[:15] if safe_float(s.get('acml_tr_pbmn', 0)) >= 10_000_000_000]
                    
                    # 🌙 야간 대응
                    if not analysis_targets and raw_stocks:
                        analysis_targets = raw_stocks[:2]

                # 💡 타겟이 없으면 삼성전자 샘플 강제 삽입
                if not analysis_targets and m_name == "KOSPI":
                    analysis_targets = [{"hts_kor_isnm": "삼성전자", "mksc_shrn_iscd": "005930", "stck_prpr": "84000", "acml_tr_pbmn": "100000000000"}]

                print(f"DEBUG: [6] {m_name} 최종 분석 대상: {[s.get('hts_kor_isnm') for s in analysis_targets]}", flush=True)

                for index, s in enumerate(analysis_targets):
                    try:
                        name = s.get('hts_kor_isnm', 'Unknown')
                        code = s.get('mksc_shrn_iscd', '')
                        price = safe_float(s.get('stck_prpr', 0))
                        volume_money = safe_float(s.get('acml_tr_pbmn', 0))
                        
                        # 가상 거래대금 부여
                        if volume_money == 0:
                            volume_money = (1000 - (index * 100)) * 100_000_000

                        print(f"💎 AI 분석 시작 ({index+1}/{len(analysis_targets)}): {name}", flush=True)
                        
                        # 🛡 429 할당량 초과 대비 재시도 로직
                        max_retries = 2
                        for attempt in range(max_retries):
                            try:
                                analysis = self.analyze_deep_with_ai(name, price, volume_money, m_name)
                                if analysis:
                                    score = safe_float(analysis.get("score", 0))
                                    while abs(score) > 1.0:
                                        score = score / 10.0
                                        if abs(score) < 0.1 and score != 0: break
                                    score = round(score, 2)
                                    
                                    # 📊 등급 세분화 (더 엄격한 기준 적용)
                                    if score >= 0.75:
                                        grade = "S"
                                    elif score >= 0.45:
                                        grade = "A"
                                    else:
                                        grade = "B"
                                    
                                    stock_data = {
                                        "code": code, "name": name, "price": price, "market": m_name,
                                        "volume": volume_money, "sentiment": score,
                                        "summary": analysis["summary"],
                                        "tech_reason": analysis["tech"],
                                        "ext_reason": analysis["ext"],
                                        "grade": grade
                                    }
                                    self.push_one_to_server(stock_data)
                                    print(f"✅ 분석 완료: {name} (점수: {score})", flush=True)
                                    break
                                    
                            except Exception as ai_e:
                                if "429" in str(ai_e) and attempt < max_retries - 1:
                                    print(f"⚠️ [Gemini] 할당량 초과! 65초 대기 후 재시도... ({attempt+1}/{max_retries})", flush=True)
                                    time.sleep(65)
                                else:
                                    raise ai_e
                        
                        time.sleep(7.5) # RPM 준수
                    except Exception as inner_e:
                        print(f"🚨 {s.get('hts_kor_isnm')} 분석 도중 에러 발생: {inner_e}", flush=True)
                        continue

            except Exception as outer_e:
                print(f"🚨 {m_name} 마켓 분석 도중 치명적 에러 발생: {outer_e}", flush=True)
                continue

        try: 
            requests.post(f"{self.api_url}/end-scan", timeout=5)
            print("✅ 모든 분석 시뮬레이션 완료!", flush=True)
        except: 
            pass

    def analyze_deep_with_ai(self, stock_name, price, volume, market):
        prompt = (
            f"종목: {stock_name}\n"
            f"데이터: 현재가 {price}원, 거래대금 {volume}원, 시장 {market}\n"
            f"매크로: {self.macro_context}\n"
            "당신은 실전 투자를 책임지는 전문 스윙 트레이더입니다. 다음 기준에 따라 분석하세요:\n"
            "1. 리스크와 보상을 냉정하게 비교하여 합산 점수를 산출하십시오.\n"
            "2. 거래대금이 풍부하거나 기술적 지지가 확실한 경우 가산점을 부여하고, 반대의 경우 감점하십시오.\n"
            "3. 점수(score)는 -1.0(매우 위험)에서 1.0(매우 유망) 사이의 소수점으로 0.01 단위로 산출하세요.\n"
            "4. 요약(summary)은 투자자가 한눈에 판단할 수 있도록 핵심 근거 위주로 작성하십시오.\n"
            "5. JSON 형식으로만 응답: {\"score\": 0.55, \"summary\": \"요약\", \"tech\": \"기술적분석\", \"ext\": \"대외전망\"}"
        )
        response = self.ai_model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text.strip())

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
