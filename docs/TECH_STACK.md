# 늘봄 기술 스택

## 문서 정보

| 항목 | 내용 |
|------|------|
| 프로젝트명 | 늘봄 (AI 기반 노인 돌봄 음성 분석 시스템) |
| 문서 버전 | 1.0 |
| 작성일 | 2026-02-09 |
| 개발 기간 | 2025년 12월 ~ 2026년 2월 (2025.12.05 ~ 2026.02.10) |
| 개발 인원 | 5명 (최선임 총괄기획, 지태민 프론트엔드, 김승민 백엔드, 최대영 DB/IoT, 조민솔 기획/문서) |

---

## 목차

1. [Backend (Python)](#backend-python)
2. [Frontend (HTML/CSS/JS)](#frontend-htmlcssjs)
3. [AI 모델](#ai-모델)
4. [인프라](#인프라)
5. [아키텍처](#아키텍처)
6. [기능별 기술 매핑](#기능별-기술-매핑)

---

## Backend (Python)

### 웹 프레임워크

| 라이브러리 | 용도 | 설명 |
|-----------|------|------|
| Flask | 메인 웹 서버 | 라우팅, 템플릿 렌더링, API 서비스 (Port 5000) |
| FastAPI | 대안 분석 서버 | 비동기 음성 분석 전용 API (Port 8000) |
| Uvicorn | ASGI 서버 | FastAPI 실행 서버 |
| Flask-CORS | CORS 처리 | 크로스 오리진 요청 허용 |
| Werkzeug | WSGI 유틸리티 | 파일 업로드, 보안 파일명 처리 |

### 데이터베이스

| 라이브러리 | 용도 | 설명 |
|-----------|------|------|
| PyMySQL | MySQL 드라이버 | care_db 연결 (192.168.0.31:3306) |

### AI / 딥러닝

| 라이브러리 | 용도 | 설명 |
|-----------|------|------|
| PyTorch | 딥러닝 프레임워크 | 감정 분석 모델 추론 |
| Transformers | NLP/Audio 모델 | HuggingFace 감정 분석 모델 로드 |
| faster-whisper | STT 엔진 | 음성-텍스트 변환 (tiny 모델, int8 양자화) |
| librosa | 오디오 처리 | 오디오 피처 추출, 피치 분석 |
| numpy | 수치 연산 | 오디오 신호 처리, 점수 계산 |
| ONNX Runtime | 모델 최적화 | 추론 성능 최적화 |

### LLM 연동

| 라이브러리 | 용도 | 설명 |
|-----------|------|------|
| OpenAI SDK | LLM API | GPT-4o-mini 대화 생성 |
| python-dotenv | 환경변수 | API 키 관리 |

### TTS (Text-to-Speech)

| 라이브러리 | 용도 | 설명 |
|-----------|------|------|
| edge-tts | 음성 합성 | Microsoft Edge TTS (한국어 8+ 음성) |
| pyttsx3 | 대안 TTS | 오프라인 음성 합성 엔진 |
| gTTS | 대안 TTS | Google TTS |

### 유틸리티

| 라이브러리 | 용도 | 설명 |
|-----------|------|------|
| requests | HTTP 클라이언트 | 외부 API 호출 |
| httpx | 비동기 HTTP | 비동기 API 호출 |
| PyOpenSSL | SSL | 자체 서명 인증서 생성 |

---

## Frontend (HTML/CSS/JS)

### 코어

| 기술 | 용도 | 설명 |
|------|------|------|
| HTML5 | 마크업 | Jinja2 템플릿 엔진 기반 |
| CSS3 | 스타일링 | 반응형 디자인, 커스텀 속성(CSS Variables) |
| JavaScript (ES6+) | 인터랙션 | 4,300+ 라인의 프론트엔드 로직 |

### UI 라이브러리

| 라이브러리 | 용도 | 설명 |
|-----------|------|------|
| Chart.js | 데이터 시각화 | 감정 분석 차트, 활동 통계 그래프 |
| Material Icons | 아이콘 | Google Material Design 아이콘 |
| Daum Postcode API | 주소 검색 | 회원가입 시 주소 입력 |

### 브라우저 API

| API | 용도 | 설명 |
|-----|------|------|
| MediaRecorder API | 음성 녹음 | 브라우저에서 마이크 입력 캡처 |
| EventSource API | SSE 스트리밍 | 실시간 분석 진행 상태 수신 |
| Fetch API | HTTP 통신 | 서버 API 호출 |

---

## AI 모델

### STT (Speech-to-Text)

| 항목 | 내용 |
|------|------|
| 모델 | OpenAI Whisper (tiny) |
| 엔진 | faster-whisper |
| 양자화 | int8 (CT2 변환) |
| 언어 | 한국어 (ko) |
| 용도 | 어르신 음성을 텍스트로 변환 |

### 텍스트 감정 분석

| 항목 | 내용 |
|------|------|
| 모델 | MelissaJ/koelectra-emotion-6-emotion-base |
| 기반 | KcELECTRA |
| 감정 클래스 | 기쁨, 중립, 분노, 슬픔, 불안, 당황 |
| 용도 | 텍스트 기반 감정 분류 |

### 오디오 감정 분석

| 항목 | 내용 |
|------|------|
| 모델 | jungjongho/wav2vec2-xlsr-korean-speech-emotion-recognition |
| 기반 | Wav2Vec2-XLSR |
| 용도 | 음성 신호 기반 감정 분류 |
| 특징 | Z-peak > 2.5 시 오디오 감정 우선 적용 |

### 감정 앙상블

| 항목 | 내용 |
|------|------|
| 방식 | 투표 기반 (텍스트 primary + 오디오 secondary) |
| 피치 분석 | YIN 알고리즘, Z-peak 계산 |
| 최종 결정 | 텍스트 감정 기본, Z-peak 높으면 오디오 감정 반영 |

### LLM (대화 생성)

| 항목 | 내용 |
|------|------|
| 모델 | OpenAI GPT-4o-mini |
| 전략 | Q&A 데이터셋 매칭 우선 → 매칭 실패 시 LLM 호출 |
| 프롬프트 | 감정 인식 기반 맞춤형 응답 |
| Q&A 카테고리 | 인사, 약 복용, 식사, 건강, 관계, 시간, 응급 등 |

### TTS (Text-to-Speech)

| 항목 | 내용 |
|------|------|
| 엔진 | Microsoft Edge TTS |
| 기본 음성 | ko-KR-SunHiNeural |
| 지원 음성 | sun-hi, ji-min, seo-hyeon, bong-jin 등 8종 |
| 출력 형식 | MP3 |

---

## 인프라

### 서버 환경

| 항목 | 내용 |
|------|------|
| OS | Windows |
| Python | 3.x |
| 데이터베이스 | MySQL (192.168.0.31:3306, care_db) |
| SSL | 자체 서명 인증서 (cert.pem, key.pem) |

### 디렉토리 구조

| 경로 | 용도 |
|------|------|
| /recordings/ | 사용자 음성 녹음 파일 |
| /tts_outputs/ | TTS 생성 음성 파일 |
| /analysis_logs/ | 분석 결과 로그 |
| /static/images/ | 보미 캐릭터 이미지 (9종) |
| /api-key/ | API 키 저장 |

---

## 아키텍처

### 음성 분석 파이프라인

```
┌──────────┐    ┌──────────┐    ┌──────────────┐    ┌──────────────┐
│  음성    │    │  STT     │    │  감정 분석    │    │  점수 산출   │
│  녹음    │ →  │ (Whisper)│ →  │ (Text+Audio) │ →  │ (8차원)     │
│          │    │          │    │  Ensemble    │    │             │
└──────────┘    └──────────┘    └──────────────┘    └──────┬──────┘
                                                          │
                                                          ▼
┌──────────┐    ┌──────────┐    ┌──────────────┐    ┌──────────────┐
│  TTS     │    │  LLM     │    │  Q&A 매칭    │    │  DB 저장    │
│  음성    │ ←  │  응답    │ ←  │  + LLM 생성  │    │  + 알림     │
│  출력    │    │  생성    │    │              │    │             │
└──────────┘    └──────────┘    └──────────────┘    └──────────────┘
```

### 8차원 음성 분석 점수

| 지표 | 설명 | 최적 범위 | 가중치 |
|------|------|----------|--------|
| Speed (속도) | 분당 어절 수 (WPM) | 100~150 | 1.0 |
| Duration (길이) | 발화 지속 시간 | 3~10초 | 1.0 |
| Response Time (반응) | 응답까지 소요 시간 | 0~2초 | 1.0 |
| Word Count (어절 수) | 발화 내 단어 수 | 5~20개 | 1.0 |
| Vocabulary (어휘력) | TTR 어휘 다양성 비율 | 0.6~0.9 | 1.0 |
| Silence (침묵) | 발화 내 무음 구간 | 0~1초 | 1.0 |
| Emotion (감정) | 감정 안정성 점수 | 70~100 | **1.5** |
| Vitality (활력) | VPR 피치 비율 | 2.0~10.0 | 1.0 |

---

## 기능별 기술 매핑

| 기능 | Backend | AI 모델 | Frontend | DB |
|------|---------|---------|----------|-----|
| 회원가입/로그인 | Flask | - | HTML/JS | tb_guardian, tb_senior |
| 음성 녹음 | Flask | - | MediaRecorder API | - |
| STT 변환 | Flask | faster-whisper (tiny) | SSE 스트리밍 | tb_voice_log |
| 감정 분석 | Flask | KcELECTRA + Wav2Vec2 | Chart.js | tb_analysis |
| AI 대화 | Flask | GPT-4o-mini | JS | - |
| TTS 응답 | Flask | Edge TTS | Audio 재생 | /tts_outputs/ |
| 대시보드 | Flask | - | Chart.js | 전체 테이블 |
| 디바이스 관리 | Flask | - | HTML/JS | tb_device, tb_sensor |
| 알림 | Flask | - | JS | tb_alert |

---

## 문서 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|----------|
| 1.0 | 2026-02-09 | - | 최초 작성 |
