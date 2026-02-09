# -*- coding: utf-8 -*-
"""
노인 케어 음성 분석 서버 v1.2
Q&A 더미 데이터 감정 적용 버전
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import tempfile
from datetime import datetime
from typing import Optional

# 로컬 모듈
from analyzer import SpeechAnalyzer
from db_handler import VoiceDBHandler
from llm_handler_with_qa_v2 import LLMHandler

# ========================================
# FastAPI 앱 생성
# ========================================
app = FastAPI(
    title="노인 케어 음성 분석 서버",
    description="음성 파일을 받아서 분석하고 DB에 저장",
    version="1.2.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# 전역 변수
# ========================================
analyzer = None
db_handler = None
llm_handler = None

# ========================================
# 서버 시작/종료 이벤트
# ========================================
@app.on_event("startup")
async def startup_event():
    global analyzer, db_handler, llm_handler
    
    print("="*60)
    print(">>> SERVER v1.2 - Q&A EMOTION APPLY <<<")
    print("="*60)
    
    print("\n[1/3] 음성 분석기 로드 중...")
    try:
        analyzer = SpeechAnalyzer()
        print("[OK] 음성 분석기 로드 완료!")
    except Exception as e:
        print(f"[ERROR] 음성 분석기 로드 실패: {e}")
        raise e
    
    print("\n[2/3] DB 연결 중...")
    try:
        db_handler = VoiceDBHandler()
        if db_handler.connect():
            print("[OK] DB 연결 성공!")
        else:
            print("[WARN] DB 연결 실패")
            db_handler = None
    except Exception as e:
        print(f"[WARN] DB 초기화 실패: {e}")
        db_handler = None
    
    print("\n[3/3] LLM 초기화 중...")
    try:
        llm_handler = LLMHandler()
        print("[OK] LLM 초기화 완료!")
    except Exception as e:
        print(f"[WARN] LLM 초기화 실패: {e}")
        llm_handler = None
    
    print("\n" + "="*60)
    print("[OK] SERVER READY! (v1.2)")
    print("="*60)

@app.on_event("shutdown")
async def shutdown_event():
    global db_handler
    if db_handler:
        db_handler.close()
    print("[OK] 서버 종료 완료")

# ========================================
# API 엔드포인트
# ========================================

@app.get("/")
async def root():
    return {"message": "노인 케어 음성 분석 서버", "version": "1.2.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.2.0",
        "analyzer": analyzer is not None,
        "db": db_handler is not None,
        "llm": llm_handler is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/latest-sensing")
async def get_latest_sensing(senior_id: int = 1):
    if not db_handler:
        return {"sensing_id": None, "message": "DB 연결 없음"}
    
    try:
        cursor = db_handler.cursor
        sql = "SELECT sensing_id FROM tb_sensing ORDER BY created_at DESC LIMIT 1"
        cursor.execute(sql)
        result = cursor.fetchone()
        
        if result:
            return {"sensing_id": result[0], "message": "최신 센서 데이터"}
        else:
            return {"sensing_id": None, "message": "센서 데이터 없음"}
    except Exception as e:
        return {"sensing_id": None, "error": str(e)}

@app.post("/analyze")
async def analyze_audio(
    audio_file: UploadFile = File(...),
    senior_id: int = Form(1),
    sensing_id: Optional[int] = Form(None),
    generate_response: bool = Form(True)
):
    if not analyzer:
        raise HTTPException(status_code=503, detail="음성 분석기 초기화 안 됨")
    
    print(f"\n{'='*60}")
    print(f"[ANALYZE REQUEST] v1.2")
    print(f"{'='*60}")
    
    # ========================================
    # 1. 음성 파일 저장
    # ========================================
    try:
        suffix = os.path.splitext(audio_file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            content = await audio_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        print(f"[OK] 음성 파일 저장: {tmp_path}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"파일 저장 실패: {str(e)}")
    
    # ========================================
    # 2. 음성 분석
    # ========================================
    try:
        print("\n[분석 시작...]")
        analysis_result = analyzer.analyze(tmp_path)
        
        whisper = analysis_result['features']['whisper']
        emotion = analysis_result['features']['emotion']
        scores = analysis_result['scores']
        
        # 원본 감정 저장
        original_emotion = emotion['final_emotion']
        original_emotion_score = scores['emotion']
        
        print(f"[OK] 분석 완료!")
        print(f"   텍스트: {whisper['text']}")
        print(f"   [원본] 감정: {original_emotion}")
        print(f"   [원본] 감정점수: {original_emotion_score:.1f}점")
    except Exception as e:
        try:
            os.remove(tmp_path)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")
    
    # ========================================
    # 3. AI 응답 생성 + Q&A 감정 확인
    # ========================================
    ai_response = None
    qa_matched = False
    qa_emotion = None
    qa_emotion_score = None
    
    # 최종 감정값 (이걸 응답에 사용!)
    final_emotion_label = original_emotion
    final_emotion_score = original_emotion_score
    
    if generate_response and llm_handler:
        try:
            print("\n[AI 응답 생성 중...]")
            ai_response = llm_handler.chat(
                whisper['text'],
                emotion_info=emotion,
                scores=scores
            )
            print(f"[OK] AI 응답: {ai_response[:50]}...")
            
            # ========== Q&A 매칭 정보 확인 ==========
            qa_match_info = llm_handler.get_last_qa_match()
            
            print(f"\n[DEBUG] qa_match_info = {qa_match_info}")
            
            if qa_match_info and qa_match_info.get('matched'):
                qa_matched = True
                qa_emotion = qa_match_info.get('emotion')
                qa_emotion_score = qa_match_info.get('emotion_score')
                
                print(f"\n{'='*50}")
                print(f"[QA MATCHED] Q&A 더미 데이터 매칭 성공!")
                print(f"{'='*50}")
                print(f"   [더미] 감정: {qa_emotion}")
                print(f"   [더미] 감정점수: {qa_emotion_score}")
                
                # 핵심: 최종 감정값 덮어쓰기
                final_emotion_label = qa_emotion
                final_emotion_score = qa_emotion_score
                
                print(f"\n   [OK] 감정 덮어쓰기 완료!")
                print(f"   -> 최종 감정: {final_emotion_label}")
                print(f"   -> 최종 감정점수: {final_emotion_score}")
                print(f"{'='*50}")
            else:
                print(f"\n[WARN] Q&A 매칭 안 됨 - 원본 감정 사용: {final_emotion_label}")
                
        except Exception as e:
            print(f"[WARN] AI 응답 생성 실패: {e}")
            ai_response = None
    
    # ========================================
    # 4. 점수 재계산
    # ========================================
    final_scores = scores.copy()
    final_scores['emotion'] = final_emotion_score
    
    # 평균 재계산
    score_keys = ['speed', 'duration', 'response', 'word_count', 'vocabulary', 'silence', 'emotion', 'vitality']
    valid_scores = [final_scores.get(k, 0) for k in score_keys if k in final_scores]
    if valid_scores:
        final_scores['average'] = sum(valid_scores) / len(valid_scores)
    
    # ========================================
    # 5. DB 저장
    # ========================================
    voice_id = None
    save_sensing_id = sensing_id if sensing_id is not None else 0
    
    if db_handler:
        try:
            # Q&A 감정 적용된 결과로 저장
            if qa_matched:
                analysis_result['features']['emotion']['final_emotion'] = final_emotion_label
                analysis_result['scores']['emotion'] = final_emotion_score
            
            voice_id = db_handler.save_analysis(senior_id, analysis_result, save_sensing_id)
            if voice_id:
                print(f"[OK] DB 저장 성공 (voice_id: {voice_id})")
        except Exception as e:
            print(f"[ERROR] DB 저장 에러: {e}")
    
    # ========================================
    # 6. 임시 파일 삭제
    # ========================================
    try:
        os.remove(tmp_path)
        print(f"[OK] 임시 파일 삭제: {tmp_path}")
    except:
        pass
    
    # ========================================
    # 7. 결과 반환
    # ========================================
    response_data = {
        "success": True,
        "voice_id": voice_id,
        "analysis": {
            "text": whisper['text'],
            "emotion": {
                # 최종 감정 (Q&A 적용됨)
                "final": final_emotion_label,
                "confidence": emotion.get('final_conf', 0.0),
                "text_emotion": emotion.get('text_emotion', ''),
                "audio_emotion": emotion.get('audio_emotion', ''),
                "z_peak": emotion.get('z_peak', 0.0),
                "decision": emotion.get('decision', ''),
                # Q&A 매칭 정보
                "qa_matched": qa_matched,
                "qa_emotion": qa_emotion,
                "qa_emotion_score": qa_emotion_score,
                # 원본 감정 (참고용)
                "original_emotion": original_emotion,
                "original_emotion_score": original_emotion_score
            },
            # 최종 점수 (Q&A 적용됨)
            "scores": final_scores,
            "whisper": {
                "word_count": whisper['word_count'],
                "wpm": whisper['wpm'],
                "duration": whisper['duration'],
                "response_time": whisper['response_time']
            }
        },
        "ai_response": ai_response,
        "metadata": {
            "senior_id": senior_id,
            "sensing_id": save_sensing_id,
            "timestamp": datetime.now().isoformat(),
            "qa_matched": qa_matched,
            "version": "1.2.0"
        }
    }
    
    print(f"\n{'='*60}")
    print(f"[RESPONSE]")
    print(f"{'='*60}")
    print(f"   emotion.final = {response_data['analysis']['emotion']['final']}")
    print(f"   qa_matched = {qa_matched}")
    print(f"   scores.emotion = {final_scores['emotion']:.1f}")
    print(f"{'='*60}\n")
    
    return response_data

# ========================================
# 서버 실행
# ========================================
if __name__ == "__main__":
    print("""
    ========================================
    노인 케어 음성 분석 서버 v1.2
    Q&A 더미 데이터 감정 적용 버전
    ========================================
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
