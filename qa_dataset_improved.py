"""
Q&A 더미 데이터셋 (개선된 매칭 로직)
할머니의 질문에 정확한 답변 제공
"""

# [기존 Q&A 데이터는 동일...]

GREETING_QA = [
    {
        "question": "넌 누구야?",
        "answer": "할머니, 저 보미예요! 손녀 보미랍니다~",
        "emotion": "당황",
        "emotion_score": 53.0
    },
    {
        "question": "어디 있어?",
        "answer": "할머니, 저 여기 있어요. 할머니 옆에 있죠.",
        "emotion": "중립",
        "emotion_score": 70.0
    },
    {
        "question": "잘 지냈어?",
        "answer": "네~ 할머니! 저 잘 지냈어요~ 할머니는 어떠세요?",
        "emotion": "기쁨",
        "emotion_score": 85.0
    },
    {
        "question": "안녕하세요",
        "answer": "안녕하세요, 할머니! 저 보미예요. 반가워요!",
        "emotion": "기쁨",
        "emotion_score": 80.0
    }
]

MEDICINE_QA = [
    {
        "question": "약 복용 시간 알려줘",
        "answer": "오늘은 12시에서 2시 사이 식후 30분 뒤에 드시면 돼요.",
        "emotion": "기쁨",
        "emotion_score": 75.0
    },
    {
        "question": "약을 먹어야 해?",
        "answer": "네, 할머니. 지금 오후 2시니까 약을 드실 시간이에요. 물과 함께 드세요.",
        "emotion": "기쁨",
        "emotion_score": 75.0
    },
    {
        "question": "약은 언제 먹지?",
        "answer": "할머니, 아침 8시, 점심 12시, 저녁 6시에 드시는 거예요. 지금 몇 시인지 봐야겠어요.",
        "emotion": "기쁨",
        "emotion_score": 65.0
    },
    {
        "question": "혈압약 먹었어?",
        "answer": "할머니, 혈압약은 아침에 드셨으니까 지금은 안 드셔도 돼요. 저녁에 또 드시면 되요.",
        "emotion": "중립",
        "emotion_score": 72.0
    },
    {
        "question": "약이 많아",
        "answer": "그렇죠, 할머니. 하지만 이 약들이 할머니 건강을 지키는 거예요. 제가 도와드릴게요.",
        "emotion": "중립",
        "emotion_score": 73.0
    },
    {
        "question": "이 약이 뭐예요?",
        "answer": "이건 혈압약이에요. 할머니 혈압을 안정적으로 유지하는 약이랍니다.",
        "emotion": "중립",
        "emotion_score": 70.0
    }
]

FOOD_QA = [
    {
        "question": "배고파",
        "answer": "아, 배고프세요? 뭐 드시고 싶으세요? 제가 준비해드릴게요.",
        "emotion": "중립",
        "emotion_score": 72.0
    },
    {
        "question": "뭐 먹을 거 없어?",
        "answer": "할머니, 오늘 미역국이 있어요. 드실래요? 아니면 계란말이?",
        "emotion": "중립",
        "emotion_score": 73.0
    },
    {
        "question": "밥 줘",
        "answer": "네, 할머니! 밥 준비해드릴게요. 조금 있으면 준비돼요.",
        "emotion": "중립",
        "emotion_score": 72.0
    },
    {
        "question": "점심은 먹었어?",
        "answer": "네, 할머니! 아까 12시에 된장찌개하고 밥 드셨잖아요. 기억 안 나세요?",
        "emotion": "중립",
        "emotion_score": 70.0
    },
    {
        "question": "입맛이 없어",
        "answer": "그렇군요, 할머니. 가벼운 죽으로 준비해드릴까요? 따뜻한 미숫가루는 어때요?",
        "emotion": "슬픔",
        "emotion_score": 65.0
    },
    {
        "question": "물 줘",
        "answer": "네, 할머니! 따뜻한 물 가져다드릴게요.",
        "emotion": "중립",
        "emotion_score": 75.0
    }
]

