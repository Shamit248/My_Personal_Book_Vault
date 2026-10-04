from datetime import datetime
from flask_login import UserMixin
from app.extension import db

class Credential(db.Model,UserMixin):
    __tablename__='credential'
    
    pid=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(255),nullable=False,unique=True)
    username=db.Column(db.String(100),nullable=False,unique=True)
    password=db.Column(db.String(100),nullable=False)
    
    history = db.relationship("History",  back_populates="user")
    user_books = db.relationship("Userbook", back_populates="user")
    
    def get_id(self):
        return str(self.pid)
    
class History(db.Model,UserMixin):
    __tablename__='history'
    
    hid=db.Column(db.Integer,primary_key=True)
    pid=db.Column(db.Integer,db.ForeignKey("credential.pid"))
    username=db.Column(db.String(100),nullable=False)
    login_time=db.Column(db.DateTime,default=datetime.now)
    logout_time=db.Column(db.DateTime,nullable=True)
    
    user = db.relationship("Credential", back_populates="history")