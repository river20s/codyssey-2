from datetime import datetime
from pydantic import BaseModel, ConfigDict


class Question(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject: str
    content: str
    create_date: datetime