HEALTH_QA = [
    {
        "question": "머리 아파",
        "answer": "에구, 머리가 아프세요? 약 드셨어요? 휴식을 좀 취하세요.",
        "emotion": "슬픔",
        "emotion_score": 60.0
    },
    {
        "question": "허리가 아파요",
        "answer": "아이고, 허리가 아프세요? 제가 파스를 붙여드릴까요? 아니면 따뜻한 찜질?",
        "emotion": "슬픔",
        "emotion_score": 62.0
    },
    {
        "question": "감기 걸렸어",
        "answer": "감기에 걸리셨어요? 약을 드셔야겠어요. 따뜻한 물도 많이 드세요.",
        "emotion": "슬픔",
        "emotion_score": 58.0
    },
    {
        "question": "몸이 아파",
        "answer": "어디가 아프세요? 제가 병원에 모셔드릴까요? 먼저 약을 드셔보세요.",
        "emotion": "슬픔",
        "emotion_score": 55.0
    },
    {
        "question": "혈압이 높아",
        "answer": "혈압이 높으세요? 앉아서 쉬셔요. 혈압약을 드실 시간이 다 되었나요?",
        "emotion": "불안",
        "emotion_score": 50.0
    }
]

EMOTION_QA = [
    {
        "question": "심심해",
        "answer": "심심하세요? 제가 이야기 들어드릴게요. 요즘 어떻게 지내셨어요?",
        "emotion": "슬픔",
        "emotion_score": 65.0
    },
    {
        "question": "외로워",
        "answer": "외로우세요? 혼자가 아니에요. 저 항상 옆에 있어요. 뭐 하고 싶으세요?",
        "emotion": "슬픔",
        "emotion_score": 62.0
    },
    {
        "question": "화나",
        "answer": "화나셨어요? 뭐가 화나게 했어요? 제 말을 들어보세요.",
        "emotion": "분노",
        "emotion_score": 45.0
    },
    {
        "question": "답답해",
        "answer": "답답하시군요. 산책을 할까요? 밖에 나가면 기분이 좋아질 거예요.",
        "emotion": "슬픔",
        "emotion_score": 60.0
    },
    {
        "question": "좋은 일이 있었어",
        "answer": "와! 좋은 일이 있으셨어요? 축하드려요! 어떤 일인데요?",
        "emotion": "기쁨",
        "emotion_score": 85.0
    }
]

WEATHER_QA = [
    {
        "question": "오늘 날씨 좋네",
        "answer": "네! 정말 좋은 날씨예요! 할머니와 산책을 나갈까요?",
        "emotion": "기쁨",
        "emotion_score": 82.0
    },
    {
        "question": "추워",
        "answer": "추우세요? 담요를 들어드릴까요? 따뜻한 차를 마시실래요?",
        "emotion": "중립",
        "emotion_score": 70.0
    },
    {
        "question": "더워",
        "answer": "더우세요? 시원한 물을 마셔보세요. 에어컨을 켤까요?",
        "emotion": "중립",
        "emotion_score": 72.0
    },
    {
        "question": "비가 오네",
        "answer": "비가 오네요. 오늘은 밖에 안 나가시고 실내에서 쉬세요.",
        "emotion": "중립",
        "emotion_score": 70.0
    },
    {
        "question": "봄이 왔나",
        "answer": "네, 이제 봄이 왔어요! 날씨도 따뜻해지고, 꽃들이 피고 있어요.",
        "emotion": "기쁨",
        "emotion_score": 80.0
    }
]

FAMILY_QA = [
    {
        "question": "아들은 뭐 하니?",
        "answer": "아드님은 회사에서 일하고 있어요. 저녁에 들어올 거예요.",
        "emotion": "중립",
        "emotion_score": 72.0
    },
    {
        "question": "손자 봤어?",
        "answer": "손자가 어제 다녀갔어요. 얼마나 커졌는지 봤어요?",
        "emotion": "기쁨",
        "emotion_score": 80.0
    },
    {
        "question": "옛날 생각나",
        "answer": "그렇죠, 할머니. 저에게 옛날 얘기를 해주실래요?, 제가 들어드릴게요.",
        "emotion": "슬픔",
        "emotion_score": 68.0
    },
    {
        "question": "우리 어릴 때 기억나?",
        "answer": "네, 할머니! 그때 정말 좋았죠. 제가 할머니 손을 잡고 다니던 거 기억나요?",
        "emotion": "기쁨",
        "emotion_score": 78.0
    }
]

ACTIVITY_QA = [
    {
        "question": "산책 가자",
        "answer": "좋은 생각이에요! 밖에 나가서 신선한 공기를 마시고 올까요?",
        "emotion": "기쁨",
        "emotion_score": 82.0
    },
    {
        "question": "TV 봐도 되?",
        "answer": "물론이죠! 할머니가 좋아하는 프로그램 틀어드릴까요?",
        "emotion": "중립",
        "emotion_score": 75.0
    },
    {
        "question": "음악 듣고 싶어",
        "answer": "음악이 좋으세요? 할머니가 좋아하는 노래 틀어드릴게요.",
        "emotion": "기쁨",
        "emotion_score": 80.0
    },
    {
        "question": "책 읽어줄래?",
        "answer": "물론이죠! 할머니가 좋아하는 책이 있으세요? 읽어드릴게요.",
        "emotion": "기쁨",
        "emotion_score": 78.0
    },
    {
        "question": "손톱 깎아줄래?",
        "answer": "네, 할머니! 손톱 깎아드릴게요. 편하게 앉으세요.",
        "emotion": "중립",
        "emotion_score": 73.0
    }
]

SAFETY_QA = [
    {
        "question": "문 잠갔어?",
        "answer": "네, 할머니! 문을 다 잠갔어요. 안심하셔도 돼요.",
        "emotion": "중립",
        "emotion_score": 75.0
    },
    {
        "question": "화재경보기 있어?",
        "answer": "네, 할머니. 화재경보기가 설치되어 있어요. 안전해요.",
        "emotion": "중립",
        "emotion_score": 74.0
    },
    {
        "question": "낙상 조심해",
        "answer": "네, 할머니. 조심하겠어요. 할머니도 조심하세요. 손잡이 잡고 다니세요.",
        "emotion": "중립",
        "emotion_score": 72.0
    },
    {
        "question": "비상벨 어디 있어?",
        "answer": "침대 옆에 있어요. 필요할 때 누르시면 바로 도움을 드릴게요.",
        "emotion": "중립",
        "emotion_score": 73.0
    }
]

TIME_QA = [
    {
        "question": "지금 몇 시야?",
        "answer": "지금 오후 2시예요. 약을 드실 시간이 다 되었어요.",
        "emotion": "중립",
        "emotion_score": 72.0
    },
    {
        "question": "내일 뭐하는 날이야?",
        "answer": "내일은 병원 가는 날이에요. 오전 10시에 출발하세요.",
        "emotion": "기쁨",
        "emotion_score": 35.0
    },
    {
        "question": "언제 아들 와?",
        "answer": "아드님은 저녁 6시쯤 들어올 거예요. 조금만 기다려주세요.",
        "emotion": "중립",
        "emotion_score": 73.0
    },
    {
        "question": "금요일이 언제야?",
        "answer": "금요일은 내일 모레예요. 무슨 계획이 있으세요?",
        "emotion": "중립",
        "emotion_score": 71.0
    }
]

# 전체 통합
ALL_QA_DATASET = (
    GREETING_QA + 
    MEDICINE_QA + 
    FOOD_QA + 
    HEALTH_QA + 
    EMOTION_QA + 
    WEATHER_QA + 
    FAMILY_QA + 
    ACTIVITY_QA + 
    SAFETY_QA + 
    TIME_QA
)


# ============================================================
# 개선된 매칭 함수
# ============================================================

