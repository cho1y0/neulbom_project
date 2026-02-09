import os
from pathlib import Path
from dotenv import load_dotenv
import openai
from qa_dataset_improved import find_matching_qa, ALL_QA_DATASET

# pip install openai python-dotenv

class LLMHandler:
    """
    OpenAI API 핸들러 (감정 기반 응답 + Q&A 더미 데이터)
    - 감정 상태에 따른 동적 프롬프트
    - 점수 기반 위험 감지
    - Q&A 더미 데이터로 정답 보장 (개선된 매칭)
    - GPT-4 mini 사용
    """
    
    def __init__(self, use_qa_dataset=True):
        """
        Args:
            use_qa_dataset: Q&A 데이터셋 사용 여부 (True 권장!)
        """
        print("⏳ OpenAI API 초기화 중...")
        
        # 1. 키 파일 위치 찾기
        env_path = Path(__file__).parent / 'api-key' / 'openapi.env'
        
        # 2. .env 로딩
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            print(f"   🔑 API 키 파일 로딩: {env_path}")
        else:
            print(f"   ⚠️  경고: 키 파일을 못 찾았습니다. ({env_path})")

        # 3. API 키 확인
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("\n❌ [오류] OpenAI API 키가 없습니다.")
            raise ValueError("API Key Missing")
            
        # 4. 클라이언트 연결
        self.client = openai.OpenAI(api_key=self.api_key)
        self.history = []
        self.use_qa_dataset = use_qa_dataset
        
        # ========== 추가: 마지막 Q&A 매칭 정보 저장 ==========
        self.last_qa_match = None
        
        if use_qa_dataset:
            print(f"✅ OpenAI API 준비 완료 (Q&A 데이터셋 활성화: {len(ALL_QA_DATASET)}개 Q&A)")
        else:
            print("✅ OpenAI API 준비 완료 (순수 LLM 모드)")

    def chat(self, user_input, emotion_info=None, scores=None, max_turns=10):
        """
        대화 함수 (감정 + 점수 + Q&A 더미 데이터)
        
        Args:
            user_input: 사용자 입력 텍스트
            emotion_info: 감정 분석 결과 딕셔너리
            scores: 점수 딕셔너리
            max_turns: 최대 대화 턴 수
        
        Returns:
            ai_response: AI 응답 텍스트
        """
        # 초기화
        self.last_qa_match = None
        
        # ========== 1단계: Q&A 데이터셋에서 찾기 ==========
        if self.use_qa_dataset:
            print(f"\n🔍 Q&A 데이터셋 검색 중...")
            matching_qa = find_matching_qa(user_input)
            if matching_qa:
                print(f"✅ Q&A 데이터셋에서 매칭됨!")
                print(f"   질문: {matching_qa['question']}")
                print(f"   감정: {matching_qa['emotion']}")
                print(f"   감정점수: {matching_qa['emotion_score']}")
                
                # ========== 수정: Q&A 매칭 정보 저장 ==========
                self.last_qa_match = {
                    'matched': True,
                    'question': matching_qa['question'],
                    'emotion': matching_qa['emotion'],
                    'emotion_score': matching_qa['emotion_score']
                }
                
                return matching_qa['answer']
        
        # ========== 2단계: 데이터셋에 없으면 LLM 사용 ==========
        
        print(f"\n⚠️  데이터셋 매칭 실패 → LLM API 호출")
        
        target_model = "gpt-4o-mini"
        
        # === 1. 기본 시스템 프롬프트 ===
        system_prompt = self._build_base_prompt()
        
        # === 2. 감정 정보 반영 ===
        if emotion_info:
            emotion_prompt = self._build_emotion_prompt(emotion_info)
            system_prompt += "\n\n" + emotion_prompt
        
        # === 3. 점수 기반 위험 감지 ===
        if scores:
            risk_prompt = self._build_risk_prompt(scores)
            if risk_prompt:
                system_prompt += "\n\n" + risk_prompt
        
        # === 4. 히스토리 관리 ===
        if not self.history:
            self.history.append({"role": "system", "content": system_prompt})
        else:
            self.history[0] = {"role": "system", "content": system_prompt}
            
        self.history.append({"role": "user", "content": user_input})
        
        try:
            # === 5. API 호출 ===
            response = self.client.chat.completions.create(
                model=target_model,
                messages=self.history,
                max_completion_tokens=1500
            )
            
            # === 6. 응답 추출 ===
            ai_response = response.choices[0].message.content

            if not ai_response:
                ai_response = "..."

            # === 7. 대화 저장 ===
            self.history.append({"role": "assistant", "content": ai_response})
            
            # 기억 용량 관리
            if len(self.history) > (max_turns * 2) + 1:
                self.history = [self.history[0]] + self.history[-(max_turns * 2):]
                
            return ai_response

        except Exception as e:
            print(f"❌ API 오류 ({target_model}): {e}")
            return "할머니, 제가 잠깐 딴생각을 했나 봐요. 다시 말씀해 주시겠어요?"

    def get_last_qa_match(self):
        """
        마지막 Q&A 매칭 정보 반환
        
        Returns:
            dict or None: {'matched': True, 'emotion': '기쁨', 'emotion_score': 75.0} 또는 None
        """
        return self.last_qa_match

    def _build_base_prompt(self):
        """기본 페르소나 프롬프트"""
        return (
            "당신은 20대 손녀 '보미'입니다.\n"
            "\n"
            "【 대화 원칙 】\n"
            "- 할머니/할아버지와 편안하게 대화합니다\n"
            "- 친근한 존댓말을 사용합니다\n"
            "- AI나 기계라는 티를 절대 내지 마세요\n"
            "- 1~2문장으로 짧고 다정하게 답합니다\n"
            "- 자연스럽게 대화를 이어갑니다"
        )
    
    def _build_emotion_prompt(self, emotion_info):
        """감정 기반 프롬프트 생성"""
        final_emotion = emotion_info.get('final_emotion', '중립')
        confidence = emotion_info.get('audio_conf', 0.5)
        
        prompt = f"【 현재 감정 상태 】\n"
        prompt += f"- 감정: {final_emotion}\n"
        prompt += f"- 확신도: {confidence:.2f}\n"
        prompt += f"\n【 대화 전략 】\n"
        
        if final_emotion == '슬픔':
            prompt += (
                "- 따뜻하게 위로하고 공감해주세요\n"
                "- '괜찮아요', '제가 있잖아요' 같은 안심시키는 말을 사용하세요\n"
                "- 긍정적인 추억을 떠올리게 도와주세요\n"
                "- 너무 밝게 굴지 말고 진심으로 공감하세요"
            )
        elif final_emotion == '분노':
            prompt += (
                "- 차분하게 말씀을 경청하세요\n"
                "- 화를 더 돋우는 말은 피하세요\n"
                "- '그러셨구나', '속상하셨겠어요' 같은 이해의 표현을 사용하세요\n"
                "- 천천히 진정시켜 주세요"
            )
        elif final_emotion == '불안':
            prompt += (
                "- 안심시키고 긍정적으로 격려하세요\n"
                "- '걱정 마세요', '다 잘 될 거예요' 같은 위로를 해주세요\n"
                "- 현재에 집중하도록 도와주세요\n"
                "- 편안한 화제로 전환하세요"
            )
        elif final_emotion == '공포':
            prompt += (
                "- 매우 부드럽고 차분하게 대화하세요\n"
                "- '제가 옆에 있어요', '안전해요' 같은 말로 안심시키세요\n"
                "- 무서운 이야기는 피하고 평화로운 주제로 전환하세요"
            )
        elif final_emotion == '기쁨':
            prompt += (
                "- 밝게 맞장구치며 함께 기뻐하세요\n"
                "- '와 정말 좋으시겠어요!', '축하드려요!' 같은 긍정적 반응을 보이세요\n"
                "- 대화를 즐겁게 이어가세요"
            )
        else:  # 중립
            prompt += (
                "- 자연스럽게 대화를 이어가세요\n"
                "- 관심 있어하실 만한 화제를 제시하세요\n"
                "- 편안한 분위기를 유지하세요"
            )
        
        return prompt
    
    def _build_risk_prompt(self, scores):
        """점수 기반 위험 감지 프롬프트"""
        avg_score = scores.get('average', 100)
        emotion_score = scores.get('emotion', 100)
        
        if avg_score < 50 or emotion_score < 40:
            return (
                "【 ⚠️ 주의: 고위험 상태 감지 】\n"
                "- 현재 상태가 매우 좋지 않습니다\n"
                "- 더욱 세심하게 대화하세요\n"
                "- 가능하면 보호자에게 알릴 필요가 있습니다\n"
                "- '괜찮으세요?', '어디 불편하신 데 없으세요?' 같은 질문을 자연스럽게 섞으세요"
            )
        elif avg_score < 65 or emotion_score < 60:
            return (
                "【 주의: 관심 필요 】\n"
                "- 평소보다 상태가 좋지 않습니다\n"
                "- 더 따뜻하게 대화하세요\n"
                "- 기분이 나아질 수 있도록 도와주세요"
            )
        
        return None

    def reset_conversation(self):
        """대화 초기화"""
        self.history = []
        self.last_qa_match = None
        print("🧹 대화 기억 초기화됨")

    def get_conversation_length(self):
        """대화 턴 수 반환"""
        return (len(self.history) - 1) // 2 if self.history else 0

    def generate_report(self, scores, text_summary):
        """보호자용 리포트 생성"""
        prompt = f"""다음 데이터를 바탕으로 노인의 상태를 보호자에게 전달할 간단한 리포트를 작성해주세요.

【 점수 데이터 】
- 평균 점수: {scores.get('average', 0):.1f}점
- 감정 안정도: {scores.get('emotion', 0):.1f}점
- 말의 속도: {scores.get('speed', 0):.1f}점
- 어휘 다양성: {scores.get('vocabulary', 0):.1f}점
- 반응 속도: {scores.get('response', 0):.1f}점

【 대화 요약 】
{text_summary}

【 리포트 작성 가이드 】
- 보호자가 이해하기 쉽게 작성
- 걱정할 부분이 있으면 명확히 언급
- 긍정적인 부분도 함께 전달
- 3-4문장으로 간단히 요약
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ 리포트 생성 오류: {e}")
            return f"평균 점수 {scores.get('average', 0):.1f}점으로 {text_summary}"
