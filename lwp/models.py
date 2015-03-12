import hashlib
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False))
Base = declarative_base()
Base.query = db_session.query_property()

class User(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    username = Column(String(80), unique=True)
    password = Column(String(64))
    admin = Boolean()

    def __init__(self, name, username, password, admin=False):
        self.username = username
        self.password = hashlib.sha256(password).hexdigest()
        self.name = name
        self.admin = admin

    def __repr__(self):
        return '<User %r>' % self.username

    def auth_user(password):
        """
            return True if username/password match with the stored values
        """
        return self.password == hashlib.sha256(password).hexdigest()


    def update_password (old_pass, new_pass):
        pass
