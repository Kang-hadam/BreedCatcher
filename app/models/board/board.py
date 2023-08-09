"""User Model"""
from pydantic import Field
from server_modules.database import Base
from server_modules.model import TimeModel, DeleteTimeModel
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship, Mapped

from models.user import UserModel


class BoardModel(Base, TimeModel, DeleteTimeModel):
    """
    게시판 모델
    """
    __tablename__ = 'board'
    idx: Column = Column(Integer, primary_key=True, autoincrement=True, nullable=False,
                         comment='PK')
    writer_id: Column = Column(String(21), ForeignKey('user.id'), nullable=False, comment='작성자 ID')
    title: Column = Column(String(64), nullable=False, comment='제목')
    content: Column = Column(Text, nullable=False, comment='내용')
    view_count: Column = Column(Integer, nullable=False, server_default='0', comment='조회수')
    category: Column = Column(Integer, nullable=False, comment='카테고리')
    notice: Column = Column(Boolean, nullable=False, server_default='0', comment='공지 여부')
    secret: Column = Column(Boolean, nullable=False, server_default='0', comment='비밀 여부')
    password: Column = Column(String(4), nullable=False, server_default='', comment='비밀번호, 비밀 게시글일 경우 사용')

    writer: Mapped[UserModel] = relationship('UserModel')


BoardModel.CreateSchema().update(exclude=("created_at", "updated_at", "deleted_at", "idx",
                                          "view_count", "writer_id"),
                                 include={"password": Field('', min_length=4, max_length=4)})
BoardModel.GetSchema().update(exclude=("password",),
                              include={
                                  'dislike_count': (int, Field(..., title="싫어요 수", description="싫어요 수"),),
                                  'like_count': (int, Field(..., title="좋아요 수", description="좋아요 수"),),
                                  'comment_count': (int, Field(..., title="댓글 수", description="댓글 수"),),
                              })
BoardModel.GetAllSchema().update(exclude=("content", "password"),
                                 include={
                                     'dislike_count': (int, Field(..., title="싫어요 수", description="싫어요 수"),),
                                     'like_count': (int, Field(..., title="좋아요 수", description="좋아요 수"),),
                                     'comment_count': (int, Field(..., title="댓글 수", description="댓글 수"),),
                                 })
BoardModel.UpdateSchema().update(exclude=("created_at", "updated_at", "writer_id",
                                          "idx", "deleted_at", "view_count"),
                                 include={"password": Field('', min_length=4, max_length=4)})
