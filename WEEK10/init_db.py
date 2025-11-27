from datetime import datetime
from database import engine, SessionLocal
from models import Base, Question


def init_database():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        question1 = Question(
            subject='화성 기지 통신 시스템 점검',
            content='지구와의 통신이 불안정합니다. 점검이 필요합니다.',
            create_date=datetime.now()
        )
        question2 = Question(
            subject='산소 공급 장치 이상',
            content='3번 구역 산소 공급 장치에서 이상 소리가 들립니다.',
            create_date=datetime.now()
        )
        question3 = Question(
            subject='식량 재고 현황 보고',
            content='이번 주 식량 재고를 확인해 주세요.',
            create_date=datetime.now()
        )

        db.add_all([question1, question2, question3])
        db.commit()

        print('데이터베이스 초기화 및 테스트 데이터 추가 완료')

    except Exception as e:
        print(f'오류 발생: {e}')
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    init_database()
