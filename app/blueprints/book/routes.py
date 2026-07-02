from flask import Blueprint, flash,redirect,render_template,url_for,request
from app.blueprints.auth.modules import Credential,History
from app.blueprints.book.modules import Book,Userbook
from app.extension import db
from flask_login import login_required,login_user,current_user,logout_user
from datetime import date, datetime
from werkzeug.utils import secure_filename
from uuid import uuid4
import os

book=Blueprint('book',__name__,template_folder='templates')

@book.route('/home',methods=['GET'])
@login_required
def home():
    username=current_user.username
    books=Userbook.query.filter_by(pid=current_user.pid).all()
    if request.method=='GET':
        return render_template("book/home.html",message=f'Welcome,{username}',books=books)

@book.route('/book_add', methods=['GET', 'POST'])
@login_required
def book_add():

    if request.method == 'GET':
        return render_template("book/book_add.html")

    author = request.form.get("author")
    title = request.form.get("title")
    language = request.form.get("language")
    genre = request.form.get("genre", "None")
    description = request.form.get("description", "None")
    page_count = request.form.get("page_count")
    published_year = request.form.get("published_year", "None")

    file = request.files.get("file")

    cover_path = None

    if file and file.filename:
        
        ext = os.path.splitext(file.filename)[1].lower()

        if ext not in [".png", ".jpg", ".jpeg"]:
            flash("Only PNG, JPG and JPEG images are allowed.", "danger")
            return render_template("book/book_add.html")
        
        upload_folder = os.path.join("app", "static", "uploads",current_user.username)
        os.makedirs(upload_folder, exist_ok=True)

        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid4().hex}{ext}"

        file.save(os.path.join(upload_folder, filename))

        cover_path = f"uploads/{current_user.username}/{filename}"

    book_detail = Book.query.filter_by(
        title=title,
        author=author
    ).first()

    if not book_detail:

        book_detail = Book(
            author=author,
            title=title,
            language=language,
            genre=genre,
            description=description,
            page_count=page_count,
            published_year=published_year,
            cover_image=cover_path
        )

        db.session.add(book_detail)
        db.session.commit()

    existing_book = Userbook.query.filter_by(
        pid=current_user.pid,
        bid=book_detail.bid
    ).first()

    if existing_book:
        flash("This book is already in your library.", "warning")
        return redirect(url_for("book.home"))

    return redirect(url_for("book.userbook_details", bid=book_detail.bid))
        
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
        
        title=userbook.book.title
        if userbook.status=="Completed":
            userbook.end_date=date.today()
        
            file = request.files.get("file")

        if file and file.filename:
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in [".png", ".jpg", ".jpeg"]:
                flash("Only PNG, JPG and JPEG images are allowed.", "danger")
                return render_template("book/userbook_update.html",userbook=userbook)
            upload_folder = os.path.join("app","static","uploads",current_user.username)
            os.makedirs(upload_folder, exist_ok=True)
            filename = f"{uuid4().hex}{ext}"
            file.save(os.path.join(upload_folder, filename))
            userbook.book.cover_image = f"uploads/{current_user.username}/{filename}"
        
        db.session.commit()
        flash(f"{title} updated successfully!","success")
        return redirect(url_for("book.home"))

@book.route('/userbook_delete/<int:uid>',methods=['POST'])
@login_required
def userbook_delete(uid):
    userbook=Userbook.query.filter_by(uid=uid,pid=current_user.pid).first_or_404()
    title=userbook.book.title
    db.session.delete(userbook)
    db.session.commit()
    flash(f"{title} removed from the library","success")
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
        
        
        
        
        
        
        
        
        
    