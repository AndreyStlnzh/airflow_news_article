from sqlalchemy import Column, String, Integer
from ..db_connection import BaseModel


class WordStat(BaseModel):
    word = Column(String)
    count = Column(Integer)
