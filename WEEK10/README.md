# WEEK10 - FastAPI ORM 기반 질문 게시판 API

## 프로젝트 개요
SQLAlchemy ORM을 사용하여 질문 게시판 API를 구현한 프로젝트입니다.

## 디렉토리 구조
```
WEEK10/
├── main.py                # FastAPI 메인 애플리케이션
├── database.py            # 데이터베이스 연결 설정
├── models.py              # SQLAlchemy ORM 모델
├── init_db.py             # 데이터베이스 초기화 스크립트
├── board.db               # SQLite 데이터베이스 파일
├── domain/
│   └── question/
│       ├── __init__.py
│       └── question_router.py  # 질문 관련 라우터
└── frontend/
```

## 주요 기능
- **ORM 기반 데이터베이스 접근**: SQLAlchemy를 사용한 객체 관계 매핑
- **질문 목록 조회 API**: GET `/api/question/list`
- **자동 문서화**: FastAPI의 자동 문서 생성 기능

## 실행 방법

### 1. 데이터베이스 초기화
```bash
python init_db.py
```

### 2. 서버 실행
```bash
python -m uvicorn main:app --reload
```

### 3. API 문서 확인
브라우저에서 다음 주소로 접속:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

### 질문 목록 조회
- **URL**: `/api/question/list`
- **Method**: GET
- **설명**: 생성일 기준 내림차순으로 질문 목록을 반환합니다.
- **응답 예시**:
```json
[
  {
    "id": 1,
    "subject": "화성 기지 통신 시스템 점검",
    "content": "지구와의 통신이 불안정합니다. 점검이 필요합니다.",
    "create_date": "2025-11-27T19:50:59.267755"
  }
]
```

## 기술 스택
- Python 3.x
- FastAPI
- SQLAlchemy
- SQLite

## 특징
- PEP 8 코딩 스타일 준수
- ORM을 통한 데이터베이스 추상화
- APIRouter를 사용한 모듈화된 라우팅
- Dependency Injection을 통한 데이터베이스 세션 관리
