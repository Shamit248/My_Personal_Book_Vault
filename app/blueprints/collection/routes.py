from app.blueprints.collection.modules import Collection
from app.blueprints.auth.modules import Credential,History
from app.blueprints.book.modules import Book,Userbook
from datetime import date, datetime


from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extension import db

collection = Blueprint('collection', __name__, template_folder='templates')

@collection.route('/<int:cid>')
@login_required
def collection_detail(cid):
    collection = Collection.query.filter_by(
        cid=cid, pid=current_user.pid).first_or_404()
    books = Userbook.query.filter_by(
        cid=cid, pid=current_user.pid).all()
    return render_template("collection/collection_detail.html",
                           collection=collection, books=books)
    # cols = Collection.query.filter_by(pid=current_user.pid).all()
    # books = Userbook.query.filter_by(
    #     cid=cid, pid=current_user.pid).all()
    # return render_template("collection/collections.html", collections=cols)

@collection.route('/create', methods=['POST'])
@login_required
def create_collection():
    name = request.form.get("collection_name", "").strip()
    # if not name:
    #     flash("Collection name cannot be empty.", "warning")
    #     return redirect(url_for('book.home'))

    existing = Collection.query.filter_by(
        pid=current_user.pid, collection_name=name).first()
    if existing:
        flash(f'Collection "{name}" already exists.', "warning")
        return redirect(url_for('book.home'))

    col = Collection(pid=current_user.pid, collection_name=name)
    db.session.add(col)
    db.session.commit()
    flash(f'Collection "{name}" created.', "success")
    return redirect(url_for('book.home'))

@collection.route('/delete/<int:cid>', methods=['POST'])
@login_required
def delete_collection(cid):
    col = Collection.query.filter_by(
        cid=cid, pid=current_user.pid).first_or_404()

    # unlink books instead of deleting them
    Userbook.query.filter_by(cid=cid).update({"cid": None})
    collection_name=col.collection_name
    db.session.delete(col)
    db.session.commit()
    flash(f'Collection "{collection_name}" deleted.', "success")
    return redirect(url_for('book.home'))