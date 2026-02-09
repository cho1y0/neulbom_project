"""
Q&A 더미 데이터 사용 예제
시스템이 원하는 형태의 정답을 받는 방법
"""

from qa_dataset_improved import (
    find_matching_qa, 
    get_qa_by_category,
    ALL_QA_DATASET,
    print_qa_statistics
)


def example_1_basic_matching():
    """예제 1: 기본 질문 매칭"""
    print("\n" + "="*70)
    print("📖 예제 1: 기본 질문 매칭")
    print("="*70)
    
    test_cases = [
        "오늘 먹어야 할 약 복용 시간 알려줘",
        "배고워",
        "머리 아파",
        "좋은 일이 있었어"
    ]
    
    for question in test_cases:
        print(f"\n👵 할머니: {question}")
        
        # 매칭
        qa = find_matching_qa(question)
        
        if qa:
            print(f"🤖 보미: {qa['answer']}")
            print(f"   감정: {qa['emotion']} (점수: {qa['emotion_score']:.1f})")
        else:
            print(f"🤖 보미: [답변 없음 - LLM 사용 필요]")


def example_2_category_based():
    """예제 2: 카테고리별 Q&A 확인"""
    print("\n" + "="*70)
    print("📖 예제 2: 카테고리별 Q&A")
    print("="*70)
    
    categories = ['medicine', 'food', 'health', 'emotion', 'activity']
    
    for category in categories:
        qa_list = get_qa_by_category(category)
        print(f"\n【 {category.upper()} - {len(qa_list)}개 】")
        
        # 첫 2개만 출력
        for i, qa in enumerate(qa_list[:2], 1):
            print(f"  {i}. Q: {qa['question']}")
            print(f"     A: {qa['answer']}")
            if i < len(qa_list):
                print()


def example_3_integration_with_analyzer():
    """예제 3: analyzer.py와 통합"""
    print("\n" + "="*70)
    print("📖 예제 3: Analyzer와의 통합")
    print("="*70)
    
    # 모의 음성 분석 결과
    mock_analysis_result = {
        'features': {
            'whisper': {
                'text': '약 복용 시간 알려줘',
                'word_count': 5,
                'wpm': 120.5,
                'duration': 2.5
            },
            'emotion': {
                'final_emotion': '중립',
                'audio_conf': 0.85,
                'z_peak': 0.45
            }
        },
        'scores': {
            'average': 75.5,
            'emotion': 75.0
        }
    }
    
    user_text = mock_analysis_result['features']['whisper']['text']
    emotion = mock_analysis_result['features']['emotion']
    scores = mock_analysis_result['scores']
    
    print(f"\n📊 음성 분석 결과:")
    print(f"   텍스트: {user_text}")
    print(f"   감정: {emotion['final_emotion']} (확신도: {emotion['audio_conf']:.2f})")
    print(f"   종합 점수: {scores['average']:.1f}점")
    
    # Q&A 매칭
    qa = find_matching_qa(user_text)
    
    if qa:
        print(f"\n✅ Q&A 매칭 성공!")
        print(f"   답변: {qa['answer']}")
        print(f"   감정 태그: {qa['emotion']}")
        print(f"   감정 점수: {qa['emotion_score']:.1f}점")
    else:
        print(f"\n❌ Q&A 매칭 실패 - LLM API 호출 필요")


def example_4_create_custom_qa():
    """예제 4: 커스텀 Q&A 추가"""
    print("\n" + "="*70)
    print("📖 예제 4: 커스텀 Q&A 추가")
    print("="*70)
    
    # 새로운 Q&A 추가
    custom_qa = {
        "question": "손주 봤어?",
        "answer": "네, 할머니! 어제 손주가 놀러 왔어요. 숙제 도와주고 갔어요.",
        "emotion": "기쁨",
        "emotion_score": 82.0
    }
    
    print(f"\n📝 새로운 Q&A 추가:")
    print(f"   질문: {custom_qa['question']}")
    print(f"   답변: {custom_qa['answer']}")
    print(f"   감정: {custom_qa['emotion']} ({custom_qa['emotion_score']:.1f}점)")
    
    # 데이터셋에 추가
    ALL_QA_DATASET.append(custom_qa)
    
    print(f"\n✅ 데이터셋에 추가됨! (총 {len(ALL_QA_DATASET)}개)")
    
    # 매칭 테스트
    test_q = "손주 봤어?"
    matching = find_matching_qa(test_q)
    if matching:
        print(f"\n테스트 매칭:")
        print(f"   질문: {test_q}")
        print(f"   답변: {matching['answer']}")


