from sqlalchemy.orm import Session, relationship
from sqlalchemy import desc
from .models import LeetCode, User


class Repository:
    @staticmethod
    def get_user_by_tg_id(db: Session, tg_id: int):
        return db.query(User).filter(User.telegram_id == tg_id).first()

    def create_user(self, db: Session, tg_id: int, username: str):
        user = self.get_user_by_tg_id(db, tg_id)
        if user is None:
            db_user = User(telegram_id=tg_id, username=username)

            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        else:
            return user

    def update_user(self, db: Session, tg_id: int, username: str):
        user = self.get_user_by_tg_id(db, tg_id)
        if user and user.username != username:
            user.username = username
            db.commit()
        return user

    def create_leetcode(self, db: Session, username, total, hard, easy, medium, rating, telegram_id):
        user = self.get_user_by_tg_id(db, telegram_id)
        if user:
            db_leetcode = LeetCode(
                username=username,
                total_solved=total,
                hard_solved=hard,
                easy_solved=easy,
                medium_solved=medium,
                rating=rating,
                user=user
            )
            db.add(db_leetcode)
            db.commit()
            db.refresh(db_leetcode)
            return db_leetcode
        else:
            return None

    def update_leetcode(self, db: Session, total, hard, easy, medium, rating, telegram_id):
        user = self.get_user_by_tg_id(db, telegram_id)
        if user:
            db_leetcode = db.query(LeetCode).filter(LeetCode.user_id == user.id).first()

            if db_leetcode:
                db_leetcode.total_solved = total
                db_leetcode.hard_solved = hard
                db_leetcode.easy_solved = easy
                db_leetcode.medium_solved = medium
                db_leetcode.rating = rating
                db.commit()
                db.refresh(db_leetcode)
                return db_leetcode

    def update_username(self, db: Session, username, telegram_id):
        user = self.get_user_by_tg_id(db, telegram_id)
        if user:
            db_leetcode = db.query(LeetCode).filter(LeetCode.user_id == user.id).first()

            if db_leetcode:
                db_leetcode.username = username
                db.commit()
                db.refresh(db_leetcode)
                return db_leetcode

    def delete_leetcode(self, db: Session, telegram_id):
        user = self.get_user_by_tg_id(db, telegram_id)
        if user:
            db_leetcode = db.query(LeetCode).filter(
                LeetCode.user_id == user.id).first()
            if db_leetcode:
                db.delete(db_leetcode)
                db.commit()
                db.refresh(user)

                return True
            else:
                return False
        return False

    @staticmethod
    def get_users_id(db: Session):
        return [user.telegram_id for user in db.query(User).all()]

    @staticmethod
    def get_top_100_user(db: Session):
        top_users = db.query(User).join(User.leetcode).order_by(LeetCode.rating.desc()).limit(100).all()
        user_ratings = [(user.username, user.leetcode[0].username, user.leetcode[0].rating) for user in top_users]
        return user_ratings
