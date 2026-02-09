# 늘봄 최종 프로젝트 보고서

## 문서 정보

| 항목 | 내용 |
|------|------|
| 프로젝트명 | 늘봄 (AI 기반 노인 돌봄 음성 분석 시스템) |
| 문서 버전 | 1.0 |
| 작성일 | 2026-02-09 |
| 개발 기간 | 2025년 12월 ~ 2026년 2월 (2025.12.05 ~ 2026.02.10) |
| 개발 인원 | 5명 (최선임 총괄기획, 지태민 프론트엔드, 김승민 백엔드, 최대영 DB/IoT, 조민솔 기획/문서) |
| 문서 유형 | 최종 프로젝트 보고서 |

---

## 1. 프로젝트 개요

### 1.1 배경

우리나라는 급속한 고령화로 인해 독거 어르신 인구가 지속적으로 증가하고 있으며, 2025년 기준 65세 이상 독거노인 수는 약 200만 명을 넘어서고 있다. 독거 어르신은 사회적 고립, 건강 악화, 돌발 사고 등의 위험에 노출되어 있으나, 돌봄 인력의 부족으로 24시간 상시 케어가 어려운 실정이다.

기존의 노인 돌봄 서비스는 정기 방문 또는 단순한 안부 전화 수준에 머물러 있어, 어르신의 감정 변화나 건강 이상 징후를 조기에 감지하기 어렵다. 특히 음성은 인간의 심리 상태, 인지 기능, 신체 건강을 반영하는 핵심 바이오마커로서, AI 기반 음성 분석 기술을 활용하면 비접촉 방식으로 어르신의 상태를 지속적으로 모니터링할 수 있다.

이러한 사회적 필요에 대응하여, AI 음성 인식 및 감정 분석 기술, 대규모 언어 모델(LLM) 기반 대화 시스템, IoT 센서 연동을 결합한 통합 돌봄 플랫폼 '늘봄'을 개발하게 되었다.

### 1.2 목적

늘봄 프로젝트의 목적은 다음과 같다.

1. **AI 음성 분석을 통한 어르신 건강 모니터링**: 음성의 속도, 피치, 감정, 어휘력 등 8가지 차원을 분석하여 어르신의 인지 및 정서 상태를 정량적으로 평가한다.
2. **AI 대화 도우미 '보미'를 통한 정서적 교류**: 감정 인식 기반의 공감 대화를 제공하여 독거 어르신의 외로움을 완화하고 정서적 안정을 돕는다.
3. **보호자 원격 돌봄 지원**: 대시보드 및 리포트를 통해 보호자(가족/요양사)가 어르신의 상태를 실시간으로 확인하고, 위험 상황 시 즉각적인 알림을 받을 수 있도록 한다.
4. **비접촉 돌봄 인프라 구축**: IoT 디바이스와 센서를 활용하여 별도의 장치 조작 없이도 자연스러운 돌봄이 이루어지는 환경을 조성한다.

### 1.3 프로젝트 범위

| 구분 | 내용 |
|------|------|
| 음성 분석 | STT 변환, 감정 분석(텍스트+오디오 앙상블), 8차원 종합 점수 산출 |
| AI 대화 | Q&A 데이터셋 매칭 + GPT-4o-mini LLM 대화 생성, 감정 기반 프롬프트 |
| 음성 합성 | Edge TTS 기반 한국어 음성 합성 (8종 이상 음성 지원) |
| 보호자 대시보드 | 감정/활동/인지 현황, 일간/주간/월간 리포트, 감정 변화 차트 |
| 사용자 관리 | 보호자 회원가입/로그인, 어르신 정보 등록 및 수정 |
| 디바이스 관리 | IoT 디바이스 등록, 센서 상태 확인, 음성 세션 관리 |
| 알림 시스템 | 위험 감지 실시간 알림, 알림 이력 관리 |

### 1.4 팀 구성

| 이름 | 구분 | 주요 역할 |
|------|------|----------|
| 최선임 | 총괄기획 | 프로젝트 전체 개념 정의, 요구사항 우선순위 결정, 일정/리스크 관리, 산출물 품질관리 |
| 지태민 | 프론트엔드 | 프론트 화면 UI 구현, 어르신 친화 UX 적용, 반응형 및 접근성 기본 적용 |
| 김승민 | 백엔드 | 서비스 API 설계 및 구현, AI 모듈 호출 파이프라인 연결, 점수 산출 로직 |
| 최대영 | DB/IoT | DB 설계 및 관리, IoT 센서/디바이스 로그 수집, 생활 데이터 통합 |
| 조민솔 | 기획/문서 | 회의 운영 지원, WBS 업데이트, 시연 시나리오/FAQ/사용 가이드 작성 |

### 1.5 서비스 구성

| 서비스 | 포트 | 프레임워크 | 설명 |
|--------|------|-----------|------|
| Flask Web Server | 5000 | Flask | 메인 웹 서버 (프론트엔드 + API + 음성분석) |
| FastAPI Analysis Server | 8000 | FastAPI | 대안 음성 분석 전용 API 서버 |
| MySQL Database | 3306 | MySQL | 관계형 데이터베이스 (care_db) |

---

## 2. 시스템 아키텍처

### 2.1 전체 시스템 구성도

