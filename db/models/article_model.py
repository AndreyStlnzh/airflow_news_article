from datetime import datetime
from sqlalchemy import Column, String, DateTime, Date, Time
from ..db_connection import BaseModel

class Article(BaseModel):
    author = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    url = Column(String)
    published_at = Column(DateTime, default=datetime.utcnow)
    date = Column(Date)
    time = Column(Time)
    content = Column(String)
    sentiment = Column(String)
