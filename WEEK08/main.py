'''
WEEK08 - FastAPI를 이용한 TODO API 시스템 (CSV 기반)
main.py: FastAPI 애플리케이션 메인 파일

실행 방법:
1. 필요한 패키지 설치: pip install fastapi uvicorn
2. 서버 실행: uvicorn main:app --host 0.0.0.0 --port 8000
   또는: python main.py
3. API 문서 확인:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

주요 기능:
- CSV 파일을 사용한 데이터 영구 저장
- 완전한 CRUD 작업 지원 (Create, Read, Update, Delete)
- ID 기반 항목 관리
- Pydantic 모델을 사용한 데이터 검증
'''

from fastapi import FastAPI
import todo


# FastAPI 애플리케이션 인스턴스 생성
# title: API 문서에 표시될 제목
# description: API에 대한 설명
# version: API 버전 정보
app = FastAPI(
    title='Todo API (WEEK08)',
    description='CSV 파일 기반 완전한 CRUD Todo API - 화성 탐사 임무 관리',
    version='2.0.0'
)

# todo 라우터를 애플리케이션에 포함
# tags: Swagger UI에서 그룹화할 때 사용되는 태그
app.include_router(todo.router, tags=['Todo'])


@app.get('/')
async def root():
    '''
    루트 엔드포인트 (GET 방식)

    엔드포인트: GET /

    API가 정상적으로 실행 중인지 확인할 수 있는 기본 엔드포인트입니다.
    브라우저에서 http://localhost:8000 으로 접속하면 환영 메시지를 확인할 수 있습니다.

    Returns:
        dict: 환영 메시지 및 API 정보
    '''
    return {
        'message': 'Todo API (WEEK08)에 오신 것을 환영합니다!',
        'version': '2.0.0',
        'description': 'CSV 파일 기반 완전한 CRUD Todo API',
        'features': [
            'POST /add_todo - 새로운 todo 추가',
            'GET /retrieve_todo - 전체 todo 목록 조회',
            'GET /get_single_todo/{id} - 특정 todo 조회',
            'PUT /update_todo/{id} - todo 수정',
            'DELETE /delete_single_todo/{id} - todo 삭제'
        ],
        'docs': {
            'swagger': 'http://localhost:8000/docs',
            'redoc': 'http://localhost:8000/redoc'
        }
    }


if __name__ == '__main__':
    # 이 파일을 직접 실행할 때만 실행되는 코드
    # python main.py 명령으로 서버를 시작할 수 있습니다.
    import uvicorn

    # uvicorn 서버 실행
    # host='0.0.0.0': 모든 네트워크 인터페이스에서 접속 가능
    # port=8000: 8000번 포트 사용
    uvicorn.run(app, host='0.0.0.0', port=8000)
