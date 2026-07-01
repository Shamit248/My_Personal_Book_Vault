from flask import Blueprint, flash,redirect,render_template,url_for,request
from app.blueprints import book
from app.blueprints.auth.modules import Credential,History
from app.blueprints.book.modules import Book,Userbook
from app.extension import db
from flask_login import login_required,login_user,current_user,logout_user
from datetime import date, datetime

book=Blueprint('book',__name__,template_folder='templates')

@book.route('/home',methods=['GET'])
@login_required
def home():
    username=current_user.username
    books=Userbook.query.filter_by(pid=current_user.pid).all()
    if request.method=='GET':
        return render_template("book/home.html",message=f'Welcome,{username}',books=books)

@book.route('/book_add',methods=['GET','POST'])
@login_required
def book_add():
    if request.method=='GET':
        return render_template("book/book_add.html")
    if request.method=='POST':
        author=request.form.get("author")
        title=request.form.get("title")
        language=request.form.get("language")
        genre=request.form.get("genre","None")
        description=request.form.get("description","None")
        page_count=request.form.get("page_count")
        published_year=request.form.get("published_year","None")
        
        book_detail=Book.query.filter_by(title=title,author=author).first()
    
        
        if not book_detail:
            book_detail=Book(author=author,title=title,language=language,genre=genre,description=description,page_count=page_count,published_year=published_year)
            
            db.session.add(book_detail)
            db.session.commit()
            return redirect(url_for("book.userbook_details",bid=book_detail.bid))
        
        existing_book=Userbook.query.filter_by(pid=current_user.pid,bid=book_detail.bid).first()
        
        if existing_book:
              flash("This book is already in your library.", "warning")
              return redirect(url_for("book.home"))  
        return redirect(url_for("book.userbook_details",bid=book_detail.bid))
        
@book.route('/userbook_details/<int:bid>',methods=['GET','POST'])
@login_required
def userbook_details(bid):
    book_detail=Book.query.filter_by(bid=bid).first()
    if request.method=='GET':
        return render_template("book/userbook_details.html",book_detail=book_detail)
    if request.method=='POST':
        current_page=request.form.get("current_page")
        status=request.form.get("status")
        collection=request.form.get("collection")
        note=request.form.get("note","None")
        rating=request.form.get("rating",0)
        
        if status=="Completed":
            enddate=date.today()
        else:
            enddate=None
            
        details=Userbook(pid=current_user.pid,bid=bid,current_page=current_page,status=status,collection=collection,note=note,rating=rating,start_date=date.today(),end_date=enddate)
        db.session.add(details)
        db.session.commit()
        
        return redirect(url_for("book.home"))

@book.route('/userbook_update/<int:uid>',methods=['GET','POST'])
@login_required
def userbook_update(uid):
    userbook=Userbook.query.filter_by(uid=uid,pid=current_user.pid).first_or_404()  
    if request.method=='GET':
        return render_template("book/userbook_update.html",userbook=userbook)
    if request.method=='POST':
        userbook.current_page=request.form.get("current_page")
        userbook.status=request.form.get("status")
        userbook.collection=request.form.get("collection")
        userbook.note=request.form.get("note")
        userbook.rating=request.form.get("rating")
        
        if userbook.status=="Completed":
            userbook.end_date=date.today()
        
        db.session.commit()
        flash("{userbook.book.title} updated successfully!","success")
        return redirect(url_for("book.home"))

@book.route('/userbook_delete/<int:uid>',methods=['GET','POST'])
@login_required
def userbook_delete(uid):
    userbook=Userbook.query.filter_by(uid=uid,pid=current_user.pid).first_or_404()
    db.session.delete(userbook)
    db.session.commit()
    
    flash("{userbook.book.title} removed from the library","success")
    return redirect(url_for("book.home"))
        

@book.route('/logout')
@login_required
def logout():
    record = History.query.filter_by(
    username=current_user.username).order_by(History.login_time.desc()).first()
    if record:
        record.logout_time = datetime.now()
        db.session.commit()
        logout_user()
        return redirect(url_for("auth.index")) 
        
        
        
        
        
        
        
        
        
    