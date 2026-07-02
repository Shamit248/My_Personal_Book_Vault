from flask import Blueprint, flash,redirect,render_template,url_for,request
from app.blueprints.auth.modules import Credential,History
from app.blueprints.book.modules import Book,Userbook
from app.extension import db
from flask_login import login_required,login_user,current_user,logout_user
from datetime import date, datetime
import os

collection=Blueprint('collection',__name__,template_folder='templates')

@collection.route('/add_collection')
@login_required
def add_collection():
    return"Hello"