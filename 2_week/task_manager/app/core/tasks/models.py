from sqlalchemy import Column, INTEGER, VARCHAR, DATETIME, func, ForeignKey
from sqlalchemy.ext.declarative import ConcreteBase, declarative_base

DBBase: ConcreteBase = declarative_base()


class TaskORM(DBBase):

    __tablename__ = "users"

    id = Column(INTEGER(unsigned=True), autoincrement=True, primary_key=True)
    status = Column(VARCHAR(length=50))

    assignee_id = Column("assignee_id", INTEGER(unsigned=True), ForeignKey("workers.id"))
    creator_id = Column("creator_id", INTEGER(unsigned=True), ForeignKey("workers.id"))
    description = Column(VARCHAR(length=100), nullable=True)

    created_at = Column("creat_date", DATETIME, nullable=True, server_default=func.now())


class Worker(DBBase):
    id = Column(INTEGER(unsigned=True), autoincrement=True, primary_key=True)
    user_id = Column(INTEGER())

