"""
LLM 프롬프트 A/B/C 테스트
3가지 버전 비교
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline
from config.models import MODELS


class LLMHandler:
    """3가지 프롬프트 버전 테스트"""
    
    def __init__(self, prompt_version="B", use_cpu_offload=True):
        """
        Args:
            prompt_version: "A", "B", "C"
                A: 예시 없음 (최소)
                B: 예시 2개 (중간)
                C: 예시 5개 (최대)
        """
        print(f"⏳ LLM 로딩 중 (버전 {prompt_version})...")
        self.prompt_version = prompt_version
        self.use_cpu_offload = use_cpu_offload
        self.load_model()
        print("✅ LLM 로딩 완료!")
        
        self.history = []
    
    def load_model(self):
        """모델 로드"""
        model_name = MODELS['llm']
        options = MODELS['llm_options']
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        if torch.cuda.is_available():
            print(f"   💾 GPU VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f}GB")
        
        quantization_config = None
        if options['load_in_4bit'] and torch.cuda.is_available():
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                llm_int8_enable_fp32_cpu_offload=self.use_cpu_offload
            )
        
        device_map = "auto"
        max_memory = {0: "7GB", "cpu": "30GB"} if self.use_cpu_offload else None
        
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=quantization_config,
                device_map=device_map,
                max_memory=max_memory,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                low_cpu_mem_usage=True,
            )
            print(f"   ✅ 모델 로드 성공")
        except Exception as e:
            print(f"   ⚠️  GPU 실패, CPU 전환")
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name, device_map="cpu", torch_dtype=torch.float32
            )
        
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=200,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.15,
            do_sample=True,
        )
        
    def set_prompt_version(self, version):
        """프롬프트 버전 동적 변경 (모델 재로드 방지)"""
        self.prompt_version = version
        print(f"   🔄 프롬프트 버전이 '{version}'(으)로 변경되었습니다.")
        self.reset_conversation()
    
    def get_system_prompt(self):
        """버전별 시스템 프롬프트"""
        
        if self.prompt_version == "A":
            # ========== 버전 A: 예시 없음 (최소) ==========
            return """너는 할머니의 손녀 '보미'야.

규칙:
- AI 티 내지 마
- 제3자처럼 말하지 말고 직접 대화해
- 짧게 1-2문장

지금 할머니와 대화 중이야."""
        
        elif self.prompt_version == "B":
            # ========== 버전 B: 예시 2개 (중간) ==========
            return """너는 할머니의 손녀 '보미'야.

규칙:
- AI 티 내지 마
- 제3자처럼 말하지 말고 직접 대화해
- 짧게 1-2문장

"넌 누구야?" → "할머니, 저 보미잖아요!"
"배고파" → "뭐 드시고 싶으세요?"

지금 할머니와 대화 중이야."""
        
        else:  # version == "C"
            # ========== 버전 C: 예시 5개 (최대) ==========
            return """너는 할머니의 손녀 '보미'야.

규칙:
- AI 티 내지 마
- 제3자처럼 말하지 말고 직접 대화해
- 짧게 1-2문장

예시:
"넌 누구야?" → "할머니, 저 보미잖아요! 손녀!"
"배고파" → "아이고, 배고프시구나! 뭐 드시고 싶으세요?"
"심심해" → "심심하시구나~ 제가 이야기 들어드릴게요!"
"머리 아파" → "에구, 머리 아프세요? 약 드셨어요?"
"오늘 날씨 좋네" → "네! 정말 좋은 날씨예요~ 산책 가실래요?"

지금 할머니와 대화 중이야."""
    
    def chat(self, user_input, max_turns=10):
        """대화"""
        if not self.history:
            self.history.append({
                "role": "system", 
                "content": self.get_system_prompt()
            })
        
        self.history.append({"role": "user", "content": user_input})
        response = self._run_pipeline(self.history)
        self.history.append({"role": "assistant", "content": response})
        
        if len(self.history) > max_turns * 2 + 1:
            self.history = [self.history[0]] + self.history[-(max_turns * 2):]
        
        return response
    
    def reset_conversation(self):
        """초기화"""
        self.history = []
    
    def _run_pipeline(self, messages):
        """생성"""
        try:
            prompt = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            outputs = self.pipe(
                prompt,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.pad_token_id
            )
            generated_text = outputs[0]['generated_text']
            return generated_text[len(prompt):].strip()
        except Exception as e:
            return "할머니, 다시 말씀해 주시겠어요?"


# ========== A/B/C 테스트 ==========
def compare_versions():
    """3개 버전 비교 테스트"""
    
    test_cases = [
        "넌 누구야?",
        "배고파",
        "심심해",
        "머리 아파",
        "오늘 날씨 좋네",
        "잘 모르겠어",  # 예시에 없는 케이스
    ]
    
    print("="*70)
    print("🧪 A/B/C 테스트: 프롬프트 버전 비교")
    print("="*70)
    print("\n버전:")
    print("  A: 예시 없음 (최소)")
    print("  B: 예시 2개 (중간)")
    print("  C: 예시 5개 (최대)")
    print("\n" + "="*70)
    
    results = {}
    
    print(f"\n⏳ LLM 모델 초기 로딩 (1회만 수행)...")
    llm = LLMHandler(prompt_version="A")
    
    for version in ["A", "B", "C"]:
        print(f"\n{'='*70}")
        print(f"버전 {version} 테스트 중...")
        print("="*70)
        
        llm.set_prompt_version(version)
        results[version] = []
        
        for i, question in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] 할머니: {question}")
            response = llm.chat(question)
            print(f"보미: {response}")
            
            results[version].append({
                "question": question,
                "response": response
            })
            
            llm.reset_conversation()
        
        print()
    
    # 결과 비교
    print("\n" + "="*70)
    print("📊 결과 비교")
    print("="*70)
    
    for i, question in enumerate(test_cases):
        print(f"\n질문 {i+1}: \"{question}\"")
        print("-" * 70)
        for version in ["A", "B", "C"]:
            response = results[version][i]["response"]
            print(f"  버전 {version}: {response}")
    
    print("\n" + "="*70)
    print("💡 평가 기준")
    print("="*70)
    print("1. 자연스러운가?")
    print("2. 손녀 역할을 유지하는가?")
    print("3. 제3자 화법을 쓰는가? (나쁨)")
    print("4. 예시에 없는 질문도 잘 답하는가?")
    print("5. 창의적이고 다양한가?")
    print("\n어느 버전이 가장 좋은지 직접 판단해보세요!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "compare":
        # 비교 모드
        compare_versions()
    else:
        # 단일 테스트 (기본: 버전 B)
        version = sys.argv[1] if len(sys.argv) > 1 else "B"
        
        print(f"버전 {version} 단일 테스트")
        llm = LLMHandler(prompt_version=version)
        
        test_cases = ["넌 누구야?", "배고파", "심심해"]
        
        for msg in test_cases:
            print(f"\n할머니: {msg}")
            response = llm.chat(msg)
            print(f"보미: {response}")
            llm.reset_conversation()
