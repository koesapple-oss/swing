# Proxmox 서버 이전 가이드 (Swing Trading AI)

이 문서는 로컬 맥북 환경에서 개발된 시스템을 Proxmox(Linux) 환경으로 이전하여 24시간 가동 서버를 구축하는 방법을 설명합니다.

## 1. 서버 환경 설정 (LXC 추천)
- **OS**: Ubuntu 24.04 LTS (LXC Container)
- **Resources**: CPU 2 Core, RAM 4GB 이상 권장
- **Network**: Static IP 설정 (예: 192.168.0.100)

## 2. 필수 도구 설치
```bash
# 기본 도구 설치
sudo apt update && sudo apt install -y git python3-pip curl nginx

# uv 설치 (고속 패키지 관리자)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

## 3. 코드 배포 및 환경 변수 설정
```bash
# 저장소 클론 (또는 scp로 복사)
git clone <your-repo-url> /opt/swing
cd /opt/swing/scraper

# 맥북의 .env 파일을 /opt/swing/scraper/.env 위치로 복사
# KIS_APP_KEY, GEMINI_API_KEY 등이 정확한지 확인
```

## 4. 백엔드 서비스 등록 (Systemd)
서버 재부팅 시에도 자동으로 실행되도록 설정합니다.

### API Server (`/etc/systemd/system/swing-api.service`)
```ini
[Unit]
Description=Swing Trading API Server
After=network.target

[Service]
WorkingDirectory=/opt/swing/scraper
ExecStart=/root/.cargo/bin/uv run python api_server.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

### AI Scanner (`/etc/systemd/system/swing-scanner.service`)
```ini
[Unit]
Description=Swing Trading AI Scanner
After=swing-api.service

[Service]
WorkingDirectory=/opt/swing/scraper
ExecStart=/root/.cargo/bin/uv run python scanner.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

**활성화**: `sudo systemctl enable --now swing-api swing-scanner`

## 5. 프론트엔드 배포 (Flutter Web)
```bash
# 맥북에서 빌드 후 파일을 서버로 전송
cd frontend
flutter build web --release

# 서버의 Nginx 설정 (/etc/nginx/sites-available/default)
# root /opt/swing/frontend/build/web; 으로 경로 수정 후 restart
```

## 6. 주의 사항
- **IP 주소 수정**: Flutter 앱 내의 `localhost:8000` 주소를 Proxmox 서버의 실제 IP(`192.168.x.x:8000`)로 수정하여 다시 빌드해야 합니다.
- **방화벽**: `ufw allow 80`, `ufw allow 8000` 설정이 필요할 수 있습니다.
