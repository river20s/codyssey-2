'''
WEEK08 - FastAPI를 이용한 TODO API 시스템 (CSV 기반)
todo.py: TODO CRUD 라우터 및 비즈니스 로직

주요 기능:
- TODO 항목 추가 (POST /add_todo)
- 전체 TODO 목록 조회 (GET /retrieve_todo)
- 개별 TODO 조회 (GET /get_single_todo/{id})
- TODO 수정 (PUT /update_todo/{id})
- TODO 삭제 (DELETE /delete_single_todo/{id})

데이터 저장:
- CSV 파일(todos.csv)을 사용하여 데이터 영구 저장
'''

from fastapi import APIRouter, HTTPException
from model import TodoItem
from typing import Dict, List
import csv
import os


# APIRouter 인스턴스 생성
router = APIRouter()

# CSV 파일 경로
CSV_FILE = 'todos.csv'
CSV_HEADERS = ['id', 'task', 'priority', 'completed']


def initialize_csv():
    '''
    CSV 파일이 없으면 헤더와 함께 생성하는 함수
    '''
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()


def read_todos_from_csv() -> List[Dict]:
    '''
    CSV 파일에서 모든 todo 항목을 읽어오는 함수

    Returns:
        List[Dict]: todo 항목 리스트
    '''
    initialize_csv()
    todos = []

    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # completed 필드를 문자열에서 불리언으로 변환
            row['completed'] = row['completed'].lower() == 'true'
            todos.append(row)

    return todos


def write_todos_to_csv(todos: List[Dict]):
    '''
    CSV 파일에 모든 todo 항목을 저장하는 함수

    Args:
        todos (List[Dict]): 저장할 todo 항목 리스트
    '''
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(todos)


def get_next_id() -> str:
    '''
    다음 todo ID를 생성하는 함수

    Returns:
        str: 다음 ID (현재 최대 ID + 1)
    '''
    todos = read_todos_from_csv()
    if not todos:
        return '1'

    max_id = max(int(todo['id']) for todo in todos)
    return str(max_id + 1)


@router.post('/add_todo')
async def add_todo(todo: Dict) -> Dict:
    '''
    새로운 todo 항목을 추가하는 함수 (POST 방식)

    엔드포인트: POST /add_todo
    Content-Type: application/json

    요청 예시:
    {
        "task": "화성 토양 샘플 수집",
        "priority": "high",
        "completed": false
    }

    응답 예시:
    {
        "message": "Todo가 성공적으로 추가되었습니다.",
        "id": "1",
        "todo": {...}
    }

    Args:
        todo (Dict): 추가할 todo 항목

    Returns:
        Dict: 성공 메시지, ID, 추가된 todo 항목

    Raises:
        HTTPException: 빈 Dict가 입력되면 400 에러 발생
    '''
    if not todo:
        raise HTTPException(status_code=400, detail='빈 값은 입력할 수 없습니다.')

    # task 필드는 필수
    if 'task' not in todo or not todo['task']:
        raise HTTPException(status_code=400, detail='task 필드는 필수입니다.')

    # 새 ID 생성
    new_id = get_next_id()

    # 기본값 설정
    new_todo = {
        'id': new_id,
        'task': todo.get('task', ''),
        'priority': todo.get('priority', 'medium'),
        'completed': todo.get('completed', False)
    }

    # CSV에서 기존 데이터 읽기
    todos = read_todos_from_csv()

    # 새 항목 추가
    todos.append(new_todo)

    # CSV에 저장
    write_todos_to_csv(todos)

    return {
        'message': 'Todo가 성공적으로 추가되었습니다.',
        'id': new_id,
        'todo': new_todo
    }


@router.get('/retrieve_todo')
async def retrieve_todo() -> Dict:
    '''
    모든 todo 항목을 조회하는 함수 (GET 방식)

    엔드포인트: GET /retrieve_todo

    응답 예시:
    {
        "todos": [
            {"id": "1", "task": "화성 토양 샘플 수집", "priority": "high", "completed": false},
            {"id": "2", "task": "우주선 점검", "priority": "medium", "completed": true}
        ],
        "total_count": 2
    }

    Returns:
        Dict: 전체 todo 리스트와 총 개수
    '''
    todos = read_todos_from_csv()

    return {
        'todos': todos,
        'total_count': len(todos)
    }