```
+=====================================================================+
|                     Client (Browser / Device)                        |
|  +--------------------+  +--------------------------------------+   |
|  |  보호자 대시보드     |  |  어르신 음성 대화 인터페이스 (보미)   |   |
|  |  (PC / 모바일)      |  |  (IoT 디바이스 / 브라우저)           |   |
|  +--------+-----------+  +------------------+-------------------+   |
+===========|==============================|==========================+
            | HTTPS                        | HTTPS (Audio Stream)
            +---------------+--------------+
                            |
                            v
+=====================================================================+
|                    Flask Web Server (:5000)                           |
|  +----------------------------------------------------------------+ |
|  |  API Layer                                                      | |
|  |  /api/login  /api/signup  /api/analyze  /api/check-alert        | |
|  |  /api/activity-daily  /api/activity-weekly  /api/activity-monthly| |
|  |  /api/update-guardian  /api/update-senior  /api/change-password  | |
|  |  /api/add-device  /api/check-sensor  /api/create-voice-session  | |
|  |  /api/tts-audio/<file>  /api/voice-health  /api/alert-list      | |
|  +----------------------------------------------------------------+ |
|                                                                      |
|  +---------------+  +----------------+  +-------------------------+ |
|  |  Whisper STT  |  |  Emotion       |  |  LLM Handler            | |
|  |  (faster-     |  |  Ensemble      |  |  (GPT-4o-mini           | |
|  |   whisper     |  |  KcELECTRA     |  |   + Q&A Dataset         | |
|  |   tiny/int8)  |  |  + Wav2Vec2    |  |   50+ Q&A pairs)        | |
|  +---------------+  +----------------+  +-------------------------+ |
|                                                                      |
|  +---------------+  +----------------+  +-------------------------+ |
|  |  Edge TTS     |  |  SpeechAnalyzer|  |  VoiceDBHandler         | |
|  |  (한국어 8종) |  |  (8차원 점수)   |  |  (MySQL care_db)        | |
|  +---------------+  +----------------+  +-------------------------+ |
+===========================+==========================================+
                            |
                            v
+=====================================================================+
|                    MySQL Database (care_db)                           |
|  +--------------+ +--------------+ +--------------+ +--------------+ |
|  | tb_guardian   | | tb_senior    | | tb_device    | | tb_sensor    | |
|  +--------------+ +--------------+ +--------------+ +--------------+ |
|  +--------------+ +--------------+ +--------------+ +--------------+ |
|  | tb_sensing   | | tb_voice_log | | tb_analysis  | | tb_alert     | |
|  +--------------+ +--------------+ +--------------+ +--------------+ |
+=====================================================================+
```

### 2.2 음성 분석 파이프라인

```
+----------+     +----------+     +--------------+     +--------------+
|  음성    |     |  STT     |     |  감정 분석    |     |  점수 산출   |
|  녹음    | --> | (Whisper) | --> | (Text+Audio) | --> | (8차원)     |
| (WAV)    |     |  tiny    |     |  Ensemble    |     |  평균 점수   |
+----------+     +----------+     +--------------+     +------+-------+
                                                              |
                                                              v
+----------+     +----------+     +--------------+     +--------------+
|  TTS     |     |  LLM     |     |  Q&A 매칭    |     |  DB 저장    |
|  음성    | <-- |  응답    | <-- |  우선 시도   |     |  + 알림     |
|  출력    |     |  생성    |     |  -> LLM 호출 |     |  체크       |
| (MP3)    |     |(GPT-4o)  |     |              |     |             |
+----------+     +----------+     +--------------+     +--------------+
```

### 2.3 기술 구성 요약

| 계층 | 기술 | 역할 |
|------|------|------|
| 프론트엔드 | HTML5 + CSS3 + JavaScript (ES6+) | 보호자 대시보드, 보미 대화 UI |
| 차트 | Chart.js | 감정/활동 데이터 시각화 |
| 웹 서버 | Flask 5000 / FastAPI 8000 | API 라우팅, 템플릿 렌더링 |
| STT | faster-whisper (tiny, int8) | 한국어 음성 인식 |
| 감정 분석 (텍스트) | KcELECTRA (MelissaJ) | 6가지 감정 분류 |
| 감정 분석 (오디오) | Wav2Vec2-XLSR | 음성 신호 감정 인식 |
| 피치 분석 | librosa YIN 알고리즘 | Z-peak 역동성 계산 |
| LLM | OpenAI GPT-4o-mini | 감정 기반 대화 생성 |
| TTS | Microsoft Edge TTS | 한국어 음성 합성 (8종) |
| 데이터베이스 | MySQL (care_db) | 사용자/분석/알림 데이터 저장 |
| 보안 | PyOpenSSL (자체서명 인증서) | HTTPS 통신 암호화 |

---

## 3. 기술 스택

### 3.1 Backend

#### Flask (메인 웹 서버)

| 항목 | 내용 |
|------|------|
| 프레임워크 | Flask |
| 포트 | 5000 |
| 역할 | 전체 웹 서비스 제공 (라우팅, API, 템플릿 렌더링) |
| 주요 라이브러리 | Flask-CORS, Werkzeug, Jinja2 |
| 특이사항 | SSE(Server-Sent Events) 스트리밍으로 분석 진행 상태 실시간 전송 |

