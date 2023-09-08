from sqlalchemy import ForeignKey, Column, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer)
    username = Column(String)

    leetcode = relationship("LeetCode", back_populates="user")


class LeetCode(Base):
    __tablename__ = "leetcode"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    total_solved = Column(Integer)
    hard_solved = Column(Integer)
    easy_solved = Column(Integer)
    medium_solved = Column(Integer)
    rating = Column(Integer)

    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="leetcode")
