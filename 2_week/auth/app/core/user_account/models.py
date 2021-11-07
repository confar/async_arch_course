from app.core.user_account.enums import MailConfirmationStatus
from app.database import DBLBase
from sqlalchemy import Column, ForeignKey, func
from sqlalchemy.dialects.mysql import CHAR, DATETIME, ENUM, INTEGER, TINYINT, VARCHAR
from sqlalchemy.orm import backref, relationship

ANON_USER_ID = 0


class UserSession(DBLBase):

    __tablename__ = "sessions"

    sid = Column("sessid", CHAR(length=32), primary_key=True)
    user_id = Column("user", INTEGER(unsigned=True), ForeignKey("users.id"), default=0)
    last_used_at = Column("last_used", DATETIME, default=func.current_timestamp(), onupdate=func.current_timestamp())
    ip = Column(VARCHAR(length=64), nullable=True)
    is_app = Column(TINYINT(unsigned=True), default=0)
    is_short = Column(TINYINT(unsigned=True), default=0)

    user = relationship("User", lazy="joined", backref=backref("session", uselist=False))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(sid={self.sid}, user_id={self.user_id}"


class Group(DBLBase):

    __tablename__ = "groups"

    id = Column(INTEGER(unsigned=True), primary_key=True)
    name = Column("s_name", VARCHAR(100), nullable=False, unique=True)
    is_reader = Column(TINYINT(1, unsigned=True), default=0, nullable=False)

    users = relationship("User", secondary="groupusers", back_populates="groups")


class User(DBLBase):

    __tablename__ = "users"

    id = Column(INTEGER(unsigned=True), autoincrement=True, primary_key=True)
    email = Column("s_mail", VARCHAR(length=50), nullable=True)
    mail_confirmed_status = Column("mail_confirmed", ENUM(MailConfirmationStatus), default=0, nullable=False)

    login = Column("login", VARCHAR(length=100), nullable=True)
    password = Column("pwd", VARCHAR(length=100), nullable=True)

    full_name = Column("s_full_name", VARCHAR(length=255), nullable=True)
    first_name = Column("s_first_name", VARCHAR(length=100), nullable=True)
    last_name = Column("s_last_name", VARCHAR(length=100), nullable=True)
    middle_name = Column("s_middle_name", VARCHAR(length=100), nullable=True)

    created_at = Column("creat_date", DATETIME, nullable=True, server_default=func.now())

    groups = relationship("Group", secondary="groupusers", back_populates="users")