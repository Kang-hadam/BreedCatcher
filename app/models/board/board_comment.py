"""Board Comment Model"""
from pydantic import Field
from server_modules.database import Base
from server_modules.model import TimeModel, DeleteTimeModel
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship, Mapped

from models.board.board import BoardModel
from models.user import UserModel


class BoardCommentModel(Base, TimeModel, DeleteTimeModel):
    """
    게시판 댓글 모델
    """
    __tablename__ = 'board_comment'
    idx: Column = Column(Integer, primary_key=True, autoincrement=True, nullable=False,
                         comment='PK')
    writer_id: Column = Column(String(21), ForeignKey('user.id'), nullable=False, comment='작성자 ID')
    board_idx: Column = Column(Integer, ForeignKey('board.idx'), nullable=False, comment='게시글 IDX')
    content: Column = Column(Text, nullable=False, comment='내용')
    parent_comment_idx: Column = Column(Integer, nullable=True, comment='부모 댓글 IDX')
    secret: Column = Column(Boolean, nullable=False, server_default='0', comment='비밀 여부')

    writer: Mapped[UserModel] = relationship('UserModel')
    board: Mapped[BoardModel] = relationship('BoardModel')


BoardCommentModel.CreateSchema().update(exclude=(
    "created_at", "updated_at", "deleted_at", "idx", "writer_id",
    "board_idx", "parent_comment_idx"))
BoardCommentModel.GetSchema().update(exclude=("password",),
                                     include={
                                         'dislike_count': (int, Field(..., title="싫어요 수", description="싫어요 수"),),
                                         'like_count': (int, Field(..., title="좋아요 수", description="좋아요 수"),),
                                         'comment_count': (int, Field(..., title="댓글 수", description="댓글 수"),),
                                     })
BoardCommentModel.GetAllSchema().update(exclude=("content", "password"),
                                        include={
                                            'dislike_count': (int, Field(..., title="싫어요 수", description="싫어요 수"),),
                                            'like_count': (int, Field(..., title="좋아요 수", description="좋아요 수"),),
                                            'comment_count': (int, Field(..., title="댓글 수", description="댓글 수"),),
                                        })
BoardCommentModel.UpdateSchema().update(exclude=("created_at", "updated_at", "writer_id",
                                                 "idx", "deleted_at", "board_idx", "parent_comment_idx"))