def example_5_batch_test():
    """예제 5: 배치 테스트"""
    print("\n" + "="*70)
    print("📖 예제 5: 배치 테스트 (모든 Q&A)")
    print("="*70)
    
    print(f"\n총 {len(ALL_QA_DATASET)}개의 Q&A 쌍을 테스트합니다.\n")
    
    success_count = 0
    emotion_distribution = {}
    
    for i, qa in enumerate(ALL_QA_DATASET, 1):
        question = qa['question']
        emotion = qa['emotion']
        
        # 감정 분포 카운팅
        emotion_distribution[emotion] = emotion_distribution.get(emotion, 0) + 1
        
        # 매칭 테스트
        matched = find_matching_qa(question)
        if matched:
            success_count += 1
            status = "✅"
        else:
            status = "❌"
        
        if i % 5 == 0:
            print(f"[{i:2d}/{len(ALL_QA_DATASET)}] {status} {question[:30]:30s} ({emotion})")
    
    # 결과 요약
    print(f"\n\n📊 테스트 결과:")
    print(f"   성공: {success_count}/{len(ALL_QA_DATASET)}")
    print(f"   성공률: {(success_count/len(ALL_QA_DATASET))*100:.1f}%")
    
    print(f"\n[감정 분포]")
    for emotion, count in sorted(emotion_distribution.items(), key=lambda x: x[1], reverse=True):
        print(f"   {emotion:8s}: {count:2d}개")


def example_6_export_to_json():
    """예제 6: JSON으로 내보내기"""
    import json
    
    print("\n" + "="*70)
    print("📖 예제 6: JSON 내보내기")
    print("="*70)
    
    # JSON 형식으로 변환
    json_data = {
        "metadata": {
            "total_qa_pairs": len(ALL_QA_DATASET),
            "categories": 10,
            "version": "1.0"
        },
        "qa_pairs": ALL_QA_DATASET
    }
    
    # 파일로 저장
    output_file = "qa_dataset.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ JSON 파일 생성: {output_file}")
    print(f"   파일 크기: {len(json.dumps(json_data, ensure_ascii=False))} bytes")
    print(f"\n💾 저장 위치: ./{output_file}")


def example_7_similarity_search():
    """예제 7: 유사도 기반 검색"""
    print("\n" + "="*70)
    print("📖 예제 7: 유사도 기반 검색")
    print("="*70)
    
    def simple_similarity(s1, s2):
        """간단한 유사도 계산 (공통 단어 기반)"""
        words1 = set(s1.lower().split())
        words2 = set(s2.lower().split())
        
        if not words1 or not words2:
            return 0
        
        common = len(words1 & words2)
        total = len(words1 | words2)
        return common / total if total > 0 else 0
    
    test_question = "약 언제 먹어"
    
    print(f"\n질문: {test_question}")
    print(f"\n유사도가 높은 Q&A TOP 3:")
    print("-" * 70)
    
    # 유사도 계산
    similarities = []
    for qa in ALL_QA_DATASET:
        sim = simple_similarity(test_question, qa['question'])
        if sim > 0:
            similarities.append((sim, qa))
    
    # 상위 3개 출력
    similarities.sort(reverse=True)
    for rank, (sim, qa) in enumerate(similarities[:3], 1):
        print(f"\n[{rank}] 유사도: {sim:.2%}")
        print(f"    질문: {qa['question']}")
        print(f"    답변: {qa['answer']}")


# ========== 메인 실행 ==========
if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║      🎓 Q&A 더미 데이터 사용 예제                        ║
    ║                                                           ║
    ║      이 예제들은 LLM이 정답을 제공하는 방법을            ║
    ║      보여줍니다.                                         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # 데이터셋 통계
    print_qa_statistics()
    
    # 예제 실행
    examples = [
        ("기본 질문 매칭", example_1_basic_matching),
        ("카테고리별 Q&A", example_2_category_based),
        ("Analyzer와 통합", example_3_integration_with_analyzer),
        ("커스텀 Q&A 추가", example_4_create_custom_qa),
        ("배치 테스트", example_5_batch_test),
        ("JSON 내보내기", example_6_export_to_json),
        ("유사도 검색", example_7_similarity_search)
    ]
    
    for title, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n❌ 예제 실행 중 오류: {e}")
        
        input("\n[Enter를 눌러 다음 예제로...]")
    
    print("\n" + "="*70)
    print("✅ 모든 예제 완료!")
    print("="*70)
