from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Question as QuestionModel
from domain.question.question_schema import Question
from typing import List

router = APIRouter(
    prefix='/api/question',
)


@router.get('/list', response_model=List[Question])
def question_list(db: Session = Depends(get_db)):
    questions = db.query(QuestionModel).order_by(QuestionModel.create_date.desc()).all()
    return questions
