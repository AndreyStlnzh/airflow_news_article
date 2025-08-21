from datetime import datetime
from sqlalchemy import Column, String, DateTime
from ..db_connection import BaseModel

class Article(BaseModel):
    author = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    url = Column(String)
    publishedAt = Column(DateTime, default=datetime.utcnow)
    content = Column(String)
    sentiment = Column(String)
