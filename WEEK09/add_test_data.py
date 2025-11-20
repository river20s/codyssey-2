from datetime import datetime
from database import SessionLocal
from models import Question


def add_test_questions():
    db = SessionLocal()

    try:
        # 기존 데이터 확인
        existing_count = db.query(Question).count()
        print(f'현재 데이터베이스에 {existing_count}개의 질문이 있습니다.')

        # 테스트 질문 데이터 생성
        test_questions = [
            {
                'subject': '화성에서의 첫 번째 질문',
                'content': '화성에서 살아남기 위해 가장 중요한 것은 무엇일까요?',
                'create_date': datetime.now()
            },
            {
                'subject': '물 재활용 시스템',
                'content': '물 재활용 시스템이 고장났을 때 어떻게 대처해야 하나요?',
                'create_date': datetime.now()
            },
            {
                'subject': '지구와의 통신',
                'content': '지구와 통신이 끊겼을 때 비상 연락 방법은 무엇인가요?',
                'create_date': datetime.now()
            },
            {
                'subject': '식량 재배',
                'content': '화성 토양에서 감자를 재배할 수 있을까요?',
                'create_date': datetime.now()
            },
            {
                'subject': '구조 계획',
                'content': '구조선이 도착하기까지 얼마나 기다려야 하나요?',
                'create_date': datetime.now()
            }
        ]

        # 데이터베이스에 추가
        for question_data in test_questions:
            question = Question(
                subject=question_data['subject'],
                content=question_data['content'],
                create_date=question_data['create_date']
            )
            db.add(question)

        # 변경사항 커밋
        db.commit()

        # 추가된 데이터 확인
        new_count = db.query(Question).count()
        print(f'\n{new_count - existing_count}개의 테스트 질문이 추가되었습니다.')
        print(f'총 {new_count}개의 질문이 데이터베이스에 저장되어 있습니다.\n')

        # 추가된 질문 목록 출력
        print('=== 저장된 질문 목록 ===')
        questions = db.query(Question).order_by(Question.create_date.desc()).all()
        for idx, q in enumerate(questions, 1):
            print(f'{idx}. [{q.id}] {q.subject}')
            print(f'   내용: {q.content}')
            print(f'   작성일: {q.create_date}')
            print()

    except Exception as e:
        print(f'오류 발생: {e}')
        db.rollback()

    finally:
        db.close()


if __name__ == '__main__':
    print('=== 화성 게시판 테스트 데이터 추가 ===\n')
    add_test_questions()
    print('작업이 완료되었습니다.')
