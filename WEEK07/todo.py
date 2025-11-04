"""
WEEK07 - FastAPI를 이용한 TODO API 시스템
todo.py: TODO 라우터 및 비즈니스 로직

주요 기능:
- TODO 항목 추가 (POST /add_todo)
- TODO 목록 조회 (GET /retrieve_todo)
- 빈 값 입력 검증 (보너스 과제)

사용 방법:
1. 가상환경 활성화: .\venv\Scripts\activate (Windows)
2. 서버 실행: uvicorn main:app --host 0.0.0.0 --port 8000
3. API 문서: http://localhost:8000/docs (Swagger UI)
"""

from fastapi import APIRouter, HTTPException
from typing import Dict


# APIRouter 인스턴스 생성
# FastAPI에서 라우팅을 모듈화하기 위해 사용
router = APIRouter()

# todo 리스트 저장소
# 데이터베이스 대신 메모리에 저장 (서버 재시작 시 초기화됨)
todo_list = []


@router.post('/add_todo')
async def add_todo(todo: Dict) -> Dict:
    '''
    새로운 todo 항목을 추가하는 함수 (POST 방식)

    엔드포인트: POST /add_todo
    Content-Type: application/json

    요청 예시:
    {
        "task": "지구와 통신하기",
        "priority": "high"
    }

    응답 예시:
    {
        "message": "Todo가 성공적으로 추가되었습니다.",
        "todo": {"task": "지구와 통신하기", "priority": "high"},
        "total_count": 1
    }

    테스트 방법:
    - Swagger UI: http://localhost:8000/docs
    - curl: curl -X POST http://localhost:8000/add_todo -H "Content-Type: application/json" --data @test_todo1.json

    Args:
        todo (Dict): 추가할 todo 항목 (JSON 형식)

    Returns:
        Dict: 성공 메시지, 추가된 todo 항목, 전체 개수

    Raises:
        HTTPException: 빈 Dict가 입력되면 400 에러 발생 (보너스 과제)
    '''
    # 보너스 과제: 빈 Dict 검증
    # 빈 객체 {}가 입력되면 HTTP 400 에러와 함께 경고 메시지 반환
    if not todo:
        raise HTTPException(status_code=400, detail='빈 값은 입력할 수 없습니다.')

    # todo_list에 새 항목 추가
    todo_list.append(todo)

    # 성공 응답 반환
    return {
        'message': 'Todo가 성공적으로 추가되었습니다.',
        'todo': todo,
        'total_count': len(todo_list)
    }


@router.get('/retrieve_todo')
async def retrieve_todo() -> Dict:
    '''
    모든 todo 항목을 가져오는 함수 (GET 방식)

    엔드포인트: GET /retrieve_todo

    응답 예시:
    {
        "todos": [
            {"task": "지구와 통신하기", "priority": "high"},
            {"task": "우주선 점검하기", "priority": "medium", "completed": false}
        ],
        "total_count": 2
    }

    테스트 방법:
    - 브라우저: http://localhost:8000/retrieve_todo
    - Swagger UI: http://localhost:8000/docs
    - curl: curl -X GET http://localhost:8000/retrieve_todo

    Returns:
        Dict: 전체 todo 리스트와 총 개수
    '''
    # 현재 저장된 모든 todo 항목과 개수를 반환
    return {
        'todos': todo_list,
        'total_count': len(todo_list)
    }
