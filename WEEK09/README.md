# WEEK09 프로젝트 구조
```
WEEK09/
├── main.py                 # FastAPI 애플리케이션 진입점
├── database.py            # 데이터베이스 설정
├── models.py              # SQLAlchemy 모델 정의
├── alembic.ini            # Alembic 설정 파일
├── board.db               # SQLite 데이터베이스 파일
├── alembic/               # Alembic 마이그레이션 디렉터리
│   ├── versions/          # 마이그레이션 버전 파일
│   └── env.py            # Alembic 환경 설정
├── domain/
│   └── question/
│       ├── __init__.py
│       └── question_router.py  # 질문 관련 API 라우터
└── frontend/              # 프론트엔드 디렉터리 (예정)
```

## 기술 스택
- Python 3.x
- FastAPI: 웹 프레임워크
- SQLAlchemy: ORM (Object Relational Mapping)
- Alembic: 데이터베이스 마이그레이션 도구
- SQLite: 데이터베이스
- Uvicorn: ASGI 서버

## 데이터베이스 모델

### Question 테이블
- `id`: 질문 데이터의 고유번호 (primary key)
- `subject`: 질문 제목
- `content`: 질문 내용
- `create_date`: 질문 작성일시

## 설치 및 실행

### 1. 필요한 패키지 설치
```bash
pip install fastapi sqlalchemy alembic uvicorn
```

### 2. 데이터베이스 마이그레이션
```bash
# 마이그레이션 파일 생성
alembic revision --autogenerate -m "create question table"

# 마이그레이션 실행
alembic upgrade head
```

### 3. 서버 실행
```bash
uvicorn main:app --reload
```

### 4. API 테스트
- 메인 페이지: http://localhost:8000/
- 질문 목록: http://localhost:8000/api/question/list
- API 문서: http://localhost:8000/docs

## API 엔드포인트

### GET /
- 메인 페이지
- 응답: `{"message": "Welcome to Mars Board"}`

### GET /api/question/list
- 질문 목록 조회
- 응답: 질문 목록 (생성일시 내림차순)

## 데이터베이스 확인 방법

### Python으로 확인
```python
import sqlite3

conn = sqlite3.connect('board.db')
cursor = conn.cursor()

# 테이블 목록 확인
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())

# question 테이블 구조 확인
cursor.execute('PRAGMA table_info(question);')
print(cursor.fetchall())

conn.close()
```

### DB Browser for SQLite 사용 (보너스 과제)
- [x] DB Browser for SQLite 다운로드 및 설치
- [x] board.db 파일 열기
<img width="1298" height="827" alt="image" src="https://github.com/user-attachments/assets/285b150e-ae7b-4a37-b363-1387a1b35f93" />
- [x] question 테이블 확인
<img width="1298" height="827" alt="image" src="https://github.com/user-attachments/assets/5fdcc2c8-440d-4bb4-ad1a-b32d4e45b793" />



