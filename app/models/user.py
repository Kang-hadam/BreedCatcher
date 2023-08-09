"""User Model"""
import nanoid
from server_modules.database import Base
from server_modules.model import TimeModel, DeleteTimeModel
from sqlalchemy import Column, String, Integer
from sqlalchemy_utils import PasswordType


class UserModel(Base, TimeModel, DeleteTimeModel):
    """
    유저 모델
    """
    __tablename__ = 'user'
    id: Column = Column(String(21), primary_key=True, default=nanoid.generate, nullable=False,
                        comment='PK')
    username: Column = Column(String(32), index=True, unique=True, nullable=False, comment='접속시 필요한 유저명')
    password: Column = Column(PasswordType(schemes=[
        'pbkdf2_sha512',
        'md5_crypt'
    ], deprecated=['md5_crypt']), nullable=False, comment='비밀번호')
    name: Column = Column(String(32), nullable=False, comment='유저명')
    nickname: Column = Column(String(32), nullable=False, comment='닉네임')
    tier: Column = Column(Integer, nullable=False, comment='권한 0:관리자 1:일반')
    phone: Column = Column(String(16), nullable=False, comment='전화번호')
    email: Column = Column(String(64), nullable=False, comment='이메일')
    sns_type: Column = Column(String(8), nullable=True, comment='sns 회원가입 시 sns 종류')


UserModel.CreateSchema().update(exclude=("created_at", "updated_at", "deleted_at", "id"))
UserModel.GetSchema().update(exclude=("password",))
UserModel.GetAllSchema().update(exclude=("password",))
UserModel.UpdateSchema().update(exclude=("created_at", "updated_at", "deleted_at", "id", "username", "password"))