`bomi.py`가 Flask 메인 서버 파일로, 회원가입/로그인, 음성 분석, 활동량 조회, 디바이스 관리, 알림 등 전체 API를 포함한다.

#### FastAPI (대안 분석 서버)

| 항목 | 내용 |
|------|------|
| 프레임워크 | FastAPI |
| 포트 | 8000 |
| 역할 | 비동기 음성 분석 전용 API |
| 실행 | Uvicorn ASGI 서버 |
| 특이사항 | CORS 전체 허용, startup/shutdown 이벤트로 모델 관리 |

`server.py`가 FastAPI 서버 파일로, 음성 파일 업로드 및 분석 → Q&A 매칭/LLM 응답 → DB 저장의 전체 파이프라인을 제공한다.

### 3.2 AI 모델

#### Whisper STT (Speech-to-Text)

| 항목 | 내용 |
|------|------|
| 모델 | OpenAI Whisper (tiny) |
| 엔진 | faster-whisper (CTranslate2 기반 고속 엔진) |
| 양자화 | int8 (속도 극대화) |
| 언어 | 한국어 (ko) 고정 |
| VAD | vad_filter=True (음성 구간 자동 감지) |
| Beam Size | 1 (속도 최적화) |
| 출력 | 텍스트, 단어 수, WPM, 발화 길이, 침묵 구간 |

#### KcELECTRA (텍스트 감정 분석)

| 항목 | 내용 |
|------|------|
| 모델 | MelissaJ/koelectra-emotion-6-emotion-base |
| 기반 모델 | KcELECTRA-base-v2022 (beomi) |
| 감정 클래스 | 기쁨, 중립, 분노, 슬픔, 불안, 당황 (6가지) |
| 입력 | 텍스트 (max_length=128, truncation) |
| 출력 | 감정 라벨 + softmax 확률분포 |

#### Wav2Vec2 (오디오 감정 분석)

| 항목 | 내용 |
|------|------|
| 모델 | jungjongho/wav2vec2-xlsr-korean-speech-emotion-recognition |
| 기반 모델 | Wav2Vec2-XLSR (다국어 사전학습) |
| 입력 | 오디오 파형 (16kHz, 최대 3초) |
| 출력 | 감정 라벨 + softmax 확률분포 |
| 감정 매핑 | angry->분노, happy->기쁨, sad->슬픔, neutral->중립, fear->불안 |

#### 감정 앙상블 (Emotion Ensemble)

| 항목 | 내용 |
|------|------|
| 방식 | 멀티모달 가중치 결합 (텍스트 primary + 오디오 secondary) |
| 피치 분석 | librosa YIN 알고리즘으로 Z-score 기반 Pitch Dynamics 계산 |
| 최종 결정 규칙 | 기본: 텍스트 감정 / Z-peak > 2.5 && 오디오 감정이 강한 감정 && 오디오 신뢰도 > 0.6일 때 오디오 감정 반영 |
| Q&A 덮어쓰기 | Q&A 데이터셋 매칭 시 해당 Q&A의 감정/점수로 최종값 대체 |

#### GPT-4o-mini (LLM 대화 생성)

| 항목 | 내용 |
|------|------|
| 모델 | OpenAI GPT-4o-mini |
| 페르소나 | 20대 손녀 '보미' (친근한 존댓말, 1-2문장 짧은 응답) |
| 전략 | (1) Q&A 데이터셋(50+쌍) 매칭 우선 → (2) 매칭 실패 시 LLM 호출 |
| 프롬프트 구성 | 기본 페르소나 + 감정별 대화 전략 + 점수 기반 위험 감지 |
| 위험 감지 | 평균 점수 < 50 또는 감정 점수 < 40 → 고위험 프롬프트 추가 |
| max_completion_tokens | 1500 |
| 대화 이력 | 최대 10턴 유지 (시스템 프롬프트 실시간 업데이트) |

#### Edge TTS (음성 합성)

| 항목 | 내용 |
|------|------|
| 엔진 | Microsoft Edge TTS (edge-tts 라이브러리) |
| 기본 음성 | ko-KR-SunHiNeural (밝고 친절한 여성) |
| 지원 음성 | 여성 5종 (SunHi, JiMin, SeoHyeon, SoonBok, YuJin) + 남성 4종 (InJoon, HyunSu, BongJin, GookMin) |
| 출력 형식 | MP3 |
| 속도 조절 | rate 파라미터 (-10% ~ +10%) |
| 비동기 처리 | asyncio 기반 비동기 생성 |

### 3.3 Frontend

| 기술 | 용도 | 설명 |
|------|------|------|
| HTML5 | 마크업 | Jinja2 템플릿 엔진 기반 (9개 템플릿 페이지) |
| CSS3 | 스타일링 | 반응형 디자인, CSS Variables, 다크/라이트 테마 |
| JavaScript (ES6+) | 인터랙션 | MediaRecorder API, EventSource (SSE), Fetch API |
| Chart.js | 데이터 시각화 | 감정 분석 차트, 일간/주간/월간 활동 통계 그래프 |
| Material Icons | 아이콘 | Google Material Design 아이콘 |
| Daum Postcode API | 주소 검색 | 회원가입 시 우편번호/주소 자동 입력 |

#### 주요 화면 구성

