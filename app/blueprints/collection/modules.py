from app.extension import db
from datetime import datetime
class Collection(db.Model):
    
    __tablename__="collection"
    
    cid=db.Column(db.Integer,primary_key=True)
    pid=db.Column(db.Integer,db.ForeignKey("credential.pid"),nullable=False)
    collection_name=db.Column(db.String(100),nullable=False)
    create_at=db.Column(db.DateTime,default=datetime.utcnow)
   
    user_books = db.relationship("Userbook", back_populates="collection")
    
    __table_args__=(db.UniqueConstraint("pid","collection_name",name="unique_collection"),)
    
    def __repr__(self):
        return f"<Collection {self.collection_name}>"
    