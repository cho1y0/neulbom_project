import time
import concurrent.futures
import numpy as np
import librosa
from faster_whisper import WhisperModel
from config.models import MODELS
from config.scoring import SCORING_CRITERIA, calculate_score
from emotion_model import EmotionEnsemble

def calculate_emotion_score(emotion_info):
    if not emotion_info or 'final_emotion' not in emotion_info:
        return 70.0
    final_emotion = emotion_info.get('final_emotion', '중립')
    confidence = emotion_info.get('audio_conf', 0.5)
    POSITIVE = ['기쁨', '행복', 'happiness', 'happy']
    NEUTRAL = ['중립', 'neutral']
    if any(pos in final_emotion.lower() for pos in POSITIVE):
        score = 80.0 + (confidence * 20.0)
    elif any(neu in final_emotion.lower() for neu in NEUTRAL):
        score = 70.0 + (confidence * 10.0)
    else:
        score = 60.0 - (confidence * 60.0)
    return max(0.0, min(100.0, score))

class SpeechAnalyzer:
    def __init__(self):
        print("🚀 고속 분석 엔진 로딩 중 (Model: tiny)...")
        self.load_models()
        print("✅ 로딩 완료!")
    
    def load_models(self):
        import torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # 🚀 최적화: tiny 모델 + int8 양자화 (속도 극대화)
        self.whisper_model = WhisperModel("tiny", device=self.device, compute_type="int8")
        
        from transformers import AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(MODELS['tokenizer'])
        self.emotion_engine = EmotionEnsemble()
    
    def analyze(self, audio_path):
        start_total = time.time()
        print(f"🎤 분석 시작: {audio_path}")
        
        # 1. 고속 STT (Faster-Whisper)
        whisper_results = self._whisper_analysis_fast(audio_path)
        text = whisper_results['text']
        
        # 2. 어휘 및 감정 분석 (Pitch 최적화 버전 호출)
        vocab_results = self._vocabulary_analysis(text)
        emotion_results = self.emotion_engine.predict(audio_path, text)

        scores = self._calculate_scores(whisper_results, vocab_results, emotion_results)
        
        print(f"⏱️ 총 소요 시간: {time.time() - start_total:.2f}초")
        return {
            'features': {'whisper': whisper_results, 'vocabulary': vocab_results, 'emotion': emotion_results},
            'scores': scores
        }
    
    def _whisper_analysis_fast(self, audio_path):
        # 🚀 최적화: 오디오 로딩 없이 Whisper가 직접 파일을 읽게 함
        segments, info = self.whisper_model.transcribe(audio_path, beam_size=1, language="ko", vad_filter=True)
        
        text_segments = []
        speech_time = 0
        for segment in segments:
            text_segments.append(segment.text)
            speech_time += (segment.end - segment.start)
            
        transcription = "".join(text_segments).strip()
        duration = info.duration
        wpm = (len(transcription.split()) / duration) * 60 if duration > 0 else 0
        avg_silence = max(0, duration - speech_time)
        
        return {
            'text': transcription, 'word_count': len(transcription.split()),
            'wpm': wpm, 'duration': duration, 'response_time': 0.5,
            'avg_silence': avg_silence, 'vpr': duration / (avg_silence + 0.01)
        }

    def _vocabulary_analysis(self, text):
        if not text: return {'total_tokens':0, 'unique_tokens':0, 'ttr':0}
        tokens = self.tokenizer.tokenize(text)
        return {'total_tokens': len(tokens), 'unique_tokens': len(set(tokens)), 'ttr': len(set(tokens))/len(tokens)}

    def _calculate_scores(self, w, v, e):
        criteria = SCORING_CRITERIA
        sc = {
            'speed': calculate_score(w['wpm'], criteria['speed']['optimal_min'], criteria['speed']['optimal_max']),
            'duration': calculate_score(w['duration'], criteria['duration']['optimal_min'], criteria['duration']['optimal_max']),
            'response': 85.0,
            'word_count': calculate_score(w['word_count'], criteria['word_count']['optimal_min'], criteria['word_count']['optimal_max']),
            'vocabulary': calculate_score(v['ttr'], criteria['vocabulary']['optimal_min'], criteria['vocabulary']['optimal_max']),
            'silence': calculate_score(w['avg_silence'], criteria['silence']['optimal_min'], criteria['silence']['optimal_max']),
            'emotion': calculate_emotion_score(e),
            'vitality': calculate_score(w['vpr'], criteria['vitality']['optimal_min'], criteria['vitality']['optimal_max'])
        }
        sc['average'] = sum(sc.values()) / len(sc)
        return sc