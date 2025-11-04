"""
실행 방법:
1. 가상환경 활성화: .\venv\Scripts\activate
2. 서버 실행: uvicorn main:app --host 0.0.0.0 --port 8000
   또는: python main.py
3. API 문서 확인:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
"""

from fastapi import FastAPI
import todo


# FastAPI 애플리케이션 인스턴스 생성
# title: API 문서에 표시될 제목
# version: API 버전 정보
app = FastAPI(title='Todo API', version='1.0.0')

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
        dict: 환영 메시지
    '''
    return {'message': 'Todo API에 오신 것을 환영합니다!'}


if __name__ == '__main__':
    # 이 파일을 직접 실행할 때만 실행되는 코드
    # python main.py 명령으로 서버를 시작할 수 있습니다.
    import uvicorn

    # uvicorn 서버 실행
    # host='0.0.0.0': 모든 네트워크 인터페이스에서 접속 가능
    # port=8000: 8000번 포트 사용
    uvicorn.run(app, host='0.0.0.0', port=8000)