| 페이지 | 템플릿 파일 | 설명 |
|--------|-----------|------|
| 메인 | index.html | 랜딩 페이지 |
| 로그인 | login.html | 보호자 인증 |
| 회원가입 | signup.html | 보호자 + 어르신 정보 등록 |
| 대시보드 | dashboard.html | 감정/활동/인지 상태 종합 현황 |
| 보미 대화 | bomi.html | 어르신과 AI 대화 인터페이스 |
| 건강 정보 | health.html | 건강 상태 상세 조회 |
| 리포트 | report.html | 일간/주간/월간 분석 리포트 |
| 마이페이지 | mypage.html | 보호자/어르신 정보 수정 |
| 모달 | modals.html | 공통 모달 컴포넌트 |

### 3.4 데이터베이스

| 항목 | 내용 |
|------|------|
| DBMS | MySQL |
| 데이터베이스명 | care_db |
| 호스트 | 192.168.0.31 |
| 포트 | 3306 |
| 사용자 | root |
| 문자셋 | utf8mb4 |
| 드라이버 | PyMySQL |
| 커서 | DictCursor (bomi.py) / 기본 커서 (db_handler.py) |

---

## 4. 데이터베이스 설계

### 4.1 테이블 목록

| 테이블명 | 설명 | 비고 |
|----------|------|------|
| tb_guardian | 보호자(가족/요양사) 정보 | 인증/로그인 주체 |
| tb_senior | 어르신 정보 | 돌봄 대상, 보호자와 1:N 관계 |
| tb_device | IoT 디바이스 | 음성 수집 장치, 어르신에 귀속 |
| tb_sensor | 센서 정보 | 디바이스에 장착된 센서 (motion/env/voice) |
| tb_sensing | 센서 수집 데이터 | 센서별 측정값 및 음성 세션 |
| tb_voice_log | 음성 분석 기본 정보 | STT 텍스트, 반응시간, 발화길이 |
| tb_analysis | 감정 분석 상세 정보 | 감정 라벨, 감정별 비율 |
| tb_alert | 알림 정보 | 위험 감지/이상 상태 알림 |

### 4.2 테이블 상세

#### tb_guardian (보호자)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| guardian_id | INT (PK, AI) | 보호자 고유 ID |
| user_id | VARCHAR | 로그인 아이디 |
| password | VARCHAR | 비밀번호 |
| name | VARCHAR | 이름 |
| phone | VARCHAR | 연락처 |
| post_num | VARCHAR | 우편번호 |
| addr1 | VARCHAR | 기본 주소 |
| addr2 | VARCHAR | 상세 주소 |
| relation_with_senior | VARCHAR | 어르신과의 관계 |
| voice_collection_approved | CHAR(1) | 음성 수집 동의 여부 |
| created_at | DATETIME | 가입일시 |

#### tb_senior (어르신)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| senior_id | INT (PK, AI) | 어르신 고유 ID |
| name | VARCHAR | 이름 |
| birthdate | DATE | 생년월일 |
| gender | CHAR(1) | 성별 (M/F) |
| phone | VARCHAR | 연락처 |
| post_num | VARCHAR | 우편번호 |
| addr1 | VARCHAR | 기본 주소 |
| addr2 | VARCHAR | 상세 주소 |
| relation_with_guardian | VARCHAR | 보호자와의 관계 |
| living_type | VARCHAR | 거주 형태 (독거/가족) |
| guardian_id | INT (FK) | 보호자 ID |
| created_at | DATETIME | 등록일시 |

#### tb_device (디바이스)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| device_id | INT (PK, AI) | 디바이스 고유 ID |
| device_uid | VARCHAR | 디바이스 시리얼 번호 |
| device_name | VARCHAR | 디바이스 이름 |
| location | VARCHAR | 설치 위치 |
| senior_id | INT (FK) | 어르신 ID |
| installed_at | DATETIME | 설치일시 |

#### tb_sensor (센서)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| sensor_id | INT (PK, AI) | 센서 고유 ID |
| device_id | INT (FK) | 디바이스 ID |
| sensor_type | VARCHAR | 센서 유형 (motion/env/voice) |
| created_at | DATETIME | 등록일시 |

#### tb_sensing (센서 데이터)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| sensing_id | INT (PK, AI) | 센싱 고유 ID |
| sensor_id | INT (FK) | 센서 ID |
| sensing_type | VARCHAR | 센싱 유형 (voice_session 등) |
| sensing_value | VARCHAR | 센싱 값 |
| value | INT | 수치값 (활동 감지 등) |
| created_at | DATETIME | 측정일시 |

#### tb_voice_log (음성 분석 로그)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| voice_id | INT (PK, AI) | 음성 로그 고유 ID |
| senior_id | INT (FK) | 어르신 ID |
| sensing_id | INT (FK) | 센싱 ID (0이면 센서 미연결) |
| voice_text | TEXT | STT 변환 텍스트 |
| response_time_sec | FLOAT | 반응 시간 (초) |
| utterance_length | FLOAT | 발화 길이 (초) |
| created_at | DATETIME | 기록일시 |

