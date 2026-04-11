
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("\n🔍 [Server Diagnostic] Proxmox 서버에서 사용 가능한 모델 리스트:")
print("-" * 50)
try:
    models = genai.list_models()
    count = 0
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            print(f"👉 사용 가능: {m.name}")
            count += 1
    if count == 0:
        print("❌ 'generateContent'를 지원하는 모델이 하나도 발견되지 않았습니다.")
except Exception as e:
    print(f"❌ 모델 목록 조회 중 치명적 에러: {e}")
print("-" * 50)
print(f"총 {count}개의 유효한 모델을 찾았습니다.\n")
