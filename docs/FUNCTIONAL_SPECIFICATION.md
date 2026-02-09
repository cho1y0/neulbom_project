# 늘봄 (AI 기반 노인 돌봄 음성 분석 시스템) - 기능 명세서

---

## 문서 정보

| 항목 | 내용 |
|------|------|
| **프로젝트명** | 늘봄 (AI 기반 노인 돌봄 음성 분석 시스템) |
| **문서 유형** | 기능 명세서 (Functional Specification) |
| **문서 버전** | 1.0 |
| **작성일** | 2026-02-09 |
| 개발 기간 | 2025년 12월 ~ 2026년 2월 (2025.12.05 ~ 2026.02.10) |
| 개발 인원 | 5명 (최선임 총괄기획, 지태민 프론트엔드, 김승민 백엔드, 최대영 DB/IoT, 조민솔 기획/문서) |
| **백엔드 프레임워크** | Flask 5000번 포트 / FastAPI 8000번 포트 |
| **데이터베이스** | MySQL (care_db) |
| **AI 모델** | faster-whisper (tiny), KcELECTRA, Wav2Vec2, GPT-4o-mini |

---

## 목차

1. [회원가입 (FN-AUTH-001)](#1-회원가입)
2. [로그인 (FN-AUTH-002)](#2-로그인)
3. [아이디 중복 확인 (FN-AUTH-003)](#3-아이디-중복-확인)
4. [비밀번호 변경 (FN-AUTH-004)](#4-비밀번호-변경)
5. [음성 분석 (FN-VOICE-001)](#5-음성-분석)
6. [음성 세션 생성 (FN-VOICE-002)](#6-음성-세션-생성)
7. [TTS 음성 재생 (FN-VOICE-003)](#7-tts-음성-재생)
8. [일간 활동량 조회 (FN-ACTIVITY-001)](#8-일간-활동량-조회)
9. [주간 활동량 조회 (FN-ACTIVITY-002)](#9-주간-활동량-조회)
10. [월간 활동량 조회 (FN-ACTIVITY-003)](#10-월간-활동량-조회)
11. [보호자 정보 수정 (FN-USER-001)](#11-보호자-정보-수정)
12. [어르신 정보 수정 (FN-USER-002)](#12-어르신-정보-수정)
13. [기기 등록 (FN-DEVICE-001)](#13-기기-등록)
14. [센서 확인 (FN-DEVICE-002)](#14-센서-확인)
15. [실시간 알림 확인 (FN-ALERT-001)](#15-실시간-알림-확인)
16. [알림 목록 조회 (FN-ALERT-002)](#16-알림-목록-조회)
17. [알림 전체 읽음 처리 (FN-ALERT-003)](#17-알림-전체-읽음-처리)
18. [데이터 시뮬레이션 (FN-DEV-001)](#18-데이터-시뮬레이션)
19. [DB 테이블 설계](#19-db-테이블-설계)
20. [AI 모델 상세](#20-ai-모델-상세)
21. [8차원 음성 점수 체계](#21-8차원-음성-점수-체계)
22. [화면 구성](#22-화면-구성)
23. [문서 이력](#23-문서-이력)

---

## 1. 회원가입

| 항목 | 내용 |
|------|------|
| **기능 ID** | FN-AUTH-001 |
| **화면 경로** | `/templates/signup.html` |
| **API 엔드포인트** | `POST /api/signup` |
| **접근 권한** | 비인증 사용자 (공개) |

### 1.1 기능 설명

보호자가 본인 정보와 어르신 정보를 함께 입력하여 회원가입한다. 보호자 1명당 어르신 1명이 연결되며, 보호자 레코드 생성 후 해당 guardian_id를 FK로 어르신 레코드를 생성한다.

### 1.2 입력 항목 - 보호자 (guardian)

| 필드명 | 타입 | 필수 | 검증 규칙 | 설명 |
|--------|------|------|-----------|------|
| `guardian.username` | string | Y | 영문/숫자, 중복 불가 | 보호자 로그인 아이디 |
| `guardian.password` | string | Y | - | 비밀번호 (평문 저장) |
| `guardian.name` | string | Y | - | 보호자 이름 |
| `guardian.phone` | string | Y | 전화번호 형식 | 보호자 연락처 |
| `guardian.zipcode` | string | Y | 5자리 숫자 | 우편번호 |
| `guardian.address` | string | Y | - | 기본 주소 |
| `guardian.addressDetail` | string | N | - | 상세 주소 |

### 1.3 입력 항목 - 어르신 (senior)

| 필드명 | 타입 | 필수 | 검증 규칙 | 설명 |
|--------|------|------|-----------|------|
| `senior.name` | string | Y | - | 어르신 이름 |
| `senior.relation` | string | Y | - | 보호자와의 관계 |
| `senior.gender` | string | Y | `male` / `female` | 성별 (DB 저장 시 M/F 변환) |
| `senior.birthYear` | string | Y | 4자리 연도 | 생년 |
| `senior.birthMonth` | string | Y | 1~12 | 생월 |
| `senior.birthDay` | string | Y | 1~31 | 생일 |
| `senior.fullBirthdate` | string | N | YYYY-MM-DD | 완전한 생년월일 (우선 사용) |
| `senior.phone` | string | Y | 전화번호 형식 | 어르신 연락처 |
| `senior.zipcode` | string | Y | 5자리 숫자 | 우편번호 |
| `senior.address` | string | Y | - | 기본 주소 |
| `senior.addressDetail` | string | N | - | 상세 주소 |
| `senior.living` | string | Y | `독거` / `가족` | 거주 형태 |

### 1.4 처리 로직

1. 클라이언트에서 JSON 형식으로 보호자 + 어르신 정보를 전송한다.
2. `tb_guardian` 테이블에 보호자 정보를 INSERT한다.
   - `voice_collection_approved`는 기본값 `'Y'`로 설정한다.
   - `created_at`은 `NOW()`로 현재 시각을 기록한다.
3. INSERT 후 `cursor.lastrowid`로 생성된 `guardian_id`를 획득한다.
4. 어르신 생년월일을 조립한다.
   - `fullBirthdate` 필드가 있으면 해당 값을 사용한다.
   - 없으면 `birthYear-birthMonth(zfill2)-birthDay(zfill2)` 형식으로 조합한다.
5. 성별을 변환한다: `female` 포함 시 `'F'`, 그 외 `'M'`.
6. `tb_senior` 테이블에 어르신 정보를 INSERT한다.
   - `relation_with_guardian`은 `"보호자"`로 고정한다.
   - `guardian_id`에 3단계에서 획득한 값을 설정한다.
7. 트랜잭션을 COMMIT한다.
8. 예외 발생 시 ROLLBACK하고 에러를 반환한다.

### 1.5 출력

| 상태 | HTTP 코드 | 응답 |
|------|-----------|------|
| 성공 | 200 | `{"message": "가입 성공", "guardian_id": <int>}` |
| 실패 | 500 | `{"error": "<에러 메시지>"}` |

---

## 2. 로그인

| 항목 | 내용 |
|------|------|
| **기능 ID** | FN-AUTH-002 |
| **화면 경로** | `/templates/login.html` |
| **API 엔드포인트** | `POST /api/login` |
| **접근 권한** | 비인증 사용자 (공개) |

### 2.1 기능 설명

보호자 아이디와 비밀번호로 로그인한다. 성공 시 보호자 정보, 어르신 정보, 등록된 기기 목록을 한꺼번에 반환한다.

### 2.2 입력 항목

| 필드명 | 타입 | 필수 | 검증 규칙 | 설명 |
|--------|------|------|-----------|------|
| `username` | string | Y | - | 보호자 로그인 아이디 |
| `password` | string | Y | - | 비밀번호 |

### 2.3 처리 로직

1. `tb_guardian`에서 `user_id`와 `password`가 일치하는 레코드를 조회한다.
2. 일치하는 레코드가 없으면 401 에러를 반환한다.
3. 보호자 정보를 응답 객체에 매핑한다 (`username`, `name`, `phone`, `zipcode`, `address`, `addressDetail`).
4. `tb_senior`에서 해당 `guardian_id`로 어르신 정보를 조회한다.
5. 어르신이 존재하면 생년월일을 `birthYear`, `birthMonth`, `birthDay`로 분리하고, 성별을 `male`/`female`로 변환하여 매핑한다.
6. `tb_device`에서 해당 `senior_id`로 기기 목록을 조회한다.
7. 기기별로 `id`(DEV + device_id), `serial`(device_uid), `name`(device_name), `location`, `status`(기본 online)를 매핑한다.
8. 최종 응답 객체를 반환한다.

### 2.4 출력

| 상태 | HTTP 코드 | 응답 |
|------|-----------|------|
| 성공 | 200 | `{"username": "...", "name": "...", "phone": "...", "zipcode": "...", "address": "...", "addressDetail": "...", "senior": {...}, "devices": [...]}` |
| 인증 실패 | 401 | `{"error": "로그인 실패"}` |
| 서버 에러 | 500 | `{"error": "<에러 메시지>"}` |

### 2.5 성공 응답 상세

```json
{
  "username": "보호자 아이디",
  "name": "보호자 이름",
  "phone": "연락처",
  "zipcode": "우편번호",
  "address": "기본 주소",
  "addressDetail": "상세 주소",
  "senior": {
    "name": "어르신 이름",
    "gender": "male | female",
    "phone": "연락처",
    "living": "독거 | 가족",
    "birthYear": "YYYY",
    "birthMonth": "MM",
    "birthDay": "DD",
    "zipcode": "우편번호",
    "address": "기본 주소",
    "addressDetail": "상세 주소"
  },
  "devices": [
    {
      "id": "DEV1",
      "serial": "기기 UID",
      "name": "기기 이름",
      "location": "설치 위치",
      "status": "online"
    }
  ]
}
```

---

## 3. 아이디 중복 확인

| 항목 | 내용 |
|------|------|
| **기능 ID** | FN-AUTH-003 |
| **화면 경로** | `/templates/signup.html` |
| **API 엔드포인트** | `POST /api/check-duplicate` |
| **접근 권한** | 비인증 사용자 (공개) |

### 3.1 기능 설명

회원가입 화면에서 아이디 입력 후 중복 여부를 실시간으로 확인한다.

### 3.2 입력 항목

| 필드명 | 타입 | 필수 | 검증 규칙 | 설명 |
|--------|------|------|-----------|------|
| `username` | string | Y | - | 확인할 아이디 |

### 3.3 처리 로직

1. `tb_guardian`에서 해당 `user_id`의 레코드 수를 COUNT한다.
2. 1개 이상이면 중복, 0개이면 사용 가능으로 판단한다.

### 3.4 출력

| 상태 | HTTP 코드 | 응답 |
|------|-----------|------|
| 중복 | 200 | `{"isDuplicate": true}` |
| 사용 가능 | 200 | `{"isDuplicate": false}` |
| 에러 | 500 | `{"error": "<에러 메시지>"}` |

---

## 4. 비밀번호 변경

| 항목 | 내용 |
|------|------|
| **기능 ID** | FN-AUTH-004 |
| **화면 경로** | `/templates/mypage.html` |
| **API 엔드포인트** | `POST /api/change-password` |
| **접근 권한** | 인증된 보호자 |

### 4.1 기능 설명

마이페이지에서 현재 비밀번호를 확인한 후 새 비밀번호로 변경한다.

### 4.2 입력 항목

| 필드명 | 타입 | 필수 | 검증 규칙 | 설명 |
|--------|------|------|-----------|------|
| `username` | string | Y | - | 보호자 아이디 |
| `currentPassword` | string | Y | - | 현재 비밀번호 |
| `newPassword` | string | Y | - | 새 비밀번호 |

### 4.3 처리 로직

1. `tb_guardian`에서 `user_id`와 `password`가 일치하는 레코드를 조회한다.
2. 일치하지 않으면 400 에러를 반환한다 ("현재 비밀번호가 일치하지 않습니다").
3. 일치하면 `password` 컬럼을 `newPassword` 값으로 UPDATE한다.
4. 트랜잭션을 COMMIT한다.

### 4.4 출력

| 상태 | HTTP 코드 | 응답 |
|------|-----------|------|
| 성공 | 200 | `{"message": "비밀번호 변경 성공"}` |
| 현재 비밀번호 불일치 | 400 | `{"error": "현재 비밀번호가 일치하지 않습니다."}` |
| 서버 에러 | 500 | `{"error": "<에러 메시지>"}` |

---

## 5. 음성 분석

| 항목 | 내용 |
|------|------|
| **기능 ID** | FN-VOICE-001 |
| **화면 경로** | `/templates/bomi.html` |
| **API 엔드포인트** | `POST /api/analyze` |
| **접근 권한** | 인증된 보호자 |

### 5.1 기능 설명

어르신의 음성 파일을 업로드하면 STT(음성 인식), 감정 분석, 8차원 점수화, AI 대화 응답 생성, TTS 음성 합성을 수행하고, 결과를 SSE(Server-Sent Events) 스트림으로 실시간 전달한다. 이 API는 시스템의 핵심 기능이다.

### 5.2 입력 항목

| 필드명 | 타입 | 필수 | 검증 규칙 | 설명 |
|--------|------|------|-----------|------|
| `audio_file` | File (multipart) | Y | 음성 파일 (.wav, .mp3, .m4a 등) | 어르신 음성 녹음 파일 |
| `senior_id` | int (Form) | N | 기본값: 1 | 어르신 ID |
| `sensing_id` | int (Form) | Y | `/api/create-voice-session`으로 사전 생성 필요 | 센싱 세션 ID |
| `generate_response` | string (Form) | N | `"true"` / `"false"`, 기본값: `"true"` | AI 응답 생성 여부 |

### 5.3 처리 로직

**Phase 1: 요청 데이터 추출 (SSE 제너레이터 외부)**

1. `speech_analyzer` 초기화 여부를 확인한다. 미초기화 시 503 에러를 반환한다.
2. `request.files`에서 `audio_file`을 추출한다. 없으면 400 에러를 반환한다.
3. `sensing_id`가 누락되면 400 에러를 반환한다 (사전에 `/api/create-voice-session` 호출 필요).
4. 음성 파일을 `tempfile.NamedTemporaryFile`로 임시 저장한다.

**Phase 2: SSE 스트림 제너레이터**

5. **[Step 1]** 파일 저장 완료 메시지를 SSE로 전송한다.
6. **[Step 2]** STT 음성 인식 시작 메시지를 전송한다.
7. `SpeechAnalyzer.analyze(tmp_path)`를 호출하여 음성 분석을 수행한다.
   - **STT**: faster-whisper (tiny 모델, int8 양자화)로 한국어 음성을 텍스트로 변환한다.
   - **어휘 분석**: KcELECTRA 토크나이저로 TTR(Type-Token Ratio)을 계산한다.
   - **감정 분석**: EmotionEnsemble (KcELECTRA + Wav2Vec2 앙상블)로 감정을 판별한다.
   - **8차원 점수**: 속도, 발화 길이, 반응 시간, 단어 수, 어휘 다양성, 침묵, 감정, 활력도를 0~100점으로 채점한다.
8. **[Step 3]** STT 완료 메시지와 텍스트 미리보기(50자)를 전송한다.
9. **[Step 5]** AI 응답 생성을 시작한다.
   - Q&A 데이터셋 (10개 카테고리, 44개 항목)에서 3단계 매칭(정확 일치 -> 부분 일치 -> 키워드 일치)을 시도한다.
   - 매칭 성공 시: 데이터셋의 응답과 감정 점수를 사용하고 원본 감정을 덮어쓴다.
   - 매칭 실패 시: GPT-4o-mini API를 호출하여 감정 기반 동적 프롬프트로 응답을 생성한다.
     - 페르소나: 20대 손녀 '보미' (친근한 존댓말, 1~2문장)
     - 감정별 대화 전략 적용 (슬픔: 위로, 분노: 경청, 불안: 안심, 기쁨: 맞장구)
     - 점수 기반 위험 감지 (평균 < 50 또는 감정 < 40: 고위험 알림)
10. **[Step 5.5]** TTS 음성 생성을 시작한다.
    - Edge TTS (Microsoft)로 AI 응답 텍스트를 MP3 파일로 변환한다.
    - 파일명: `response_YYYYMMDD_HHMMSS.mp3`
    - 저장 경로: `./tts_outputs/`
11. **[Step 5.7]** TTS 완료 메시지와 `tts_file` 파일명, `ai_response` 텍스트를 전송한다.
12. **[Step 4]** 감정 분석 결과 메시지를 전송한다 (예: "당황 (53%)").
13. **[Step 6]** DB 저장을 수행한다.
    - `tb_voice_log`에 음성 로그를 INSERT한다 (senior_id, sensing_id, voice_text, response_time_sec, utterance_length).
    - `tb_analysis`에 감정 분석 결과를 INSERT한다 (voice_idx, emotion_label, stt_text, 7개 감정 비율).
14. **[Step 7]** 임시 파일을 삭제한다.
15. **[Step complete]** 최종 결과 JSON을 전송한다.

**Phase 3: SSE 응답 반환**

16. `Response` 객체를 `text/event-stream` MIME 타입으로 반환한다.

### 5.4 출력 (SSE 스트림)

각 단계별로 `data: {JSON}\n\n` 형식의 SSE 이벤트가 순차 전송된다.

**진행 상황 이벤트**:

| step | message 예시 |
|------|-------------|
| 1 | "파일 저장 완료" |
| 2 | "STT 음성 인식 중..." |
| 3 | "STT 완료" (+ `text_preview`) |
| 4 | "감정 분석: 당황 (53%)" |
| 5 | "AI 응답 생성 중..." |
| 5.5 | "목소리 만드는 중..." |
| 5.7 | "TTS 완료" (+ `tts_file`, `ai_response`) |
| 6 | "DB 저장 중..." |

**최종 결과 이벤트** (`step: "complete"`):

```json
{
  "step": "complete",
  "success": true,
  "voice_id": 42,
  "analysis": {
    "text": "인식된 텍스트",
    "emotion": {
      "final": "당황",
      "confidence": 0.53,
      "text_emotion": "중립",
      "audio_emotion": "당황",
      "z_peak": 1.82,
      "decision": "분석 완료"
    },
    "scores": {
      "speed": 85.0,
      "duration": 72.0,
      "response": 85.0,
      "word_count": 90.0,
      "vocabulary": 78.5,
      "silence": 65.0,
      "emotion": 53.0,
      "vitality": 80.0,
      "average": 76.1
    },
    "whisper": {
      "text": "인식된 텍스트",
      "word_count": 12,
      "wpm": 120.5,
      "duration": 5.2,
      "response_time": 0.5,
      "avg_silence": 0.8,
      "vpr": 5.5
    }
  },
  "ai_response": "할머니, 저 보미예요! 잘 지내셨어요?",
  "tts_file": "response_20260209_143025.mp3",
  "metadata": {
    "senior_id": 1,
    "sensing_id": 15,
    "timestamp": "2026-02-09T14:30:25.123456"
  }
}
```

**에러 이벤트** (`step: "error"`):

```json
{
  "step": "error",
  "error": "에러 메시지"
}
```

---

## 6. 음성 세션 생성

| 항목 | 내용 |
|------|------|
| **기능 ID** | FN-VOICE-002 |
| **화면 경로** | `/templates/bomi.html` |
| **API 엔드포인트** | `POST /api/create-voice-session` |
| **접근 권한** | 인증된 보호자 |

### 6.1 기능 설명

음성 녹음을 시작하기 전에 `tb_sensing` 테이블에 세션 레코드를 생성하고 `sensing_id`를 반환한다. 이 `sensing_id`는 이후 `/api/analyze` 호출 시 필수 파라미터로 사용된다.

### 6.2 입력 항목

| 필드명 | 타입 | 필수 | 검증 규칙 | 설명 |
|--------|------|------|-----------|------|
| `username` | string | Y | - | 보호자 아이디 |

### 6.3 처리 로직

1. 보호자 아이디로 `tb_guardian -> tb_senior -> tb_device -> tb_sensor` 조인 경로를 통해 센서를 찾는다.
2. 센서가 없으면 404 에러를 반환한다 ("센서를 먼저 등록해주세요").
3. `tb_sensing`에 `sensing_type='voice_session'`, `sensing_value='recording_start'`로 INSERT한다.
4. `cursor.lastrowid`로 생성된 `sensing_id`를 획득한다.
5. 성공 응답을 반환한다.

### 6.4 출력

| 상태 | HTTP 코드 | 응답 |
|------|-----------|------|
| 성공 | 200 | `{"success": true, "sensing_id": <int>, "sensor_id": <int>, "sensor_type": "...", "device_name": "...", "message": "음성 세션이 시작되었습니다"}` |
| 센서 없음 | 404 | `{"success": false, "message": "센서를 찾을 수 없습니다..."}` |
| 파라미터 누락 | 400 | `{"success": false, "message": "사용자 아이디가 필요합니다"}` |
| 서버 에러 | 500 | `{"success": false, "error": "<에러 메시지>"}` |

---

## 7. TTS 음성 재생

| 항목 | 내용 |
|------|------|
| **기능 ID** | FN-VOICE-003 |
| **화면 경로** | `/templates/bomi.html` |
| **API 엔드포인트** | `GET /api/tts-audio/<filename>` |
| **접근 권한** | 인증된 보호자 |

### 7.1 기능 설명

`/api/analyze`에서 생성된 TTS MP3 파일을 제공한다. 클라이언트가 SSE 스트림에서 받은 `tts_file` 파일명으로 요청한다.

### 7.2 입력 항목

| 필드명 | 타입 | 필수 | 검증 규칙 | 설명 |
|--------|------|------|-----------|------|
| `filename` | string (URL 경로) | Y | 파일명 형식 | TTS 출력 파일명 (예: `response_20260209_143025.mp3`) |

### 7.3 처리 로직

1. `tts_outputs/` 디렉토리에서 요청된 파일명과 일치하는 파일을 찾는다.
2. Flask `send_from_directory`로 파일을 반환한다.

### 7.4 출력

| 상태 | 응답 |
|------|------|
| 성공 | MP3 오디오 파일 (audio/mpeg) |
| 파일 없음 | 404 Not Found |

### 7.5 지원 음성 목록

Edge TTS에서 지원하는 한국어 음성은 다음과 같다.

| 키 | 음성 ID | 성별 | 특징 |
|----|---------|------|------|
| `sun-hi` | ko-KR-SunHiNeural | 여성 | 밝고 친절 (기본값) |
| `ji-min` | ko-KR-JiMinNeural | 여성 | 차분함 |
| `seo-hyeon` | ko-KR-SeoHyeonNeural | 여성 | 부드러움 |
| `soon-bok` | ko-KR-SoonBokNeural | 여성 | 할머니 느낌 |
| `yu-jin` | ko-KR-YuJinNeural | 여성 | 젊음 |
| `in-joon` | ko-KR-InJoonNeural | 남성 | 차분함 |
| `hyun-su` | ko-KR-HyunsuNeural | 남성 | 명랑 |
| `bong-jin` | ko-KR-BongJinNeural | 남성 | 할아버지 느낌 |
| `gook-min` | ko-KR-GookMinNeural | 남성 | 젊음 |

---

## 8. 일간 활동량 조회

| 항목 | 내용 |
|------|------|
| **기능 ID** | FN-ACTIVITY-001 |
| **화면 경로** | `/templates/dashboard.html` |
| **API 엔드포인트** | `POST /api/activity-daily` |
| **접근 권한** | 인증된 보호자 |

### 8.1 기능 설명

대시보드에서 오늘 하루 동안 모션 센서가 감지한 활동 횟수를 조회한다.

### 8.2 입력 항목

| 필드명 | 타입 | 필수 | 검증 규칙 | 설명 |
|--------|------|------|-----------|------|
| `username` | string | Y | - | 보호자 아이디 |

### 8.3 처리 로직

1. 보호자 아이디로 `tb_guardian -> tb_senior -> tb_device -> tb_sensor` 조인 경로를 통해 `sensor_type = 'motion'`인 센서 ID를 찾는다.
2. `tb_sensing`에서 해당 `sensor_id`의 오늘 날짜(`DATE(created_at) = CURDATE()`) 레코드 수를 COUNT한다.
3. 센서가 없거나 에러 시 0을 반환한다.

### 8.4 출력

| 상태 | HTTP 코드 | 응답 |
|------|-----------|------|
| 성공 | 200 | `{"count": <int>}` |
| 센서 없음/에러 | 200 | `{"count": 0}` |

---

## 9. 주간 활동량 조회

| 항목 | 내용 |
|------|------|
| **기능 ID** | FN-ACTIVITY-002 |
| **화면 경로** | `/templates/dashboard.html`, `/templates/report.html` |
| **API 엔드포인트** | `POST /api/activity-weekly` |
| **접근 권한** | 인증된 보호자 |

### 9.1 기능 설명

최근 7일간의 일별 활동 횟수를 배열로 반환한다. 대시보드 및 리포트 화면에서 주간 추이 그래프에 사용된다.

### 9.2 입력 항목

| 필드명 | 타입 | 필수 | 검증 규칙 | 설명 |
|--------|------|------|-----------|------|
| `username` | string | Y | - | 보호자 아이디 |

### 9.3 처리 로직

1. 보호자 아이디로 모션 센서 ID를 찾는다 (FN-ACTIVITY-001과 동일 쿼리).
2. 오늘 날짜를 기준으로 6일 전부터 오늘까지 7일간 루프를 돈다.
3. 각 날짜별로 `tb_sensing`에서 해당 `sensor_id`, 해당 날짜의 레코드 수를 COUNT한다.
4. 7개 요소 배열을 반환한다 (인덱스 0 = 6일 전, 인덱스 6 = 오늘).

### 9.4 출력

| 상태 | HTTP 코드 | 응답 |
|------|-----------|------|
| 성공 | 200 | `{"data": [0, 3, 5, 2, 8, 1, 4]}` |
| 에러 | 200 | `{"data": [0, 0, 0, 0, 0, 0, 0]}` |

---

## 10. 월간 활동량 조회

| 항목 | 내용 |
|------|------|
| **기능 ID** | FN-ACTIVITY-003 |
| **화면 경로** | `/templates/dashboard.html`, `/templates/report.html` |
| **API 엔드포인트** | `POST /api/activity-monthly` |
| **접근 권한** | 인증된 보호자 |

### 10.1 기능 설명

최근 4주간의 주별 활동 횟수를 배열로 반환한다. 월간 추이 그래프에 사용된다.

### 10.2 입력 항목

| 필드명 | 타입 | 필수 | 검증 규칙 | 설명 |
|--------|------|------|-----------|------|
| `username` | string | Y | - | 보호자 아이디 |

### 10.3 처리 로직

1. 보호자 아이디로 모션 센서 ID를 찾는다.
2. 오늘 기준으로 4주간 루프를 돈다 (i=0: 이번주, i=3: 3주전).
3. 각 주의 시작일(end_date - 6일)부터 종료일(end_date)까지 `BETWEEN`으로 레코드 수를 COUNT한다.
4. 배열 인덱스를 역순으로 채운다 (인덱스 0 = 3주전, 인덱스 3 = 이번주).

### 10.4 출력

| 상태 | HTTP 코드 | 응답 |
|------|-----------|------|
| 성공 | 200 | `{"data": [12, 25, 18, 30]}` |
| 에러 | 200 | `{"data": [0, 0, 0, 0]}` |

---

## 11. 보호자 정보 수정

| 항목 | 내용 |
|------|------|
| **기능 ID** | FN-USER-001 |
| **화면 경로** | `/templates/mypage.html` |
| **API 엔드포인트** | `POST /api/update-guardian` |
| **접근 권한** | 인증된 보호자 |

### 11.1 기능 설명

마이페이지에서 보호자 본인의 연락처 및 주소 정보를 수정한다.

### 11.2 입력 항목

| 필드명 | 타입 | 필수 | 검증 규칙 | 설명 |
|--------|------|------|-----------|------|
| `username` | string | Y | - | 보호자 아이디 |
| `phone` | string | Y | 전화번호 형식 | 새 연락처 |
| `zipcode` | string | Y | 5자리 숫자 | 새 우편번호 |
| `address` | string | Y | - | 새 기본 주소 |
| `addressDetail` | string | N | - | 새 상세 주소 |

### 11.3 처리 로직

1. `tb_guardian`에서 `user_id`가 일치하는 레코드의 `phone`, `post_num`, `addr1`, `addr2`를 UPDATE한다.
2. 트랜잭션을 COMMIT한다.

### 11.4 출력

| 상태 | HTTP 코드 | 응답 |
|------|-----------|------|
| 성공 | 200 | `{"message": "보호자 정보 수정 성공"}` |
| 에러 | 500 | `{"error": "<에러 메시지>"}` |

---

## 12. 어르신 정보 수정

| 항목 | 내용 |
|------|------|
| **기능 ID** | FN-USER-002 |
| **화면 경로** | `/templates/mypage.html` |
| **API 엔드포인트** | `POST /api/update-senior` |
| **접근 권한** | 인증된 보호자 |

### 12.1 기능 설명

마이페이지에서 보호자가 관리하는 어르신의 연락처 및 주소 정보를 수정한다.

### 12.2 입력 항목

| 필드명 | 타입 | 필수 | 검증 규칙 | 설명 |
|--------|------|------|-----------|------|
| `username` | string | Y | - | 보호자 아이디 |
| `phone` | string | Y | 전화번호 형식 | 어르신 새 연락처 |
| `zipcode` | string | Y | 5자리 숫자 | 새 우편번호 |
| `address` | string | Y | - | 새 기본 주소 |
| `addressDetail` | string | N | - | 새 상세 주소 |

### 12.3 처리 로직

1. `tb_guardian`에서 `user_id`로 `guardian_id`를 조회한다.
2. 보호자가 존재하지 않으면 404 에러를 반환한다.
3. `tb_senior`에서 해당 `guardian_id`의 레코드 `phone`, `post_num`, `addr1`, `addr2`를 UPDATE한다.
4. 트랜잭션을 COMMIT한다.

### 12.4 출력

| 상태 | HTTP 코드 | 응답 |
|------|-----------|------|
| 성공 | 200 | `{"message": "어르신 정보 수정 성공"}` |
| 보호자 없음 | 404 | `{"error": "보호자 정보를 찾을 수 없습니다."}` |
| 에러 | 500 | `{"error": "<에러 메시지>"}` |

---

## 13. 기기 등록

| 항목 | 내용 |
|------|------|
| **기능 ID** | FN-DEVICE-001 |
| **화면 경로** | `/templates/dashboard.html` |
| **API 엔드포인트** | `POST /api/add-device` |
| **접근 권한** | 인증된 보호자 |

### 13.1 기능 설명

보호자가 IoT 기기(센서 디바이스)를 등록한다. 기기 등록 시 자동으로 센서 레코드도 함께 생성된다. 기기명에 '환경'이 포함되면 환경 센서(`env`), 그 외에는 모션 센서(`motion`)로 자동 분류된다.

### 13.2 입력 항목

| 필드명 | 타입 | 필수 | 검증 규칙 | 설명 |
|--------|------|------|-----------|------|
| `serial` | string | Y | - | 기기 시리얼 번호 (device_uid) |
| `name` | string | Y | - | 기기 이름 (예: "거실 모션센서", "방 환경센서") |
| `location` | string | Y | - | 설치 위치 (예: "거실", "안방") |
| `username` | string | Y | - | 보호자 아이디 |

### 13.3 처리 로직

1. `tb_guardian`에서 `user_id`로 `guardian_id`를 찾는다. 없으면 404 에러를 반환한다.
2. `tb_senior`에서 해당 `guardian_id`로 `senior_id`를 찾는다. 없으면 404 에러를 반환한다.
3. `tb_device`에 기기 정보를 INSERT한다 (`device_uid`, `device_name`, `location`, `senior_id`, `installed_at`).
4. 생성된 `device_id`를 획득한다.
5. 센서 타입을 결정한다: 기기명에 `'환경'` 포함 시 `'env'`, 그 외 `'motion'`.
6. `tb_sensor`에 센서 레코드를 INSERT한다 (`device_id`, `sensor_type`, `created_at`).
7. 트랜잭션을 COMMIT한다.

### 13.4 출력

| 상태 | HTTP 코드 | 응답 |
|------|-----------|------|
| 성공 | 200 | `{"message": "등록 성공", "device_id": <int>}` |
| 보호자 없음 | 404 | `{"error": "사용자 정보를 찾을 수 없습니다."}` |
| 어르신 없음 | 404 | `{"error": "등록된 어르신이 없습니다."}` |
| DB 연결 실패 | 500 | `{"error": "DB 연결 실패"}` |
| 에러 | 500 | `{"error": "<에러 메시지>"}` |

---

## 14. 센서 확인

| 항목 | 내용 |
|------|------|
| **기능 ID** | FN-DEVICE-002 |
| **화면 경로** | `/templates/bomi.html` |
| **API 엔드포인트** | `POST /api/check-sensor` 또는 `GET /api/check-sensor?username=...` |
| **접근 권한** | 인증된 보호자 |

### 14.1 기능 설명

보미(음성 대화) 화면에서 녹음 버튼 활성화/비활성화를 결정하기 위해 보호자의 어르신에게 등록된 센서가 있는지 확인한다. GET과 POST 두 가지 방식을 모두 지원한다.

### 14.2 입력 항목

| 필드명 | 타입 | 필수 | 검증 규칙 | 설명 |
|--------|------|------|-----------|------|
| `username` | string | Y | - | 보호자 아이디 (POST: JSON body, GET: query param) |

### 14.3 처리 로직

1. POST 또는 GET에서 `username`을 추출한다.
2. `tb_guardian -> tb_senior -> tb_device -> tb_sensor` 조인으로 가장 최근 센서를 1개 조회한다.
3. 센서가 있으면 `has_sensor: true`와 센서 상세 정보를 반환한다.
4. 센서가 없으면 `has_sensor: false`와 안내 메시지를 반환한다.

### 14.4 출력

| 상태 | HTTP 코드 | 응답 |
|------|-----------|------|
| 센서 있음 | 200 | `{"has_sensor": true, "sensor_id": <int>, "sensor_type": "motion", "device_id": <int>, "device_name": "...", "location": "...", "message": "센서 사용 가능 (...)"}` |
| 센서 없음 | 200 | `{"has_sensor": false, "message": "등록된 센서가 없습니다..."}` |
| 파라미터 누락 | 400 | `{"has_sensor": false, "message": "사용자 아이디가 필요합니다"}` |
| 에러 | 500 | `{"has_sensor": false, "error": "<에러 메시지>"}` |

---

## 15. 실시간 알림 확인

| 항목 | 내용 |
|------|------|
| **기능 ID** | FN-ALERT-001 |
| **화면 경로** | `/templates/dashboard.html` (폴링 방식) |
| **API 엔드포인트** | `GET /api/check-alert` |
| **접근 권한** | 인증된 보호자 |

### 15.1 기능 설명

가장 최근의 읽지 않은 알림 1건을 조회한다. 프론트엔드에서 주기적으로 폴링하여 새 알림이 있으면 팝업을 표시한다. 이 API는 읽음 처리를 하지 않으므로 같은 알림이 반복 조회될 수 있으며, 프론트엔드에서 `alert_id` 비교로 중복을 걸러낸다.

### 15.2 입력 항목

없음 (GET 요청, 파라미터 없음).

### 15.3 처리 로직

1. `tb_alert`에서 `received_yes = 0` (미읽음) 조건으로 `sented_at DESC` 정렬, 1건만 조회한다.
2. 알림이 있으면 날짜를 `YYYY-MM-DD HH:MM:SS` 포맷으로 변환하여 반환한다.
3. 알림이 없으면 `null`을 반환한다.

### 15.4 출력

| 상태 | HTTP 코드 | 응답 |
|------|-----------|------|
| 알림 있음 | 200 | `{"alert_id": <int>, "alert_type": "...", "alert_content": "...", "sented_at": "2026-02-09 14:30:00"}` |
| 알림 없음 | 200 | `null` |
| 에러 | 500 | `{"error": "<에러 메시지>"}` |

---

## 16. 알림 목록 조회

| 항목 | 내용 |
|------|------|
| **기능 ID** | FN-ALERT-002 |
| **화면 경로** | `/templates/dashboard.html` |
| **API 엔드포인트** | `POST /api/alert-list` |
| **접근 권한** | 인증된 보호자 |

### 16.1 기능 설명

최근 알림 10건을 조회한다. 읽음/미읽음 상태와 무관하게 전체를 반환한다.

### 16.2 입력 항목

없음 (현재 사용자 필터링 미구현, 전체 알림 조회).

### 16.3 처리 로직

1. `tb_alert`에서 `sented_at DESC` 정렬, 최대 10건을 조회한다.
2. 날짜를 `YYYY-MM-DD HH:MM:SS` 포맷으로 변환한다.
3. 배열로 반환한다.

### 16.4 출력

| 상태 | HTTP 코드 | 응답 |
|------|-----------|------|
| 성공 | 200 | `[{"alert_id": 1, "alert_type": "...", "alert_content": "...", "sented_at": "...", "received_yes": 0}, ...]` |
| 에러 | 200 | `[]` (빈 배열) |

---

## 17. 알림 전체 읽음 처리

| 항목 | 내용 |
|------|------|
| **기능 ID** | FN-ALERT-003 |
| **화면 경로** | `/templates/dashboard.html` |
| **API 엔드포인트** | `POST /api/alert-read-all` |
| **접근 권한** | 인증된 보호자 |

### 17.1 기능 설명

모든 알림을 읽음 처리한다. 현재는 사용자 구분 없이 테이블 전체를 대상으로 한다.

### 17.2 입력 항목

없음.

### 17.3 처리 로직

1. `tb_alert` 테이블의 모든 레코드에 대해 `received_yes = 1`로 UPDATE한다.
2. 트랜잭션을 COMMIT한다.

### 17.4 출력

| 상태 | HTTP 코드 | 응답 |
|------|-----------|------|
| 성공 | 200 | `{"message": "모든 알림 읽음 처리 완료"}` |
| 에러 | 500 | `{"error": "<에러 메시지>"}` |

---

## 18. 데이터 시뮬레이션

| 항목 | 내용 |
|------|------|
| **기능 ID** | FN-DEV-001 |
| **화면 경로** | `/templates/dashboard.html` |
| **API 엔드포인트** | `POST /api/simulate-data` |
| **접근 권한** | 인증된 보호자 (개발/데모용) |

### 18.1 기능 설명

개발 및 데모 목적으로, 모션 센서 감지 데이터를 DB에 삽입하여 활동량 수치를 인위적으로 증가시킨다. 대시보드 시연 시 활동량 그래프에 데이터를 채우는 데 사용한다.

### 18.2 입력 항목

| 필드명 | 타입 | 필수 | 검증 규칙 | 설명 |
|--------|------|------|-----------|------|
| `username` | string | Y | - | 보호자 아이디 |

### 18.3 처리 로직

1. 보호자 아이디로 모션 센서 ID를 찾는다.
2. `tb_sensing`에 `(sensor_id, value=1, created_at=NOW())` 레코드를 INSERT한다.
3. 오늘의 총 감지 횟수를 COUNT하여 반환한다.

### 18.4 출력

| 상태 | HTTP 코드 | 응답 |
|------|-----------|------|
| 성공 | 200 | `{"count": <int>}` (현재 오늘 총 횟수) |
| 에러 | 200 | `{"count": 0}` |

---

## 19. DB 테이블 설계

### 19.1 tb_guardian (보호자)

| 컬럼명 | 타입 | 제약 조건 | 설명 |
|--------|------|-----------|------|
| `guardian_id` | INT | PK, AUTO_INCREMENT | 보호자 고유 ID |
| `user_id` | VARCHAR | UNIQUE, NOT NULL | 로그인 아이디 |
| `password` | VARCHAR | NOT NULL | 비밀번호 (평문) |
| `name` | VARCHAR | NOT NULL | 이름 |
| `phone` | VARCHAR | - | 연락처 |
| `post_num` | VARCHAR | - | 우편번호 |
| `addr1` | VARCHAR | - | 기본 주소 |
| `addr2` | VARCHAR | - | 상세 주소 |
| `relation_with_senior` | VARCHAR | - | 어르신과의 관계 |
| `voice_collection_approved` | CHAR(1) | 기본값 'Y' | 음성 수집 동의 여부 |
| `created_at` | DATETIME | - | 가입 일시 |

### 19.2 tb_senior (어르신)

| 컬럼명 | 타입 | 제약 조건 | 설명 |
|--------|------|-----------|------|
| `senior_id` | INT | PK, AUTO_INCREMENT | 어르신 고유 ID |
| `name` | VARCHAR | NOT NULL | 이름 |
| `birthdate` | DATE | - | 생년월일 |
| `gender` | CHAR(1) | 'M' / 'F' | 성별 |
| `phone` | VARCHAR | - | 연락처 |
| `post_num` | VARCHAR | - | 우편번호 |
| `addr1` | VARCHAR | - | 기본 주소 |
| `addr2` | VARCHAR | - | 상세 주소 |
| `relation_with_guardian` | VARCHAR | - | 보호자와의 관계 |
| `living_type` | VARCHAR | - | 거주 형태 (독거/가족) |
| `guardian_id` | INT | FK -> tb_guardian | 담당 보호자 ID |
| `created_at` | DATETIME | - | 등록 일시 |

### 19.3 tb_device (기기)

| 컬럼명 | 타입 | 제약 조건 | 설명 |
|--------|------|-----------|------|
| `device_id` | INT | PK, AUTO_INCREMENT | 기기 고유 ID |
| `device_uid` | VARCHAR | - | 기기 시리얼 번호 |
| `device_name` | VARCHAR | - | 기기 이름 |
| `location` | VARCHAR | - | 설치 위치 |
| `senior_id` | INT | FK -> tb_senior | 어르신 ID |
| `installed_at` | DATETIME | - | 설치 일시 |

### 19.4 tb_sensor (센서)

| 컬럼명 | 타입 | 제약 조건 | 설명 |
|--------|------|-----------|------|
| `sensor_id` | INT | PK, AUTO_INCREMENT | 센서 고유 ID |
| `device_id` | INT | FK -> tb_device | 소속 기기 ID |
| `sensor_type` | VARCHAR | 'motion' / 'env' | 센서 유형 |
| `created_at` | DATETIME | - | 등록 일시 |

### 19.5 tb_sensing (센싱 데이터)

| 컬럼명 | 타입 | 제약 조건 | 설명 |
|--------|------|-----------|------|
| `sensing_id` | INT | PK, AUTO_INCREMENT | 센싱 고유 ID |
| `sensor_id` | INT | FK -> tb_sensor | 센서 ID |
| `sensing_type` | VARCHAR | - | 센싱 유형 (voice_session 등) |
| `sensing_value` | VARCHAR | - | 센싱 값 |
| `value` | INT | - | 수치 값 (활동량 시뮬레이션용) |
| `created_at` | DATETIME | - | 감지 일시 |

### 19.6 tb_voice_log (음성 로그)

| 컬럼명 | 타입 | 제약 조건 | 설명 |
|--------|------|-----------|------|
| `voice_id` | INT | PK, AUTO_INCREMENT | 음성 로그 고유 ID |
| `senior_id` | INT | FK -> tb_senior | 어르신 ID |
| `sensing_id` | INT | FK -> tb_sensing | 센싱 세션 ID |
| `voice_text` | TEXT | - | STT 변환 텍스트 |
| `response_time_sec` | FLOAT | - | 응답 시간 (초) |
| `utterance_length` | FLOAT | - | 발화 길이 (초) |
| `created_at` | DATETIME | - | 기록 일시 |

### 19.7 tb_analysis (분석 결과)

| 컬럼명 | 타입 | 제약 조건 | 설명 |
|--------|------|-----------|------|
| `analysis_id` | INT | PK, AUTO_INCREMENT | 분석 고유 ID |
| `voice_idx` | INT | FK -> tb_voice_log | 음성 로그 ID |
| `emotion_label` | VARCHAR | - | 최종 감정 레이블 (기쁨, 슬픔, 분노, 불안, 당황, 중립 등) |
| `stt_text` | TEXT | - | STT 텍스트 (중복 저장) |
| `behavior_policy` | VARCHAR | - | 행동 정책 (현재 미사용, NULL) |
| `hap_ratio` | FLOAT | - | 행복 감정 비율 |
| `sad_ratio` | FLOAT | - | 슬픔 감정 비율 |
| `neu_ratio` | FLOAT | - | 중립 감정 비율 |
| `ang_ratio` | FLOAT | - | 분노 감정 비율 |
| `anxi_ratio` | FLOAT | - | 불안 감정 비율 |
| `emba_ratio` | FLOAT | - | 당황 감정 비율 |
| `heart_ratio` | FLOAT | - | 상처 감정 비율 |

### 19.8 tb_alert (알림)

| 컬럼명 | 타입 | 제약 조건 | 설명 |
|--------|------|-----------|------|
| `alert_id` | INT | PK, AUTO_INCREMENT | 알림 고유 ID |
| `alert_type` | VARCHAR | - | 알림 유형 |
| `alert_content` | TEXT | - | 알림 내용 |
| `sented_at` | DATETIME | - | 발송 일시 |
| `received_yes` | INT | 기본값 0 | 읽음 여부 (0: 미읽음, 1: 읽음) |

### 19.9 테이블 관계도 (ERD 요약)

```
tb_guardian (1) ──── (N) tb_senior
                              │
                         (1)──(N)
                              │
                         tb_device
                              │
                         (1)──(N)
                              │
                         tb_sensor
                              │
                         (1)──(N)
                              │
                         tb_sensing
                              │
                    ┌─────────┘
                    │
              tb_voice_log
                    │
               (1)──(1)
                    │
              tb_analysis

tb_alert (독립 테이블 - Grafana 연동)
```

---

## 20. AI 모델 상세

### 20.1 STT (Speech-to-Text)

| 항목 | 내용 |
|------|------|
| 모델 | faster-whisper (tiny) |
| 양자화 | int8 |
| 언어 | 한국어 (ko) |
| VAD 필터 | 활성화 |
| Beam Size | 1 (속도 최적화) |
| 출력 | 텍스트, 단어 수, WPM, 발화 길이, 침묵 시간, VPR |

### 20.2 텍스트 감정 분석

| 항목 | 내용 |
|------|------|
| 모델 | MelissaJ/koelectra-emotion-6-emotion-base (KcELECTRA 기반) |
| 입력 | STT 변환 텍스트 (최대 128 토큰) |
| 출력 | 감정 레이블 + 신뢰도 (softmax) |
| 감정 카테고리 | 기쁨, 슬픔, 분노, 불안, 당황, 중립 |

### 20.3 음성 감정 분석

| 항목 | 내용 |
|------|------|
| 모델 | jungjongho/wav2vec2-xlsr-korean-speech-emotion-recognition |
| 입력 | 오디오 신호 (16kHz, 최대 3초) |
| 출력 | 감정 레이블 + 신뢰도 (softmax) |
| 전처리 | librosa 리샘플링 (16kHz), 3초 제한 |

### 20.4 멀티모달 감정 앙상블

| 항목 | 내용 |
|------|------|
| 알고리즘 | 가중치 기반 결합 (텍스트 우선, Z-peak 보정) |
| Pitch 분석 | YIN 알고리즘 (librosa.yin, 65~500Hz) |
| Z-peak | Pitch Z-score 최대값 (목소리 역동성 측정) |
| 결합 규칙 | Z-peak > 2.5 + 음성 감정이 강한 감정(분노/기쁨/슬픔) + (텍스트가 중립이거나 음성 신뢰도 > 0.6) -> 음성 감정으로 교체 |
| 감정 매핑 | angry -> 분노, happy -> 기쁨, sad -> 슬픔, neutral -> 중립, fear -> 불안, surprise -> 당황 |

### 20.5 어휘 분석

| 항목 | 내용 |
|------|------|
| 토크나이저 | beomi/KcELECTRA-base-v2022 |
| 지표 | TTR (Type-Token Ratio) = 고유 토큰 수 / 전체 토큰 수 |
| 의미 | TTR이 높을수록 어휘가 다양함 (인지 기능 지표) |

### 20.6 AI 대화 (LLM)

| 항목 | 내용 |
|------|------|
| 모델 | GPT-4o-mini (OpenAI API) |
| 페르소나 | 20대 손녀 '보미' |
| 대화 규칙 | 친근한 존댓말, 1~2문장, AI 티 금지 |
| 토큰 제한 | max_completion_tokens: 1500 |
| 히스토리 | 최대 10턴 유지 |
| Q&A 데이터셋 | 10개 카테고리, 44개 항목 (인사, 약복용, 식사, 건강, 감정, 날씨, 가족, 활동, 안전, 시간) |
| Q&A 매칭 | 3단계 - 정확 일치 -> 부분 일치(포함 관계) -> 키워드 일치(1개 이상 공통 단어) |
| 위험 감지 | 평균 점수 < 50 또는 감정 점수 < 40 -> 고위험 프롬프트 적용 |

### 20.7 TTS (Text-to-Speech)

| 항목 | 내용 |
|------|------|
| 엔진 | Microsoft Edge TTS (edge-tts 라이브러리) |
| 기본 음성 | ko-KR-SunHiNeural (sun-hi, 밝고 친절) |
| 출력 형식 | MP3 |
| 음성 수 | 9개 한국어 음성 (여성 5, 남성 4) |
| 속도 조절 | rate 파라미터 (+10%: 빠르게, -10%: 느리게, +0%: 보통) |

---

## 21. 8차원 음성 점수 체계

음성 분석 시 어르신의 상태를 8가지 차원으로 점수화한다. 각 차원은 0~100점 범위이며, 최적 범위 내에 있으면 100점, 범위를 벗어나면 비례적으로 감점된다.

### 21.1 점수 기준표

| 차원 | 키 | 단위 | 최적 범위 (min~max) | 가중치 | 설명 |
|------|-----|------|---------------------|--------|------|
| 말의 속도 | `speed` | WPM | 100 ~ 150 | 1.0 | 분당 단어 수 (Words Per Minute) |
| 발화 길이 | `duration` | 초 | 3.0 ~ 10.0 | 1.0 | 한 번 말하는 총 길이 |
| 반응 시간 | `response` | 초 | 0.0 ~ 2.0 | 1.0 | 질문 후 응답까지 걸린 시간 (현재 기본값 85점) |
| 단어 수 | `word_count` | 개 | 5 ~ 20 | 1.0 | 한 번 발화의 단어 수 |
| 어휘 다양성 | `vocabulary` | TTR | 0.6 ~ 0.9 | 1.0 | Type-Token Ratio (고유 어휘 비율) |
| 침묵 패턴 | `silence` | 초 | 0.0 ~ 1.0 | 1.0 | 발화 중 평균 침묵 시간 |
| 감정 안정도 | `emotion` | 점 | 70.0 ~ 100.0 | 1.5 | 감정 분석 기반 안정도 (가중치 높음) |
| 활력도 | `vitality` | VPR | 2.0 ~ 10.0 | 1.0 | Vocalization-to-Pause Ratio (발화/침묵 비율) |

### 21.2 점수 계산 공식

```
if optimal_min <= value <= optimal_max:
    score = 100.0
elif value < optimal_min:
    score = (value / optimal_min) * 100.0
else:  # value > optimal_max
    score = 100.0 - ((value - optimal_max) / optimal_max) * 100.0

score = clamp(score, 0.0, 100.0)
```

### 21.3 감정 점수 계산 공식

```
긍정 감정 (기쁨, 행복):
    score = 80.0 + (confidence * 20.0)   -> 80~100점

중립 감정:
    score = 70.0 + (confidence * 10.0)   -> 70~80점

부정 감정 (분노, 슬픔, 불안, 공포):
    score = 60.0 - (confidence * 60.0)   -> 0~60점
```

### 21.4 종합 점수

```
average = (speed + duration + response + word_count + vocabulary + silence + emotion + vitality) / 8
```

### 21.5 감정 피드백 기준

| 점수 범위 | 상태 | 대응 |
|-----------|------|------|
| 80 ~ 100 | 매우 안정적 | 일반 대화 유지 |
| 70 ~ 79 | 안정적 | 일반 대화 유지 |
| 50 ~ 69 | 주의 필요 | 더 따뜻하게 대화 |
| 30 ~ 49 | 불안정 | 관심 필요, 보호자 알림 고려 |
| 0 ~ 29 | 매우 불안정 | 즉시 보호자 알림 |

---

## 22. 화면 구성

### 22.1 화면 목록

| 파일명 | 경로 | 설명 | 주요 기능 |
|--------|------|------|-----------|
| `index.html` | `/` | 메인 페이지 | 서비스 소개 및 로그인 화면으로 이동 |
| `login.html` | `/templates/login.html` | 로그인 | 아이디/비밀번호 입력, FN-AUTH-002 호출 |
| `signup.html` | `/templates/signup.html` | 회원가입 | 보호자+어르신 정보 입력, 중복 확인(FN-AUTH-003), 가입(FN-AUTH-001) |
| `dashboard.html` | `/templates/dashboard.html` | 대시보드 | 활동량 그래프(일/주/월), 기기 관리, 실시간 알림, 데이터 시뮬레이션 |
| `bomi.html` | `/templates/bomi.html` | 보미 (음성 대화) | 음성 녹음, 센서 확인(FN-DEVICE-002), 세션 생성(FN-VOICE-002), 분석(FN-VOICE-001), TTS 재생(FN-VOICE-003) |
| `report.html` | `/templates/report.html` | 리포트 | 주간/월간 활동 추이, 음성 분석 이력, 감정 통계 |
| `health.html` | `/templates/health.html` | 건강 관리 | 건강 데이터 조회 및 관리 |
| `mypage.html` | `/templates/mypage.html` | 마이페이지 | 보호자/어르신 정보 수정(FN-USER-001, FN-USER-002), 비밀번호 변경(FN-AUTH-004) |
| `modals.html` | `/templates/modals.html` | 모달 컴포넌트 | 공통 팝업/다이얼로그 템플릿 |

### 22.2 화면 흐름

```
login.html ──── 로그인 성공 ──── dashboard.html
    │                                   │
signup.html                    ┌────────┼────────┐
                               │        │        │
                          bomi.html report.html health.html
                                        │
                                   mypage.html
```

### 22.3 인증 흐름

1. 사용자가 `login.html`에서 로그인한다.
2. 성공 시 응답 데이터(보호자, 어르신, 기기 목록)를 클라이언트 측에 저장한다.
3. Flask `session`을 통해 서버 측 세션을 유지한다 (`secret_key: 'bomi_secret_key'`).
4. 세션 쿠키 설정: `SameSite=None`, `Secure=True` (Ngrok HTTPS 지원).
5. 이후 API 요청 시 `username`을 JSON body로 전송하여 인증 대체한다.

---

## 23. 문서 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 1.0 | 2026-02-09 | - | 초기 작성. 전체 17개 API 엔드포인트, 8개 DB 테이블, 8차원 음성 점수 체계, AI 모델 상세, 화면 구성 포함 |
