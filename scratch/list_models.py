import os
import google.generativeai as genai
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '../scraper/.env'))

def list_available_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        return

    try:
        genai.configure(api_key=api_key)
        print("🔍 사용 가능한 Gemini 모델 목록:")
        print("-" * 50)
        
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # 모델 이름과 지원 기능 출력
                print(f"✅ 명칭: {m.name}")
                print(f"   설명: {m.description}")
                print("-" * 50)
                
    except Exception as e:
        print(f"🚨 모델 목록을 가져오는 중 에러 발생: {e}")

if __name__ == "__main__":
    list_available_models()
