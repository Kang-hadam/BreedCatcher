"""Board Like Model"""
from server_modules.database import Base
from server_modules.model import TimeModel
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped

from models.board.board import BoardModel
from models.user import UserModel


class BoardLikeModel(Base, TimeModel):
    """
    게시판 좋아요 모델

    제거 시점을 알 필요가 없으므로 DeleteTimeModel을 상속하지 않음
    """
    __tablename__ = 'board_like'
    user_id: Column = Column(String(21), ForeignKey('user.id'), nullable=False, primary_key=True, comment='작성자 ID')
    board_idx: Column = Column(Integer, ForeignKey('board.idx'), nullable=False, primary_key=True, comment='게시글 IDX')
    like: Column = Column(Boolean, nullable=False, comment='좋아요/싫어요')

    user: Mapped[UserModel] = relationship('UserModel')
    board: Mapped[BoardModel] = relationship('BoardModel')


BoardLikeModel.CreateSchema().update(exclude=("created_at", "updated_at", "board_idx", "user_id"))