#### tb_analysis (감정 분석 상세)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| analysis_id | INT (PK, AI) | 분석 고유 ID |
| voice_idx | INT (FK) | 음성 로그 ID |
| emotion_label | VARCHAR | 최종 감정 라벨 |
| stt_text | TEXT | STT 텍스트 |
| behavior_policy | VARCHAR | 행동 정책 (예약) |
| hap_ratio | FLOAT | 기쁨 비율 |
| sad_ratio | FLOAT | 슬픔 비율 |
| neu_ratio | FLOAT | 중립 비율 |
| ang_ratio | FLOAT | 분노 비율 |
| anxi_ratio | FLOAT | 불안 비율 |
| emba_ratio | FLOAT | 당황 비율 |
| heart_ratio | FLOAT | 상처 비율 |

#### tb_alert (알림)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| alert_id | INT (PK, AI) | 알림 고유 ID |
| alert_type | VARCHAR | 알림 유형 |
| alert_content | TEXT | 알림 내용 |
| sented_at | DATETIME | 발송일시 |
| received_yes | INT | 읽음 여부 (0=미읽음, 1=읽음) |

### 4.3 ER 다이어그램

```
tb_guardian (1) ---------- (N) tb_senior
                                    |
                                    | (1)
                                    v
                               tb_device (N)
                                    |
                                    | (1)
                                    v
                               tb_sensor (N)
                                    |
                                    | (1)
                                    v
                               tb_sensing (N)
                                    |
                    +---------------+---------------+
                    v                               v
              tb_voice_log (N)                tb_alert (N)
                    |
                    | (1)
                    v
              tb_analysis (1)
```

---

## 5. 주요 기능

### 5.1 음성 분석 파이프라인

늘봄의 음성 분석 파이프라인은 다음 단계로 구성된다.

1. **음성 녹음**: 브라우저 MediaRecorder API 또는 PyAudio 기반 녹음기를 통해 어르신의 음성을 WAV 형식으로 수집한다. 배경 소음 자동 보정(RMS 기반) 및 상대적 침묵 감지(배경의 2배 + 최대음량의 20% 하이브리드)를 지원한다.
2. **STT 변환**: faster-whisper 엔진의 Whisper tiny 모델(int8 양자화)을 사용하여 한국어 음성을 텍스트로 변환한다. VAD 필터를 적용하여 음성 구간만 선별하고, 발화 시간/침묵 시간을 동시에 계산한다.
3. **감정 분석**: 텍스트와 오디오 두 가지 모달리티를 활용한 앙상블 방식으로 감정을 인식한다 (5.2절 상세).
4. **8차원 점수 산출**: 8가지 음성 품질 지표를 각각 0~100점으로 산출하고 평균 종합 점수를 계산한다 (5.3절 상세).
5. **AI 응답 생성**: 분석 결과를 기반으로 감정 인식 대화를 생성한다 (5.4절 상세).
6. **TTS 출력**: 생성된 텍스트 응답을 Edge TTS를 통해 음성으로 합성하여 어르신에게 전달한다.
7. **DB 저장**: 모든 분석 결과를 tb_voice_log와 tb_analysis에 저장하고, 위험 상태 감지 시 tb_alert에 알림을 기록한다.

### 5.2 감정 앙상블 분석

감정 분석은 텍스트 기반과 오디오 기반 두 가지 모델의 결과를 결합하는 앙상블 방식을 사용한다.

**텍스트 감정 분석 (KcELECTRA)**
- MelissaJ/koelectra-emotion-6-emotion-base 모델을 사용하여 6가지 감정(기쁨, 중립, 분노, 슬픔, 불안, 당황)을 분류한다.
- softmax 확률분포를 통해 감정별 신뢰도를 산출한다.

**오디오 감정 분석 (Wav2Vec2)**
- jungjongho/wav2vec2-xlsr-korean-speech-emotion-recognition 모델을 사용하여 음성 파형에서 직접 감정을 인식한다.
- 16kHz 리샘플링, 최대 3초 구간만 분석하여 속도를 최적화한다.

**Z-score 기반 Pitch Dynamics**
- librosa YIN 알고리즘으로 피치(f0)를 추출하고, Z-score를 계산하여 음성의 역동성(Z-peak)을 측정한다.
- Z-peak가 높을수록 감정적 변화가 큰 발화임을 나타낸다.

**최종 감정 결정 규칙**
1. 기본: 텍스트 감정을 따른다.
2. Z-peak > 2.5이고, 오디오 감정이 분노/기쁨/슬픔이며, 텍스트가 중립이거나 오디오 신뢰도 > 0.6이면 오디오 감정으로 교체한다.
3. Q&A 데이터셋 매칭 시 해당 Q&A의 정의된 감정/점수로 최종값을 덮어쓴다.

### 5.3 8차원 음성 분석 점수

어르신의 음성을 8가지 차원에서 분석하여 0~100점의 점수를 산출한다.

| 차원 | 지표 | 최적 범위 | 가중치 | 설명 |
|------|------|----------|--------|------|
| Speed | WPM (분당 어절 수) | 100~150 | 1.0 | 말의 속도 |
| Duration | 발화 시간 (초) | 3~10 | 1.0 | 적절한 발화 길이 |
| Response | 반응 시간 (초) | 0~2 | 1.0 | 질문 후 응답까지 시간 |
| Word Count | 단어 수 | 5~20 | 1.0 | 발화 내 어절 수 |
| Vocabulary | TTR (Type-Token Ratio) | 0.6~0.9 | 1.0 | 어휘 다양성 |
| Silence | 무음 구간 (초) | 0~1 | 1.0 | 발화 내 침묵 패턴 |
| Emotion | 감정 안정성 | 70~100 | **1.5** | 감정 분석 기반 점수 (가중치 높음) |
| Vitality | VPR (발화/침묵 비율) | 2.0~10.0 | 1.0 | 활력도 (우울/무기력 지표) |

