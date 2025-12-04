# WEEK11 - contextlib를 사용한 의존성 주입

## 문제 설명

데이터베이스 연결을 사용 후 제대로 종료하지 않아 발생하는 문제를 해결하기 위해 `contextlib`를 사용한 의존성 주입(Dependency Injection) 기능을 구현합니다.

## 주요 구현 내용

### 1. database.py - contextlib를 이용한 DB 연결 관리

```python
from contextlib import contextmanager

def get_db():
    db = SessionLocal()
    try:
        print('데이터베이스 연결 시작')
        yield db
    finally:
        print('데이터베이스 연결 종료')
        db.close()
```

- `contextlib`를 import하여 컨텍스트 관리 기능 사용
- `get_db()` 함수는 제너레이터 함수로 구현
- FastAPI의 `Depends`가 자동으로 컨텍스트 관리를 처리
- 연결 시작/종료 메시지로 동작 확인 가능

### 2. question_schema.py - Pydantic 스키마 작성

```python
from pydantic import BaseModel, ConfigDict

class Question(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject: str
    content: str
    create_date: datetime
```

- Pydantic V2 스타일 사용 (`ConfigDict`, `from_attributes`)
- ORM 객체를 직접 Pydantic 모델로 변환 가능

### 3. question_router.py - 스키마 적용

```python
@router.get('/list', response_model=List[Question])
def question_list(db: Session = Depends(get_db)):
    questions = db.query(QuestionModel).order_by(QuestionModel.create_date.desc()).all()
    return questions
```

- `response_model`로 응답 스키마 지정
- `Depends(get_db)`로 의존성 주입
- 요청마다 자동으로 DB 연결/종료

## 실행 방법

### 1. 데이터베이스 초기화

```bash
cd WEEK11
python init_db.py
```

### 2. FastAPI 서버 실행

```bash
python -m uvicorn main:app --reload
```

### 3. API 테스트

```bash
# 루트 엔드포인트
curl http://localhost:8000/

# 질문 목록 조회
curl http://localhost:8000/api/question/list
```

## 보너스 과제 - from_attributes 비교

### 테스트 실행

```bash
python test_orm_mode.py
```

### 결과 분석

#### from_attributes = False

- ORM 객체를 직접 Pydantic 모델로 변환 불가
- 딕셔너리로 변환 후에만 사용 가능
- 에러 발생: `ValidationError: Input should be a valid dictionary`

#### from_attributes = True (권장)

- ORM 객체를 직접 Pydantic 모델로 변환 가능
- 딕셔너리로도 변환 가능 (호환성 유지)
- FastAPI에서 ORM 모델을 반환할 때 필수 설정

### 왜 이런 결과가 나올까?

Pydantic은 기본적으로 딕셔너리나 JSON 형태의 데이터를 검증하도록 설계되었습니다.

- `from_attributes = False` (기본값): Pydantic은 입력을 딕셔너리로 예상하고, 객체의 속성(attributes)을 읽을 수 없습니다.
- `from_attributes = True`: Pydantic이 객체의 속성을 직접 읽어올 수 있도록 허용합니다. SQLAlchemy ORM 모델 같은 객체를 직접 변환할 수 있게 됩니다.

FastAPI에서 데이터베이스 모델을 직접 반환할 때는 반드시 `from_attributes = True`를 설정해야 합니다.

## 프로젝트 구조

```
WEEK11/
├── database.py              # DB 연결 설정 (contextlib 사용)
├── models.py                # SQLAlchemy ORM 모델
├── main.py                  # FastAPI 애플리케이션
├── init_db.py               # DB 초기화 스크립트
├── test_orm_mode.py         # 보너스 과제 테스트
├── domain/
│   └── question/
│       ├── __init__.py
│       ├── question_router.py    # 질문 API 라우터
│       └── question_schema.py    # Pydantic 스키마
└── board.db                 # SQLite 데이터베이스
```

## 학습 포인트

1. **의존성 주입 (Dependency Injection)**
   - FastAPI의 `Depends`를 통한 자동 의존성 관리
   - 리소스의 생성과 정리를 자동화

2. **컨텍스트 관리 (Context Manager)**
   - `contextlib`를 통한 리소스 관리
   - try-finally 패턴의 자동화

3. **Pydantic 스키마**
   - API 응답의 명확한 타입 정의
   - ORM 모델과 API 응답 분리
   - `from_attributes`의 중요성

4. **자동 연결 관리**
   - 매 요청마다 DB 연결 생성/종료
   - 메모리 누수 방지
   - 안정적인 리소스 관리
