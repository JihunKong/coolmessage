# CoolMessenger AI 자동화

쿨메신저 메시지를 자동으로 분석하여 Google 캘린더 이벤트나 Tasks에 추가하는 프로그램입니다.

## 기능

- 쿨메신저 .udb 파일 실시간 감지
- OpenAI GPT를 통한 메시지 분석
- Google 캘린더 자동 이벤트 생성
- Google Tasks 자동 할일 추가
- 윈도우 시작 시 자동 실행
- 백그라운드 실행 (시스템 트레이)

## 설치

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. Google API 설정:
   - Google Cloud Console에서 프로젝트 생성
   - Calendar API와 Tasks API 활성화
   - OAuth 2.0 클라이언트 ID 생성
   - `credentials.json` 파일을 프로젝트 폴더에 저장

3. OpenAI API 키 설정:
   - `coolmessenger_auto.py` 파일에서 `OPENAI_API_KEY` 변수 수정

4. 데이터베이스 경로 설정:
   - `coolmessenger_auto.py` 파일에서 `DB_PATH` 변수를 실제 .udb 파일 경로로 수정

## 사용법

### 기본 실행
```bash
python coolmessenger_auto.py
```

### 윈도우 시작 프로그램 등록
```bash
python coolmessenger_auto.py --setup-startup
```

### 윈도우 시작 프로그램 제거
```bash
python coolmessenger_auto.py --remove-startup
```

### 백그라운드 모드 실행 (시스템 트레이)
```bash
python coolmessenger_auto.py --background
```

### 시스템 트레이 없이 백그라운드 실행
```bash
python coolmessenger_auto.py --background --no-tray
```

## 설정

### 1. .udb 파일 경로 찾기
쿨메신저 데이터베이스 파일은 보통 다음 위치에 있습니다:
```
C:\Users\[사용자명]\AppData\Local\CoolMessenger\Memo\[이름].udb
```

### 2. Google API 인증
처음 실행 시 브라우저에서 Google 로그인이 필요합니다.

### 3. 메시지 분석 규칙
- 날짜/시간이 포함된 메시지 → 캘린더 이벤트
- 할일/작업 관련 메시지 → Tasks 추가
- 우선순위: 캘린더 > Tasks

## 문제 해결

### 시스템 트레이 오류
```bash
pip install pystray Pillow
```

### Google API 인증 오류
1. `credentials.json` 파일 확인
2. Google Cloud Console에서 API 활성화 확인
3. `token.pickle` 파일 삭제 후 재인증

### .udb 파일 감지 안됨
1. 파일 경로 확인
2. 파일 권한 확인
3. 쿨메신저가 실행 중인지 확인

## 주의사항

- OpenAI API 사용료가 발생할 수 있습니다
- Google API 할당량 제한이 있습니다
- 개인정보가 포함된 메시지 처리 시 주의하세요

## 🚀 상세 설치 및 설정 가이드

### 사전 요구사항

- Windows 10/11
- Python 3.8 이상
- 쿨메신저 설치 및 사용 중
- OpenAI API 계정
- Google 계정 (Google Cloud Console 접근)

### 설치 방법

#### 1. 저장소 클론
```bash
git clone https://github.com/your-username/coolmessage.git
cd coolmessage
```

#### 2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

#### 3. 환경 설정 파일 생성
```bash
# .env.example을 .env로 복사
copy .env.example .env
```

#### 4. 설정 파일 편집
`.env` 파일을 열어서 다음 정보를 입력하세요:

```env
# OpenAI API 키
OPENAI_API_KEY=sk-your-actual-openai-api-key

# 쿨메신저 데이터베이스 파일 경로
UDB_PATH=C:\Users\YOUR_USERNAME\AppData\Local\CoolMessenger\Memo\YOUR_NAME.udb

# Google API 설정 파일명 (기본값: credentials.json)
GOOGLE_CREDENTIALS_FILE=credentials.json
```

### 상세 설정 가이드

#### OpenAI API 키 발급

1. [OpenAI 플랫폼](https://platform.openai.com/api-keys)에 접속
2. 로그인 후 "Create new secret key" 클릭
3. 생성된 키를 `.env` 파일의 `OPENAI_API_KEY`에 입력

#### 쿨메신저 데이터베이스 경로 찾기

1. Windows 탐색기에서 주소창에 다음 입력:
   ```
   %LOCALAPPDATA%\CoolMessenger\Memo
   ```
2. 본인 이름으로 된 `.udb` 파일 경로를 복사
3. `.env` 파일의 `UDB_PATH`에 전체 경로 입력

**예시:**
```
C:\Users\홍길동\AppData\Local\CoolMessenger\Memo\홍길동.udb
```

#### Google API 설정

##### 1. Google Cloud Console 설정
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. API 및 서비스 > 라이브러리에서 다음 API 활성화:
   - Google Calendar API
   - Google Tasks API

##### 2. OAuth 2.0 클라이언트 ID 생성
1. API 및 서비스 > 사용자 인증 정보
2. "사용자 인증 정보 만들기" > "OAuth 클라이언트 ID"
3. 애플리케이션 유형: "데스크톱 애플리케이션"
4. 이름: "CoolMessenger" (또는 원하는 이름)
5. JSON 파일 다운로드
6. 다운로드한 파일을 프로젝트 폴더에 `credentials.json`으로 저장

##### 3. OAuth 동의 화면 설정 (필요시)
1. API 및 서비스 > OAuth 동의 화면
2. 사용자 유형: "외부" 선택
3. 앱 정보 입력 (앱 이름, 사용자 지원 이메일 등)
4. 범위 추가: 
   - `../auth/calendar.events`
   - `../auth/tasks.readonly`

### 사용법

#### 기본 실행
```bash
python coolmessenger_auto.py
```

#### 윈도우 시작 프로그램 등록
```bash
python coolmessenger_auto.py --setup-startup
```

#### 윈도우 시작 프로그램 제거
```bash
python coolmessenger_auto.py --remove-startup
```

#### 백그라운드 모드 실행 (시스템 트레이)
```bash
python coolmessenger_auto.py --background
```

#### 시스템 트레이 없이 백그라운드 실행
```bash
python coolmessenger_auto.py --background --no-tray
```

### 첫 실행 시 확인사항

#### 1. Google 인증
- 첫 실행 시 브라우저에서 Google 로그인 필요
- 인증 완료 후 `token.pickle` 파일이 자동 생성됨

#### 2. 메시지 분석 테스트
- 쿨메신저에 테스트 메시지 전송
- 콘솔에서 분석 결과 확인

#### 3. 자동 실행 설정
```bash
# 시작 프로그램 등록
python coolmessenger_auto.py --setup-startup

# 백그라운드 모드로 실행
python coolmessenger_auto.py --background
```

### 파일 구조

```
coolmessage/
├── coolmessenger_auto.py    # 메인 프로그램
├── startup_manager.py       # 윈도우 시작 프로그램 관리
├── system_tray.py          # 시스템 트레이 기능
├── requirements.txt        # 필요한 패키지 목록
├── .env                    # 환경 설정 (생성 필요)
├── .env.example           # 환경 설정 예시
├── .gitignore             # Git 무시 파일 목록
├── credentials.json       # Google API 인증 파일 (생성 필요)
├── token.pickle          # Google 인증 토큰 (자동 생성)
├── last_processed.txt    # 마지막 처리된 메시지 (자동 생성)
└── README.md             # 이 파일
```

### 문제 해결

#### 시스템 트레이 오류
```bash
pip install pystray Pillow
```

#### Google API 인증 오류
1. `credentials.json` 파일 확인
2. Google Cloud Console에서 API 활성화 확인
3. `token.pickle` 파일 삭제 후 재인증

#### .udb 파일 감지 안됨
1. `.env` 파일의 `UDB_PATH` 경로 확인
2. 파일 권한 확인
3. 쿨메신저가 실행 중인지 확인

#### OpenAI API 오류
1. `.env` 파일의 `OPENAI_API_KEY` 확인
2. OpenAI 계정 크레딧 잔액 확인
3. API 키 권한 확인

#### 인코딩 오류 (한글 깨짐)
Windows 터미널에서 UTF-8 설정:
```bash
chcp 65001
```

### 주의사항

- OpenAI API 사용료가 발생할 수 있습니다
- Google API 할당량 제한이 있습니다
- 개인정보가 포함된 메시지 처리 시 주의하세요
- `.env` 파일과 `credentials.json`은 절대 공유하지 마세요

### 기여하기

1. 이 저장소를 포크하세요
2. 새 기능 브랜치를 만드세요 (`git checkout -b feature/새기능`)
3. 변경사항을 커밋하세요 (`git commit -am '새 기능 추가'`)
4. 브랜치에 푸시하세요 (`git push origin feature/새기능`)
5. Pull Request를 생성하세요

### 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.

### 지원

문제가 있거나 질문이 있으시면 [Issues](https://github.com/your-username/coolmessage/issues)에 등록해주세요.
