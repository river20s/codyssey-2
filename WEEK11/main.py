from fastapi import FastAPI
from domain.question import question_router

app = FastAPI()

app.include_router(question_router.router)


@app.get('/')
def root():
    return {'message': 'Welcome to Mars Board'}
