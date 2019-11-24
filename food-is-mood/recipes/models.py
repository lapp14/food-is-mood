from pyramid.security import Allow, Everyone

from sqlalchemy import (
    Column,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import register

DBSession = scoped_session(sessionmaker())
register(DBSession)
Base = declarative_base()

class Page(Base):
    __tablename__ = 'wikipages'
    uid = Column(Integer, primary_key=True)
    title = Column(Text, unique=True)
    description = Column(Text)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class Root(object):
    __acl__ = [(Allow, Everyone, 'edit'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass
