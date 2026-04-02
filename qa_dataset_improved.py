"""
Q&A 더미 데이터셋 (개선된 매칭 로직)
할머니의 질문에 정확한 답변 제공
"""

import json
import os

# JSON 파일 경로 설정 (data 폴더 내)
DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'qa_data.json')

def load_qa_dataset():
    """JSON 파일에서 Q&A 데이터셋을 로드합니다."""
    if not os.path.exists(DATA_FILE_PATH):
        print(f"⚠️ 경고: Q&A 데이터 파일을 찾을 수 없습니다. ({DATA_FILE_PATH})")
        return {}, []
        
    try:
        with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        all_qa = []
        for category, qa_list in raw_data.items():
            all_qa.extend(qa_list)
            
        return raw_data, all_qa
    except Exception as e:
        print(f"❌ Q&A 데이터 로드 중 오류 발생: {e}")
        return {}, []

# 데이터 로드 및 전역 변수 초기화
RAW_QA_DATA, ALL_QA_DATASET = load_qa_dataset()

# 하위 호환성을 위한 카테고리별 변수 매핑
GREETING_QA = RAW_QA_DATA.get('greeting', [])
MEDICINE_QA = RAW_QA_DATA.get('medicine', [])
FOOD_QA = RAW_QA_DATA.get('food', [])
HEALTH_QA = RAW_QA_DATA.get('health', [])
EMOTION_QA = RAW_QA_DATA.get('emotion', [])
WEATHER_QA = RAW_QA_DATA.get('weather', [])
FAMILY_QA = RAW_QA_DATA.get('family', [])
ACTIVITY_QA = RAW_QA_DATA.get('activity', [])
SAFETY_QA = RAW_QA_DATA.get('safety', [])
TIME_QA = RAW_QA_DATA.get('time', [])


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
