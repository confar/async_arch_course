from sqlalchemy import Column, INTEGER, VARCHAR, DATETIME, func
from sqlalchemy.ext.declarative import ConcreteBase, declarative_base

DBBase: ConcreteBase = declarative_base()


class User(DBBase):

    __tablename__ = "users"

    id = Column(INTEGER(unsigned=True), autoincrement=True, primary_key=True)
    email = Column("s_mail", VARCHAR(length=50), nullable=True)

    login = Column("login", VARCHAR(length=100), nullable=True)
    password = Column("pwd", VARCHAR(length=100), nullable=True)

    first_name = Column("s_first_name", VARCHAR(length=100), nullable=True)
    last_name = Column("s_last_name", VARCHAR(length=100), nullable=True)

    created_at = Column("creat_date", DATETIME, nullable=True, server_default=func.now())

