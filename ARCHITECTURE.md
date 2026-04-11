# Phase 0: 시스템 아키텍처 (Swing Trading AI)

이 문서는 모든 에이전트와 개발자가 준수해야 할 기본 규칙을 정의합니다.

## 🧠 AI Infrastructure (2026 Edition)
- **Core Engine**: Gemini 3.1 Flash-Lite (Latest)
- **Service Tier**: Gemini Advanced (Paid Subscription)
- **Optimization Strategy**: 
  - Ultra-speed sequential scanning (0.3s delay)
  - Full-market scan coverage (KOSPI 100 + KOSDAQ 100)
  - Deep reasoning for Technical & External factors

## 🛠️ Tech Stack & Connectivity
- **Frontend**: Flutter (Riverpod 3.0 Notifier)
- **Backend / Scanner**: Python (KIS OpenAPI, Gemini AI)
- **Infrastructure**: Local Hybrid Mode (Zero Cloud Cost)
- **API Bridge**: FastAPI (localhost:8000)

## 🎨 Andrej Karpathy Coding Principles
1. **Data > Code**: 데이터 품질 우선 조사.
2. **Overfit to a Batch**: 24시간 내 핵심 케이스(Single Case) 성공 증명.
3. **Simplicity is Scalability**: 코드를 보고 데이터 흐름이 읽히게 단순화.
4. **Gradient Descent Thinking**: 반복적 최적화로 실패율 감소.
5. **High-Bandwidth Sync**: 모든 근거와 기록의 투명한 문서화.

## 📂 Project Structure
- `frontend/`: Flutter 애플리케이션
- `scraper/`: Python 데이터 스캐너 및 FastAPI 로컬 서버
- `.antigravity_config.json`: AI 모델 및 요금제 설정 저장소

---
*Last updated: 2026-04-11 (Gemini 3.1 Ultra-Speed Mode Applied)*
