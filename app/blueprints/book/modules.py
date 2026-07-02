from datetime import date
from app.extension import db
from app.blueprints.auth.modules import Credential
class Book(db.Model):
    __tablename__="book"
    bid=db.Column(db.Integer,primary_key=True)
    author=db.Column(db.String(100),nullable=False)
    title=db.Column(db.String(100),nullable=False)
    language=db.Column(db.String(100),nullable=False)
    genre=db.Column(db.String(100),nullable=True)
    description=db.Column(db.Text,nullable=True)
    page_count=db.Column(db.Integer,nullable=False)
    published_year=db.Column(db.Integer,nullable=True)
    cover_image = db.Column(db.String(500), nullable=True)
    
    user_books = db.relationship("Userbook", back_populates="book")
    
    def __repr__(self):
        return f"<Book {self.title}>"
    
class Userbook(db.Model):
    __tablename__="userbook"
    uid=db.Column(db.Integer,primary_key=True)
    pid=db.Column(db.Integer,db.ForeignKey("credential.pid"),nullable=False)
    bid=db.Column(db.Integer,db.ForeignKey("book.bid"),nullable=False)
    # cid=db.Column(db.Integer,db.Foreignkey("collection.cid"),nullable=False)
    current_page=db.Column(db.Integer,nullable=False)
    status=db.Column(db.String(100),nullable=False)
    collection=db.Column(db.String(100),nullable=False)
    note=db.Column(db.Text,nullable=True)
    rating=db.Column(db.Integer,db.CheckConstraint("rating >= 0 AND rating <= 5"),nullable=True)
    start_date=db.Column(db.Date,default=date.today())
    end_date=db.Column(db.Date,nullable=True)
    
    __table_args__=(db.UniqueConstraint("pid","bid",name="unique_user_book"),)
    
    user = db.relationship("Credential", back_populates="user_books")
    
    book = db.relationship("Book",back_populates="user_books")

    def __repr__(self):
        return f"<UserBook pid={self.pid} bid={self.bid}>"
    
       
    
    