**점수 계산 로직**
- 최적 범위 내: 100점
- 최적 범위 미만: `(실측값 / 최적하한) x 100`
- 최적 범위 초과: `100 - ((초과분 / 최적상한) x 100)`
- 감정 점수: 긍정 감정 80~100점, 중립 70~80점, 부정 감정 0~60점 (신뢰도 반영)
- 종합 점수: 8개 차원의 산술 평균

### 5.4 Q&A 데이터셋 + LLM 대화

AI 대화 도우미 '보미'는 2단계 응답 전략을 사용한다.

**1단계: Q&A 데이터셋 매칭 (우선)**
- 10개 카테고리(인사, 약 복용, 식사, 건강, 감정, 날씨, 가족, 활동, 안전, 시간)의 50개 이상 Q&A 쌍을 보유한다.
- 3단계 매칭 로직: (1) 정확한 일치 → (2) 부분 일치(포함 관계) → (3) 키워드 일치(공통 단어 1개 이상)
- 매칭 성공 시 사전 정의된 답변, 감정 라벨, 감정 점수를 사용한다.
- 데이터셋 매칭이 성공하면 분석 결과의 감정/점수도 데이터셋 값으로 덮어쓴다.

**2단계: LLM 호출 (매칭 실패 시)**
- GPT-4o-mini를 호출하여 감정 인식 기반 자연스러운 대화를 생성한다.
- 시스템 프롬프트는 3가지 요소로 구성된다: (1) 기본 페르소나(20대 손녀 보미), (2) 현재 감정 상태에 따른 대화 전략(슬픔->위로, 분노->경청, 불안->안심 등), (3) 점수 기반 위험 감지(고위험/중위험 프롬프트 추가)
- 대화 이력을 최대 10턴까지 유지하여 문맥을 이어간다.

### 5.5 TTS 음성 합성

Edge TTS를 사용하여 AI 응답을 자연스러운 한국어 음성으로 합성한다.

- 기본 음성: ko-KR-SunHiNeural (밝고 친절한 여성 목소리)
- 9종의 한국어 음성을 지원하며, 어르신에게 친근감을 줄 수 있는 목소리를 선택할 수 있다.
- 비동기(asyncio) 방식으로 MP3 파일을 생성하고, 브라우저에서 재생한다.

### 5.6 대시보드

보호자 대시보드는 다음 정보를 제공한다.

- **감정 현황**: 최근 감정 분석 결과 및 감정 변화 추이 차트
- **활동량**: 일간/주간/월간 움직임 감지 횟수 (모션 센서 기반)
- **인지 상태**: 어휘 다양성, 반응 속도 등 인지 관련 지표
- **알림**: 위험 상태 감지 알림 및 읽음 관리
- 모든 차트는 Chart.js를 활용하여 시각화된다.

---

## 6. 보안 설계

### 6.1 HTTPS 통신

| 항목 | 내용 |
|------|------|
| 방식 | 자체 서명(Self-signed) SSL 인증서 |
| 인증서 파일 | cert.pem, key.pem |
| 생성 도구 | PyOpenSSL (generate_cert.py) |
| 키 알고리즘 | RSA 2048 |
| 유효기간 | 1년 |
| 적용 대상 | Flask 서버 (:5000) |

자체 서명 인증서를 통해 클라이언트-서버 간 HTTPS 암호화 통신을 적용한다. 브라우저의 MediaRecorder API는 보안 컨텍스트(HTTPS)에서만 동작하므로 SSL 적용이 필수적이다.

### 6.2 API 키 관리

| 항목 | 내용 |
|------|------|
| 대상 | OpenAI API 키 |
| 저장 위치 | api-key/openapi.env |
| 로딩 방식 | python-dotenv로 환경변수에서 로드 |
| 접근 방식 | os.getenv("OPENAI_API_KEY") |

API 키는 소스코드에 직접 포함하지 않고, .env 파일에 분리하여 환경변수 방식으로 관리한다.

### 6.3 세션 관리

| 항목 | 내용 |
|------|------|
| 세션 키 | Flask secret_key 설정 |
| SameSite | None (외부 도메인 허용, Ngrok 대응) |
| Secure | True (HTTPS에서만 쿠키 전송) |
| CORS | 전체 허용 (allow_origins=["*"]) |

### 6.4 데이터베이스 보안

| 항목 | 내용 |
|------|------|
| SQL Injection 방지 | 파라미터 바인딩 (PreparedStatement) |
| 트랜잭션 | 저장 실패 시 rollback() 처리 |
| 비밀번호 저장 | 평문 저장 (향후 해싱 적용 권장) |

---

## 7. API 설계

### 7.1 엔드포인트 목록

| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| GET | `/` | 메인 페이지 | - |
| GET | `/health` | 서버 상태 확인 (FastAPI) | - |
| POST | `/api/signup` | 보호자 회원가입 (보호자+어르신 동시 등록) | - |
| POST | `/api/login` | 보호자 로그인 (기기 목록 포함 반환) | - |
| POST | `/api/check-duplicate` | 아이디 중복 확인 | - |
| POST | `/api/update-guardian` | 보호자 정보 수정 | 로그인 필요 |
| POST | `/api/update-senior` | 어르신 정보 수정 | 로그인 필요 |
| POST | `/api/change-password` | 비밀번호 변경 | 로그인 필요 |
| POST | `/api/analyze` | 음성 파일 분석 (SSE 스트리밍) | 로그인 필요 |
| POST | `/analyze` | 음성 파일 분석 (FastAPI JSON) | - |
| GET | `/api/voice-health` | 음성 분석 시스템 상태 확인 | - |
| GET/POST | `/api/check-sensor` | 센서 존재 여부 확인 | 로그인 필요 |
| POST | `/api/create-voice-session` | 음성 세션 생성 (sensing_id 발급) | 로그인 필요 |
| GET | `/api/tts-audio/<filename>` | TTS 음성 파일 제공 | - |
| POST | `/api/add-device` | IoT 디바이스 등록 | 로그인 필요 |
| POST | `/api/activity-daily` | 일간 활동량 조회 | 로그인 필요 |
| POST | `/api/activity-weekly` | 주간 활동량 조회 (7일) | 로그인 필요 |
| POST | `/api/activity-monthly` | 월간 활동량 조회 (4주) | 로그인 필요 |
| POST | `/api/simulate-data` | 데이터 시뮬레이션 (테스트용) | 로그인 필요 |
| GET | `/api/check-alert` | 실시간 알림 확인 (미읽음 최신 1건) | - |
| POST | `/api/alert-list` | 최근 알림 목록 조회 (10건) | - |
| POST | `/api/alert-read-all` | 모든 알림 읽음 처리 | - |
| GET | `/latest-sensing` | 최신 센서 데이터 조회 (FastAPI) | - |

### 7.2 주요 API 상세

#### POST /api/analyze (음성 분석)

**요청 (multipart/form-data)**:
- `audio_file`: 음성 파일 (필수)
- `senior_id`: 시니어 ID (기본값: 1)
- `sensing_id`: 센싱 ID (필수)
- `generate_response`: AI 응답 생성 여부 (기본값: true)

**응답 (SSE Stream)**:
단계별 진행 상태를 SSE(Server-Sent Events)로 실시간 전송하고, 최종 결과를 JSON으로 반환한다.

```
step 1: 파일 저장 완료
step 2: STT 음성 인식 중...
step 3: STT 완료
step 4: 감정 분석: {감정} ({신뢰도}%)
step 5: AI 응답 생성 중...
step 5.5: 목소리 만드는 중...
step 5.7: TTS 완료
step 6: DB 저장 중...
step complete: 최종 결과 JSON
```

#### POST /api/login (로그인)

**요청 (JSON)**: `{ "username": "...", "password": "..." }`

**응답 (JSON)**: 보호자 정보, 어르신 정보, 등록된 디바이스 목록을 포함한 사용자 데이터 반환.

---

## 8. 배포 환경

### 8.1 서버 구성

| 항목 | 내용 |
|------|------|
| 운영체제 | Windows |
| Python 버전 | 3.x (venv 가상환경) |
| GPU | CUDA 지원 시 자동 활용 (torch.cuda) |
| 메인 서버 | Flask (:5000) - bomi.py |
| 대안 서버 | FastAPI (:8000) - server.py |
| 데이터베이스 | MySQL (:3306) - 192.168.0.31 |

### 8.2 디렉토리 구조

```
neulbomProject/
+-- bomi.py                     # Flask 메인 서버 (보호자 웹)
+-- server.py                   # FastAPI 분석 서버 (대안)
+-- main.py                     # 파일 분석 모드 (단독 실행)
+-- integration.py              # 통합 시스템 (녹음+분석+LLM+TTS+DB)
+-- analyzer.py                 # 음성 분석 엔진 (STT + 감정 + 점수)
+-- emotion_model.py            # 감정 앙상블 엔진 (KcELECTRA + Wav2Vec2)
+-- llm_handler.py              # LLM 핸들러 (GPT-4o-mini 직접)
+-- llm_handler_with_qa_v2.py   # LLM 핸들러 (Q&A 매칭 + GPT-4o-mini)
+-- db_handler.py               # DB 핸들러 (분석 결과 저장)
+-- db_handler_server.py        # DB 핸들러 (서버용)
+-- tts_handler.py              # TTS 핸들러 (Edge TTS)
+-- audio_recorder.py           # 음성 녹음기 (PyAudio)
+-- qa_dataset_improved.py      # Q&A 데이터셋 (50+ 쌍)
+-- visualize.py                # 분석 결과 시각화 (matplotlib)
+-- generate_cert.py            # SSL 인증서 생성
+-- cert.pem / key.pem          # SSL 인증서 파일
+-- config/
|   +-- __init__.py
|   +-- models.py               # AI 모델 설정
|   +-- scoring.py              # 점수 계산 기준
|   +-- db_config.py            # DB 연결 설정
+-- templates/
|   +-- index.html              # 메인 페이지
|   +-- login.html              # 로그인
|   +-- signup.html             # 회원가입
|   +-- dashboard.html          # 대시보드
|   +-- bomi.html               # 보미 대화
|   +-- health.html             # 건강 정보
|   +-- report.html             # 리포트
|   +-- mypage.html             # 마이페이지
|   +-- modals.html             # 공통 모달
+-- static/
|   +-- script.js               # 프론트엔드 JavaScript
|   +-- style.css               # 스타일시트
|   +-- images/                 # 보미 캐릭터 이미지
+-- api-key/
|   +-- openapi.env             # OpenAI API 키
+-- recordings/                 # 녹음 파일 저장
+-- tts_outputs/                # TTS 출력 파일 저장
+-- analysis_logs/              # 분석 로그
+-- data/                       # 테스트 오디오 데이터
+-- docs/                       # 프로젝트 문서
```