@router.get('/get_single_todo/{todo_id}')
async def get_single_todo(todo_id: str) -> Dict:
    '''
    특정 ID의 todo 항목을 조회하는 함수 (GET 방식)

    엔드포인트: GET /get_single_todo/{todo_id}

    경로 매개변수:
        todo_id (str): 조회할 todo의 ID

    응답 예시:
    {
        "id": "1",
        "task": "화성 토양 샘플 수집",
        "priority": "high",
        "completed": false
    }

    Returns:
        Dict: 조회된 todo 항목

    Raises:
        HTTPException: 해당 ID의 todo가 없으면 404 에러 발생
    '''
    todos = read_todos_from_csv()

    # ID로 todo 찾기
    for todo in todos:
        if todo['id'] == todo_id:
            return todo

    # 찾지 못한 경우
    raise HTTPException(
        status_code=404,
        detail=f'ID {todo_id}에 해당하는 todo를 찾을 수 없습니다.'
    )


@router.put('/update_todo/{todo_id}')
async def update_todo(todo_id: str, todo_item: TodoItem) -> Dict:
    '''
    특정 ID의 todo 항목을 수정하는 함수 (PUT 방식)

    엔드포인트: PUT /update_todo/{todo_id}
    Content-Type: application/json

    경로 매개변수:
        todo_id (str): 수정할 todo의 ID

    요청 예시 (모든 필드는 선택사항):
    {
        "task": "화성 토양 샘플 분석",
        "priority": "high",
        "completed": true
    }

    응답 예시:
    {
        "message": "Todo가 성공적으로 수정되었습니다.",
        "todo": {
            "id": "1",
            "task": "화성 토양 샘플 분석",
            "priority": "high",
            "completed": true
        }
    }

    Args:
        todo_id (str): 수정할 todo의 ID
        todo_item (TodoItem): 수정할 내용 (Pydantic 모델)

    Returns:
        Dict: 성공 메시지와 수정된 todo 항목

    Raises:
        HTTPException: 해당 ID의 todo가 없으면 404 에러 발생
    '''
    todos = read_todos_from_csv()

    # ID로 todo 찾기
    found = False
    for i, todo in enumerate(todos):
        if todo['id'] == todo_id:
            found = True

            # 필드별로 업데이트 (None이 아닌 값만)
            if todo_item.task is not None:
                todos[i]['task'] = todo_item.task
            if todo_item.priority is not None:
                todos[i]['priority'] = todo_item.priority
            if todo_item.completed is not None:
                todos[i]['completed'] = todo_item.completed

            # CSV에 저장
            write_todos_to_csv(todos)

            return {
                'message': 'Todo가 성공적으로 수정되었습니다.',
                'todo': todos[i]
            }

    # 찾지 못한 경우
    if not found:
        raise HTTPException(
            status_code=404,
            detail=f'ID {todo_id}에 해당하는 todo를 찾을 수 없습니다.'
        )


@router.delete('/delete_single_todo/{todo_id}')
async def delete_single_todo(todo_id: str) -> Dict:
    '''
    특정 ID의 todo 항목을 삭제하는 함수 (DELETE 방식)

    엔드포인트: DELETE /delete_single_todo/{todo_id}

    경로 매개변수:
        todo_id (str): 삭제할 todo의 ID

    응답 예시:
    {
        "message": "Todo가 성공적으로 삭제되었습니다.",
        "deleted_id": "1"
    }

    Args:
        todo_id (str): 삭제할 todo의 ID

    Returns:
        Dict: 성공 메시지와 삭제된 ID

    Raises:
        HTTPException: 해당 ID의 todo가 없으면 404 에러 발생
    '''
    todos = read_todos_from_csv()

    # ID로 todo 찾아서 삭제
    found = False
    for i, todo in enumerate(todos):
        if todo['id'] == todo_id:
            found = True
            deleted_todo = todos.pop(i)

            # CSV에 저장
            write_todos_to_csv(todos)

            return {
                'message': 'Todo가 성공적으로 삭제되었습니다.',
                'deleted_id': todo_id,
                'deleted_todo': deleted_todo
            }

    # 찾지 못한 경우
    if not found:
        raise HTTPException(
            status_code=404,
            detail=f'ID {todo_id}에 해당하는 todo를 찾을 수 없습니다.'
        )