def find_matching_qa(user_question):
    """
    사용자 질문과 유사한 Q&A 찾기 (3단계 매칭)
    
    1단계: 정확한 일치 (완벽 매칭)
    2단계: 부분 일치 (포함 관계)
    3단계: 키워드 일치 (단어 기반)
    
    Args:
        user_question: 사용자의 질문 문자열
    
    Returns:
        가장 유사한 Q&A 쌍 또는 None
    """
    user_q_lower = user_question.lower().strip()
    
    # ========== 1단계: 정확한 일치 ==========
    for qa in ALL_QA_DATASET:
        qa_q_lower = qa['question'].lower().strip()
        if user_q_lower == qa_q_lower:
            return qa  # 완벽 매칭!
    
    # ========== 2단계: 부분 일치 ==========
    for qa in ALL_QA_DATASET:
        qa_q_lower = qa['question'].lower().strip()
        
        # 패턴 1: 사용자 질문이 Q&A에 포함
        if user_q_lower in qa_q_lower:
            return qa
        
        # 패턴 2: Q&A 질문이 사용자 질문에 포함
        if qa_q_lower in user_q_lower:
            return qa
    
    # ========== 3단계: 키워드 일치 ==========
    user_words = set([w for w in user_q_lower.replace('?', '').split() if len(w) >= 2])
    
    best_match = None
    best_score = 0
    
    for qa in ALL_QA_DATASET:
        qa_q_lower = qa['question'].lower().strip()
        qa_words = set([w for w in qa_q_lower.replace('?', '').split() if len(w) >= 2])
        
        # 공통 단어 개수
        common = len(user_words & qa_words)
        
        if common > best_score:
            best_score = common
            best_match = qa
    
    if best_score >= 1:  # 최소 1개 이상 공통 단어
        return best_match
    
    return None  # 매칭 실패


def get_qa_by_category(category):
    """카테고리별 Q&A 반환"""
    category_map = {
        'greeting': GREETING_QA,
        'medicine': MEDICINE_QA,
        'food': FOOD_QA,
        'health': HEALTH_QA,
        'emotion': EMOTION_QA,
        'weather': WEATHER_QA,
        'family': FAMILY_QA,
        'activity': ACTIVITY_QA,
        'safety': SAFETY_QA,
        'time': TIME_QA
    }
    return category_map.get(category, [])


def print_qa_statistics():
    """Q&A 데이터셋 통계 출력"""
    print("\n" + "="*60)
    print("📊 Q&A 데이터셋 통계")
    print("="*60)
    
    print(f"\n총 Q&A 쌍: {len(ALL_QA_DATASET)}개")
    
    categories = {
        'Greeting': GREETING_QA,
        'Medicine': MEDICINE_QA,
        'Food': FOOD_QA,
        'Health': HEALTH_QA,
        'Emotion': EMOTION_QA,
        'Weather': WEATHER_QA,
        'Family': FAMILY_QA,
        'Activity': ACTIVITY_QA,
        'Safety': SAFETY_QA,
        'Time': TIME_QA
    }
    
    print("\n[카테고리별 개수]")
    for cat_name, qa_list in categories.items():
        print(f"  {cat_name:15s}: {len(qa_list):2d}개")
    
    # 감정 분포
    emotion_count = {}
    for qa in ALL_QA_DATASET:
        emotion = qa['emotion']
        emotion_count[emotion] = emotion_count.get(emotion, 0) + 1
    
    print("\n[감정 분포]")
    for emotion, count in sorted(emotion_count.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(ALL_QA_DATASET)) * 100
        print(f"  {emotion:8s}: {count:2d}개 ({percentage:5.1f}%)")
    
    avg_emotion_score = sum(qa['emotion_score'] for qa in ALL_QA_DATASET) / len(ALL_QA_DATASET)
    print(f"\n평균 감정 점수: {avg_emotion_score:.1f}점")
    print("="*60)


# ========== 테스트 ==========
if __name__ == "__main__":
    print_qa_statistics()
    
    # 테스트 질문
    test_questions = [
        "약 복용 시간 알려줘",
        "약 언제 먹어?",
        "배고워",
        "뭐 먹을거 없어",
        "머리 아파",
        "산책 가자"
    ]
    
    print("\n" + "="*60)
    print("🧪 매칭 테스트")
    print("="*60)
    
    for q in test_questions:
        qa = find_matching_qa(q)
        if qa:
            print(f"\n✅ Q: {q}")
            print(f"   A: {qa['answer']}")
        else:
            print(f"\n❌ Q: {q}")
            print(f"   매칭 실패")