### 8.3 실행 방법

```bash
# 가상환경 활성화
.venv\Scripts\activate

# Flask 메인 서버 실행 (모델 자동 로드)
python bomi.py

# 또는 FastAPI 서버 실행
python server.py
```

서버 시작 시 다음 순서로 모델이 로드된다:
1. SpeechAnalyzer (Whisper + KcELECTRA + Wav2Vec2) - 2~3분 소요
2. LLMHandler (OpenAI API 연결)
3. VoiceDBHandler (MySQL 연결)
4. EdgeTTSHandler (TTS 초기화)

---

## 9. 프로젝트 성과

### 9.1 주요 성과

1. **멀티모달 감정 분석 구현**: 텍스트(KcELECTRA)와 오디오(Wav2Vec2)를 결합한 앙상블 감정 분석을 구현하여, 단일 모달리티 대비 감정 인식의 정확성과 강건성을 높였다.

2. **8차원 종합 음성 분석 체계 수립**: 말의 속도, 발화 길이, 반응 속도, 단어 수, 어휘 다양성, 침묵 패턴, 감정 안정성, 활력도의 8가지 차원으로 어르신의 상태를 다각적으로 평가하는 체계를 수립하였다.

3. **Q&A 데이터셋 + LLM 하이브리드 전략**: 사전 정의된 Q&A 데이터셋을 우선 검색하고, 매칭 실패 시 LLM을 호출하는 2단계 전략으로 응답의 신뢰성과 유연성을 동시에 확보하였다.

4. **실시간 분석 진행 표시**: SSE(Server-Sent Events) 스트리밍을 통해 음성 분석의 각 단계(STT, 감정 분석, AI 응답, TTS)를 실시간으로 사용자에게 표시하여 사용 경험을 개선하였다.

5. **통합 돌봄 플랫폼**: 음성 분석, AI 대화, 센서 데이터, 대시보드, 알림을 하나의 웹 플랫폼으로 통합하여 보호자가 원격에서 어르신의 상태를 종합적으로 파악할 수 있게 하였다.

### 9.2 기술 지표

| 지표 | 내용 |
|------|------|
| STT 모델 최적화 | Whisper tiny + int8 양자화 (실시간 변환 가능) |
| 감정 분석 모달리티 | 2종 (텍스트 + 오디오) |
| 감정 클래스 | 6종 (기쁨, 중립, 분노, 슬픔, 불안, 당황) |
| 음성 분석 차원 | 8종 |
| Q&A 데이터셋 | 10개 카테고리, 50+ Q&A 쌍 |
| TTS 음성 종류 | 9종 (여성 5 + 남성 4) |
| 프론트엔드 페이지 | 9개 |
| API 엔드포인트 | 21개 |
| DB 테이블 | 8개 |

---

## 10. 향후 개선 방향

### 10.1 보안 강화

- 비밀번호 해싱(bcrypt) 적용: 현재 평문 저장에서 암호화 저장으로 전환
- JWT 토큰 기반 인증: 세션 방식에서 토큰 기반 인증으로 전환
- API Rate Limiting: 과도한 요청 방지
- 공인 SSL 인증서 적용: 자체 서명에서 Let's Encrypt 등 공인 인증서로 전환

### 10.2 AI 모델 고도화

- STT 모델 업그레이드: Whisper tiny에서 small/medium으로 업그레이드하여 인식 정확도 향상
- 감정 분석 Fine-tuning: 노인 음성 데이터로 감정 모델 미세 조정
- 한국어 특화 LLM: GPT-4o-mini에서 한국어 특화 모델(예: EXAONE)로 전환 검토
- 인지 기능 평가 모델: 치매 조기 발견을 위한 인지 기능 평가 알고리즘 추가

### 10.3 기능 확장

- 영상 통화 연동: 음성 대화를 넘어 영상 기반 표정 분석 추가
- 다국어 지원: 한국어 외 다국어 STT/TTS 지원
- 약 복용 알림: 실시간 약 복용 시간 알림 및 복용 확인
- 긴급 호출 시스템: 음성 명령을 통한 119/보호자 긴급 호출
- 건강 데이터 연동: 혈압계, 체온계 등 건강 기기 데이터 통합

### 10.4 인프라 개선

- Docker 컨테이너화: 배포 자동화 및 환경 일관성 확보
- 클라우드 배포: AWS/GCP/Azure 클라우드 환경으로 이전
- 로드 밸런싱: 다수 사용자 동시 접속 대응
- CI/CD 파이프라인: 자동 빌드/테스트/배포 체계 구축
- 모니터링/로깅: Grafana, Prometheus 등을 활용한 시스템 모니터링

---

## 문서 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|----------|
| 1.0 | 2026-02-09 | - | 최초 작성 |
