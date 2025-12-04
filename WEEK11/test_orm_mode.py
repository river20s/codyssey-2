from datetime import datetime
from pydantic import BaseModel, ConfigDict
from database import SessionLocal
from models import Question as QuestionModel

# 테스트 1: from_attributes = False
class QuestionWithoutORM(BaseModel):
    model_config = ConfigDict(from_attributes=False)

    id: int
    subject: str
    content: str
    create_date: datetime


# 테스트 2: from_attributes = True
class QuestionWithORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject: str
    content: str
    create_date: datetime


def test_orm_modes():
    db = SessionLocal()
    try:
        # 데이터베이스에서 질문 조회
        question_model = db.query(QuestionModel).first()
        print('=' * 80)
        print('데이터베이스에서 조회한 객체:')
        print(f'타입: {type(question_model)}')
        print(f'내용: {question_model}')
        print(f'id: {question_model.id}')
        print(f'subject: {question_model.subject}')
        print()

        # 테스트 1: from_attributes = False
        print('=' * 80)
        print('테스트 1: from_attributes = False')
        print('-' * 80)
        try:
            question_without_orm = QuestionWithoutORM.model_validate(question_model)
            print(f'성공! 결과: {question_without_orm}')
        except Exception as e:
            print(f'실패! 에러: {type(e).__name__}: {e}')
        print()

        # from_attributes = False일 때는 딕셔너리로 변환해야 함
        print('딕셔너리로 변환 후 시도:')
        try:
            question_dict = {
                'id': question_model.id,
                'subject': question_model.subject,
                'content': question_model.content,
                'create_date': question_model.create_date
            }
            question_without_orm = QuestionWithoutORM.model_validate(question_dict)
            print(f'성공! 결과: {question_without_orm}')
        except Exception as e:
            print(f'실패! 에러: {type(e).__name__}: {e}')
        print()

        # 테스트 2: from_attributes = True
        print('=' * 80)
        print('테스트 2: from_attributes = True')
        print('-' * 80)
        try:
            question_with_orm = QuestionWithORM.model_validate(question_model)
            print(f'성공! 결과: {question_with_orm}')
        except Exception as e:
            print(f'실패! 에러: {type(e).__name__}: {e}')
        print()

        # 딕셔너리로도 동작하는지 확인
        print('딕셔너리로 변환 후 시도:')
        try:
            question_dict = {
                'id': question_model.id,
                'subject': question_model.subject,
                'content': question_model.content,
                'create_date': question_model.create_date
            }
            question_with_orm = QuestionWithORM.model_validate(question_dict)
            print(f'성공! 결과: {question_with_orm}')
        except Exception as e:
            print(f'실패! 에러: {type(e).__name__}: {e}')
        print()

        print('=' * 80)
        print('결론:')
        print('-' * 80)
        print('from_attributes = False:')
        print('  - ORM 객체를 직접 Pydantic 모델로 변환 불가')
        print('  - 딕셔너리로 변환 후에만 사용 가능')
        print()
        print('from_attributes = True:')
        print('  - ORM 객체를 직접 Pydantic 모델로 변환 가능')
        print('  - 딕셔너리로도 변환 가능 (호환성 유지)')
        print()
        print('FastAPI에서 ORM 모델을 반환할 때는 from_attributes = True가 필수!')
        print('=' * 80)

    finally:
        db.close()


if __name__ == '__main__':
    test_orm_modes()
