
import os
import google.generativeai as genai
from dotenv import load_dotenv
import re

load_dotenv()

def analyze_stock(stock_name):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-3-flash-preview')
    
    prompt = (
        f"당신은 20년 경력의 수석 애널리스트입니다. 주식 '{stock_name}'을 분석하세요. "
        "반드시 아래 형식을 지키되, 각 항목은 30자 이상의 전문적인 통찰을 담으세요.\n"
        "점수|요약|기술적분석|대외적요인\n"
        "- 점수: -1.00에서 1.00 사이의 실수.\n"
        "- 요약: 현재 시장에서의 핵심 위치와 평가.\n"
        "- 기술적분석: 이평선, 거래량, 캔들 패턴 기반의 향후 전망.\n"
        "- 대외적요인: 산업 트렌드, 거시 경제, 개별 뉴스 호재/악재 분석."
    )
    
    print(f"🚀 '{stock_name}' 분석 시작 (모델: gemini-3-flash-preview)...")
    try:
        response = model.generate_content(prompt)
        print("✅ 분석 완료!")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
    except Exception as e:
        print(f"❌ 분석 실패: {e}")

if __name__ == "__main__":
    analyze_stock("대한해운")
