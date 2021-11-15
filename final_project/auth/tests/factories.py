import factory
from sqlalchemy import orm

DBLSession = orm.scoped_session(orm.sessionmaker())


class DBLBaseModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "flush"
        sqlalchemy_session = DBLSession

