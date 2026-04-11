# Swing Project: Deployment & Architecture Guide

이 문서는 프로젝트의 실제 배포 및 운영 절차를 정의합니다.

## 1. Firebase 설정 (Infrastructure)

### Firestore 보안 규칙 (Security Rules)
```javascript
service cloud.firestore {
  match /databases/{database}/documents {
    // 추천 종목: 스캐너만 생성 가능, 모든 유저 읽기 가능
    match /recommendations/{docId} {
      allow read: if true;
      allow write: if request.auth.token.admin == true; // Admin 전용
    }
    
    // 유저 데이터: 본인만 접근 가능
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

### 환경 변수 관리
- **Scraper**: `scraper/.env`를 생성하여 KIS 및 Gemini 키 관리.
- **Frontend**: Firebase 프로젝트 설정 후 `firebase_options.dart` 자동 생성.

## 2. 한국투자증권(KIS) API 연동

### 인증 아키텍처
1. `POST /oauth2/tokenP` 호출하여 Access Token 획득.
2. 획득한 토큰(유효기간 24시간)을 캐싱하여 사용.
3. 시세 조회 시 `TR_ID: FHKST01010100`을 헤더에 포함.

## 3. 배포 파이프라인 (CI/CD)

### GitHub Actions (Proposed)
1. **Scraper Job**: 매일 오전 9시 시장 분석 시작 -> 결과 Firebase 업로드.
2. **Flutter Build**: 메인 브랜치 푸시 시 Firebase Hosting으로 웹 배포.

## 4. 보안 체크리스트
- [ ] `.env` 파일이 `.gitignore`에 포함되었는가?
- [ ] Firebase Key JSON 파일이 외부에 노출되지 않았는가?
- [ ] API 호출 시 슬로틀링(Throttle) 규정을 준수하는가? (초당 호출 제한)
