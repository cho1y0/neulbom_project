"""
적응형 감정 통합 엔진 (Adaptive Emotion Fusion) - 고속 최적화 버전
- Pitch 분석 알고리즘 최적화 (yin 사용)
- 오디오 샘플링 및 로드 구간 제한 (3초)
- 멀티모달 앙상블 유지
"""

import torch
import torch.nn.functional as F
import librosa
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import Wav2Vec2Processor, Wav2Vec2ForSequenceClassification
from config.models import MODELS

class EmotionEnsemble:
    """
    개선된 감정 분석 엔진 (최적화 버전)
    - Z-score 기반 Pitch Dynamics 분석 (고속)
    - 텍스트(KcELECTRA) + 음성(Wav2Vec2) 멀티모달 결합
    """
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"❤️‍🩹 고속 감정 분석 엔진 초기화 (Device: {self.device})")

        try:
            # Config에서 모델명 가져오기
            text_model_name = MODELS['emotion_text']
            audio_model_name = MODELS['emotion_audio']
            
            # 1. 텍스트 모델 로드
            self.text_tokenizer = AutoTokenizer.from_pretrained(text_model_name)
            self.text_model = AutoModelForSequenceClassification.from_pretrained(text_model_name).to(self.device)
            
            # 2. 음성 모델 로드
            self.audio_processor = Wav2Vec2Processor.from_pretrained(audio_model_name)
            self.audio_model = Wav2Vec2ForSequenceClassification.from_pretrained(audio_model_name).to(self.device)
            
            self.text_model.eval()
            self.audio_model.eval()
            
        except Exception as e:
            print(f"❌ 모델 로드 실패: {e}")
            raise e

    def predict(self, audio_path, text):
        """
        [고속 버전] 음성 파일과 텍스트를 결합하여 감정 분석
        """
        try:
            # 🚀 최적화: 16kHz로 리샘플링하며 앞부분 최대 3초만 로드 (병목 제거)
            y, sr = librosa.load(audio_path, sr=16000, duration=3.0)
            
            # 1. 고속 Pitch 분석 (Z-peak)
            z_peak = self._calculate_pitch_zscore(y, sr)
            
            # 2. 음성 감정 분석 (Wav2Vec2)
            audio_inputs = self.audio_processor(y, sampling_rate=sr, return_tensors="pt").to(self.device)
            with torch.no_grad():
                audio_logits = self.audio_model(**audio_inputs).logits
            
            audio_probs = F.softmax(audio_logits, dim=-1)
            audio_conf, audio_idx = torch.max(audio_probs, dim=-1)
            audio_label = self._translate_audio(self.audio_model.config.id2label[audio_idx.item()])

            # 3. 텍스트 감정 분석 (KcELECTRA)
            text_inputs = self.text_tokenizer(
                text, 
                return_tensors="pt", 
                truncation=True, 
                max_length=128
            ).to(self.device)
            
            with torch.no_grad():
                text_logits = self.text_model(**text_inputs).logits
            
            text_probs = F.softmax(text_logits, dim=-1)
            text_conf, text_idx = torch.max(text_probs, dim=-1)
            text_label = self.text_model.config.id2label[text_idx.item()]

            # 4. 멀티모달 가중치 결합 (PDF 기술노트 기반 로직)
            # 기본적으로 텍스트 감정을 따르되, 목소리 톤(Z-peak)이 강하면 음성 감정 반영
            final_emotion = text_label
            
            # 규칙: 목소리에 감정 변화가 크고(Z-peak 가 높고) 음성이 확실할 때
            if z_peak > 2.5 and audio_label in ['분노', '기쁨', '슬픔']:
                # 텍스트가 중립이거나 음성 신뢰도가 높을 때 교체
                if text_label == '중립' or audio_conf > 0.6:
                    final_emotion = audio_label

            return {
                'final_emotion': final_emotion,
                'text_label': text_label,
                'audio_label': audio_label,
                'z_peak': float(z_peak),
                'audio_conf': float(audio_conf),
                'text_conf': float(text_conf)
            }

        except Exception as e:
            print(f"❌ 분석 오류: {e}")
            return {
                'final_emotion': '중립',
                'text_label': '중립',
                'audio_label': '중립',
                'z_peak': 0.0,
                'audio_conf': 0.0
            }

    def _calculate_pitch_zscore(self, y, sr, sigma_min=5.0):
        """
        🚀 초고속 Pitch 분석 (YIN 알고리즘 적용)
        """
        try:
            # librosa.yin은 pyin보다 훨씬 빠름
            f0 = librosa.yin(y, fmin=65, fmax=500, sr=sr, frame_length=1024)
            
            # 유효한 피치 값만 추출
            f0_valid = f0[f0 > 0]
            if len(f0_valid) < 5:
                return 0.0
            
            # Z-score 계산 (목소리의 역동성 측정)
            mu_f0 = np.mean(f0_valid)
            sigma_f0 = np.std(f0_valid)
            sigma_safe = max(sigma_f0, sigma_min)
            
            z_scores = np.abs((f0_valid - mu_f0) / sigma_safe)
            return float(np.max(z_scores))
            
        except:
            return 0.0

    def _translate_audio(self, label):
        """음성 감정 레이블 한글 매핑"""
        label = str(label).lower()
        mapping = {
            'angry': '분노', 'fear': '불안', 'happy': '기쁨', 
            'neutral': '중립', 'sad': '슬픔', 'surprise': '당황',
            '0': '분노', '1': '기쁨', '2': '불안', '3': '슬픔', '4': '중립'
        }
        for k, v in mapping.items():
            if k in label:
                return v
        return '중립'