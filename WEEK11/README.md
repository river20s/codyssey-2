# WEEK11 - contextlib를 사용한 의존성 주입
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

