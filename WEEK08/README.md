# WEEK08 - FastAPI를 이용한 TODO API 시스템 (CSV 기반)

## 개요
CSV 파일을 사용하여 데이터를 영구 저장하는 완전한 CRUD Todo API 시스템입니다.
Pydantic 모델을 사용한 데이터 검증과 ID 기반 항목 관리를 지원합니다.

## 주요 파일
- `main.py`: FastAPI 애플리케이션 메인 파일
- `todo.py`: Todo CRUD 라우터 및 비즈니스 로직
- `model.py`: Pydantic 데이터 모델 정의
- `client.py`: Todo API 클라이언트 애플리케이션 (보너스 과제)
- `todos.csv`: Todo 데이터 저장 파일 (자동 생성)

## 실행 방법

### 1. 필요한 패키지 설치
Requirement already satisfied: fastapi in c:\python38\lib\site-packages (0.121.0)
Collecting uvicorn
  Downloading uvicorn-0.33.0-py3-none-any.whl.metadata (6.6 kB)
Requirement already satisfied: starlette<0.50.0,>=0.40.0 in c:\python38\lib\site-packages (from fastapi) (0.44.0)
Requirement already satisfied: pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,!=2.1.0,<3.0.0,>=1.7.4 in c:\python38\lib\site-packages (from fastapi) (2.10.6)
Requirement already satisfied: typing-extensions>=4.8.0 in c:\python38\lib\site-packages (from fastapi) (4.13.2)
Requirement already satisfied: annotated-doc>=0.0.2 in c:\python38\lib\site-packages (from fastapi) (0.0.3)
Collecting click>=7.0 (from uvicorn)
  Downloading click-8.1.8-py3-none-any.whl.metadata (2.3 kB)
Requirement already satisfied: h11>=0.8 in c:\python38\lib\site-packages (from uvicorn) (0.16.0)
Collecting colorama (from click>=7.0->uvicorn)
  Using cached colorama-0.4.6-py2.py3-none-any.whl.metadata (17 kB)
Requirement already satisfied: annotated-types>=0.6.0 in c:\python38\lib\site-packages (from pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,!=2.1.0,<3.0.0,>=1.7.4->fastapi) (0.7.0)
Requirement already satisfied: pydantic-core==2.27.2 in c:\python38\lib\site-packages (from pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,!=2.1.0,<3.0.0,>=1.7.4->fastapi) (2.27.2)
Requirement already satisfied: anyio<5,>=3.4.0 in c:\python38\lib\site-packages (from starlette<0.50.0,>=0.40.0->fastapi) (4.5.2)
Requirement already satisfied: idna>=2.8 in c:\python38\lib\site-packages (from anyio<5,>=3.4.0->starlette<0.50.0,>=0.40.0->fastapi) (3.11)
Requirement already satisfied: sniffio>=1.1 in c:\python38\lib\site-packages (from anyio<5,>=3.4.0->starlette<0.50.0,>=0.40.0->fastapi) (1.3.1)
Requirement already satisfied: exceptiongroup>=1.0.2 in c:\python38\lib\site-packages (from anyio<5,>=3.4.0->starlette<0.50.0,>=0.40.0->fastapi) (1.3.0)
Downloading uvicorn-0.33.0-py3-none-any.whl (62 kB)
Downloading click-8.1.8-py3-none-any.whl (98 kB)
Using cached colorama-0.4.6-py2.py3-none-any.whl (25 kB)
Installing collected packages: colorama, click, uvicorn
Successfully installed click-8.1.8 colorama-0.4.6 uvicorn-0.33.0

### 2. API 서버 실행


### 3. API 문서 확인
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 4. 클라이언트 앱 실행 (보너스)


## API 엔드포인트

### 1. 루트 엔드포인트
- **GET /**
- API 정보 및 사용 가능한 기능 목록 조회

### 2. Todo 추가
- **POST /add_todo**
- 새로운 todo 항목을 추가합니다.
- 요청 본문 예시:
  

### 3. 전체 Todo 목록 조회
- **GET /retrieve_todo**
- 모든 todo 항목을 조회합니다.

### 4. 개별 Todo 조회
- **GET /get_single_todo/{todo_id}**
- 특정 ID의 todo 항목을 조회합니다.

### 5. Todo 수정
- **PUT /update_todo/{todo_id}**
- 특정 ID의 todo 항목을 수정합니다.
- 요청 본문 예시 (모든 필드는 선택사항):
  

### 6. Todo 삭제
- **DELETE /delete_single_todo/{todo_id}**
- 특정 ID의 todo 항목을 삭제합니다.

## curl을 사용한 테스트 예시

### Todo 추가
Internal Server Error

### 전체 목록 조회
{"todos":[{"id":"1","task":"화성 토양 샘플 분석 완료","priority":"high","completed":true},{"id":"2","task":"우주선 시스템 점검","priority":"medium","completed":false}],"total_count":2}

### 개별 Todo 조회
{"id":"1","task":"화성 토양 샘플 분석 완료","priority":"high","completed":true}

### Todo 수정
Internal Server Error

### Todo 삭제
{"message":"Todo가 성공적으로 삭제되었습니다.","deleted_id":"1","deleted_todo":{"id":"1","task":"화성 토양 샘플 분석 완료","priority":"high","completed":true}}

## 주요 기능
1. **CSV 파일 기반 데이터 저장**: 데이터베이스 없이 CSV 파일로 데이터 영구 저장
2. **완전한 CRUD 작업**: Create, Read, Update, Delete 모두 지원
3. **ID 기반 관리**: 자동 증가하는 ID로 항목 관리
4. **데이터 검증**: Pydantic 모델을 사용한 입력 데이터 검증
5. **에러 처리**: 존재하지 않는 ID 조회 시 404 에러 반환
6. **클라이언트 앱**: Python urllib만 사용한 대화형 CLI 클라이언트 (보너스)

## 클라이언트 앱 사용법 (보너스 과제)
1. API 서버가 실행 중인지 확인
2. `python client.py` 실행
3. 메뉴에서 원하는 작업 선택:
   - 1: 모든 todo 목록 보기
   - 2: 특정 todo 조회
   - 3: 새 todo 추가
   - 4: todo 수정
   - 5: todo 삭제
   - 0: 종료

## 기술 스택
- Python 3.x
- FastAPI: 웹 프레임워크
- Pydantic: 데이터 검증
- CSV: 데이터 저장
- urllib: HTTP 클라이언트 (client.py)

## 코딩 스타일
- PEP 8 가이드 준수
- 작은따옴표(') 우선 사용
- 함수명: snake_case
- 클래스명: CapWords
- 들여쓰기: 공백 4칸
