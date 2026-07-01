from flask import Blueprint, flash,redirect,render_template,url_for,request
from app.blueprints.auth.modules import Credential,History
from app.extension import db,bcrypt
from flask_login import login_required,login_user,current_user,logout_user
from datetime import datetime

auth=Blueprint('auth',__name__,template_folder='templates')

@auth.route('/',methods=['GET','POST'])
def index():
    
    if current_user.is_authenticated:
        return redirect(url_for("book.home"))
    
    if request.method=='GET':
        return render_template("auth/index.html")
    
    if request.method=='POST':
        email=request.form.get("email")
        password=request.form.get("password")
        remember=request.form.get("remember")=='on'
        
        user=Credential.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password,password):
            login_user(user,remember)
            login=History(username=user.username,login_time=datetime.now(),logout_time=None)
            db.session.add(login)
            db.session.commit()
            return redirect(url_for("book.home"))
        else:
            return "Invalid Credential"
        
@auth.route('/register',methods=["GET","POST"])
def register():
    if request.method=="GET":
        return render_template("auth/register.html")
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
        username=request.form.get("username")
        
        existing_e=Credential.query.filter_by(email=email).first()
        existing_u=Credential.query.filter_by(username=username).first()
        
        if existing_e:
            flash("Email already exists","danger")
            return redirect(url_for("auth.index"))
        if existing_u:
            flash("Username already exists","danger")
            return render_template("auth/register.html",email=email,password=password)
        
        hashed_password=bcrypt.generate_password_hash(password).decode("utf-8")
        user=Credential(email=email,password=hashed_password,username=username)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for("auth.index"))
    
@auth.route('/logout')
def logout():
    record = History.query.filter_by(
        username=current_user.username).order_by(History.login_time.desc()).first()
    if record:
        record.logout_time=datetime.now()
        db.session.commit()
        logout_user()
        return redirect(url_for("auth.index"))
        