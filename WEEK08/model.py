'''
WEEK08 - FastAPI를 이용한 TODO API 시스템
model.py: 데이터 모델 정의

주요 모델:
- TodoItem: Todo 항목 수정을 위한 Pydantic 모델
'''

from pydantic import BaseModel
from typing import Optional


class TodoItem(BaseModel):
    '''
    Todo 항목 수정을 위한 데이터 모델

    Attributes:
        task (Optional[str]): Todo 작업 내용
        priority (Optional[str]): 우선순위 (예: 'high', 'medium', 'low')
        completed (Optional[bool]): 완료 여부

    사용 예시:
    {
        "task": "화성 탐사 일지 작성",
        "priority": "medium",
        "completed": false
    }
    '''
    task: Optional[str] = None
    priority: Optional[str] = None
    completed: Optional[bool] = None
